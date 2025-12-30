#!/usr/bin/env python3
import asyncio
import logging

from credentials_helper import get_credentials
from evohome_security_async import EvohomeSecurityClient

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")


async def test():
    try:
        username, password = get_credentials()
    except ValueError as err:
        print(f"Error: {err}")
        return

    async with EvohomeSecurityClient(username, password) as client:
        await client.authenticate()
        print("\nGetting status...")
        status = await client.get_status()
        print(f"Status: {status.name} ({status.value})")


asyncio.run(test())
