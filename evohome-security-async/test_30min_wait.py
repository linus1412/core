#!/usr/bin/env python3
"""
Test script that waits 30 minutes for server session to fully expire.

The Total Connect server appears to maintain sessions for longer than
initially thought. This extended wait gives it plenty of time.
"""

import asyncio
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, "/workspaces/core/evohome-security-async")

from credentials_helper import get_credentials  # noqa: E402
from evohome_security_async import (  # noqa: E402
    AuthenticationError,
    EvohomeSecurityClient,
    SessionExpiredError,
)


async def wait_with_countdown(seconds: int) -> None:
    """Wait for specified seconds with countdown."""
    print("=" * 70)
    print("WAITING 30 MINUTES FOR SERVER SESSION TO FULLY EXPIRE")
    print("=" * 70)
    print()

    for remaining in range(seconds, 0, -60):
        minutes = remaining // 60
        print(f"Waiting... {minutes} minute(s) remaining", end="\r")
        await asyncio.sleep(60)

    print(" " * 50)  # Clear line
    print()


async def test_authentication() -> bool:
    """Test authentication with the Total Connect system."""
    print("=" * 70)
    print("STARTING AUTHENTICATION TEST (After 30-minute wait)")
    print("=" * 70)
    print()

    try:
        username, password = get_credentials()
    except ValueError as err:
        print(f"Error: {err}")
        return False

    try:
        print("Testing authentication...")

        async with EvohomeSecurityClient(username, password) as client:
            logger.debug("Authenticating with Total Connect system")
            await client.authenticate()

            logger.debug("Authentication successful!")
            print("✓ Authentication successful!")
            print()

            # Try to get status
            print("Getting current alarm status...")
            status = await client.get_status()
            print(f"✓ Current alarm status: {status.name}")
            print()

            return True

    except SessionExpiredError as e:
        print(f"\n✗ Session Error: {e}\n")
        print("The server session is STILL active after 30 minutes.")
        print("This indicates the session timeout is longer than expected.")
        print("Try waiting longer (possibly up to 1 hour).")
        return False

    except AuthenticationError as e:
        print(f"\n✗ Authentication failed: {e}\n")
        return False

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}\n")
        logger.exception("Unexpected error during authentication")
        return False


async def main() -> None:
    """Main entry point."""
    try:
        # Wait for session to expire
        await wait_with_countdown(1800)  # 30 minutes = 1800 seconds

        # Test authentication
        success = await test_authentication()

        if success:
            print("=" * 70)
            print("SUCCESS! The library is working correctly.")
            print("=" * 70)
            sys.exit(0)
        else:
            print("=" * 70)
            print("FAILURE: Session is still active.")
            print("=" * 70)
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        logger.exception("Unexpected error in main")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
