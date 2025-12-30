#!/usr/bin/env python3
"""Test arming and disarming the alarm system."""

import asyncio
import logging

from credentials_helper import get_credentials
from evohome_security_async import EvohomeSecurityClient

# Enable info logging only
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


async def main():
    try:
        username, password = get_credentials()
    except ValueError as err:
        print(f"Error: {err}")
        return

    async with EvohomeSecurityClient(username, password) as client:
        print("Authenticating...")
        await client.authenticate()
        print("✓ Authenticated\n")

        # Get current status
        print("Getting current status...")
        status = await client.get_status()
        print(f"Current status: {status.name}\n")

        # Test 1: Arm to Partial (Home)
        print("=" * 50)
        print("TEST 1: Arming to PARTIAL (Home mode)")
        print("=" * 50)
        await client.arm_partial()
        print("✓ Command sent")
        await asyncio.sleep(2)  # Wait for system to process
        status = await client.get_status()
        print(f"New status: {status.name}")
        print()

        # Wait before next change
        await asyncio.sleep(3)

        # Test 2: Arm to Total (Away)
        print("=" * 50)
        print("TEST 2: Arming to TOTAL (Away mode)")
        print("=" * 50)
        await client.arm_total()
        print("✓ Command sent")
        await asyncio.sleep(2)
        status = await client.get_status()
        print(f"New status: {status.name}")
        print()

        # Wait before next change
        await asyncio.sleep(3)

        # Test 3: Disarm
        print("=" * 50)
        print("TEST 3: Disarming")
        print("=" * 50)
        await client.disarm()
        print("✓ Command sent")
        await asyncio.sleep(2)
        status = await client.get_status()
        print(f"New status: {status.name}")
        print()

        print("=" * 50)
        print("All tests completed!")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
