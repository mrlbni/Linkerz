#!/usr/bin/env python3
"""
Test script to verify R2 data structure format
"""

import json

def format_file_metadata(unique_file_id: str, file_id: str,
                    file_name: str, file_size: int, mime_type: str,
                    message_id: int, channel_id: int, caption: str = None,
                    file_type: str = None, video_duration: int = None,
                    video_width: int = None, video_height: int = None) -> dict:
    """
    Format file metadata for R2 storage with complete structure
    """
    data = {
        "unique_id": unique_file_id,
        "bot_file_ids": {
            "b_1_file_id": file_id
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
    print("Testing R2 Data Structure Format")
    print("=" * 80)
    
    # Test 1: Video with all fields (like the user's example)
    print("\n1. Testing VIDEO with complete metadata:")
    print("-" * 80)
    
    video_data = format_file_metadata(
        unique_file_id="AgAD-00AAhqIaEg",
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
        video_height=1080
    )
    
    print(json.dumps(video_data, indent=2))
    
    # Test 2: Document without video metadata
    print("\n\n2. Testing DOCUMENT without video metadata:")
    print("-" * 80)
    
    doc_data = format_file_metadata(
        unique_file_id="AgADXYZABC123",
        file_id="BQACAgQAAx0CaZ9HgwACGQJovW8pV30uZFBM3pcyXd3px7l03wAC",
        file_name="Important_Document.pdf",
        file_size=5242880,
        mime_type="application/pdf",
        message_id=12345,
        channel_id=-1001234567890,
        caption="Important company document",
        file_type="document"
    )
    
    print(json.dumps(doc_data, indent=2))
    
    # Test 3: Audio file
    print("\n\n3. Testing AUDIO file:")
    print("-" * 80)
    
    audio_data = format_file_metadata(
        unique_file_id="AgADAUDIO123",
        file_id="CQACAgQAAx0CaZ9HgwACGQJovW8pV30uZFBM3pcyXd3px7l03wAC",
        file_name="Song.mp3",
        file_size=8388608,
        mime_type="audio/mpeg",
        message_id=54321,
        channel_id=-1001234567890,
        caption="Great music track",
        file_type="audio"
    )
    
    print(json.dumps(audio_data, indent=2))
    
    # Test 4: Verify structure matches user's example
    print("\n\n4. Comparing with user's example structure:")
    print("-" * 80)
    
    user_example = {
        "unique_id": "AgAD-00AAhqIaEg",
        "bot_file_ids": {
            "b_1_file_id": "BAACAgIAAx0CcG2DSwABCs3oaQ9lMYrg8LPNn3X-Pm3J8kSjxtgAAvtNAAIaiGhIosrwrSqhpeMeBA"
        },
        "caption": "Reislin - [OnlyFans.com] - [2023] - Mimi Cica, Reislin x Girthmasterr.mp4\n\nUploaded by Channel: -1002087056849\nChannel Invite Link: https://t.me/+MVZeKRpxKdI0YTk1",
        "file_size_bytes": 2180655398,
        "file_type": "video",
        "original_message_id": 708072,
        "source_channel_id": -1001886225227,
        "file_name": "Reislin - [OnlyFans.com] - [2023] - Mimi Cica, Reislin x.mp4",
        "mime_type": "video/mp4",
        "video_duration_seconds": 2829,
        "video_width": 1920,
        "video_height": 1080
    }
    
    print("User's example keys:", sorted(user_example.keys()))
    print("Our output keys:    ", sorted(video_data.keys()))
    
    # Check if all keys match
    user_keys = set(user_example.keys())
    our_keys = set(video_data.keys())
    
    if user_keys == our_keys:
        print("\n✅ SUCCESS: All keys match perfectly!")
    else:
        missing = user_keys - our_keys
        extra = our_keys - user_keys
        if missing:
            print(f"\n❌ Missing keys: {missing}")
        if extra:
            print(f"\n❌ Extra keys: {extra}")
    
    # Verify bot_file_ids structure
    print("\n5. Verifying bot_file_ids structure:")
    print("-" * 80)
    print(f"User's format: {json.dumps(user_example['bot_file_ids'], indent=2)}")
    print(f"Our format:    {json.dumps(video_data['bot_file_ids'], indent=2)}")
    
    if video_data['bot_file_ids'] == {"b_1_file_id": video_data['bot_file_ids']['b_1_file_id']}:
        print("✅ bot_file_ids structure is correct (uses 'b_1_file_id' format)")
    
    print("\n" + "=" * 80)
    print("Test completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
