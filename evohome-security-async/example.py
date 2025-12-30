"""Example usage of evohome-security-async library."""

import asyncio
import logging
import os
from getpass import getpass

from evohome_security_async import EvohomeSecurityClient

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def main() -> None:
    """Run example operations."""
    # Get credentials from environment or prompt
    username = os.getenv("EVOHOME_USERNAME")
    password = os.getenv("EVOHOME_PASSWORD")

    if not username:
        username = input("Enter username: ")
    if not password:
        password = getpass("Enter password: ")

    # Create client using async context manager
    async with EvohomeSecurityClient(username=username, password=password) as client:
        try:
            # Authenticate
            print("Authenticating...")
            await client.authenticate()
            print("✓ Authentication successful!")

            # Get current status
            print("\nGetting current status...")
            status = await client.get_status()
            print(f"✓ Current status: {status}")

            # Example: Arm the system (uncomment to test)
            # print("\nArming system (away mode)...")
            # await client.arm_total()
            # print("✓ System armed")

            # Wait a moment and check status again
            # await asyncio.sleep(2)
            # status = await client.get_status()
            # print(f"✓ New status: {status}")

            # Example: Disarm the system (uncomment to test)
            # print("\nDisarming system...")
            # await client.disarm(code="1234")  # Use your actual code
            # print("✓ System disarmed")

        except Exception as err:
            print(f"✗ Error: {err}")
            raise


async def continuous_monitoring() -> None:
    """Example of continuous status monitoring."""
    username = os.getenv("EVOHOME_USERNAME")
    password = os.getenv("EVOHOME_PASSWORD")

    if not username or not password:
        print("Please set EVOHOME_USERNAME and EVOHOME_PASSWORD environment variables")
        return

    async with EvohomeSecurityClient(username=username, password=password) as client:
        await client.authenticate()

        print("Starting continuous monitoring (Ctrl+C to stop)...")
        last_status = None

        try:
            while True:
                status = await client.get_status()

                if status != last_status:
                    print(f"Status changed: {last_status} -> {status}")
                    last_status = status
                else:
                    print(f"Status: {status}")

                # Poll every 30 seconds
                await asyncio.sleep(30)

        except KeyboardInterrupt:
            print("\nStopping monitoring...")


if __name__ == "__main__":
    # Run the basic example
    asyncio.run(main())

    # Or run continuous monitoring (uncomment to use)
    # asyncio.run(continuous_monitoring())
