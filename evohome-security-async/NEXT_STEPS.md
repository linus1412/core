# Next Steps to Find Arm/Disarm Endpoints

## Current Status
✅ Authentication is FULLY WORKING with format: `username:password:1:0`
✅ homeSessionId extraction working
✅ API calls with x-session-token header working

❌ Arm/disarm commands return 503 errors
❌ Status queries don't return actual alarm state

## Problem
We're guessing at the API endpoints for arm/disarm operations. The endpoints we tried:
- `/applicationservice/domoweb/panel/commands/arm/partial` → 503
- `/applicationservice/domoweb/panel/commands/arm/full` → 503
- `/applicationservice/domoweb/panel/commands/disarm` → 503
- `/applicationservice/domoweb/panel/commands/status` → Returns `{'id': xxx, 'status': 'success'}` without actual alarm state

## Solution: Capture Real Browser Operations

### Option 1: HAR File Capture (RECOMMENDED)
1. Open Chrome/Firefox with Developer Tools
2. Go to Network tab
3. Check "Preserve log"
4. Login to https://tc20e.total-connect.eu
5. **Click the "Arm Partial" button** in the UI
6. Watch the Network tab for the request that gets sent
7. Right-click on the request → "Copy as cURL"
8. Or save the entire HAR file

This will show us:
- The EXACT URL endpoint used
- The HTTP method (PUT/POST/GET)
- The request payload/body
- The response format
- Any additional headers needed

### Option 2: Browser DevTools Live Inspection
1. Open https://tc20e.total-connect.eu in Chrome
2. Open DevTools (F12)
3. Go to Network tab, filter by "Fetch/XHR"
4. Clear the network log
5. Click "Arm Partial" button
6. Look at what request appears
7. Click on it to see:
   - Request URL
   - Request Method
   - Request Headers
   - Request Payload
   - Response

### Option 3: JavaScript Debugging
1. In DevTools, go to Sources tab
2. Search for "arm" or "disarm" in the JavaScript files
3. Set breakpoints on button click handlers
4. Click the arm button and step through the code
5. See what URL it constructs and calls

## What We Need to Find

For **arm/disarm commands**:
- Correct endpoint URL
- HTTP method (PUT/POST/GET)
- Request body/payload format
- Any additional headers
- Expected response format

For **status retrieval**:
- Endpoint that returns actual alarm state (0/1/2)
- Not just command acknowledgment
- Might be embedded in home page HTML
- Might be a different API call

## Alternative: Check Original Library
The reference library might have clues:
```bash
curl -s https://raw.githubusercontent.com/linus1412/evohome_tc_security_int/master/evosec2.py | grep -A 10 "def.*arm\|def.*disarm\|def.*status"
```

## Current Test Script
Run `/workspaces/core/evohome-security-async/test_arm_disarm.py` to test once endpoints are found.

## Once We Have the Correct Endpoints
1. Update `evohome_security_async/client.py` methods:
   - `arm_partial()`
   - `arm_total()`
   - `disarm()`
   - `get_status()`
2. Update request methods/payloads/headers as needed
3. Run test_arm_disarm.py to verify
4. Move on to building Home Assistant integration
