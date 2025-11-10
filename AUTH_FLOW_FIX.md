# Authentication Flow Fix

## Problem
When users tried to verify OTP and create a session, the foreign key constraint was preventing session creation because the user didn't exist in the `users` table yet.

**Error:**
```
Failed to create session: insert or update on table "login_sessions" violates foreign key constraint "login_sessions_telegram_user_id_fkey"
DETAIL: Key (telegram_user_id)=(513611281) is not present in table "users".
```

## Root Cause
The authentication flow was:
1. Generate OTP ✅
2. Verify OTP ✅
3. Create session ❌ (fails because user doesn't exist)

The foreign key constraint `login_sessions.telegram_user_id` → `users.telegram_user_id` requires that a user record exists before a session can be created.

## Solution
Modified the authentication flow to create/update the user record **before** creating a session:

### Changes Made

#### 1. Web API (`/app/WebStreamer/server/auth_routes.py`)
Added user creation in the OTP verification endpoint:

```python
# After OTP verification succeeds:
verified = db.auth.verify_otp(telegram_user_id, otp)

if verified:
    # Create or update user record (required for foreign key constraint)
    db.auth.create_user(telegram_user_id, first_name, last_name, username)
    
    # Now create session (user exists in database)
    session_token = db.auth.create_session(telegram_user_id)
```

The API now accepts optional user details in the request:
- `first_name`
- `last_name`
- `username`

#### 2. Bot Command (`/app/WebStreamer/bot/plugins/start.py`)
Updated the `/verify` command to create user before session:

```python
# After OTP verification succeeds:
verified = db.auth.verify_otp(telegram_user_id, otp)

if verified:
    # Create or update user record
    db.auth.create_user(
        telegram_user_id=telegram_user_id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username
    )
    
    # Create session
    session_token = db.auth.create_session(telegram_user_id)
```

#### 3. Logout Route Fix
Added missing commit after session deletion in logout endpoint.

## New Authentication Flow

### Web-based Login:
1. User enters Telegram User ID on website
2. System generates OTP and sends via bot ✅
3. User enters OTP on website
4. System verifies OTP ✅
5. **System creates/updates user record** ✅ (NEW)
6. System creates session token ✅
7. User is logged in ✅

### Bot-based Verification:
1. User starts bot with `/start` (creates user record) ✅
2. User receives OTP from website
3. User sends `/verify <OTP>` to bot
4. Bot verifies OTP ✅
5. **Bot creates/updates user record** ✅ (NEW)
6. Bot creates session token ✅
7. User receives session token

## Benefits
- ✅ Foreign key constraint is satisfied
- ✅ User data is preserved (first_name, last_name, username)
- ✅ Database referential integrity maintained
- ✅ Works for both web and bot authentication flows
- ✅ No orphaned sessions in database

## Database Schema
```
users (telegram_user_id PK)
  ↑
  | (foreign key)
  |
login_sessions (session_token PK, telegram_user_id FK)
```

The user must exist before a session can reference them.
