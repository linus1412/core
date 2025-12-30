# Evohome Security Async - Quick Start Guide

## Installation

```bash
pip install evohome-security-async
```

Or for development:
```bash
git clone https://github.com/yourusername/evohome-security-async.git
cd evohome-security-async
pip install -e .
```

## Basic Usage

### Simple Authentication & Status Check

```python
import asyncio
from evohome_security_async import EvohomeSecurityClient

async def main():
    username = "your.email@example.com"
    password = "your_password"

    async with EvohomeSecurityClient(username, password) as client:
        # Authenticate with the server
        await client.authenticate()

        # Get current alarm status
        status = await client.get_status()
        print(f"Alarm status: {status.name}")

asyncio.run(main())
```

## Common Operations

### Check Alarm Status

```python
async with EvohomeSecurityClient(username, password) as client:
    await client.authenticate()
    status = await client.get_status()

    # Check status value
    if status == ArmStatus.DISARMED:
        print("System is disarmed")
    elif status == ArmStatus.ARMED_HOME:
        print("System is armed (home mode)")
    elif status == ArmStatus.ARMED_AWAY:
        print("System is armed (away mode)")
```

### Arm System (Away/Total)

```python
async with EvohomeSecurityClient(username, password) as client:
    await client.authenticate()

    # Arm in away mode
    new_status = await client.arm_total()
    print(f"System armed: {new_status.name}")
```

### Arm System (Home/Partial)

```python
async with EvohomeSecurityClient(username, password) as client:
    await client.authenticate()

    # Arm in home mode (partial)
    new_status = await client.arm_partial()
    print(f"System partially armed: {new_status.name}")
```

### Disarm System

```python
async with EvohomeSecurityClient(username, password) as client:
    await client.authenticate()

    # Disarm with security code
    new_status = await client.disarm("1234")
    print(f"System disarmed: {new_status.name}")
```

## Advanced Usage

### Custom Base URL (Regional Support)

```python
# For UK region
client = EvohomeSecurityClient(
    username="your.email@example.com",
    password="your_password",
    base_url="https://tc20.total-connect.co.uk"
)

# For EU region (default)
client = EvohomeSecurityClient(
    username="your.email@example.com",
    password="your_password"
    # base_url="https://tc20e.total-connect.eu"  # Default
)
```

### Manual Session Management

```python
from evohome_security_async import EvohomeSecurityClient

client = EvohomeSecurityClient(username, password)

try:
    # Connect and authenticate
    await client.__aenter__()  # Calls connect() automatically
    await client.authenticate()

    # Use the client
    status = await client.get_status()
    print(f"Status: {status.name}")

finally:
    # Always disconnect (logs out properly)
    await client.__aexit__(None, None, None)
```

Or using context manager (recommended):

```python
async with EvohomeSecurityClient(username, password) as client:
    await client.authenticate()
    status = await client.get_status()
    print(f"Status: {status.name}")
# Automatically logs out on exit
```

### Error Handling

```python
from evohome_security_async import (
    EvohomeSecurityClient,
    AuthenticationError,
    SessionExpiredError,
    ApiError,
)

async with EvohomeSecurityClient(username, password) as client:
    try:
        await client.authenticate()
        status = await client.get_status()
    except AuthenticationError as e:
        print(f"Authentication failed: {e}")
    except SessionExpiredError as e:
        print(f"Session expired: {e}")
        print("Please wait 10-15 minutes and try again")
    except ApiError as e:
        print(f"API error: {e}")
```

## Status Values

The `ArmStatus` enum provides clear status values:

```python
from evohome_security_async import ArmStatus

# Available statuses:
ArmStatus.DISARMED      # Status code: 0
ArmStatus.ARMED_HOME    # Status code: 1
ArmStatus.ARMED_AWAY    # Status code: 2
ArmStatus.ARMING        # Status code: 3
ArmStatus.TRIGGERED     # Status code: 4
ArmStatus.UNKNOWN       # Status code: -1 (error)
```

## Debugging

### Enable Debug Logging

```python
import logging

# Set library to debug mode
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("evohome_security_async")
logger.setLevel(logging.DEBUG)

# Now run your code - will show all HTTP requests/responses
```

Debug output includes:
- HTTP request details (URL, headers, cookies)
- Response status and body
- Authentication steps
- Cookie management
- Error messages with context

### Session Troubleshooting

If you get "session already exists" error:

```
ERROR: A session already exists for this account.
Please wait 10-15 minutes for the session to expire and try again.
```

This means:
1. Your previous session is still active on the server
2. The server won't allow a new session until the old one expires
3. Solution: Wait 10-15 minutes (not much you can do)
4. Prevention: Always use `async with` context manager to ensure proper logout

## Home Assistant Integration Pattern

Example for Home Assistant custom component:

```python
# homeassistant/components/evohome_security/coordinator.py
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from evohome_security_async import EvohomeSecurityClient

class EvohomeSecurityCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, username, password):
        super().__init__(hass, logger=_LOGGER, name=DOMAIN)
        self.client = EvohomeSecurityClient(username, password)

    async def _async_update_data(self):
        async with self.client:
            await self.client.authenticate()
            return await self.client.get_status()
```

## Testing with Mocks

```python
import pytest
from unittest.mock import AsyncMock, patch
from evohome_security_async import EvohomeSecurityClient, ArmStatus

@pytest.mark.asyncio
async def test_get_status():
    with patch("evohome_security_async.EvohomeSecurityClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance
        mock_instance.authenticate = AsyncMock()
        mock_instance.get_status = AsyncMock(return_value=ArmStatus.DISARMED)

        async with mock_client("test@test.com", "pass") as client:
            status = await client.get_status()
            assert status == ArmStatus.DISARMED
```

## Configuration Examples

### Environment Variables

```python
import os
from evohome_security_async import EvohomeSecurityClient

username = os.getenv("EVOHOME_USERNAME")
password = os.getenv("EVOHOME_PASSWORD")
base_url = os.getenv("EVOHOME_URL", "https://tc20e.total-connect.eu")

client = EvohomeSecurityClient(username, password, base_url=base_url)
```

### Config File (YAML)

```yaml
evohome_security:
  username: your.email@example.com
  password: your_password
  base_url: https://tc20e.total-connect.eu  # Optional
```

Then in your code:
```python
import yaml
from evohome_security_async import EvohomeSecurityClient

with open("config.yaml") as f:
    config = yaml.safe_load(f)
    evohome_config = config["evohome_security"]

client = EvohomeSecurityClient(
    evohome_config["username"],
    evohome_config["password"],
    base_url=evohome_config.get("base_url")
)
```

## Performance Tips

1. **Reuse Sessions**: Keep client alive between operations
   ```python
   async with EvohomeSecurityClient(...) as client:
       await client.authenticate()
       # Use multiple times - don't create new sessions
       status1 = await client.get_status()
       status2 = await client.get_status()  # Reuses existing session
   ```

2. **Batch Commands**: Send multiple commands in one session
   ```python
   async with EvohomeSecurityClient(...) as client:
       await client.authenticate()
       await client.arm_total()
       # Don't disconnect and reconnect for next command
   ```

3. **Concurrent Operations**: Use asyncio.gather for parallel requests
   ```python
   async with EvohomeSecurityClient(...) as client:
       await client.authenticate()

       # Run multiple operations concurrently
       results = await asyncio.gather(
           client.get_status(),
           client.get_status(),
           # Other operations...
       )
   ```

## Troubleshooting

### "module not found" error
Make sure the package is installed:
```bash
pip install -e .  # For development
# or
pip install evohome-security-async  # For release
```

### Connection timeouts
The API server may be slow. Consider increasing timeouts:
```python
# (If timeout parameter is exposed - check current API)
client = EvohomeSecurityClient(
    username,
    password,
    # timeout=30  # Adjust as needed
)
```

### SSL certificate errors
Ensure you have current SSL certificates:
```bash
pip install --upgrade certifi
```

### Authentication always fails
1. Verify username and password are correct
2. Check if account is locked (multiple failed logins)
3. Try from web interface: https://tc20e.total-connect.eu
4. If web login works but library doesn't, it's a header/session issue

### "session already exists" error
Only solution is to wait:
```python
import asyncio
import time

async def safe_auth_with_retry(username, password, max_wait=900):
    """Try to authenticate, waiting for session to expire if needed."""
    wait_time = 0
    while wait_time < max_wait:
        try:
            async with EvohomeSecurityClient(username, password) as client:
                await client.authenticate()
                return  # Success!
        except SessionExpiredError:
            wait_time += 60
            print(f"Session exists, waiting... ({wait_time}/{max_wait}s)")
            await asyncio.sleep(60)

    raise Exception(f"Failed to authenticate after {max_wait} seconds")
```

## API Reference

### EvohomeSecurityClient

Main class for interacting with Total Connect API.

#### Constructor
```python
EvohomeSecurityClient(
    username: str,
    password: str,
    base_url: str = "https://tc20e.total-connect.eu"
)
```

#### Methods
- `async authenticate()` → None
- `async logout()` → None
- `async get_status()` → ArmStatus
- `async arm_total()` → ArmStatus
- `async arm_partial()` → ArmStatus
- `async disarm(code: str)` → ArmStatus
- `async connect()` → None (called automatically in __aenter__)
- `async close()` → None (called automatically in __aexit__)

#### Context Manager
- `async __aenter__()` → EvohomeSecurityClient
- `async __aexit__()` → None

### ArmStatus Enum

```python
class ArmStatus(Enum):
    DISARMED = 0
    ARMED_HOME = 1
    ARMED_AWAY = 2
    ARMING = 3
    TRIGGERED = 4
    UNKNOWN = -1
```

### Exceptions

```python
class EvohomeSecurityException(Exception)
    # Base exception class

class AuthenticationError(EvohomeSecurityException)
    # Raised on authentication failure

class SessionExpiredError(EvohomeSecurityException)
    # Raised when session is invalid/expired

class ApiError(EvohomeSecurityException)
    # Raised on API communication errors
```

## Contributing

See CONTRIBUTING.md for development guidelines.

## License

See LICENSE file for details.

## Support

- GitHub Issues: [project]/issues
- Documentation: See docs/ folder
- Examples: See examples/ folder
