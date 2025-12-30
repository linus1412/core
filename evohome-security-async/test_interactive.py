#!/usr/bin/env python3
"""Interactive test script for Evohome Security - prompts for credentials."""

import asyncio
import logging
import sys
from getpass import getpass

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

print("=" * 70)
print("  Evohome Security Async - Interactive Test with Real System")
print("=" * 70)

# Import the library
try:
    from evohome_security_async import (
        ApiError,
        AuthenticationError,
        EvohomeSecurityClient,
    )

    print("\n✓ Library imported successfully\n")
except ImportError as e:
    print(f"\n✗ Failed to import library: {e}\n")
    sys.exit(1)

# Get credentials
print("Please enter your Total Connect credentials:")
print("(These will NOT be stored - only used for this session)\n")

username = input("Username/Email: ").strip()
if not username:
    print("✗ Username is required")
    sys.exit(1)

password = getpass("Password: ")
if not password:
    print("✗ Password is required")
    sys.exit(1)

print("\n" + "=" * 70)
print("  Starting Tests")
print("=" * 70)


async def test_real_system():  # noqa: PLR0912, PLR0915
    """Test with the real Evohome security system."""

    print("\n1. Creating client...")
    async with EvohomeSecurityClient(username=username, password=password) as client:
        print("   ✓ Client created\n")

        # Test authentication
        print("2. Authenticating with Total Connect...")
        try:
            success = await client.authenticate()
            if success:
                print("   ✓ Authentication successful!")
                print(f"   ✓ Home Session ID: {client._home_session_id[:20]}...")
            else:
                print("   ✗ Authentication failed (returned False)")
                return
        except AuthenticationError as e:
            print(f"   ✗ Authentication failed: {e}")
            return
        except Exception as e:
            print(f"   ✗ Unexpected error during authentication: {e}")
            return

        # Test status query
        print("\n3. Querying system status...")
        try:
            status = await client.get_status()
            print("   ✓ Status query successful!")
            print(f"   ✓ Current status: {status}")
            print(f"   ✓ Status value: {status.value}")
        except ApiError as e:
            print(f"   ✗ Status query failed: {e}")
        except Exception as e:
            print(f"   ✗ Unexpected error during status query: {e}")
            import traceback  # noqa: PLC0415

            traceback.print_exc()

        # Ask if user wants to test arm/disarm
        print("\n" + "=" * 70)
        print("  WARNING: The following tests will ARM/DISARM your system!")
        print("=" * 70)

        response = (
            input("\nDo you want to test ARM/DISARM operations? (yes/no): ")
            .strip()
            .lower()
        )

        if response == "yes":
            print("\n4. Testing ARM operations...")

            # Test arm total
            test_arm = (
                input("   Test ARM TOTAL (away mode)? (yes/no): ").strip().lower()
            )
            if test_arm == "yes":
                try:
                    print("   Sending ARM TOTAL command...")
                    await client.arm_total()
                    print("   ✓ ARM TOTAL command sent successfully")

                    await asyncio.sleep(2)
                    status = await client.get_status()
                    print(f"   ✓ New status: {status}")
                except Exception as e:
                    print(f"   ✗ ARM TOTAL failed: {e}")

            # Test arm partial
            test_arm = (
                input("   Test ARM PARTIAL (home mode)? (yes/no): ").strip().lower()
            )
            if test_arm == "yes":
                try:
                    print("   Sending ARM PARTIAL command...")
                    await client.arm_partial()
                    print("   ✓ ARM PARTIAL command sent successfully")

                    await asyncio.sleep(2)
                    status = await client.get_status()
                    print(f"   ✓ New status: {status}")
                except Exception as e:
                    print(f"   ✗ ARM PARTIAL failed: {e}")

            # Test disarm
            test_disarm = input("   Test DISARM? (yes/no): ").strip().lower()
            if test_disarm == "yes":
                disarm_code = input(
                    "   Enter disarm code (or press Enter for blank): "
                ).strip()
                try:
                    print("   Sending DISARM command...")
                    await client.disarm(code=disarm_code)
                    print("   ✓ DISARM command sent successfully")

                    await asyncio.sleep(2)
                    status = await client.get_status()
                    print(f"   ✓ New status: {status}")
                except Exception as e:
                    print(f"   ✗ DISARM failed: {e}")
        else:
            print("   Skipping ARM/DISARM tests")

        print("\n" + "=" * 70)
        print("  Test Complete!")
        print("=" * 70)


# Run the async test
try:
    asyncio.run(test_real_system())
except KeyboardInterrupt:
    print("\n\n✗ Test interrupted by user")
except Exception as e:
    print(f"\n✗ Unexpected error: {e}")
    import traceback

    traceback.print_exc()

print("\nDone! 🎉\n")
