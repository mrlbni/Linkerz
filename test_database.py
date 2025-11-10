#!/usr/bin/env python3
"""
Test script for database operations
"""
import psycopg2
import random

DB_URL = 'postgresql://ub43lrb060grpj:p6b25662823ff195e64587ea3d463bc0481c6f5d923e27771b1de8534307bf5a9@caq9uabolvh3on.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com:5432/d81se6dparnrca'

def test_database():
    """Test database operations"""
    try:
        print("🔗 Connecting to database...")
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Test 1: Insert a test file
        print("\n📝 Test 1: Inserting test file...")
        unique_id = "test_unique_file_123"
        cursor.execute("""
            INSERT INTO media_files (unique_file_id, b_1, b_2, file_name, file_size, mime_type)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (unique_file_id) DO UPDATE 
            SET b_1 = EXCLUDED.b_1, b_2 = EXCLUDED.b_2
        """, (unique_id, "file_id_bot1", "file_id_bot2", "test_video.mp4", 12345678, "video/mp4"))
        print("✅ Test file inserted")
        
        # Test 2: Retrieve file
        print("\n📥 Test 2: Retrieving file...")
        cursor.execute("""
            SELECT b_1, b_2, b_3, b_4, b_5, b_6, b_7, b_8, b_9, b_10, b_11,
                   file_name, file_size, mime_type
            FROM media_files WHERE unique_file_id = %s
        """, (unique_id,))
        result = cursor.fetchone()
        
        if result:
            print(f"✅ File retrieved successfully")
            print(f"   File name: {result[11]}")
            print(f"   File size: {result[12]} bytes")
            print(f"   MIME type: {result[13]}")
            print(f"   Available bot file_ids:")
            for i in range(11):
                if result[i]:
                    print(f"     - b_{i+1}: {result[i]}")
        
        # Test 3: Update with another bot's file_id
        print("\n🔄 Test 3: Updating with bot 3's file_id...")
        cursor.execute("""
            UPDATE media_files 
            SET b_3 = %s, updated_at = CURRENT_TIMESTAMP
            WHERE unique_file_id = %s
        """, ("file_id_bot3", unique_id))
        print("✅ Updated with bot 3's file_id")
        
        # Test 4: Random selection simulation
        print("\n🎲 Test 4: Random file_id selection...")
        cursor.execute("""
            SELECT b_1, b_2, b_3, b_4, b_5, b_6, b_7, b_8, b_9, b_10, b_11
            FROM media_files WHERE unique_file_id = %s
        """, (unique_id,))
        result = cursor.fetchone()
        
        available_bots = {}
        for i in range(11):
            if result[i]:
                available_bots[i] = result[i]
        
        if available_bots:
            selected_bot = random.choice(list(available_bots.keys()))
            print(f"✅ Randomly selected bot {selected_bot + 1} with file_id: {available_bots[selected_bot]}")
        
        # Test 5: List all files
        print("\n📋 Test 5: Listing all files in database...")
        cursor.execute("SELECT unique_file_id, file_name, file_size FROM media_files LIMIT 10")
        all_files = cursor.fetchall()
        print(f"✅ Found {len(all_files)} file(s) in database")
        for file in all_files:
            print(f"   - {file[0]}: {file[1]} ({file[2]} bytes)")
        
        # Cleanup test data
        print("\n🧹 Cleaning up test data...")
        cursor.execute("DELETE FROM media_files WHERE unique_file_id = %s", (unique_id,))
        print("✅ Test data removed")
        
        cursor.close()
        conn.close()
        
        print("\n✅ All tests passed successfully! 🎉")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_database()
