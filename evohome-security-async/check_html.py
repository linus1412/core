#!/usr/bin/env python3
import asyncio

from credentials_helper import get_credentials
from evohome_security_async import EvohomeSecurityClient


async def check_home_html():
    try:
        username, password = get_credentials()
    except ValueError as err:
        print(f"Error: {err}")
        return

    async with EvohomeSecurityClient(username, password) as client:
        await client.authenticate()

        # Re-fetch home page to look for status
        async with client._session.get(f"{client.base_url}/go/home") as resp:
            html = await resp.text()

            # Look for panel initialization or status variables
            keywords = ["statusCode", "armState", "disarm", "alarm", "panel"]

            for keyword in keywords:
                if keyword.lower() in html.lower():
                    idx = html.lower().find(keyword.lower())
                    if idx != -1:
                        context = html[max(0, idx - 80) : min(len(html), idx + 200)]
                        print(f"\nFound '{keyword}':")
                        print(repr(context))
                        print()


asyncio.run(check_home_html())
