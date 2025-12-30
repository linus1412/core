#!/usr/bin/env python3
import asyncio
import json

from credentials_helper import get_credentials

HTTP_OK = 200


async def test_endpoints():
    # Test different endpoints to find where the status actually comes from
    try:
        username, password = get_credentials()
    except ValueError as err:
        print(f"Error: {err}")
        return

    from evohome_security_async import EvohomeSecurityClient  # noqa: PLC0415

    async with EvohomeSecurityClient(username, password) as client:
        await client.authenticate()

        # Get the session token
        session_token = client._home_session_id

        endpoints = [
            "/applicationservice/domoweb/panel?fromHomeview=false",
            "/applicationservice/domoweb/panel/commands",
            "/applicationservice/domoweb/alarmpanel",
            "/applicationservice/domoweb/panel/general",
        ]

        headers = {
            "x-session-token": session_token,
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json",
        }

        for endpoint in endpoints:
            url = f"https://tc20e.total-connect.eu{endpoint}"
            print(f"\n{'=' * 60}")
            print(f"Testing: {endpoint}")
            print("=" * 60)
            try:
                async with client._session.get(url, headers=headers) as resp:
                    print(f"Status: {resp.status}")
                    if resp.status == HTTP_OK:
                        data = await resp.json()
                        print(f"Response: {json.dumps(data, indent=2)[:500]}...")
            except Exception as e:
                print(f"Error: {e}")


asyncio.run(test_endpoints())
