# Deployment Guide - Session Fix Update

## What's Changed

This update fixes critical session handling errors and improves file streaming reliability.

### Fixed Issues:
1. ✅ Session expiry auto-recovery
2. ✅ "Client is already terminated" error
3. ✅ "FileId object has no attribute 'message_id'" warning

---

## Quick Start

### 1. Ensure Environment Variables are Set

Required variables in your deployment environment:

```bash
# Telegram API Credentials
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
BOT_ID=your_bot_id

# GitHub Session Backup (Optional but recommended)
GITHUB_TOKEN=your_github_token
GITHUB_USERNAME=your_username
GITHUB_REPO=your_repo_name

# Other settings
BIN_CHANNEL=your_channel_id
FQDN=your_domain.com
PORT=8080
```

### 2. Deploy the Updated Code

```bash
# Pull latest changes
git pull origin main

# Install dependencies (if needed)
pip install -r requirements.txt

# Run the application
python -m WebStreamer
```

### 3. Monitor Startup Logs

Look for these log messages to confirm proper operation:

**Normal Startup (existing session valid):**
```
-------------------- Downloading Session File --------------------
-------------------- Initializing Telegram Bot --------------------
------------------------------ DONE ------------------------------
-------------------- Uploading Session File --------------------
```

**Session Re-authentication (expired session):**
```
-------------------- Downloading Session File --------------------
-------------------- Initializing Telegram Bot --------------------
WARNING - Session error detected: no such table: version
-------------------- Re-authenticating with Bot Token --------------------
INFO - Deleted corrupted session file: /path/to/session.session
INFO - Successfully re-authenticated with Bot Token
------------------------------ DONE ------------------------------
INFO - New session file uploaded to GitHub successfully
```

---

## Behavior Changes

### Session Handling

**Before:**
- Bot crashed on session expiry
- Required manual deletion of session file
- Manual restart needed

**After:**
- Bot automatically detects session errors
- Deletes corrupted session file
- Re-authenticates using BOT_TOKEN
- Uploads new session to GitHub
- Continues normal operation

### File Streaming

**Before:**
- Pre-validated every file before streaming
- Made extra Telegram API calls
- Sometimes failed with "message_id" attribute errors

**After:**
- Skips pre-validation (file info already in URL)
- Validates during actual streaming
- Reduces API calls
- No more "message_id" warnings

### Cleanup Process

**Before:**
- Could crash with "Client is already terminated"
- Ungraceful shutdown

**After:**
- Checks if client is connected before stopping
- Gracefully handles already-terminated clients
- Clean shutdown logs

---

## Testing the Fix

### Test 1: Session Expiry Recovery

```bash
# 1. Stop the bot
# 2. Delete or corrupt the session file
rm *.session

# 3. Start the bot
python -m WebStreamer

# 4. Check logs - should see re-authentication
# 5. Verify new session file created
ls *.session

# 6. Check GitHub - new session should be uploaded
```

### Test 2: File Streaming

```bash
# Test a file download
curl -I "https://your-domain.com/dl/unique_id/file_id/size/filename.ext"

# Should return 200 or 206 (partial content)
# Check logs - no "message_id" warnings
```

### Test 3: Graceful Shutdown

```bash
# Start the bot
python -m WebStreamer

# Stop it (Ctrl+C or SIGTERM)
# Check logs - should see clean shutdown
# No "already terminated" errors
```

---

## Troubleshooting

### Issue: Bot still fails on startup

**Symptoms:**
```
ERROR - Failed to re-authenticate: [some error]
```

**Solutions:**
1. Verify BOT_TOKEN is correct and active
2. Check API_ID and API_HASH are valid
3. Ensure bot has proper permissions
4. Check network connectivity to Telegram servers

### Issue: Session not uploaded to GitHub

**Symptoms:**
```
WARNING - Failed to upload new session to GitHub
```

**Solutions:**
1. Verify GITHUB_TOKEN has write permissions
2. Check GITHUB_USERNAME and GITHUB_REPO are correct
3. Ensure repository exists and is accessible
4. Check network connectivity to GitHub

### Issue: Files still showing validation warnings

**Symptoms:**
- Warnings about file attributes in logs

**Solutions:**
1. Ensure you're running the updated code
2. Check stream_routes.py line 328-330 for the new logging
3. Restart the bot to load new code
4. Clear any cached Python bytecode: `find . -type d -name __pycache__ -exec rm -rf {} +`

---

## Rollback Instructions

If you need to rollback to previous version:

```bash
# 1. Git rollback
git revert HEAD

# 2. Or restore from backup
git checkout <previous-commit-hash>

# 3. Restart the bot
python -m WebStreamer
```

**Note:** Previous version will still have session expiry issues.

---

## Performance Impact

✅ **Positive Impacts:**
- Reduced Telegram API calls (removed pre-validation)
- Faster file streaming start
- Automatic recovery = less downtime

⚠️ **Considerations:**
- First session error will take ~5-10 seconds to re-authenticate
- GitHub upload adds ~1-2 seconds to startup
- Overall: Minimal impact, better reliability

---

## Support

For issues or questions:
1. Check logs for error messages
2. Review SESSION_FIX_SUMMARY.md for technical details
3. Test with test_session_fix.py to verify logic
4. Check GitHub repository for session file

---

## Next Steps

After deployment:
1. ✅ Monitor logs for first 24 hours
2. ✅ Test file downloads
3. ✅ Verify session persistence
4. ✅ Document any issues
5. ✅ Update monitoring/alerting if needed

---

**Last Updated:** December 2024
**Version:** 2.0 (Session Fix)
