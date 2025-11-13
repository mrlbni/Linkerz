#!/usr/bin/env python3
"""
Verification script for the Bot 9/10 file ID bug fix.

This script verifies that the TokenParser now correctly assigns
MULTI_TOKEN environment variables to bot indices using numerical sorting.
"""

import os
import sys

def test_token_parser():
    """Test the fixed TokenParser with simulated environment"""
    
    # Save original environment
    original_env = {}
    for i in range(1, 11):
        key = f'MULTI_TOKEN{i}'
        if key in os.environ:
            original_env[key] = os.environ[key]
    
    try:
        # Set up test environment
        for i in range(1, 11):
            os.environ[f'MULTI_TOKEN{i}'] = f'test_token_{i}'
        
        # Import and test
        sys.path.insert(0, '/app')
        from WebStreamer.utils.config_parser import TokenParser
        
        parser = TokenParser()
        tokens = parser.parse_from_env()
        
        print("=" * 70)
        print("TOKEN PARSER VERIFICATION")
        print("=" * 70)
        print()
        print("Bot Index | Expected Token    | Actual Token      | Status")
        print("-" * 70)
        
        all_correct = True
        for bot_idx in range(1, 11):
            expected = f'test_token_{bot_idx}'
            actual = tokens.get(bot_idx, 'MISSING')
            status = "✅ PASS" if expected == actual else "❌ FAIL"
            
            if expected != actual:
                all_correct = False
            
            print(f"Bot {bot_idx:5} | {expected:17} | {actual:17} | {status}")
        
        print()
        print("=" * 70)
        
        if all_correct:
            print("✅ ALL TESTS PASSED!")
            print()
            print("Key fixes verified:")
            print("  ✅ Bot 9 uses MULTI_TOKEN9 (not MULTI_TOKEN8)")
            print("  ✅ Bot 10 uses MULTI_TOKEN10 (not MULTI_TOKEN9)")
            print("  ✅ All bots correctly assigned to their respective tokens")
            print()
            print("The bug is FIXED! Bot 9 and Bot 10 will now have different file IDs.")
            return 0
        else:
            print("❌ TESTS FAILED!")
            print()
            print("The token assignment is still incorrect.")
            print("Please check the TokenParser implementation.")
            return 1
            
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        # Restore original environment
        for i in range(1, 11):
            key = f'MULTI_TOKEN{i}'
            if key in original_env:
                os.environ[key] = original_env[key]
            elif key in os.environ:
                del os.environ[key]

if __name__ == '__main__':
    exit_code = test_token_parser()
    sys.exit(exit_code)
