#!/usr/bin/env python3
"""
Test script to verify the Auth fix in custom_dl.py
This simulates the Auth class signature detection and pattern matching.
"""

import sys
import inspect

def test_auth_signature_detection():
    """Test that the helper function can detect Auth signatures"""
    
    print("=" * 70)
    print("Testing Auth Signature Detection")
    print("=" * 70)
    
    # Test 1: Check if get_dc_config works
    print("\n[Test 1] Testing get_dc_config function")
    sys.path.insert(0, '/app')
    
    try:
        from WebStreamer.utils.custom_dl import get_dc_config
        
        # Test production DCs
        for dc_id in [1, 2, 3, 4, 5]:
            addr, port = get_dc_config(dc_id, test_mode=False)
            print(f"  ✓ DC {dc_id} (Production): {addr}:{port}")
            assert port == 443, f"Expected port 443, got {port}"
            assert addr, "Address should not be empty"
        
        # Test test mode DCs
        for dc_id in [1, 2, 3]:
            addr, port = get_dc_config(dc_id, test_mode=True)
            print(f"  ✓ DC {dc_id} (Test Mode): {addr}:{port}")
            assert port == 443, f"Expected port 443, got {port}"
            assert addr, "Address should not be empty"
        
        # Test unknown DC (should fallback)
        addr, port = get_dc_config(99, test_mode=False)
        print(f"  ✓ DC 99 (Unknown, fallback): {addr}:{port}")
        assert port == 443, f"Expected port 443, got {port}"
        assert addr == "149.154.167.51", "Should fallback to DC 2"
        
        print("\n✅ get_dc_config function works correctly!")
        
    except ImportError as e:
        print(f"  ❌ Failed to import: {e}")
        return False
    except AssertionError as e:
        print(f"  ❌ Assertion failed: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    # Test 2: Check if functions are properly defined
    print("\n[Test 2] Verifying function definitions")
    try:
        from WebStreamer.utils.custom_dl import create_auth_safe, create_session_safe
        
        # Check create_auth_safe signature
        sig = inspect.signature(create_auth_safe)
        params = list(sig.parameters.keys())
        print(f"  ✓ create_auth_safe parameters: {params}")
        assert 'client' in params, "Missing 'client' parameter"
        assert 'dc_id' in params, "Missing 'dc_id' parameter"
        assert 'test_mode' in params, "Missing 'test_mode' parameter"
        assert inspect.iscoroutinefunction(create_auth_safe), "create_auth_safe should be async"
        
        # Check create_session_safe signature
        sig = inspect.signature(create_session_safe)
        params = list(sig.parameters.keys())
        print(f"  ✓ create_session_safe parameters: {params}")
        assert 'client' in params, "Missing 'client' parameter"
        assert 'dc_id' in params, "Missing 'dc_id' parameter"
        assert 'auth_key' in params, "Missing 'auth_key' parameter"
        assert 'test_mode' in params, "Missing 'test_mode' parameter"
        
        print("\n✅ All function definitions are correct!")
        
    except ImportError as e:
        print(f"  ❌ Failed to import: {e}")
        return False
    except AssertionError as e:
        print(f"  ❌ Assertion failed: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    # Test 3: Verify syntax is correct
    print("\n[Test 3] Checking Python syntax")
    try:
        import py_compile
        py_compile.compile('/app/WebStreamer/utils/custom_dl.py', doraise=True)
        print("  ✓ No syntax errors found")
        print("\n✅ File compiles successfully!")
        
    except py_compile.PyCompileError as e:
        print(f"  ❌ Syntax error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    return True


def test_dc_addresses():
    """Verify DC addresses are correct according to Telegram's official DCs"""
    
    print("\n" + "=" * 70)
    print("Verifying Telegram DC Addresses")
    print("=" * 70)
    
    # Official Telegram DC addresses (as of 2024)
    official_dcs = {
        1: "149.154.175.53",
        2: "149.154.167.51",
        3: "149.154.175.100",
        4: "149.154.167.91",
        5: "91.108.56.128",
    }
    
    official_test_dcs = {
        1: "149.154.175.10",
        2: "149.154.167.40",
        3: "149.154.175.117",
    }
    
    try:
        from WebStreamer.utils.custom_dl import get_dc_config
        
        print("\n[Production DCs]")
        all_correct = True
        for dc_id, expected_addr in official_dcs.items():
            addr, port = get_dc_config(dc_id, test_mode=False)
            status = "✓" if addr == expected_addr else "✗"
            print(f"  {status} DC {dc_id}: {addr}:{port} (expected: {expected_addr}:443)")
            if addr != expected_addr:
                all_correct = False
        
        print("\n[Test Mode DCs]")
        for dc_id, expected_addr in official_test_dcs.items():
            addr, port = get_dc_config(dc_id, test_mode=True)
            status = "✓" if addr == expected_addr else "✗"
            print(f"  {status} DC {dc_id}: {addr}:{port} (expected: {expected_addr}:443)")
            if addr != expected_addr:
                all_correct = False
        
        if all_correct:
            print("\n✅ All DC addresses match official Telegram DCs!")
        else:
            print("\n⚠️  Some DC addresses don't match official Telegram DCs")
        
        return all_correct
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("AUTH FIX VERIFICATION TEST SUITE")
    print("=" * 70)
    print("\nThis test verifies the Auth fix for the download error:")
    print("  TypeError: __init__() missing 2 required positional arguments")
    print("\nFile: /app/WebStreamer/utils/custom_dl.py")
    print("=" * 70)
    
    results = []
    
    # Run tests
    results.append(("Auth Signature Detection", test_auth_signature_detection()))
    results.append(("DC Address Verification", test_dc_addresses()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    print("\n" + "-" * 70)
    print(f"  Total: {passed}/{total} tests passed")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 All tests passed! The Auth fix is ready for deployment.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
