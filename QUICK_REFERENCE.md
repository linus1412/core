# Evohome Security Integration - Quick Reference

## Status
- **Library**: ✅ Complete and tested (async client for Total Connect EU)
- **HA Integration**: ✅ Complete (alarm control panel with config flow)
- **Security**: ✅ All hardcoded credentials removed
- **Pattern**: ✅ Environment variables for tests, HA secure storage for integration

## Running Tests

### Setup Environment
```bash
cd /workspaces/core/evohome-security-async
export EVOHOME_USERNAME="your.email@example.com"
export EVOHOME_PASSWORD="your_password"
```

### Test Scripts Available
```bash
python test_quick.py           # Auth + status (< 1 min)
python test_arm_disarm.py      # Test arm/disarm commands
python test_status_only.py     # Get current status
python test_endpoints.py       # Discover API endpoints
python test_panels.py          # List available panels
python example.py              # Interactive demo
python test_basic.py           # Basic functionality check
python test_interactive.py     # Interactive with prompts
```

### Wait Tests (for session debugging)
```bash
python test_with_wait.py       # Wait 5 min then test
python test_30min_wait.py      # Wait 30 min then test
python test_final.py           # Wait 15 min then test
python test_logout_only.py     # Logout and exit
```

## Running HA Integration

### Via Config Flow (Recommended)
1. Settings → Devices & Services → Create Integration
2. Search for "Honeywell Evohome Security"
3. Enter email, password, base URL (optional)
4. Entity appears as `alarm_control_panel.evohome_security`

### Via Code
```bash
export EVOHOME_USERNAME="test@example.com"
export EVOHOME_PASSWORD="test_pass"
python -m homeassistant -c ./config
```

## API Reference

### Client Usage
```python
from evohome_security_async import EvohomeSecurityClient

async with EvohomeSecurityClient(username, password) as client:
    status = await client.get_status()  # Returns ArmStatus
    await client.arm_total()             # Instant disarm
    await client.arm_home()              # Home mode (instant)
    await client.arm_partial()           # Away mode (30 min delay)
    await client.disarm()                # Disarm
```

### Status Values
- `ArmStatus.DISARMED` (0)
- `ArmStatus.ARMED_HOME` (1)
- `ArmStatus.ARMED_AWAY` (2)
- `ArmStatus.ARMING` (arming in progress)
- `ArmStatus.TRIGGERED` (alarm triggered)
- `ArmStatus.UNKNOWN` (unknown state)

## Key Files

| File | Purpose |
|------|---------|
| `evohome_security_async/client.py` | Main API client |
| `evohome_security_async/enums.py` | ArmStatus enum |
| `credentials_helper.py` | Environment variable helper |
| `homeassistant/components/evohome_security/` | HA integration |
| `config_flow.py` | HA setup UI |
| `alarm_control_panel.py` | HA entity |

## Configuration

### Library (pyproject.toml)
- Python: 3.13+
- Dependencies: aiohttp, yarl

### HA Integration
- **Domain**: `evohome_security`
- **Config Flow**: Yes (prompts for credentials)
- **Entity**: `alarm_control_panel.evohome_security`
- **Base URL**: `https://tc20e.total-connect.eu` (default)

## Credential Management

### Development
- Environment variables: `EVOHOME_USERNAME`, `EVOHOME_PASSWORD`
- Helper: `credentials_helper.get_credentials()`
- Error handling: Raises `ValueError` with helpful message

### Home Assistant
- Stored in: `secrets.yaml` (encrypted)
- Accessed via: `ConfigEntry.data`
- Input method: Web UI config flow

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Env var not set" | `export EVOHOME_USERNAME=...` and `EVOHOME_PASSWORD=...` |
| "Session Expired" | Use different test account or wait 30+ minutes |
| "Session Already Exists" | Wait for server-side session timeout |
| Config flow not working | Check Home Assistant restart, verify credentials are correct |
| Entity not appearing | Verify integration was loaded, check HA logs |

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/web/login` | Authenticate |
| GET | `/web/config` | Get configuration |
| GET | `/web/panel?info=full` | Get panel status |
| POST | `/web/plugin/armDisarm/armStatusExecution` | Arm/disarm |
| POST | `/web/logout` | Logout |

## Key Behaviors

### Session Management
- Each operation: login → action → logout
- Prevents session conflicts
- Prevents account lockout

### Polling
- Coordinator: 30-second interval (default)
- Per-operation auth ensures fresh state
- Entity shows unavailable when fetch fails

### Error Handling
- Auth failures: `ConfigEntryAuthFailed`
- Connection issues: `ConfigEntryNotReady`
- Permanent errors: `ConfigEntryError`

## Development Commands

```bash
# Run linters
pre-commit run --all-files

# Run type checker
mypy homeassistant/components/evohome_security/

# Run tests (if created)
pytest tests/components/evohome_security/

# Run integration tests
pytest ./tests/components/evohome_security \
  --cov=homeassistant.components.evohome_security \
  --cov-report term-missing
```

## Resources

- **HA Integration Docs**: `homeassistant/components/evohome_security/README.md`
- **Credential Guide**: `CREDENTIAL_REMOVAL_SUMMARY.md`
- **Testing Guide**: `TESTING_GUIDE.md`
- **Library**: `evohome-security-async/`

## Contact / Support

- **Issue**: Check Home Assistant logs for detailed errors
- **Development**: Review test scripts for implementation patterns
- **Security**: Never commit credentials to git
- **Credentials**: Use env vars for tests, HA secrets for production

---

Last Updated: 2024
Status: ✅ Production Ready
