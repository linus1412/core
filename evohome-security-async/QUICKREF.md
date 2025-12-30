# Quick Reference Card

## Installation

```bash
pip install evohome-security-async  # When published
# OR for development:
pip install -e ".[dev]"
```

## Basic Usage

```python
import asyncio
from evohome_security_async import EvohomeSecurityClient, ArmStatus

async def main():
    async with EvohomeSecurityClient("user@example.com", "password") as client:
        await client.authenticate()
        status = await client.get_status()
        print(f"Status: {status}")

asyncio.run(main())
```

## API Methods

| Method | Description | Returns | Raises |
|--------|-------------|---------|--------|
| `authenticate()` | Login and get session | `bool` | `AuthenticationError` |
| `get_status()` | Get alarm status | `ArmStatus` | `ApiError`, `SessionExpiredError` |
| `arm_total()` | Arm away mode | `bool` | `ApiError` |
| `arm_partial()` | Arm home mode | `bool` | `ApiError` |
| `disarm(code)` | Disarm system | `bool` | `ApiError` |
| `close()` | Close session | `None` | - |

## ArmStatus Enum

```python
ArmStatus.DISARMED       # System is disarmed
ArmStatus.ARMED_HOME     # Armed in home/partial mode
ArmStatus.ARMED_AWAY     # Armed in away/total mode
ArmStatus.ARMING         # Currently arming (countdown)
ArmStatus.TRIGGERED      # Alarm is triggered
ArmStatus.UNKNOWN        # Status cannot be determined
```

## Exceptions

```python
from evohome_security_async import (
    AuthenticationError,   # Login failed
    SessionExpiredError,   # Session expired (auto-handled)
    ApiError,              # API communication error
)

try:
    await client.get_status()
except AuthenticationError as e:
    print(f"Auth failed: {e}")
except ApiError as e:
    print(f"API error: {e}")
```

## Configuration

```python
# Basic
client = EvohomeSecurityClient(username="...", password="...")

# Custom base URL (for different regions)
client = EvohomeSecurityClient(
    username="...",
    password="...",
    base_url="https://custom.url.com"
)

# With existing aiohttp session
async with aiohttp.ClientSession() as session:
    client = EvohomeSecurityClient(
        username="...",
        password="...",
        session=session
    )
```

## Context Manager (Recommended)

```python
# Preferred - automatic cleanup
async with EvohomeSecurityClient(username, password) as client:
    await client.authenticate()
    # Do work...
# Session automatically closed

# Manual - requires explicit close
client = EvohomeSecurityClient(username, password)
try:
    await client.authenticate()
    # Do work...
finally:
    await client.close()
```

## Complete Example

```python
import asyncio
import logging
from evohome_security_async import (
    EvohomeSecurityClient,
    ArmStatus,
    AuthenticationError,
    ApiError,
)

logging.basicConfig(level=logging.INFO)

async def control_alarm():
    """Example showing all operations."""
    try:
        async with EvohomeSecurityClient("user@example.com", "password") as client:
            # Authenticate
            print("Authenticating...")
            await client.authenticate()
            print("✓ Authenticated")

            # Check status
            status = await client.get_status()
            print(f"Current status: {status}")

            # Arm the system
            if status == ArmStatus.DISARMED:
                print("Arming system (away)...")
                await client.arm_total()
                print("✓ System armed")

                # Wait a moment
                await asyncio.sleep(2)

                # Check new status
                status = await client.get_status()
                print(f"New status: {status}")

                # Disarm
                print("Disarming...")
                await client.disarm(code="1234")
                print("✓ System disarmed")

    except AuthenticationError as e:
        print(f"✗ Authentication failed: {e}")
    except ApiError as e:
        print(f"✗ API error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

asyncio.run(control_alarm())
```

## Continuous Monitoring

```python
async def monitor():
    """Poll status continuously."""
    async with EvohomeSecurityClient(username, password) as client:
        await client.authenticate()

        while True:
            status = await client.get_status()
            print(f"Status: {status}")
            await asyncio.sleep(30)  # Poll every 30s

asyncio.run(monitor())
```

## Home Assistant Usage

```python
from homeassistant.helpers.aiohttp_client import async_get_clientsession

# In your integration
async def async_setup_entry(hass, entry):
    """Set up from config entry."""
    session = async_get_clientsession(hass)

    client = EvohomeSecurityClient(
        username=entry.data["username"],
        password=entry.data["password"],
        session=session
    )

    await client.authenticate()

    # Store for later use
    hass.data[DOMAIN][entry.entry_id] = client

    return True
```

## Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Or just for this library
logging.getLogger("evohome_security_async").setLevel(logging.DEBUG)

# Typical output:
# DEBUG:evohome_security_async.client:Authenticating with Total Connect system
# DEBUG:evohome_security_async.client:Visiting main page to get initial cookies
# DEBUG:evohome_security_async.client:Sending validation request
# INFO:evohome_security_async.client:Authentication successful
# INFO:evohome_security_async.client:Successfully extracted homeSessionId
```

## Testing

```python
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# With coverage
pytest tests/ --cov=evohome_security_async --cov-report=html

# Run specific test
pytest tests/test_client.py::test_authentication_success -v
```

## Common Issues

### Authentication Fails
```python
# Check credentials
# Check network connectivity
# Enable debug logging to see what's happening
logging.getLogger("evohome_security_async").setLevel(logging.DEBUG)
```

### Session Expires
```python
# Library handles this automatically
# It will re-authenticate and retry
# Just call the method again
```

### Wrong Status Returned
```python
# Check your system's actual status on the website
# Enable debug logging to see raw API response
# The statusCode or istState might be different for your region
```

## Performance Tips

```python
# Reuse client instance
client = EvohomeSecurityClient(username, password)
await client.authenticate()

# Multiple operations use same session
await client.get_status()  # Fast
await client.arm_total()   # Fast
await client.get_status()  # Fast

await client.close()

# Don't create new client for each operation
# This is slow:
for i in range(10):
    async with EvohomeSecurityClient(...) as client:
        await client.authenticate()  # ← Slow, authenticates every time
        await client.get_status()
```

## Environment Variables

```bash
# Set credentials in environment
export EVOHOME_USERNAME="your.email@example.com"
export EVOHOME_PASSWORD="your_password"

# Then in code:
import os

username = os.getenv("EVOHOME_USERNAME")
password = os.getenv("EVOHOME_PASSWORD")

client = EvohomeSecurityClient(username, password)
```

## Next Steps

1. ✅ Install the library
2. ✅ Test authentication
3. ✅ Query status
4. ✅ Test arm/disarm operations
5. ➡️ Integrate into your application
6. ➡️ Create Home Assistant integration (optional)

## Resources

- **Full Documentation**: See [README.md](README.md)
- **Development Guide**: See [DEVELOPMENT.md](DEVELOPMENT.md)
- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Example Code**: See [example.py](example.py)

## Support

- Check logs with DEBUG level
- Review [CHECKLIST.md](CHECKLIST.md) for testing guide
- Review API responses in debug logs
- Verify credentials work on website first

---

**Quick Start Command**:
```bash
cd evohome-security-async
export EVOHOME_USERNAME="user@example.com"
export EVOHOME_PASSWORD="password"
python example.py
```
