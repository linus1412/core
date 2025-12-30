#!/usr/bin/env python3
"""Wait 15 minutes then test authentication with full debugging."""

import asyncio
import logging

from credentials_helper import get_credentials
from evohome_security_async import EvohomeSecurityClient

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")


async def main():
    try:
        username, password = get_credentials()
    except ValueError as err:
        print(f"Error: {err}")
        return

    print("\n" + "=" * 70)
    print("WAITING 15 MINUTES FOR SERVER SESSION TO EXPIRE")
    print("=" * 70 + "\n")

    for i in range(15):
        remaining = 15 - i
        print(f"Waiting... {remaining} minute(s) remaining", end="\r")
        await asyncio.sleep(60)

    print("\n" + "=" * 70)
    print("STARTING AUTHENTICATION TEST")
    print("=" * 70 + "\n")

    async with EvohomeSecurityClient(username, password) as client:
        try:
            print("Testing authentication...")
            await client.authenticate()
            print("✓ Authentication successful!")

            print("\nTesting status query...")
            status = await client.get_status()
            print(f"✓ Current alarm status: {status}")

            print("\n" + "=" * 70)
            print("SUCCESS! All tests passed!")
            print("=" * 70)
        except Exception as e:
            print(f"\n✗ Error: {e}")
            print(
                "\nIf you see 'session already exists', the server session"
                " hasn't fully expired yet."
            )
            print("Try again in a few more minutes.")


if __name__ == "__main__":
    asyncio.run(main())
