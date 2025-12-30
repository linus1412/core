#!/usr/bin/env python3
"""Test logout only to clear any existing session."""

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

    async with EvohomeSecurityClient(username, password) as client:
        print("Attempting to logout any existing session...")
        await client.logout()
        print("Logout complete. Waiting 10 seconds...")
        await asyncio.sleep(10)
        print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
