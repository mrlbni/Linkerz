# Quick Start Guide

## Testing the Implementation

### 1. Test Database Connection (Local)
```bash
cd /app
python3 test_database.py
```
Expected: ✅ All tests passed successfully! 🎉

### 2. Check Database Table
```bash
python3 << 'EOF'
import psycopg2
conn = psycopg2.connect('postgresql://ub43lrb060grpj:p6b25662823ff195e64587ea3d463bc0481c6f5d923e27771b1de8534307bf5a9@caq9uabolvh3on.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com:5432/d81se6dparnrca')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM media_files")
print(f"Total files in database: {cursor.fetchone()[0]}")
cursor.close()
conn.close()
EOF
```

### 3. Verify Requirements
```bash
cat requirements.txt | grep psycopg2
# Expected: psycopg2-binary==2.9.11
```

### 4. Check Environment Variable
```bash
cat .env | grep DATABASE_URL
# Should show DATABASE_URL=postgresql://...
```

## Deployment Checklist

### Pre-deployment
- [x] Bug fix: BOT_METHOD_INVALID resolved
- [x] Database module created
- [x] Media handler plugin created
- [x] Download endpoint added
- [x] Database table created
- [x] Dependencies installed
- [x] Environment variable set

### Post-deployment (Heroku)
- [ ] Verify bot starts: `heroku logs --tail`
- [ ] Send test file to bot
- [ ] Check database: `heroku pg:psql -c "SELECT * FROM media_files LIMIT 5;"`
- [ ] Test download: `curl https://your-app.herokuapp.com/download/<unique_file_id>`

## Testing on Heroku

### 1. Check Logs
```bash
heroku logs --tail
```
Look for:
- "Successfully connected to PostgreSQL database"
- "Table 'media_files' is ready"
- "Database initialized successfully"

### 2. Send a Test File
Send any video/audio/document to your bot

Check logs for:
```
Stored media: filename.mp4 (unique_id: AgAD..., bot: b_1)
```

### 3. Verify Database
```bash
heroku pg:psql
```
```sql
-- See all files
SELECT unique_file_id, file_name, file_size FROM media_files;

-- Check specific file
SELECT * FROM media_files WHERE unique_file_id = 'YOUR_UNIQUE_ID';
```

### 4. Test Download Endpoint
```bash
# Get unique_file_id from database, then:
curl -v "https://your-app.herokuapp.com/download/<unique_file_id>"
```

Expected response:
- Status: 200 or 206
- Content-Type: video/mp4 (or appropriate type)
- Body: File data stream

## Manual Testing Scenarios

### Scenario 1: Single Bot, Private Message
1. Send video to bot via private message
2. Bot stores file with b_1 = file_id
3. Database has 1 entry, b_1 populated
4. Download works using b_1

### Scenario 2: Multiple Bots, Channel Post
1. Post video in channel (all bots present)
2. Each bot stores its file_id independently
3. Database has 1 entry with b_1, b_2, b_3... populated
4. Download randomly picks from available bots

### Scenario 3: Failover Test
1. Store file with bot 1 (b_1)
2. Add same file with bot 2 (b_2)
3. Stop bot 1
4. Download still works using bot 2

## Quick Commands Reference

### Database Queries
```sql
-- Total files
SELECT COUNT(*) FROM media_files;

-- Recent files
SELECT unique_file_id, file_name, created_at 
FROM media_files 
ORDER BY created_at DESC 
LIMIT 10;

-- Files with multiple bots
SELECT unique_file_id, file_name,
  CASE WHEN b_1 IS NOT NULL THEN 1 ELSE 0 END +
  CASE WHEN b_2 IS NOT NULL THEN 1 ELSE 0 END +
  CASE WHEN b_3 IS NOT NULL THEN 1 ELSE 0 END as bot_count
FROM media_files
WHERE (b_1 IS NOT NULL OR b_2 IS NOT NULL OR b_3 IS NOT NULL);
```

### Heroku Commands
```bash
# View logs
heroku logs --tail --app your-app-name

# Database shell
heroku pg:psql --app your-app-name

# Config vars
heroku config --app your-app-name

# Restart app
heroku restart --app your-app-name
```

### Testing Downloads
```bash
# Basic download
curl -O "https://your-app.herokuapp.com/download/unique_file_id"

# Check headers only
curl -I "https://your-app.herokuapp.com/download/unique_file_id"

# Test range request
curl -H "Range: bytes=0-1024" \
  "https://your-app.herokuapp.com/download/unique_file_id"

# Verbose output
curl -v "https://your-app.herokuapp.com/download/unique_file_id"
```

## Troubleshooting

### Issue: Database connection failed
**Check:**
```bash
heroku config:get DATABASE_URL
```
**Fix:**
```bash
heroku config:set DATABASE_URL="postgresql://..."
```

### Issue: Table doesn't exist
**Fix:**
```bash
heroku pg:psql
CREATE TABLE media_files (...);  # Use schema from FEATURE_DATABASE_STORAGE.md
```

### Issue: Files not being stored
**Check logs:**
```bash
heroku logs --tail | grep "Stored media"
```
**Verify:**
- Bot is running
- Bot is in the channel (for channel posts)
- DATABASE_URL is set
- No errors in logs

### Issue: Download not working
**Debug:**
1. Verify file exists: `SELECT * FROM media_files WHERE unique_file_id = '...'`
2. Check at least one b_X column is not NULL
3. Verify bots are authenticated: Check heroku logs
4. Test endpoint: `curl -v https://...`

## Expected Log Output

### Successful Startup
```
-------------------- Downloading Session File --------------------
[...]
-------------------- Initializing Telegram Bot --------------------
[...]
------------------------------ DONE ------------------------------
-------------------- Uploading Session File --------------------
[...]
---------------------- Initializing Clients ----------------------
[...]
------------------------------ DONE ------------------------------
------------------ Pre-caching BIN_CHANNEL Peer ------------------
[...] Successfully cached BIN_CHANNEL: ChannelName
------------------------------ DONE ------------------------------
-------------------- Initializing Database --------------------
[...] Successfully connected to PostgreSQL database
[...] Table 'media_files' is ready
[...] Database initialized successfully
------------------------------ DONE ------------------------------
[...]
------------------------- Service Started -------------------------
```

### File Storage
```
[...][INFO] => Stored media: video.mp4 (unique_id: AgADYQAD..., bot: b_1)
```

### Download Request
```
[...][INFO] => Download request for unique_file_id: AgADYQAD...
[...][INFO] => Attempting to stream using bot 1, file_id: BQAD...
[...][INFO] => Successfully streaming file using bot 1
```

## Success Indicators

✅ Bot starts without errors  
✅ Database connection successful  
✅ Media files being stored (check logs)  
✅ Download endpoint returns 200/206  
✅ Files stream correctly  
✅ Multiple bots can store same file  

## Support

If issues persist:
1. Check all logs: `heroku logs --tail`
2. Verify database: `heroku pg:psql`
3. Review IMPLEMENTATION_SUMMARY.md
4. Check FEATURE_DATABASE_STORAGE.md

---

**Ready to deploy!** 🚀
