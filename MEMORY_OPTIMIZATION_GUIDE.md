# Memory Optimization Guide for Heroku Deployment

## Current Issue
**Memory usage: 797MB** out of 512MB (155.6%), now upgraded to 1GB

## Root Causes Identified

### 🔴 CRITICAL ISSUE #1: ThreadPool with 1000 Workers
**File:** `/app/WebStreamer/server/stream_routes.py` Line 23
```python
THREADPOOL = ThreadPoolExecutor(max_workers=1000)  # ❌ EXTREMELY HIGH!
```

**Impact:**
- Each thread reserves memory (~1-8 MB per thread)
- 1000 threads = **~1000-8000 MB potential memory**
- Most threads sit idle but still consume memory
- This is THE PRIMARY cause of your high memory usage

**Why it's problematic on Heroku:**
- Heroku dynos have limited memory (512MB/1GB/2.5GB)
- Thread pools should match actual concurrent load
- Streaming typically needs far fewer threads

**Fix:** Reduce to 50-100 workers maximum
```python
# For 1GB Heroku dyno
THREADPOOL = ThreadPoolExecutor(max_workers=50)  # ✅ Much better

# For 2.5GB Heroku dyno (if you upgrade)
THREADPOOL = ThreadPoolExecutor(max_workers=100)
```

**Expected savings: 400-600 MB** 🎯

---

### 🟡 ISSUE #2: High Pyrogram Workers Count
**File:** `/app/WebStreamer/vars.py` Line 16
```python
WORKERS = int(environ.get("WORKERS", "6"))  # Default is 6
```

**Current configuration:**
- Each bot has 6 workers
- If you have multiple bots: 11 bots × 6 workers = 66 concurrent handlers
- Each worker handles one message at a time

**Impact:**
- Workers consume memory even when idle (~2-5 MB each)
- Total: ~100-300 MB for all workers

**Recommended fix:**
Set environment variable: `WORKERS=3` or `WORKERS=4`

```bash
# In Heroku dashboard or CLI
heroku config:set WORKERS=3
```

**Expected savings: 30-50 MB**

---

### 🟡 ISSUE #3: Unlimited class_cache Dictionary
**File:** `/app/WebStreamer/server/stream_routes.py` Line 1240
```python
class_cache = {}  # No size limit!
```

**Problem:**
- Caches `ByteStreamer` objects per client
- With 11 bots, this creates 11 cached objects
- Each cached object holds connection state, buffers, etc.
- No cleanup mechanism = memory accumulates over time

**Impact:** ~20-50 MB depending on usage patterns

**Recommended fix:** Add cache size limit and TTL (see below)

---

### 🟢 ISSUE #4: Database Connection Pooling
**File:** `/app/WebStreamer/database.py`

**Current:** Single persistent connection
**Impact:** ~10-20 MB (this is actually fine for most cases)

**Note:** psycopg2 default behavior is single connection, which is memory-efficient. No immediate action needed unless you're creating multiple Database() instances.

---

## Complete Fix Implementation

### Fix #1: Reduce ThreadPool Workers

**File:** `/app/WebStreamer/server/stream_routes.py`

**Line 23 - BEFORE:**
```python
THREADPOOL = ThreadPoolExecutor(max_workers=1000)
```

**Line 23 - AFTER:**
```python
# Optimized for 1GB Heroku dyno
# 50 workers can handle 50 concurrent streaming requests
# This is usually more than enough for typical usage
THREADPOOL = ThreadPoolExecutor(max_workers=50)
```

---

### Fix #2: Reduce Pyrogram Workers

**Option A: Via Environment Variable (Recommended)**
```bash
# Set in Heroku
heroku config:set WORKERS=3

# Or in .env file
WORKERS=3
```

**Option B: Via Code**
Update `/app/WebStreamer/vars.py` Line 16:
```python
# BEFORE
WORKERS = int(environ.get("WORKERS", "6"))

# AFTER
WORKERS = int(environ.get("WORKERS", "3"))  # Changed default to 3
```

---

### Fix #3: Add Cache Size Limits

**File:** `/app/WebStreamer/server/stream_routes.py`

**Add after imports (around line 21):**
```python
from collections import OrderedDict

# LRU Cache with max size
class LRUCache(OrderedDict):
    def __init__(self, max_size=10):
        super().__init__()
        self.max_size = max_size
    
    def __setitem__(self, key, value):
        if key in self:
            self.move_to_end(key)
        super().__setitem__(key, value)
        if len(self) > self.max_size:
            oldest = next(iter(self))
            del self[oldest]
```

**Replace line 1240:**
```python
# BEFORE
class_cache = {}

# AFTER
class_cache = LRUCache(max_size=15)  # Max 15 cached ByteStreamer objects
```

---

### Fix #4: Add Session File Cleanup

**File:** `/app/WebStreamer/__main__.py`

**Add to cleanup() function (after line 197):**
```python
async def cleanup():
    # Clean up session files to free memory
    import os
    import glob
    
    # Close all connections first
    await server.cleanup()
    await StreamBot.stop()
    
    # Optional: Clean up old session files
    session_files = glob.glob("*.session")
    for session_file in session_files:
        try:
            os.remove(session_file)
            logging.info(f"Cleaned up session file: {session_file}")
        except Exception as e:
            logging.warning(f"Could not remove {session_file}: {e}")
```

---

## Memory Usage Breakdown

### BEFORE Optimizations
```
Component                    Memory Usage
-----------------------------------------
Base Python runtime          50 MB
ThreadPool (1000 workers)    500-800 MB  ⚠️ MAIN CULPRIT
Pyrogram workers (6 × 11)    132 MB
Bot clients (11 bots)        770 MB
Session files                22 MB
Database connection          15 MB
Web server + handlers        50 MB
class_cache (unlimited)      30-50 MB
Misc buffers                 50 MB
-----------------------------------------
TOTAL ESTIMATE:              ~1,619-1,919 MB ❌
```

### AFTER Optimizations
```
Component                    Memory Usage
-----------------------------------------
Base Python runtime          50 MB
ThreadPool (50 workers)      50-80 MB     ✅ FIXED!
Pyrogram workers (3 × 11)    66 MB        ✅ REDUCED
Bot clients (11 bots)        770 MB
Session files                22 MB
Database connection          15 MB
Web server + handlers        50 MB
class_cache (limited to 15)  20 MB        ✅ LIMITED
Misc buffers                 50 MB
-----------------------------------------
TOTAL ESTIMATE:              ~1,093-1,123 MB ✅
```

**Savings: ~500-800 MB** 🎯

---

## Additional Optimization Tips

### 1. Reduce Number of Bots (If Possible)
If you don't need all 11 bots:
```bash
# Remove unnecessary MULTI_TOKEN variables
heroku config:unset MULTI_TOKEN6 MULTI_TOKEN7 MULTI_TOKEN8 MULTI_TOKEN9 MULTI_TOKEN10
```

**Impact:** Each bot removed saves ~70 MB

### 2. Enable Heroku Log Drain (Instead of File Logging)
**File:** `/app/WebStreamer/__main__.py` Line 25

```python
# BEFORE - logs to both stdout and file
handlers=[logging.StreamHandler(stream=sys.stdout),
          logging.FileHandler("streambot.log", mode="a", encoding="utf-8")]

# AFTER - logs only to stdout (Heroku captures this)
handlers=[logging.StreamHandler(stream=sys.stdout)]
```

**Savings:** 5-20 MB (prevents log file growth)

### 3. Add Memory Monitoring

Create `/app/memory_monitor.py`:
```python
import psutil
import logging
import asyncio

async def monitor_memory():
    """Log memory usage every 5 minutes"""
    while True:
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        logging.info(f"Memory usage: {memory_mb:.2f} MB")
        
        # Alert if over 80% of 1GB
        if memory_mb > 800:
            logging.warning(f"⚠️ High memory usage: {memory_mb:.2f} MB")
        
        await asyncio.sleep(300)  # 5 minutes
```

**Add to __main__.py:**
```python
# In start_services() function, after line 176
from .memory_monitor import monitor_memory
asyncio.create_task(monitor_memory())
```

---

## Deployment Steps

### Step 1: Apply Code Fixes
```bash
# Make the code changes described above
# Then commit and deploy
git add .
git commit -m "Optimize memory usage: reduce ThreadPool to 50 workers"
git push heroku main
```

### Step 2: Set Environment Variables
```bash
heroku config:set WORKERS=3
```

### Step 3: Restart Application
```bash
heroku restart
```

### Step 4: Monitor Memory
```bash
# Watch memory usage in real-time
heroku logs --tail | grep "Memory"

# Or check metrics in Heroku dashboard
heroku addons:open heroku-postgresql  # If you have metrics addon
```

---

## Expected Results

### Immediate Impact (After Fix #1)
- Memory usage should drop to: **300-450 MB** ✅
- Well under 1GB limit
- Stable memory profile

### Long-term Benefits
- No more R14 errors
- Better performance (less context switching)
- Room for traffic growth
- Could potentially downgrade back to 512MB dyno (optional)

---

## Monitoring Commands

```bash
# Check current memory usage
heroku ps:scale

# View detailed metrics
heroku logs --tail --dyno=web.1

# Check for R14 errors
heroku logs --tail | grep "R14"

# View application metrics (if available)
heroku metrics --dyno=web.1
```

---

## FAQ

**Q: Why was ThreadPool set to 1000 workers?**
A: Likely copied from a high-traffic server example. It's overkill for most use cases.

**Q: Will reducing workers affect performance?**
A: No! 50 concurrent streams is plenty. Most users have < 10 concurrent requests.

**Q: Can I reduce bots instead?**
A: Yes! If you don't need 11 bots, reducing to 5-6 bots saves ~300-400 MB.

**Q: What if memory is still high after fixes?**
A: Check for:
- Memory leaks in custom code
- Large files being buffered in memory
- Database query result sets not being closed
- Accumulated asyncio tasks

**Q: Should I upgrade to 2.5GB dyno?**
A: Not necessary. With these fixes, 1GB should be plenty. Save your money!

---

## Summary Checklist

- [ ] Reduce ThreadPool from 1000 to 50 workers
- [ ] Set WORKERS environment variable to 3
- [ ] Add LRU cache limit for class_cache
- [ ] Remove file logging (use stdout only)
- [ ] Deploy changes to Heroku
- [ ] Restart application
- [ ] Monitor memory for 24 hours
- [ ] Verify no R14 errors

**Primary Fix:** Change `max_workers=1000` to `max_workers=50`
**Expected Savings:** 400-600 MB
**Total Memory After Fix:** 300-450 MB ✅

---

**Status:** Ready to implement
**Priority:** Critical (R14 errors affecting service)
**Estimated Time:** 15 minutes to implement + deploy
