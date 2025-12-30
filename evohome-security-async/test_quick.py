#!/usr/bin/env python3
"""Quick test with credentials from environment variables."""

import asyncio
import logging
import os

from evohome_security_async import EvohomeSecurityClient

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")


async def main():
    username = os.environ.get("EVOHOME_USERNAME")
    password = os.environ.get("EVOHOME_PASSWORD")

    if not username or not password:
        print(
            "Error: EVOHOME_USERNAME and EVOHOME_PASSWORD environment"
            " variables required"
        )
        print("Set them before running:")
        print("  export EVOHOME_USERNAME='your-email'")
        print("  export EVOHOME_PASSWORD='your-password'")
        return

    async with EvohomeSecurityClient(username, password) as client:
        print("Testing authentication...")
        await client.authenticate()
        print("✓ Authentication successful!")

        print("\nTesting status query...")
        status = await client.get_status()
        print(f"✓ Current alarm status: {status}")


if __name__ == "__main__":
    asyncio.run(main())
