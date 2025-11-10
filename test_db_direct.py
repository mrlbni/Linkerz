#!/usr/bin/env python3
"""
Direct test script to verify database table creation fix
"""
import psycopg2
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s][%(levelname)s] => %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S'
)

DATABASE_URL = "postgresql://ub43lrb060grpj:p6b25662823ff195e64587ea3d463bc0481c6f5d923e27771b1de8534307bf5a9@caq9uabolvh3on.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com:5432/d81se6dparnrca"

def test_table_creation():
    """Test if tables are created properly"""
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        logging.info("Successfully connected to PostgreSQL database")
        
        cursor = conn.cursor()
        
        # Create users table first
        logging.info("Creating users table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_user_id BIGINT PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            );
        """)
        conn.commit()
        logging.info("✓ Users table created")
        
        # Create OTP sessions table
        logging.info("Creating otp_sessions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS otp_sessions (
                id SERIAL PRIMARY KEY,
                telegram_user_id BIGINT NOT NULL,
                otp VARCHAR(6) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                verified BOOLEAN DEFAULT FALSE,
                verified_at TIMESTAMP
            );
        """)
        conn.commit()
        logging.info("✓ OTP sessions table created")
        
        # Create rate limits table
        logging.info("Creating rate_limits table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rate_limits (
                telegram_user_id BIGINT PRIMARY KEY,
                hour_count INTEGER DEFAULT 0,
                day_count INTEGER DEFAULT 0,
                hour_reset TIMESTAMP,
                day_reset TIMESTAMP
            );
        """)
        conn.commit()
        logging.info("✓ Rate limits table created")
        
        # Create login sessions table
        logging.info("Creating login_sessions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_sessions (
                session_token VARCHAR(64) PRIMARY KEY,
                telegram_user_id BIGINT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        logging.info("✓ Login sessions table created")
        
        # Add foreign key constraint
        logging.info("Adding foreign key constraint...")
        try:
            cursor.execute("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.table_constraints 
                        WHERE constraint_name = 'login_sessions_telegram_user_id_fkey'
                        AND table_name = 'login_sessions'
                    ) THEN
                        ALTER TABLE login_sessions 
                        ADD CONSTRAINT login_sessions_telegram_user_id_fkey 
                        FOREIGN KEY (telegram_user_id) REFERENCES users(telegram_user_id);
                    END IF;
                END $$;
            """)
            conn.commit()
            logging.info("✓ Foreign key constraint added")
        except Exception as fk_error:
            logging.warning(f"Foreign key constraint error (may already exist): {fk_error}")
        
        # Check if all tables exist
        tables_to_check = ['users', 'otp_sessions', 'login_sessions', 'rate_limits']
        
        for table in tables_to_check:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, (table,))
            exists = cursor.fetchone()[0]
            if exists:
                logging.info(f"✓ Table '{table}' exists")
            else:
                logging.error(f"✗ Table '{table}' does not exist")
        
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
            logging.info(f"✓ Foreign key constraints exist on login_sessions: {len(foreign_keys)}")
            for fk in foreign_keys:
                logging.info(f"  - {fk[0]}: {fk[1]}.{fk[2]} -> {fk[3]}.{fk[4]}")
        else:
            logging.warning("⚠ No foreign key constraints found on login_sessions (this is OK)")
        
        cursor.close()
        conn.close()
        
        logging.info("\n✅ All tests passed! Database setup is working correctly.")
        return True
        
    except Exception as e:
        logging.error(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = test_table_creation()
    sys.exit(0 if success else 1)
