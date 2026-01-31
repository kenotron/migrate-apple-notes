#!/usr/bin/env python3
"""
Script to migrate notes from Apple Notes to Google Keep.
Requires: pip install gkeepapi
"""

import sqlite3
import os
import gzip
import json
from pathlib import Path
from datetime import datetime
import getpass

try:
    import gkeepapi
except ImportError:
    print("Please install gkeepapi: pip install gkeepapi")
    exit(1)


def extract_apple_notes():
    """Extract notes from Apple Notes SQLite database."""
    # Apple Notes database location
    notes_db = os.path.expanduser(
        "~/Library/Group Containers/group.com.apple.notes/NoteStore.sqlite"
    )

    if not os.path.exists(notes_db):
        print(f"Error: Apple Notes database not found at {notes_db}")
        return []

    # Connect to the database
    conn = sqlite3.connect(notes_db)
    cursor = conn.cursor()

    # Query to get notes with their content
    # The ZICNOTEDATA table contains the actual note content (gzipped)
    # The ZICCLOUDSYNCINGOBJECT table contains metadata
    query = """
    SELECT
        ZICCLOUDSYNCINGOBJECT.ZTITLE1 as title,
        ZICCLOUDSYNCINGOBJECT.ZSNIPPET as snippet,
        ZICNOTEDATA.ZDATA as data,
        ZICCLOUDSYNCINGOBJECT.ZCREATIONDATE1 as created,
        ZICCLOUDSYNCINGOBJECT.ZMODIFICATIONDATE1 as modified
    FROM ZICCLOUDSYNCINGOBJECT
    LEFT JOIN ZICNOTEDATA ON ZICCLOUDSYNCINGOBJECT.Z_PK = ZICNOTEDATA.ZNOTE
    WHERE ZICCLOUDSYNCINGOBJECT.ZTITLE1 IS NOT NULL
    AND ZICCLOUDSYNCINGOBJECT.ZMARKEDFORDELETION = 0
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    notes = []
    for row in rows:
        title, snippet, data, created, modified = row

        # Extract note content
        content = ""
        if data:
            try:
                # Apple Notes data is gzipped
                decompressed = gzip.decompress(data)
                # Try to decode as text
                content = decompressed.decode('utf-8', errors='ignore')
                # Clean up the content (remove protobuf artifacts)
                # This is a basic cleanup - Apple Notes uses protobuf format
                content = ''.join(char for char in content if char.isprintable() or char in '\n\r\t')
            except Exception as e:
                print(f"Warning: Could not decompress note '{title}': {e}")
                content = snippet if snippet else ""
        else:
            content = snippet if snippet else ""

        notes.append({
            'title': title or 'Untitled',
            'content': content,
            'created': created,
            'modified': modified
        })

    conn.close()
    print(f"Extracted {len(notes)} notes from Apple Notes")
    return notes


def upload_to_google_keep(notes, username, password):
    """Upload notes to Google Keep."""
    print("\nConnecting to Google Keep...")
    keep = gkeepapi.Keep()

    try:
        # Login to Google Keep
        keep.login(username, password)
        print("Successfully logged in to Google Keep")
    except Exception as e:
        print(f"Error logging in to Google Keep: {e}")
        print("\nNote: If you have 2FA enabled, you need to use an App Password:")
        print("1. Go to https://myaccount.google.com/apppasswords")
        print("2. Generate a new app password for 'Mail'")
        print("3. Use that password instead of your regular password")
        return False

    print(f"\nUploading {len(notes)} notes to Google Keep...")

    success_count = 0
    failed_count = 0

    for i, note_data in enumerate(notes, 1):
        try:
            # Create a new note in Google Keep
            gnote = keep.createNote(
                title=note_data['title'],
                text=note_data['content']
            )

            print(f"[{i}/{len(notes)}] Uploaded: {note_data['title'][:50]}")
            success_count += 1

        except Exception as e:
            print(f"[{i}/{len(notes)}] Failed to upload '{note_data['title']}': {e}")
            failed_count += 1

    # Sync changes
    try:
        keep.sync()
        print("\nSync completed!")
    except Exception as e:
        print(f"\nWarning: Sync error: {e}")

    print(f"\nResults: {success_count} succeeded, {failed_count} failed")
    return True


def save_backup(notes):
    """Save a JSON backup of the notes."""
    backup_file = f"apple_notes_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)

    print(f"\nBackup saved to: {backup_file}")


def main():
    print("=" * 60)
    print("Apple Notes to Google Keep Migration Tool")
    print("=" * 60)

    # Step 1: Extract notes from Apple Notes
    print("\nStep 1: Extracting notes from Apple Notes...")
    notes = extract_apple_notes()

    if not notes:
        print("No notes found or error reading Apple Notes database.")
        return

    # Step 2: Save backup
    print("\nStep 2: Creating backup...")
    save_backup(notes)

    # Step 3: Get Google credentials
    print("\nStep 3: Google Keep login")
    print("-" * 60)
    username = input("Enter your Google email: ").strip()
    password = getpass.getpass("Enter your Google password (or App Password): ")

    # Step 4: Upload to Google Keep
    print("\nStep 4: Uploading to Google Keep...")
    print("-" * 60)

    upload_to_google_keep(notes, username, password)

    print("\n" + "=" * 60)
    print("Migration complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
