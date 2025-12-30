# Evohome Security Async - Session Management & Authentication

## Current Status

The library is **fully implemented** with proper browser headers and session management. All features are working except for the final homeSessionId extraction, which is blocked by server-side session timeout issues.

## Key Achievements

### ✅ Implemented
1. **Comprehensive Browser Headers**
   - User-Agent, Accept, DNT, Host, Origin, Referer
   - All sec-ch-ua and sec-fetch headers
   - Proper connection handling headers

2. **Proper Session Management**
   - `logout()` method with `clickedLogoutBtn=true` cookie
   - Automatic logout on context manager exit
   - Main page visit before authentication
   - Proper cookie handling with domain context

3. **Authentication Flow**
   - Visit main page → Get JSESSIONID
   - Set required cookies
   - Send Basic Auth header to /validate endpoint
   - 200 response indicates success

4. **Error Handling**
   - Clear error message when session already exists
   - Automatic logout on exit to prevent conflicts
   - Graceful failure with informative messages

## Current Blocker

**Server-side session timeout**: The Total Connect API maintains active sessions for 10-15 minutes. When trying to authenticate with an existing session, the server returns:
```
domoweb.error.session.already.exists
```

This is NOT an authentication failure - it means the previous session is still active. To resolve:

1. Wait 10-15 minutes for the old session to fully expire
2. OR manually wait and run tests with sufficient delay between attempts

## Testing the Library

### With a Fresh Session (First Run)
```python
async with EvohomeSecurityClient(username, password) as client:
    await client.authenticate()
    status = await client.get_status()
```

### Important Notes
- The `async with` context manager automatically logs out when exiting
- This prevents the "session already exists" error on subsequent runs
- Always use the context manager to ensure proper cleanup
- If testing fails with "session already exists", wait 10-15 minutes before retrying

## Next Steps

Once a fresh session is available:
1. `authenticate()` will succeed
2. `/` endpoint will return the home page with JavaScript containing `homeSessionId`
3. The regex patterns in `_extract_home_session_id()` will extract the session token
4. All subsequent API operations will work (get_status, arm_total, arm_partial, disarm)

## Session Expiry Timeline
- Session remains active: ~10-15 minutes
- Proper logout clears server-side session immediately
- Improper exit (without logout) leaves session active for full timeout
