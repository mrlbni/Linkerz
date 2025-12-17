# Session Re-Authentication GitHub Upload Fix

## Problem
When authentication expires and the bot performs re-authentication, a new session file is created but it's NOT being uploaded to GitHub. This causes the bot to re-authenticate on every restart because it keeps downloading the old expired session from GitHub.

## Root Cause Analysis
1. **Session file not fully committed**: Pyrogram uses SQLite for session storage. When `bot.start()` completes, the session file may still be in the process of being written to disk by SQLite's write-ahead log (WAL) mechanism.

2. **Immediate upload too early**: The original code attempted to upload the session file immediately after `bot.start()` completed, but SQLite might not have fully flushed the data to disk yet.

3. **Missing visibility**: The logging wasn't showing up on Heroku, making it difficult to diagnose what was happening during re-authentication.

## Solution Implemented

### 1. Force Session Commit (Lines 157-169)
After successful re-authentication, we now:
- **Stop the bot** (`await StreamBot.stop()`) - This forces SQLite to close and commit the session file
- **Wait 3 seconds** - Ensures all file system operations complete
- **Restart the bot** - Loads the now-committed session file
- This guarantees the session file is fully written before upload

```python
# CRITICAL: Stop and restart bot to ensure session is fully committed to disk
await StreamBot.stop()
await asyncio.sleep(3)
await StreamBot.start()
```

### 2. Enhanced Upload Retry Logic (Lines 183-211)
- Increased upload attempts from 3 to **5 attempts**
- Increased wait time between attempts from 2 to **3 seconds**
- Better error logging with explicit success/failure messages
- While loop ensures we retry until success or max attempts

### 3. Explicit Heroku-Compatible Logging (Throughout)
Added `print()` statements with `flush=True` at every critical step:
```python
print(f"[REAUTH] Starting bot with fresh session", flush=True)
print(f"[REAUTH] ✓✓✓ UPLOAD SUCCESS ✓✓✓", flush=True)
```
This ensures logs appear on Heroku even if the logging module has buffering issues.

### 4. Skip Duplicate Upload in STEP 3 (Lines 224-227)
When `session_retry=True`, STEP 3 now skips the upload since it was already completed in STEP 2B:
```python
if session_retry:
    log_flush("! Session was re-authenticated, upload already completed in STEP 2B")
    print(f"[UPLOAD] Skipping STEP 3 upload (already done in STEP 2B)", flush=True)
```

## What to Expect After Fix

### Normal Logs During Re-Authentication
```
[SESSION ERROR] Detected: OperationalError
[SESSION ERROR] Message: no such table: version
[SESSION ERROR] Identified as session error, starting re-auth process
[REAUTH] STEP 2B: Starting re-authentication
[REAUTH] Deleting old session files
[REAUTH] Starting bot with fresh session
[REAUTH] Bot.start() completed
[REAUTH] Bot.get_me() completed: YourBotName
[REAUTH] RE-AUTHENTICATION SUCCESSFUL
[REAUTH] Stopping bot to commit session
[REAUTH] Bot stopped, waiting...
[REAUTH] Restarting bot
[REAUTH] Bot restarted successfully
[REAUTH] Session file size: 12288 bytes
[REAUTH] Starting GitHub upload
[REAUTH] Upload attempt 1/5
[GitHub Upload] ✓✓✓ SUCCESS! File uploaded to GitHub
[REAUTH] ✓✓✓ UPLOAD SUCCESS ✓✓✓
```

### Expected Behavior
1. When auth expires, bot detects the error
2. Deletes old session files
3. Re-authenticates with BOT_TOKEN
4. **Stops and restarts to commit session**
5. **Uploads new session to GitHub** (with up to 5 retry attempts)
6. On next restart, downloads the new valid session from GitHub
7. **No more repeated re-authentication loops**

## Testing
After deploying this fix:
1. Trigger a re-authentication (or wait for natural auth expiry)
2. Check logs for `[REAUTH]` prefixed messages
3. Verify you see `[REAUTH] ✓✓✓ UPLOAD SUCCESS ✓✓✓`
4. Restart the bot - it should NOT re-authenticate again
5. Check your GitHub repo to confirm the session file has been updated (check commit timestamp)

## Files Modified
- `/app/WebStreamer/__main__.py` - Main bot startup and re-authentication logic
  - Lines 102-128: Added print statements for visibility
  - Lines 130-215: Implemented stop/restart cycle and enhanced upload
  - Lines 224-227: Skip duplicate upload in STEP 3
