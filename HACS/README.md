# Honeywell Evohome Security (HACS)

A standalone HACS-compatible custom integration for Honeywell Evohome Security (Total Connect EU). It mirrors the Home Assistant core integration and bundles the async client library so no extra pip install is required.

## Features
- UI config flow (email/password, optional base URL)
- Alarm control panel entity with arm away, arm home, disarm
- Login/logout per operation to avoid session conflicts
- 30s polling via DataUpdateCoordinator

## Installation
1. Copy or add this repository as a custom repository in HACS (category: Integration).
2. Install the integration from HACS.
3. Restart Home Assistant.
4. In Settings → Devices & Services → Add Integration, search for "Honeywell Evohome Security" and enter your credentials.

## Folder Structure
```
HACS/
  hacs.json
  README.md
  custom_components/evohome_security/
    manifest.json
    __init__.py
    const.py
    config_flow.py
    alarm_control_panel.py
    strings.json
    evohome_security_async/  # bundled client library
      __init__.py
      client.py
      enums.py
      exceptions.py
```

## Notes
- Requirements are vendored; manifest requirements are empty.
- Base URL defaults to `https://tc20e.total-connect.eu`; override in the config flow if needed for another region.
