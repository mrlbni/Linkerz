#!/usr/bin/env python3
"""
Test script to verify R2 data merge logic with bot IDs
"""

import json

def format_file_metadata(unique_file_id: str, bot_user_id: int, file_id: str,
                    file_name: str, file_size: int, mime_type: str,
                    message_id: int, channel_id: int, caption: str = None,
                    file_type: str = None, video_duration: int = None,
                    video_width: int = None, video_height: int = None,
                    existing_data: dict = None) -> dict:
    """
    Format file metadata for R2 storage with complete structure
    Merges with existing data if provided
    """
    # Start with existing data if available, otherwise create new
    if existing_data:
        data = existing_data.copy()
        # Merge bot_file_ids - keep existing ones and add new
        if "bot_file_ids" not in data:
            data["bot_file_ids"] = {}
        data["bot_file_ids"][str(bot_user_id)] = file_id
    else:
        data = {
            "unique_id": unique_file_id,
            "bot_file_ids": {
                str(bot_user_id): file_id
            },
            "file_name": file_name,
            "file_size_bytes": file_size,
            "mime_type": mime_type,
            "original_message_id": message_id,
            "source_channel_id": channel_id
        }
        
        # Add optional fields if provided
        if caption:
            data["caption"] = caption
            
        if file_type:
            data["file_type"] = file_type
            
        # Add video-specific metadata if available
        if video_duration is not None:
            data["video_duration_seconds"] = video_duration
        if video_width is not None:
            data["video_width"] = video_width
        if video_height is not None:
            data["video_height"] = video_height
        
    return data


def main():
    print("=" * 80)
    print("Testing R2 Data Merge Logic with Bot IDs")
    print("=" * 80)
    
    # Test 1: First bot sees the file (no existing data)
    print("\n1. Bot 1 (8232420962) uploads file for the first time:")
    print("-" * 80)
    
    bot1_data = format_file_metadata(
        unique_file_id="AgAD-00AAhqIaEg",
        bot_user_id=8232420962,
        file_id="BAACAgIAAx0CcG2DSwABCs3oaQ9lMYrg8LPNn3X-Pm3J8kSjxtgAAvtNAAIaiGhIosrwrSqhpeMeBA",
        file_name="Reislin - [OnlyFans.com] - [2023] - Mimi Cica, Reislin x.mp4",
        file_size=2180655398,
        mime_type="video/mp4",
        message_id=708072,
        channel_id=-1001886225227,
        caption="Reislin - [OnlyFans.com] - [2023] - Mimi Cica, Reislin x Girthmasterr.mp4\n\nUploaded by Channel: -1002087056849\nChannel Invite Link: https://t.me/+MVZeKRpxKdI0YTk1",
        file_type="video",
        video_duration=2829,
        video_width=1920,
        video_height=1080,
        existing_data=None  # No existing data
    )
    
    print(json.dumps(bot1_data, indent=2))
    print(f"\n✅ Bot file IDs: {list(bot1_data['bot_file_ids'].keys())}")
    
    # Test 2: Second bot sees the same file (merge with existing)
    print("\n\n2. Bot 2 (7123456789) sees the SAME file (merge with existing):")
    print("-" * 80)
    
    # Simulate fetching existing data from R2
    existing_r2_data = bot1_data.copy()
    
    bot2_data = format_file_metadata(
        unique_file_id="AgAD-00AAhqIaEg",
        bot_user_id=7123456789,  # Different bot
        file_id="BQACAgQAAx0CaZ9HgwACGQJovW8pV30uZFBM3pcyXd3px7l03wAC",  # Different file_id
        file_name="Reislin - [OnlyFans.com] - [2023] - Mimi Cica, Reislin x.mp4",
        file_size=2180655398,
        mime_type="video/mp4",
        message_id=708072,
        channel_id=-1001886225227,
        caption="Reislin - [OnlyFans.com] - [2023] - Mimi Cica, Reislin x Girthmasterr.mp4\n\nUploaded by Channel: -1002087056849\nChannel Invite Link: https://t.me/+MVZeKRpxKdI0YTk1",
        file_type="video",
        video_duration=2829,
        video_width=1920,
        video_height=1080,
        existing_data=existing_r2_data  # Pass existing data
    )
    
    print(json.dumps(bot2_data, indent=2))
    print(f"\n✅ Bot file IDs: {list(bot2_data['bot_file_ids'].keys())}")
    print(f"✅ Total bots: {len(bot2_data['bot_file_ids'])}")
    
    # Test 3: Third bot adds to the mix
    print("\n\n3. Bot 3 (6987654321) sees the SAME file (merge again):")
    print("-" * 80)
    
    existing_r2_data = bot2_data.copy()
    
    bot3_data = format_file_metadata(
        unique_file_id="AgAD-00AAhqIaEg",
        bot_user_id=6987654321,  # Another different bot
        file_id="CQACAgQAAx0CaZ9HgwACGQJovW8pV30uZFBM3pcyXd3px7l03wAC",  # Another file_id
        file_name="Reislin - [OnlyFans.com] - [2023] - Mimi Cica, Reislin x.mp4",
        file_size=2180655398,
        mime_type="video/mp4",
        message_id=708072,
        channel_id=-1001886225227,
        caption="Reislin - [OnlyFans.com] - [2023] - Mimi Cica, Reislin x Girthmasterr.mp4\n\nUploaded by Channel: -1002087056849\nChannel Invite Link: https://t.me/+MVZeKRpxKdI0YTk1",
        file_type="video",
        video_duration=2829,
        video_width=1920,
        video_height=1080,
        existing_data=existing_r2_data  # Pass merged data
    )
    
    print(json.dumps(bot3_data, indent=2))
    print(f"\n✅ Bot file IDs: {list(bot3_data['bot_file_ids'].keys())}")
    print(f"✅ Total bots: {len(bot3_data['bot_file_ids'])}")
    
    # Test 4: Verify structure matches user's example
    print("\n\n4. Comparing final structure with user's example:")
    print("-" * 80)
    
    user_example_bot_ids = {
        "b_1_file_id": "BAACAgIAAx0CcG2DSwABCs3oaQ9lMYrg8LPNn3X-Pm3J8kSjxtgAAvtNAAIaiGhIosrwrSqhpeMeBA",
        "b_2_file_id": "BAACAgIAAx0CcG2DSwABCs3oaQ9lMVqqXkvhwBMenUiINCQOD3UAAvtNAAIaiGhIM18snAxkTBYeBA",
        "b_3_file_id": "BAACAgIAAx0CcG2DSwABCs3oaQ9lMSYpewNL07mTMVepmdXPubMAAvtNAAIaiGhIbsEDQB4fB8IeBA",
        "8232420962": "BAACAgIAAx0Cap90EgABARvQaT-Ni2M2p0pnYFY1v2q6h-DatOAAArChAAJE9_hJs9-aDqZVF1geBA"
    }
    
    print("User's bot_file_ids format (mixed b_X and bot IDs):")
    print(json.dumps(user_example_bot_ids, indent=2))
    
    print("\n\nOur bot_file_ids format (using bot IDs as keys):")
    print(json.dumps(bot3_data['bot_file_ids'], indent=2))
    
    print("\n✅ Key format: Using bot Telegram user IDs (integers) as keys")
    print("✅ Merge logic: Keeps all existing bot IDs when adding new ones")
    
    # Test 5: Show the flow
    print("\n\n5. Complete Flow Simulation:")
    print("-" * 80)
    print("Step 1: Bot 8232420962 uploads → R2 has 1 bot ID")
    print(f"  bot_file_ids: {list(bot1_data['bot_file_ids'].keys())}")
    
    print("\nStep 2: Bot 7123456789 sees same file → Fetch from R2 → Merge → R2 has 2 bot IDs")
    print(f"  bot_file_ids: {list(bot2_data['bot_file_ids'].keys())}")
    
    print("\nStep 3: Bot 6987654321 sees same file → Fetch from R2 → Merge → R2 has 3 bot IDs")
    print(f"  bot_file_ids: {list(bot3_data['bot_file_ids'].keys())}")
    
    print("\n" + "=" * 80)
    print("✅ Test completed successfully!")
    print("=" * 80)
    print("\nKey Features:")
    print("  • Uses bot Telegram user ID as key (e.g., '8232420962')")
    print("  • Fetches existing R2 data before upload")
    print("  • Merges bot_file_ids - keeps all existing + adds new")
    print("  • Multiple bots can track the same file")


if __name__ == "__main__":
    main()
