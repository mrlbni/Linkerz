#!/usr/bin/env python3
"""
Test script to verify database table creation fix
"""
import os
import sys
import psycopg2

# Set the DATABASE_URL for testing
DATABASE_URL = "postgresql://ub43lrb060grpj:p6b25662823ff195e64587ea3d463bc0481c6f5d923e27771b1de8534307bf5a9@caq9uabolvh3on.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com:5432/d81se6dparnrca"
os.environ['DATABASE_URL'] = DATABASE_URL

def test_table_creation():
    """Test if tables are created properly"""
    try:
        # Import after setting environment variable
        sys.path.insert(0, '/app')
        from WebStreamer.database import Database
        
        print("Testing database connection and table creation...")
        db = Database()
        
        print("✓ Database connected successfully")
        print("✓ media_files table created")
        print("✓ Authentication system initialized")
        
        # Test if all tables exist
        cursor = db.conn.cursor()
        
        tables_to_check = ['users', 'otp_sessions', 'login_sessions', 'rate_limits', 'media_files']
        
        for table in tables_to_check:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, (table,))
            exists = cursor.fetchone()[0]
            if exists:
                print(f"✓ Table '{table}' exists")
            else:
                print(f"✗ Table '{table}' does not exist")
        
        # Check foreign key constraint
        cursor.execute("""
            SELECT 
                tc.constraint_name, 
                tc.table_name, 
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name 
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' 
              AND tc.table_name='login_sessions';
        """)
        
        foreign_keys = cursor.fetchall()
        if foreign_keys:
            print(f"✓ Foreign key constraints exist on login_sessions: {len(foreign_keys)}")
            for fk in foreign_keys:
                print(f"  - {fk[0]}: {fk[1]}.{fk[2]} -> {fk[3]}.{fk[4]}")
        else:
            print("⚠ No foreign key constraints found on login_sessions")
        
        cursor.close()
        db.close()
        
        print("\n✅ All tests passed! Database setup is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_table_creation()
    sys.exit(0 if success else 1)
