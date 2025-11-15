#!/usr/bin/env python3
"""
Test script to verify worker configuration
Run this to check current worker settings
"""

import os
import sys

print("=" * 60)
print("Worker Configuration Test")
print("=" * 60)
print()

# Check environment variables
threadpool_workers = os.environ.get("THREADPOOL_WORKERS", "250")
pyrogram_workers = os.environ.get("WORKERS", "6")
cache_size = os.environ.get("LRU_CACHE_SIZE", "50")

print("📊 Current Configuration (from environment or defaults):")
print(f"  • THREADPOOL_WORKERS: {threadpool_workers}")
print(f"  • WORKERS (Pyrogram): {pyrogram_workers}")
print(f"  • LRU_CACHE_SIZE: {cache_size}")
print()

# Try to import and check actual values
try:
    sys.path.insert(0, '/app')
    
    # Check vars.py
    from WebStreamer.vars import Var
    print("✅ WebStreamer.vars imported successfully")
    print(f"  • Var.WORKERS: {Var.WORKERS}")
    print()
    
except Exception as e:
    print(f"⚠️  Could not import WebStreamer.vars: {e}")
    print("   (This is expected if API_ID/API_HASH not set)")
    print()

# Calculate memory estimate
try:
    threadpool_mem = int(threadpool_workers) * 1  # ~1MB per worker
    pyrogram_mem = int(pyrogram_workers) * 15  # ~15MB per worker
    cache_mem_min = int(cache_size) * 2  # ~2-5MB per cache entry
    cache_mem_max = int(cache_size) * 5
    
    base_mem = 300  # Bot clients and other components
    
    total_min = base_mem + threadpool_mem + pyrogram_mem + cache_mem_min
    total_max = base_mem + threadpool_mem + pyrogram_mem + cache_mem_max
    
    print("💾 Estimated Memory Usage:")
    print(f"  • ThreadPool: ~{threadpool_mem} MB")
    print(f"  • Pyrogram Workers: ~{pyrogram_mem} MB")
    print(f"  • LRU Cache: ~{cache_mem_min}-{cache_mem_max} MB")
    print(f"  • Bot Clients & Other: ~{base_mem} MB")
    print(f"  • TOTAL ESTIMATED: ~{total_min}-{total_max} MB")
    print()
    
    if total_max > 800:
        print("⚠️  WARNING: Estimated memory may exceed 800MB under load")
        print("   Consider reducing workers if you see R14 errors")
    elif total_max > 700:
        print("✅ Memory usage is within acceptable range (700-800MB)")
    else:
        print("✅ Memory usage looks good (<700MB)")
    print()
    
except Exception as e:
    print(f"⚠️  Could not calculate memory estimate: {e}")
    print()

# Performance recommendations
print("🎯 Performance Profile:")
threadpool_int = int(threadpool_workers)
if threadpool_int >= 250:
    print(f"  • {threadpool_int} ThreadPool workers → Handles 500+ concurrent streams")
elif threadpool_int >= 150:
    print(f"  • {threadpool_int} ThreadPool workers → Handles 200-400 concurrent streams")
elif threadpool_int >= 100:
    print(f"  • {threadpool_int} ThreadPool workers → Handles 100-200 concurrent streams")
else:
    print(f"  ⚠️  {threadpool_int} ThreadPool workers → May experience timeouts with high load")

pyrogram_int = int(pyrogram_workers)
if pyrogram_int >= 6:
    print(f"  • {pyrogram_int} Pyrogram workers → Fast message reply handling")
elif pyrogram_int >= 4:
    print(f"  • {pyrogram_int} Pyrogram workers → Good message handling")
else:
    print(f"  ⚠️  {pyrogram_int} Pyrogram workers → May experience reply delays")

print()

# Configuration recommendations
print("🔧 To adjust configuration (Heroku):")
print("  heroku config:set THREADPOOL_WORKERS=250")
print("  heroku config:set WORKERS=6")
print("  heroku config:set LRU_CACHE_SIZE=50")
print()

print("📚 For more info, see:")
print("  /app/PERFORMANCE_OPTIMIZATION_APPLIED.md")
print()

print("=" * 60)
