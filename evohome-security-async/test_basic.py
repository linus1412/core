#!/usr/bin/env python3
"""Quick test script to verify the library works."""

import asyncio
import logging
import os
import sys

# Set up logging to see what's happening
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

print("=" * 60)
print("Evohome Security Async - Quick Test")
print("=" * 60)

# Test imports
print("\n1. Testing imports...")
try:
    from evohome_security_async import (
        ArmStatus,
        EvohomeSecurityClient,
    )

    print("   ✓ All imports successful")
except ImportError as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

# Test enum
print("\n2. Testing ArmStatus enum...")
try:
    statuses = [
        ArmStatus.DISARMED,
        ArmStatus.ARMED_HOME,
        ArmStatus.ARMED_AWAY,
        ArmStatus.ARMING,
        ArmStatus.TRIGGERED,
        ArmStatus.UNKNOWN,
    ]
    print(f"   ✓ All statuses available: {[str(s) for s in statuses]}")
except Exception as e:
    print(f"   ✗ Enum test failed: {e}")
    sys.exit(1)

# Test client instantiation
print("\n3. Testing client instantiation...")
try:
    client = EvohomeSecurityClient(username="test@example.com", password="testpass")
    print("   ✓ Client created successfully")
    print(f"   ✓ Base URL: {client.base_url}")
    print(f"   ✓ Authenticated: {client.is_authenticated}")
except Exception as e:
    print(f"   ✗ Client instantiation failed: {e}")
    sys.exit(1)

# Test async context manager
print("\n4. Testing async context manager...")


async def test_context_manager():
    try:
        async with EvohomeSecurityClient(
            username="test@example.com", password="testpass"
        ) as client:
            print("   ✓ Context manager entered")
            assert client._session is not None
            print("   ✓ Session created")
        print("   ✓ Context manager exited cleanly")
    except Exception as e:
        print(f"   ✗ Context manager test failed: {e}")
        return False
    else:
        return True


try:
    result = asyncio.run(test_context_manager())
    if not result:
        sys.exit(1)
except Exception as e:
    print(f"   ✗ Async test failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL BASIC TESTS PASSED!")
print("=" * 60)

# Check for credentials
print("\n5. Checking for real credentials...")

username = os.getenv("EVOHOME_USERNAME")
password = os.getenv("EVOHOME_PASSWORD")

if username and password:
    print(f"   ✓ Found username: {username}")
    print(f"   ✓ Found password: {'*' * len(password)}")
    print("\n" + "=" * 60)
    print("Ready to test with REAL system!")
    print("=" * 60)
    print("\nRun: python example.py")
    print("This will authenticate and query your real system.")
else:
    print("   ⚠ No credentials found in environment")
    print("\nTo test with your real system:")
    print('  export EVOHOME_USERNAME="your.email@example.com"')
    print('  export EVOHOME_PASSWORD="your_password"')
    print("  python example.py")

print("\nLibrary validation complete! 🎉\n")
