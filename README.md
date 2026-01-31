# Apple Notes to Google Keep Migration

This script migrates your notes from Apple Notes to Google Keep.

## Prerequisites

1. **Python 3.12+** installed on your Mac
2. **uv** package manager ([install here](https://github.com/astral-sh/uv))
3. **Apple Notes** with notes you want to migrate
4. **Google Account** for Google Keep

## Setup

This project uses `uv` for fast dependency management. Everything is already configured!

### 2. Google Account Setup

If you have 2-factor authentication enabled (recommended), you'll need to create an App Password:

1. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
2. Select "Mail" as the app
3. Select "Mac" as the device
4. Click "Generate"
5. Save the 16-character password - you'll use this instead of your regular password

## Usage

### Run the script:

```bash
uv run main.py
```

That's it! `uv` will automatically create a virtual environment and install dependencies on first run.

### The script will:

1. **Extract** all notes from Apple Notes database
2. **Create a backup** JSON file with all your notes
3. **Prompt** for your Google credentials
4. **Upload** each note to Google Keep as an individual note
5. **Report** success/failure for each note

## What Gets Migrated

- ✅ Note titles
- ✅ Note content/body
- ✅ All notes (not deleted)
- ⚠️  Formatting may be simplified (Apple Notes uses rich text)
- ❌ Attachments/images (not supported by gkeepapi)
- ❌ Folder structure (Google Keep uses labels instead)

## Backup

The script automatically creates a timestamped JSON backup file before uploading:
```
apple_notes_backup_YYYYMMDD_HHMMSS.json
```

Keep this file safe in case you need to reference the original data.

## Troubleshooting

### "Apple Notes database not found"
- Make sure you're running this on macOS
- Check that you have notes in the Notes app
- The database location is: `~/Library/Group Containers/group.com.apple.notes/NoteStore.sqlite`

### "Login failed" or authentication errors
- If you have 2FA enabled, use an App Password (see setup above)
- Make sure your Google credentials are correct
- Try logging into Google Keep web interface first to ensure your account is accessible

### Notes content looks garbled
- Apple Notes uses a proprietary protobuf format
- The script does basic text extraction
- Check the backup JSON file to see the raw extracted content
- Some formatting and special characters may not transfer perfectly

## Security Note

- Your Google password is never stored
- The script only runs locally on your machine
- Your notes data stays on your computer (except for the upload to Google Keep)
- Review the backup JSON file to see exactly what will be uploaded

## License

Free to use and modify for personal use.
