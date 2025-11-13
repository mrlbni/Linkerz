# R2 Integration - Quick Reference Card

## 🎯 What Was Done

Added Cloudflare R2 storage integration to your Telegram bot:
- ✅ Check R2 before storing files (avoid duplicates)
- ✅ Upload file metadata to R2 when new files arrive
- ✅ Maintain both PostgreSQL and R2 storage
- ✅ Different user messages for new vs existing files

## 📋 Environment Variables

Add to your `.env` file:

```bash
# R2 Storage (with defaults)
R2_Domain=tga-hd.api.hashhackers.com
R2_Folder=linkerz
R2_Public=tg-files-identifier.hashhackers.com
```

## 🔄 How It Works

```
File Posted → Check R2 → Exists? → Yes → "Already Exists" + Details
                       ↓
                       No → Upload to R2 + PostgreSQL → "Stored Successfully" + Details
```

## 📊 R2 Data Format

```json
{
  "unique_id": "AgAD-A0AAij8UVE",
  "bot_file_ids": {
    "b_1_file_id": "BQACAgQ...",
    "b_2_file_id": "BQACAgQ...",
    ...
  },
  "caption": "filename.mkv",
  "file_size_bytes": 1774606367,
  "file_type": "document",
  "original_message_id": 6402,
  "source_channel_id": -1001772046211,
  "file_name": "filename.mkv",
  "mime_type": "video/x-matroska"
}
```

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your values

# 3. Test R2 integration
python3 test_r2_simple.py

# 4. Run the bot
python3 -m WebStreamer
```

## 📝 Files Changed

**Created:**
- `WebStreamer/r2_storage.py` - R2 client module
- `.env.example` - Environment template
- `test_r2_simple.py` - Test suite
- Documentation files

**Modified:**
- `WebStreamer/vars.py` - Added R2 config
- `WebStreamer/bot/plugins/media_handler.py` - Integrated R2

## 🧪 Testing

```bash
# Test R2 integration
python3 test_r2_simple.py

# Verify all components
./verify_r2_integration.sh
```

## 🔍 API Endpoints

**Check File:**
```
GET https://tg-files-identifier.hashhackers.com/linkerz/{unique_file_id}.json
```

**Upload File:**
```
PUT https://tga-hd.api.hashhackers.com/tga-r2/linkerz?id={unique_file_id}
Content-Type: application/json
Body: {JSON data}
```

## 💬 User Messages

**New File:**
```
📁 File Stored Successfully

Name: movie.mkv
Size: 1.65 GB
Type: video/x-matroska
Location: DC 4

🔗 View and download at: https://...
```

**Existing File:**
```
✅ File Already Exists

Name: movie.mkv
Size: 1.65 GB
Type: video/x-matroska
Location: DC 4

🔗 View and download at: https://...
```

## 🛠️ Troubleshooting

**R2 not working?**
```bash
# Check configuration
python3 -c "from WebStreamer.vars import Var; print(Var.R2_Domain)"

# Check logs
tail -f streambot.log | grep R2

# Test manually
python3 test_r2_simple.py
```

## 📚 Documentation

- `R2_IMPLEMENTATION_SUMMARY.md` - Complete summary
- `R2_INTEGRATION_GUIDE.md` - Detailed guide
- `.env.example` - Configuration template

## ✅ Key Features

✓ Duplicate detection via R2 check
✓ Automatic upload to R2
✓ Dual storage (PostgreSQL + R2)
✓ Multi-bot support (b_1 to b_11)
✓ Proper user feedback
✓ Error handling & fallback

## 🎉 Ready to Use!

The integration is complete and tested. Just:
1. Configure your `.env` file
2. Run the bot
3. Add bot to a channel
4. Post files and see it work!
