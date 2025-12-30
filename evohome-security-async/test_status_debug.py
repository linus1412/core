#!/usr/bin/env python3
"""Quick status debug test."""

import asyncio
import logging

from credentials_helper import get_credentials
from evohome_security_async import EvohomeSecurityClient

logging.basicConfig(
    level=logging.DEBUG, format="%(name)s - %(levelname)s - %(message)s"
)


async def main():
    try:
        username, password = get_credentials()
    except ValueError as err:
        print(f"Error: {err}")
        return

    async with EvohomeSecurityClient(username, password) as client:
        await client.authenticate()
        print("\n=== GETTING STATUS ===")
        status = await client.get_status()
        print(f"=== STATUS: {status.name} ({status.value}) ===\n")


asyncio.run(main())
