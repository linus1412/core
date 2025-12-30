#!/usr/bin/env python3
"""Wait 5 minutes then test authentication."""

import asyncio
import logging

from credentials_helper import get_credentials
from evohome_security_async import EvohomeSecurityClient

# Enable debug logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


async def main():
    try:
        username, password = get_credentials()
    except ValueError as err:
        print(f"Error: {err}")
        return

    print("Waiting 5 minutes (300 seconds) for any existing session to expire...")
    await asyncio.sleep(300)
    print("\n" + "=" * 70)
    print("Starting authentication test...")
    print("=" * 70 + "\n")

    async with EvohomeSecurityClient(username, password) as client:
        print("Testing authentication...")
        await client.authenticate()
        print("✓ Authentication successful!")

        print("\nTesting status query...")
        status = await client.get_status()
        print(f"✓ Current alarm status: {status}")


if __name__ == "__main__":
    asyncio.run(main())
