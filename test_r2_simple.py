#!/usr/bin/env python3
"""
Simple R2 Storage Test - Tests R2 module without full bot setup
"""

import os
import sys
import requests

# Set minimal environment variables for testing
os.environ['API_ID'] = '12345'
os.environ['API_HASH'] = 'test_hash'
os.environ['BOT_TOKEN'] = 'test_token'
os.environ['BIN_CHANNEL'] = '123456'
os.environ['BIN_CHANNEL_WITHOUT_MINUS'] = '123456'
os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost:5432/test'

# R2 Configuration (you can override these)
os.environ['R2_Domain'] = os.environ.get('R2_Domain', 'tga-hd.api.hashhackers.com')
os.environ['R2_Folder'] = os.environ.get('R2_Folder', 'linkerz')
os.environ['R2_Public'] = os.environ.get('R2_Public', 'tg-files-identifier.hashhackers.com')

# Now import after setting env vars
from WebStreamer.vars import Var
from WebStreamer.r2_storage import get_r2_storage

def test_configuration():
    """Test R2 configuration"""
    print("\n" + "=" * 70)
    print("R2 STORAGE CONFIGURATION TEST")
    print("=" * 70)
    
    print(f"✓ R2_Domain:  {Var.R2_Domain}")
    print(f"✓ R2_Folder:  {Var.R2_Folder}")
    print(f"✓ R2_Public:  {Var.R2_Public}")
    print()

def test_check_file():
    """Test checking if a file exists"""
    print("=" * 70)
    print("R2 FILE CHECK TEST")
    print("=" * 70)
    
    r2 = get_r2_storage()
    
    # Test with the example unique_file_id from requirements
    test_file_id = "AgAD-A0AAij8UVE"
    check_url = f"https://{Var.R2_Public}/{Var.R2_Folder}/{test_file_id}.json"
    
    print(f"Testing file ID: {test_file_id}")
    print(f"Check URL: {check_url}")
    print()
    
    result = r2.check_file_exists(test_file_id)
    
    if result:
        print("✅ SUCCESS: File EXISTS in R2")
        print(f"\nFile Data:")
        print(f"  - Unique ID: {result.get('unique_id')}")
        print(f"  - File Name: {result.get('file_name')}")
        print(f"  - File Size: {result.get('file_size_bytes')} bytes")
        print(f"  - File Type: {result.get('file_type')}")
        print(f"  - MIME Type: {result.get('mime_type')}")
        print(f"  - Bot File IDs: {len(result.get('bot_file_ids', {}))} bots")
        for bot_key, file_id in result.get('bot_file_ids', {}).items():
            print(f"    • {bot_key}: {file_id[:40]}...")
    else:
        print("ℹ️  File NOT FOUND in R2 (expected for new/non-existent files)")
    print()

def test_format_data():
    """Test data formatting"""
    print("=" * 70)
    print("R2 DATA FORMAT TEST")
    print("=" * 70)
    
    r2 = get_r2_storage()
    
    # Create sample data
    test_data = r2.format_file_data(
        unique_file_id="TEST_AgAD123456",
        bot_file_ids={
            "b_1_file_id": "BQACAgQAAx0CaZ9HgwACGQJovW8pV30uZFBM3pcyXd3px7l03wAC",
            "b_2_file_id": "BQACAgQAAx0CaZ9HgwACGQJovW8pM2PowzL7fw2p06qvnU-KBwAC"
        },
        caption="Test Movie File",
        file_size=1774606367,
        file_type="document",
        message_id=12345,
        channel_id=-1001234567890,
        file_name="Test.Movie.2020.1080p.mkv",
        mime_type="video/x-matroska"
    )
    
    print("Sample formatted data:")
    import json
    print(json.dumps(test_data, indent=2))
    print()
    
    # Validate structure
    required_fields = [
        'unique_id', 'bot_file_ids', 'caption', 'file_size_bytes',
        'file_type', 'original_message_id', 'source_channel_id',
        'file_name', 'mime_type'
    ]
    
    missing = [field for field in required_fields if field not in test_data]
    
    if not missing:
        print("✅ SUCCESS: All required fields present")
    else:
        print(f"❌ ERROR: Missing fields: {missing}")
    print()

def test_upload():
    """Test uploading to R2 (optional - only if you want to actually upload)"""
    print("=" * 70)
    print("R2 UPLOAD TEST (DRY RUN)")
    print("=" * 70)
    
    r2 = get_r2_storage()
    
    test_unique_id = "TEST_DRY_RUN_123"
    upload_url = f"https://{Var.R2_Domain}/tga-r2/{Var.R2_Folder}?id={test_unique_id}"
    
    print(f"Upload URL would be: {upload_url}")
    print(f"Method: PUT")
    print(f"Content-Type: application/json")
    print()
    print("To test actual upload, uncomment the upload code in this function.")
    print()
    
    # Uncomment below to test actual upload:
    """
    test_data = r2.format_file_data(
        unique_file_id=test_unique_id,
        bot_file_ids={"b_1_file_id": "TEST_FILE_ID_123"},
        caption="Test Upload",
        file_size=1024,
        file_type="document",
        message_id=999,
        channel_id=-1001234567890,
        file_name="test.txt",
        mime_type="text/plain"
    )
    
    success = r2.upload_file_data(test_unique_id, test_data)
    if success:
        print("✅ Upload successful!")
    else:
        print("❌ Upload failed!")
    """

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("R2 STORAGE INTEGRATION - SIMPLE TEST SUITE")
    print("=" * 70)
    
    try:
        test_configuration()
        test_check_file()
        test_format_data()
        test_upload()
        
        print("=" * 70)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Run the full bot with: python3 -m WebStreamer")
        print("2. Add bot to a Telegram channel")
        print("3. Post a file and check the response")
        print()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
