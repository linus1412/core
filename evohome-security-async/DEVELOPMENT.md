# Development and Testing Guide

## Installation for Development

```bash
cd evohome-security-async
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest tests/
```

With coverage:
```bash
pytest tests/ --cov=evohome_security_async --cov-report=html
```

## Running the Example

```bash
# Set environment variables
export EVOHOME_USERNAME="your.email@example.com"
export EVOHOME_PASSWORD="your_password"

# Run the example
python example.py
```

Or without environment variables (will prompt):
```bash
python example.py
```

## Code Quality

Run linting:
```bash
ruff check evohome_security_async/
```

Run type checking:
```bash
mypy evohome_security_async/
```

Auto-format code:
```bash
ruff format evohome_security_async/
```

## Library Architecture

### Key Components

1. **EvohomeSecurityClient** - Main client class
   - Manages aiohttp session
   - Handles authentication flow
   - Provides methods for all security operations

2. **Session Management**
   - JSESSIONID cookie (from initial page visit)
   - homeSessionId token (extracted from HTML, used as x-session-token header)
   - Automatic re-authentication on session expiry

3. **API Operations**
   - `authenticate()` - Initial authentication
   - `get_status()` - Query current alarm state
   - `arm_total()` - Arm away mode
   - `arm_partial()` - Arm home mode
   - `disarm(code)` - Disarm with optional code

### Authentication Flow

```
1. GET /                        -> Get initial JSESSIONID cookie
2. GET /validate?_=<timestamp>  -> Authenticate with Basic Auth header
3. GET /go/home                 -> Extract homeSessionId from HTML
4. Store homeSessionId          -> Use as x-session-token for all API calls
```

### API Request Pattern

All command/status requests use:
- Method: PUT
- URL: /applicationservice/domoweb/panel/commands/{action}
- Headers: x-session-token (homeSessionId)
- Cookies: JSESSIONID + required cookies
- Body: JSON payload {"key": "", "value": ""}

### Status Response

```json
{
  "statusCode": 0,  // 0=disarmed, 1=partial, 2=total
  "panelId": {
    "istState": "REQ-DISARM",  // Alternative status indicator
    ...
  }
}
```

## Publishing to PyPI

1. Update version in `pyproject.toml`
2. Build the package:
   ```bash
   python -m build
   ```
3. Upload to PyPI:
   ```bash
   python -m twine upload dist/*
   ```

## Next Steps for Home Assistant Integration

Once this library is stable and published to PyPI:

1. Create HACS custom component structure
2. Use this library as a dependency in manifest.json
3. Implement config flow for username/password
4. Create alarm_control_panel entity
5. Add data update coordinator for status polling
6. Optionally add binary sensors for zones/sensors

See the Home Assistant documentation for integration development:
https://developers.home-assistant.io/docs/creating_integration_manifest
