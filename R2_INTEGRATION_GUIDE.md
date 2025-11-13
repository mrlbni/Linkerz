# R2 Storage Integration Guide

## Overview

This guide explains the Cloudflare R2 storage integration that has been added to the Telegram file streaming bot.

## What's New

The bot now integrates with Cloudflare R2 storage to:
1. **Check for duplicate files** before storing
2. **Upload file metadata** to R2 for distributed access
3. **Maintain dual storage** - both PostgreSQL (local) and R2 (cloud)

## Architecture

### Dual Storage System

```
Telegram Channel File → Bot Receives → Check R2
                                         ↓
                          ┌──────────────┴──────────────┐
                          │                             │
                    File EXISTS               File NOT EXISTS
                          │                             │
                          ↓                             ↓
                  Update PostgreSQL                Upload to R2
                  (add bot file_id)                     +
                          +                      Update PostgreSQL
                  Reply: "Already Exists"               +
                                               Reply: "Stored Successfully"
```

## Configuration

### Environment Variables

Add these to your `.env` file or environment:

```bash
# R2 Storage Configuration
R2_Domain=tga-hd.api.hashhackers.com
R2_Folder=linkerz
R2_Public=tg-files-identifier.hashhackers.com
```

- **R2_Domain**: The API endpoint for uploading to R2
- **R2_Folder**: The folder/bucket name in R2 (default: linkerz)
- **R2_Public**: The public URL for checking file existence

## How It Works

### 1. File Upload Flow

When a file is posted in a channel where the bot is added:

1. **Receive File**: Bot detects media (video, audio, document)
2. **Extract Metadata**: Gets unique_file_id, file_id, name, size, etc.
3. **Check R2**: Makes GET request to `https://{R2_Public}/{R2_Folder}/{unique_file_id}.json`
4. **Decision**:
   - If **file exists**: Reply "File Already Exists" + show details
   - If **file NOT exists**: Upload to R2, store in PostgreSQL, reply "Stored Successfully"

### 2. R2 Data Format

Files are stored in R2 with this JSON structure:

```json
{
    "unique_id": "AgAD-A0AAij8UVE",
    "bot_file_ids": {
        "b_1_file_id": "BQACAgQAAx0CaZ9HgwACGQJovW8pV30uZFBM3pcyXd3px7l03wAC...",
        "b_2_file_id": "BQACAgQAAx0CaZ9HgwACGQJovW8pM2PowzL7fw2p06qvnU-KBwAC...",
        "b_3_file_id": "BQACAgQAAx0CaZ9HgwACGQJovW8pjYCpyK7E_GY9hHerHsZmSQAC..."
    },
    "caption": "Movie.2020.1080p.mkv",
    "file_size_bytes": 1774606367,
    "file_type": "document",
    "original_message_id": 6402,
    "source_channel_id": -1001772046211,
    "file_name": "Movie.2020.1080p.mkv",
    "mime_type": "video/x-matroska"
}
```

### 3. Multi-Bot Support

The system supports up to 11 bots (b_1 to b_11):
- Each bot can have a different `file_id` for the same file
- All bot file_ids are collected and uploaded to R2
- This provides redundancy and load distribution

## API Endpoints

### Check File Existence

```
GET https://{R2_Public}/{R2_Folder}/{unique_file_id}.json
```

**Response**:
- `200 OK`: File exists, returns JSON data
- `404 Not Found`: File doesn't exist

### Upload File Data

```
PUT https://{R2_Domain}/tga-r2/{R2_Folder}?id={unique_file_id}
Content-Type: application/json

{
  "unique_id": "...",
  "bot_file_ids": {...},
  ...
}
```

**Response**:
- `200 OK`: Upload successful
- `4xx/5xx`: Upload failed

## Code Structure

### New Files

1. **`WebStreamer/r2_storage.py`**: R2 storage client
   - `check_file_exists()`: Check if file exists in R2
   - `upload_file_data()`: Upload file metadata to R2
   - `format_file_data()`: Format data according to spec

2. **`.env.example`**: Environment variable template

### Modified Files

1. **`WebStreamer/vars.py`**: Added R2 configuration variables
2. **`WebStreamer/bot/plugins/media_handler.py`**: Integrated R2 checks and uploads

## Testing

### Test Script

Run the test script to verify R2 integration:

```bash
cd /app
python3 test_r2_integration.py
```

This will test:
1. Configuration loading
2. File existence checking
3. File upload functionality

### Manual Testing

1. **Start the bot**:
   ```bash
   cd /app
   python3 -m WebStreamer
   ```

2. **Add bot to a channel** where you're an admin

3. **Post a file** in the channel

4. **Check the bot's response**:
   - First time: "📁 File Stored Successfully"
   - Subsequent times: "✅ File Already Exists"

## User Experience

### New File

When a file is posted for the first time:

```
📁 File Stored Successfully

Name: Movie.2020.1080p.mkv
Size: 1.65 GB
Type: video/x-matroska
Location: DC 4

🔗 View and download at: https://your-domain.com/files/AgAD-A0AAij8UVE

[📥 View File]
```

### Existing File

When the same file is posted again:

```
✅ File Already Exists

Name: Movie.2020.1080p.mkv
Size: 1.65 GB
Type: video/x-matroska
Location: DC 4

🔗 View and download at: https://your-domain.com/files/AgAD-A0AAij8UVE

[📥 View File]
```

## Benefits

1. **Deduplication**: Prevents storing duplicate files
2. **Distributed Storage**: Files available via both PostgreSQL and R2
3. **Scalability**: R2 handles large-scale file metadata storage
4. **Redundancy**: Multiple bots = multiple file_ids for same file
5. **Cloud Backup**: File metadata backed up to R2

## Troubleshooting

### R2 Connection Issues

If R2 checks fail:
- Verify `R2_Domain` and `R2_Public` are correct
- Check network connectivity
- Review logs: `/var/log/supervisor/backend.err.log`

### Upload Failures

If uploads to R2 fail:
- Files are still stored in PostgreSQL
- Check R2 API endpoint is accessible
- Verify JSON format is correct

### Configuration Issues

Check environment variables are loaded:
```python
from WebStreamer.vars import Var
print(Var.R2_Domain)
print(Var.R2_Folder)
print(Var.R2_Public)
```

## Monitoring

### Logs

Monitor R2 operations in logs:
```bash
tail -f streambot.log | grep R2
```

Look for:
- `File found in R2: {unique_file_id}`
- `File not found in R2: {unique_file_id}`
- `Successfully uploaded to R2: {unique_file_id}`
- `Failed to upload to R2`

### Database

Check PostgreSQL for stored files:
```sql
SELECT unique_file_id, file_name, file_size, created_at 
FROM media_files 
ORDER BY created_at DESC 
LIMIT 10;
```

## Future Enhancements

Possible improvements:
1. Retry mechanism for failed R2 uploads
2. Periodic sync between PostgreSQL and R2
3. R2 as primary storage with PostgreSQL as cache
4. Webhook notifications on new uploads
5. R2 CDN integration for faster access

## Support

For issues or questions:
1. Check logs: `tail -f streambot.log`
2. Verify configuration: `python3 test_r2_integration.py`
3. Review this guide
4. Check R2 API documentation
