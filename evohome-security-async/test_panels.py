#!/usr/bin/env python3
"""Test script to check available panels/installations."""

import asyncio
import logging

from credentials_helper import get_credentials
from evohome_security_async import EvohomeSecurityClient

logging.basicConfig(level=logging.DEBUG)

HTTP_OK = 200


async def main():
    try:
        username, password = get_credentials()
    except ValueError as err:
        print(f"Error: {err}")
        return

    async with EvohomeSecurityClient(username, password) as client:
        print("Authenticating...")
        await client.authenticate()
        print("✓ Authenticated")

        # Try to get list of panels/installations
        panels_url = (
            f"{client.base_url}/applicationservice/domoweb/clients/panels/installed"
        )
        print(f"\nChecking panels at: {panels_url}")

        headers = client._get_api_headers()

        async with client._session.get(panels_url, headers=headers) as response:
            print(f"Status: {response.status}")
            if response.status == HTTP_OK:
                data = await response.json()
                print(f"Panels data: {data}")
            else:
                text = await response.text()
                print(f"Response: {text}")

        # Try panel info endpoint
        panel_url = f"{client.base_url}/applicationservice/domoweb/panel"
        print(f"\nChecking panel endpoint: {panel_url}")

        async with client._session.get(panel_url, headers=headers) as response:
            print(f"Status: {response.status}")
            text = await response.text()
            print(f"Response: {text[:500]}")

        # Try to get panel details from the home page
        home_url = f"{client.base_url}/go/home"
        print("\nChecking home page for panel info...")

        async with client._session.get(home_url) as response:
            html = await response.text()

            # Look for panel-related JavaScript variables
            keywords = ["panelId", "installationId", "clientId", "alarmPanel"]
            for keyword in keywords:
                if keyword in html:
                    print(f"Found '{keyword}' in HTML")
                    # Find the line containing it
                    for line in html.split("\n"):
                        if keyword in line and ("var " in line or "=" in line):
                            print(f"  {line.strip()[:200]}")


if __name__ == "__main__":
    asyncio.run(main())
