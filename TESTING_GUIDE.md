# Testing Evohome Security Integration

## Quick Start

### Prerequisites
Set up environment variables with your Total Connect credentials:
```bash
export EVOHOME_USERNAME="your.email@example.com"
export EVOHOME_PASSWORD="your_password"
```

### Running Tests
```bash
# Navigate to the library directory
cd /workspaces/core/evohome-security-async

# Run any test script
python test_quick.py           # Quick auth + status test
python test_arm_disarm.py      # Test arm/disarm commands
python test_status_only.py     # Test status retrieval
python test_endpoints.py       # Discover endpoints
python test_panels.py          # Discover panels
```

## Credential Management

### Test Scripts (credentials_helper.py)
All test scripts use the `credentials_helper` module:

```python
from credentials_helper import get_credentials

try:
    username, password = get_credentials()
except ValueError as err:
    print(f"Error: {err}")
    print("Please set EVOHOME_USERNAME and EVOHOME_PASSWORD environment variables")
    return
```

This pattern:
- ✅ Reads from env vars (EVOHOME_USERNAME, EVOHOME_PASSWORD)
- ✅ Raises helpful error if env vars not set
- ✅ Prevents accidental credential commits
- ✅ Works across all test scripts consistently

### Home Assistant Integration
The HA integration handles credentials through the web UI:

1. **Setup**: Configuration → Integrations → Create Integration
2. **Input**: Enter email, password, and optional base URL
3. **Validation**: Integration tests credentials during setup
4. **Storage**: HA encrypts and stores in secrets.yaml
5. **Usage**: Coordinator accesses from ConfigEntry.data

## Environment Variable Setup

### Temporary (current session only)
```bash
export EVOHOME_USERNAME="your.email@example.com"
export EVOHOME_PASSWORD="your_password"
python test_quick.py
```

### Persistent (Linux/Mac ~/.bashrc or ~/.zshrc)
```bash
echo 'export EVOHOME_USERNAME="your.email@example.com"' >> ~/.bashrc
echo 'export EVOHOME_PASSWORD="your_password"' >> ~/.bashrc
source ~/.bashrc
```

### Persistent (Windows PowerShell $PROFILE)
```powershell
[Environment]::SetEnvironmentVariable("EVOHOME_USERNAME", "your.email@example.com", "User")
[Environment]::SetEnvironmentVariable("EVOHOME_PASSWORD", "your_password", "User")
```

## Testing the HA Integration

### In Home Assistant Dev Environment
```bash
# Set up test config entry (from tests/conftest.py patterns)
EVOHOME_USERNAME="your.email@example.com" EVOHOME_PASSWORD="your_password" \
python -m homeassistant -c ./config
```

### Via UI
1. Start Home Assistant
2. Settings → Devices & Services → Create Integration
3. Select "Honeywell Evohome Security"
4. Enter credentials when prompted
5. Verify entity appears and responds

## Library Usage (Direct)

```python
from evohome_security_async import EvohomeSecurityClient

# Using credentials from environment
from credentials_helper import get_credentials

username, password = get_credentials()

# Use with context manager (handles login/logout)
async with EvohomeSecurityClient(username, password) as client:
    # Automatically authenticates on entry
    status = await client.get_status()
    print(f"Alarm status: {status.name}")

    # Automatically logs out on exit
```

## Troubleshooting

### "Error: EVOHOME_USERNAME environment variable not set"
**Solution**: Set the environment variable before running:
```bash
export EVOHOME_USERNAME="your.email@example.com"
export EVOHOME_PASSWORD="your_password"
```

### "Session Expired" or "Session Already Exists"
**Issue**: Total Connect server maintains sessions for 15-60+ minutes
**Solutions**:
- Use a different test account
- Wait for server-side session to expire
- Use the login/logout-per-operation pattern (already implemented)

### HA Integration Not Appearing
**Checklist**:
1. ✅ Integration installed in `homeassistant/components/evohome_security/`
2. ✅ manifest.json configured correctly
3. ✅ Restart Home Assistant after adding integration files
4. ✅ Check Home Assistant logs for errors

## Security Notes

⚠️ **IMPORTANT**:
- Never commit credentials to git
- Never hardcode passwords in scripts
- Environment variables are per-session (not saved)
- HA's secure storage (secrets.yaml) is encrypted at rest
- Use strong, unique passwords for test accounts

## API Reference

### Client Methods
- `authenticate()` - Validate credentials
- `get_status()` - Get current alarm status
- `arm_total()` - Arm with instant disarm
- `arm_home()` - Arm in home mode
- `arm_partial()` - Arm with time delay
- `disarm()` - Disarm the system
- `logout()` - Explicit logout (auto-called by context manager)

### Status Values (ArmStatus enum)
- `DISARMED` (0) - System disarmed
- `ARMED_HOME` (1) - Armed in home mode
- `ARMED_AWAY` (2) - Armed away
- `ARMING` - System is arming
- `TRIGGERED` - Alarm triggered
- `UNKNOWN` - Unknown status

## References

- **Library**: `/workspaces/core/evohome-security-async/`
- **HA Integration**: `/workspaces/core/homeassistant/components/evohome_security/`
- **Test Scripts**: `/workspaces/core/evohome-security-async/test_*.py`
- **Credential Helper**: `/workspaces/core/evohome-security-async/credentials_helper.py`
