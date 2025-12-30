# Architecture Diagrams

## Overall Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Application                         │
│  (Home Assistant / Custom Script / Other Python App)        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ import evohome_security_async
                         │
┌────────────────────────▼────────────────────────────────────┐
│           evohome-security-async Library                     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  EvohomeSecurityClient                                │  │
│  │  ├─ authenticate()                                    │  │
│  │  ├─ get_status()                                      │  │
│  │  ├─ arm_total()                                       │  │
│  │  ├─ arm_partial()                                     │  │
│  │  └─ disarm(code)                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Session Management                                   │  │
│  │  ├─ JSESSIONID cookie                                 │  │
│  │  ├─ homeSessionId token                               │  │
│  │  └─ Auto reconnection                                 │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ aiohttp (async HTTP)
                         │
┌────────────────────────▼────────────────────────────────────┐
│          Total Connect API (tc20e.total-connect.eu)         │
│                                                              │
│  ├─ /                  (Initial cookies)                    │
│  ├─ /validate          (Authentication)                     │
│  ├─ /go/home           (homeSessionId)                      │
│  └─ /applicationservice/domoweb/panel/commands/             │
│      ├─ status         (Query status)                       │
│      ├─ arm            (Arm total/away)                     │
│      ├─ partialarm     (Arm partial/home)                   │
│      └─ disarm         (Disarm)                             │
└─────────────────────────────────────────────────────────────┘
```

## Authentication Flow

```
┌──────────┐                                    ┌──────────────┐
│  Client  │                                    │ Total Connect│
└─────┬────┘                                    └──────┬───────┘
      │                                                │
      │  1. GET /                                      │
      │ ──────────────────────────────────────────>   │
      │                                                │
      │  2. 200 OK + JSESSIONID cookie                │
      │ <──────────────────────────────────────────   │
      │                                                │
      │  3. GET /validate?_=<timestamp>                │
      │     Authorization: Basic <base64>             │
      │ ──────────────────────────────────────────>   │
      │                                                │
      │  4. 200 OK (Authentication success)           │
      │ <──────────────────────────────────────────   │
      │                                                │
      │  5. GET /go/home                               │
      │     Cookie: JSESSIONID=...                    │
      │ ──────────────────────────────────────────>   │
      │                                                │
      │  6. 200 OK + HTML with homeSessionId          │
      │ <──────────────────────────────────────────   │
      │                                                │
      │  7. Extract homeSessionId from HTML            │
      │     Store as x-session-token                  │
      │                                                │
      │  Authentication Complete                       │
      │  ✓ JSESSIONID cookie set                      │
      │  ✓ homeSessionId extracted                    │
      │                                                │
```

## API Request Flow (Status Query Example)

```
┌──────────┐                                    ┌──────────────┐
│  Client  │                                    │ Total Connect│
└─────┬────┘                                    └──────┬───────┘
      │                                                │
      │  PUT /applicationservice/.../status            │
      │  Headers:                                      │
      │    x-session-token: <homeSessionId>           │
      │    Content-Type: application/json             │
      │  Cookie: JSESSIONID=...                       │
      │  Body: {"key":"","value":""}                  │
      │ ──────────────────────────────────────────>   │
      │                                                │
      │  200 OK                                        │
      │  {                                             │
      │    "statusCode": 0,  // 0=disarm, 1=home, 2=away
      │    "panelId": {                                │
      │      "istState": "REQ-DISARM",                │
      │      ...                                       │
      │    }                                           │
      │  }                                             │
      │ <──────────────────────────────────────────   │
      │                                                │
      │  Parse response → ArmStatus.DISARMED          │
      │                                                │
```

## Class Structure

```
┌─────────────────────────────────────────────────────────┐
│  EvohomeSecurityClient                                  │
├─────────────────────────────────────────────────────────┤
│  Properties:                                            │
│    - username: str                                      │
│    - password: str                                      │
│    - base_url: str                                      │
│    - _session: aiohttp.ClientSession                    │
│    - _home_session_id: str | None                       │
│    - _is_authenticated: bool                            │
├─────────────────────────────────────────────────────────┤
│  Public Methods:                                        │
│    + async authenticate() -> bool                       │
│    + async get_status() -> ArmStatus                    │
│    + async arm_total() -> bool                          │
│    + async arm_partial() -> bool                        │
│    + async disarm(code: str) -> bool                    │
│    + async close() -> None                              │
├─────────────────────────────────────────────────────────┤
│  Private Methods:                                       │
│    - _set_required_cookies() -> None                    │
│    - async _get_home_session_id() -> None               │
│    - _extract_home_session_id(html: str) -> str | None  │
│    - async _ensure_authenticated() -> None              │
│    - _get_api_headers() -> dict[str, str]               │
│    - _parse_status_response(data: dict) -> ArmStatus    │
│    - async _send_command(...) -> bool                   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  ArmStatus (Enum)                                       │
├─────────────────────────────────────────────────────────┤
│  - DISARMED                                             │
│  - ARMED_HOME                                           │
│  - ARMED_AWAY                                           │
│  - ARMING                                               │
│  - TRIGGERED                                            │
│  - UNKNOWN                                              │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Exceptions                                             │
├─────────────────────────────────────────────────────────┤
│  EvohomeSecurityException (base)                        │
│    ├─ AuthenticationError                               │
│    ├─ SessionExpiredError                               │
│    └─ ApiError                                          │
└─────────────────────────────────────────────────────────┘
```

## State Machine

```
┌─────────────────┐
│  Initial State  │
│  (not auth'd)   │
└────────┬────────┘
         │
         │ authenticate()
         ▼
┌─────────────────┐
│ Authenticated   │◄──────┐
│ (ready)         │       │
└────┬────────────┘       │
     │                    │
     │ get_status()       │
     │ arm_total()        │ auto re-auth
     │ arm_partial()      │ on 401/403
     │ disarm()           │
     ▼                    │
┌─────────────────┐       │
│  API Request    │       │
│  (in progress)  │       │
└────┬────────────┘       │
     │                    │
     ├─ Success ──────────┤
     │                    │
     └─ 401/403 ──────────┘

     close()
     │
     ▼
┌─────────────────┐
│    Closed       │
│ (session ended) │
└─────────────────┘
```

## Data Flow: Complete Operation

```
Application Code
    │
    │ 1. Create client with credentials
    ▼
EvohomeSecurityClient.__init__()
    │
    │ 2. Enter context manager
    ▼
__aenter__() → create aiohttp.ClientSession
    │
    │ 3. Call authenticate()
    ▼
authenticate()
    │
    ├─→ GET / → receive JSESSIONID cookie
    │
    ├─→ GET /validate → authenticate with Basic Auth
    │
    └─→ GET /go/home → extract homeSessionId
    │
    │ 4. Call get_status()
    ▼
get_status()
    │
    ├─→ Check if authenticated
    │
    ├─→ PUT /status with x-session-token header
    │
    ├─→ Parse JSON response
    │
    └─→ Return ArmStatus enum
    │
    │ 5. Exit context manager
    ▼
__aexit__() → close session
    │
    ▼
Application receives result
```

## Session Cookie Management

```
Session Lifecycle:

Initial Visit:
    GET /
    ← Set-Cookie: JSESSIONID=ABC123...

Stored Cookies (persisted in ClientSession):
    ┌─────────────────────────────────────┐
    │ JSESSIONID=ABC123...                │  ← From server
    │ dw_c_contextpath=                   │  ← Set by client
    │ binstallationscreen=false           │  ← Set by client
    │ dw_c_clientName=                    │  ← Set by client
    │ clickedLogoutBtn=false              │  ← Set by client
    │ dw_c_defaultLocale=en               │  ← Set by client
    │ dw_c_defaultLocaleIndex=1           │  ← Set by client
    └─────────────────────────────────────┘

All cookies automatically sent with each request

Extracted from HTML (not cookie):
    homeSessionId → used as x-session-token header
```

## Error Handling Flow

```
API Request
    │
    ▼
┌───────────────┐
│ Send Request  │
└───────┬───────┘
        │
        ├─→ Success (200) ──────────→ Parse & Return
        │
        ├─→ Auth Error (401/403) ───→ Clear auth state
        │                              │
        │                              ▼
        │                         Re-authenticate
        │                              │
        │                              ▼
        │                         Retry request
        │
        ├─→ Client Error (4xx) ─────→ Raise ApiError
        │
        ├─→ Server Error (5xx) ─────→ Raise ApiError
        │
        └─→ Network Error ──────────→ Raise ApiError
```

---

## Usage Pattern Comparison

### Synchronous (Original)
```python
client = TotalConnectClient()
try:
    if client.authenticate():
        status = client.get_status()
        if status:
            print(status)
        client.logout()
finally:
    client.close()
```

### Asynchronous (New)
```python
async with EvohomeSecurityClient(username, password) as client:
    await client.authenticate()
    status = await client.get_status()
    print(status)
# Auto cleanup - no manual logout/close needed
```

---

These diagrams show:
1. How the library fits into larger applications
2. The authentication handshake sequence
3. How API requests work
4. The internal class structure
5. State transitions during operations
6. Complete data flow from app to API
7. Cookie and session management
8. Error handling strategies
9. Usage pattern improvements
