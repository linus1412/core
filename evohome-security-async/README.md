# Evohome Security Async

An async Python client library for Honeywell Evohome (Total Connect) Security Systems (International/EMEA).

## Features

- Fully async using aiohttp
- Persistent session management with automatic token refresh
- Support for arm/disarm operations
- Status polling
- Standalone library (not dependent on Home Assistant)

## Installation

```bash
pip install evohome-security-async
```

## Usage

```python
import asyncio
from evohome_security_async import EvohomeSecurityClient, ArmStatus

async def main():
    async with EvohomeSecurityClient(username="user@example.com", password="password") as client:
        # Authenticate
        await client.authenticate()

        # Get status
        status = await client.get_status()
        print(f"Current status: {status}")

        # Arm away
        await client.arm_total()

        # Disarm
        await client.disarm(code="1234")

asyncio.run(main())
```

## API Reference

### EvohomeSecurityClient

Main client class for interacting with the Evohome security system.

#### Methods

- `authenticate()` - Authenticate and establish session
- `get_status()` - Get current alarm status
- `arm_total()` - Arm the system in away mode
- `arm_partial()` - Arm the system in home mode
- `disarm(code)` - Disarm the system
- `close()` - Close the session

### ArmStatus

Enum representing system states:
- `DISARMED`
- `ARMED_HOME`
- `ARMED_AWAY`
- `ARMING`
- `TRIGGERED`

## License

Apache 2.0
