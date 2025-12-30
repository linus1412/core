"""Main client for Evohome Security."""

from __future__ import annotations

import asyncio
import base64
import logging
import re
import time
from http.cookies import SimpleCookie
from pathlib import Path
from typing import Any, Self

import aiohttp
from yarl import URL

from .enums import ArmStatus
from .exceptions import ApiError, AuthenticationError

_LOGGER = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://tc20e.total-connect.eu"

HTTP_OK = 200
HTTP_CREATED = 201

DISARMED_CODE = 0
ARMED_HOME_CODE = 1
ARMED_AWAY_CODE = 2


class EvohomeSecurityClient:
    """Client for interacting with the Total Connect security system."""

    def __init__(
        self,
        username: str,
        password: str,
        base_url: str = DEFAULT_BASE_URL,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self.username = username
        self.password = password
        self.base_url = base_url
        self._session = session
        self._own_session = session is None
        self._home_session_id: str | None = None
        self._is_authenticated = False

    async def __aenter__(self) -> Self:
        if self._session is None:
            parsed_url = URL(self.base_url)
            host = parsed_url.host or "tc20e.total-connect.eu"

            user_agent = (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
            )
            sec_ch_ua = (
                '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"'
            )
            headers = {
                "User-Agent": user_agent,
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8,pl;q=0.7",
                "Connection": "keep-alive",
                "Content-Type": "application/json; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "DNT": "1",
                "Host": host,
                "Origin": self.base_url,
                "sec-ch-ua": sec_ch_ua,
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"macOS"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
            }
            self._session = aiohttp.ClientSession(headers=headers)
        return self

    async def __aexit__(self, *args: object) -> None:
        if self._is_authenticated:
            try:
                await self.logout()
            except Exception as err:  # noqa: BLE001
                _LOGGER.warning("Error during logout: %s", err)
        await self.close()

    async def close(self) -> None:
        if self._own_session and self._session:
            await self._session.close()
            self._session = None

    @property
    def is_authenticated(self) -> bool:
        return self._is_authenticated and self._home_session_id is not None

    async def authenticate(self) -> bool:
        if self._session is None:
            msg = "Session not initialized. Use async with context manager."
            raise RuntimeError(msg)

        _LOGGER.debug("Authenticating with Total Connect system")

        try:
            _LOGGER.debug("Visiting main page to get initial cookies")
            async with self._session.get(self.base_url) as response:
                if response.status != HTTP_OK:
                    msg = f"Failed to access main page: {response.status}"
                    raise AuthenticationError(msg)
                _LOGGER.debug(
                    "Received main page, cookies should now include JSESSIONID"
                )

            self._set_required_cookies()

            auth_string = f"{self.username}:{self.password}:1:0"
            auth_bytes = auth_string.encode("ascii")
            base64_bytes = base64.b64encode(auth_bytes)
            base64_auth = base64_bytes.decode("ascii")

            auth_headers = {
                "Authorization": f"Basic {base64_auth}",
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{self.base_url}/",
                "x-captcha": "",
                "x-remember-me": "false",
            }

            timestamp = int(time.time() * 1000)
            validate_url = f"{self.base_url}/validate?_={timestamp}"

            _LOGGER.debug("Sending validation request")
            async with self._session.get(
                validate_url, headers=auth_headers
            ) as response:
                if response.status != HTTP_OK:
                    msg = f"Authentication failed: {response.status}"
                    raise AuthenticationError(msg)
                _LOGGER.debug("Validation response status: %s", response.status)
                response_text = await response.text()
                _LOGGER.debug("Validation response body: %r", response_text)

                if not response_text.startswith("#"):
                    msg = (
                        "Authentication failed: unexpected response: "
                        f"{response_text}"
                    )
                    raise AuthenticationError(msg)

                _LOGGER.debug("Cookies after validation:")
                for cookie in self._session.cookie_jar:
                    _LOGGER.debug("  %s: %s", cookie.key, cookie.value)

            _LOGGER.info("Authentication successful - validation passed")
            self._is_authenticated = True

            await asyncio.sleep(1.0)

            if "Authorization" in self._session.headers:
                del self._session.headers["Authorization"]

            self._session.headers["Referer"] = f"{self.base_url}/go/home"

            self._set_required_cookies()

            await self._get_home_session_id()

        except aiohttp.ClientError as err:
            _LOGGER.exception("Authentication error")
            self._is_authenticated = False
            msg = f"Authentication failed: {err}"
            raise AuthenticationError(msg) from err
        return True

    def _set_required_cookies(self) -> None:
        if self._session is None:
            return

        base_url = URL(self.base_url)

        cookies_to_set = {
            "dw_c_contextpath": "",
            "binstallationscreen": "false",
            "dw_c_clientName": "",
            "clickedLogoutBtn": "false",
            "dw_c_defaultLocale": "en",
            "dw_c_defaultLocaleIndex": "1",
        }

        _LOGGER.debug("Setting required cookies")
        simple_cookie = SimpleCookie()
        for name, value in cookies_to_set.items():
            simple_cookie[name] = value

        self._session.cookie_jar.update_cookies(simple_cookie, response_url=base_url)

        _LOGGER.debug("Current cookies in jar:")
        for cookie in self._session.cookie_jar:
            domain = cookie.get("domain", "")
            path = cookie.get("path", "")
            _LOGGER.debug(
                "  %s: %s (domain=%s, path=%s)", cookie.key, cookie.value, domain, path
            )

    async def _get_home_session_id(self) -> None:
        if self._session is None:
            msg = "Session not initialized"
            raise RuntimeError(msg)

        _LOGGER.debug("Getting home page to extract homeSessionId")

        self._set_required_cookies()

        home_url = f"{self.base_url}/go/home"

        home_headers = {
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,image/apng,*/*;q=0.8,"
                "application/signed-exchange;v=b3;q=0.7"
            ),
            "Referer": f"{self.base_url}/",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
        }

        _LOGGER.debug("Requesting home page: %s", home_url)

        _LOGGER.debug("Cookies being sent with request:")
        for cookie in self._session.cookie_jar:
            _LOGGER.debug("  %s=%s", cookie.key, cookie.value)

        async with self._session.get(
            home_url, headers=home_headers, allow_redirects=True
        ) as response:
            _LOGGER.debug("Final URL after redirects: %s", response.url)
            _LOGGER.debug("Response status: %s", response.status)
            _LOGGER.debug("Response headers: %s", dict(response.headers))

            if response.status != HTTP_OK:
                msg = f"Failed to get home page: {response.status}"
                raise AuthenticationError(msg)

            html_content = await response.text()
            _LOGGER.debug("Received home page HTML (%d bytes)", len(html_content))

            home_session_id = self._extract_home_session_id(html_content)

            if not home_session_id:
                try:
                    debug_file = Path("/tmp/evohome_home_page_debug.html")
                    debug_file.write_text(html_content)
                    msg_long = (
                        "Failed to extract homeSessionId. HTML saved to "
                        "/tmp/evohome_home_page_debug.html for inspection"
                    )
                    _LOGGER.error(msg_long)
                except Exception:  # noqa: BLE001
                    pass
                msg = "Failed to extract homeSessionId from home page"
                raise AuthenticationError(msg)

            self._home_session_id = home_session_id
            _LOGGER.info("Successfully extracted homeSessionId")

    def _extract_home_session_id(self, html_content: str) -> str | None:
        _LOGGER.debug(
            "Extracting homeSessionId from HTML (%d chars)", len(html_content)
        )

        if "homeSessionId" in html_content:
            idx = html_content.find("homeSessionId")
            start = max(0, idx - 100)
            end = min(len(html_content), idx + 200)
            _LOGGER.debug(
                "Found 'homeSessionId' in HTML, context: %s",
                html_content[start:end],
            )
        else:
            _LOGGER.debug("'homeSessionId' string not found in HTML")
            _LOGGER.debug("HTML preview (first 500 chars): %s", html_content[:500])

        patterns = [
            r"var\s+homeSessionId\s*=\s*['\"]([^'\"]+)['\"]",
            r"homeSessionId\s*=\s*['\"]([^'\"]+)['\"]",
            r'"homeSessionId":\s*"([^"]+)"',
            r"homeSessionId='([^']+)'",
            r'homeSessionId="([^"]+)"',
                r'data-home-session-id="([^"]+)"',
            r"data-home-session-id='([^']+)'",
            r"<input[^>]*name=['\"]homeSessionId['\"][^>]*value=['\"]([^'\"]+)['\"]",
        ]

        for pattern in patterns:
            match = re.search(pattern, html_content)
            if match:
                _LOGGER.debug("Found homeSessionId using pattern: %s", pattern)
                return match.group(1)

        _LOGGER.debug("Could not extract homeSessionId using any pattern")
        return None

    async def _ensure_authenticated(self) -> None:
        if not self.is_authenticated:
            _LOGGER.debug("Not authenticated, authenticating first")
            await self.authenticate()

    def _get_api_headers(self) -> dict[str, str]:
        jsessionid = ""
        if self._session and self._session.cookie_jar:
            for cookie in self._session.cookie_jar:
                if cookie.key == "JSESSIONID":
                    jsessionid = cookie.value
                    break

        cookie_header = (
            f"dw_c_contextpath=; binstallationscreen=false; dw_c_clientName=; "
            f"dw_c_defaultLocale=en; dw_c_defaultLocaleIndex=1; "
            f"JSESSIONID={jsessionid}; clickedLogoutBtn=false"
        )

        headers = {
            "cookie": cookie_header,
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{self.base_url}/go/home",
            "Origin": self.base_url,
            "Connection": "keep-alive",
            "DNT": "1",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

        if self._home_session_id:
            headers["x-session-token"] = self._home_session_id

        return headers

    async def get_status(self) -> ArmStatus:
        await self._ensure_authenticated()

        if self._session is None:
            msg = "Session not initialized"
            raise RuntimeError(msg)

        _LOGGER.debug("Getting current system status")

        status_url = (
            f"{self.base_url}/applicationservice/domoweb/panel/commands/status"
            "?isBusy=true&checkCompletion=true"
        )

        headers = self._get_api_headers()
        payload = {"key": "", "value": ""}

        try:
            async with self._session.put(
                status_url, headers=headers, json=payload
            ) as response:
                if response.status in {401, 403}:
                    _LOGGER.warning("Session expired, re-authenticating")
                    self._is_authenticated = False
                    await self.authenticate()
                    return await self.get_status()
                if response.status not in (HTTP_OK, HTTP_CREATED):
                    msg = f"Status query failed: {response.status}"
                    raise ApiError(msg)

                data = await response.json()
                _LOGGER.debug("Status response: %s", data)
                return self._parse_status_response(data)

        except aiohttp.ClientError as err:
            _LOGGER.exception("Error getting status")
            msg = f"Failed to get status: {err}"
            raise ApiError(msg) from err

    def _parse_status_response(self, data: dict[str, Any]) -> ArmStatus:  # noqa: PLR0911
        if "statusCode" in data:
            status_code = data["statusCode"]
            if status_code == DISARMED_CODE:
                return ArmStatus.DISARMED
            if status_code == ARMED_HOME_CODE:
                return ArmStatus.ARMED_HOME
            if status_code == ARMED_AWAY_CODE:
                return ArmStatus.ARMED_AWAY

        if "panelId" in data and "istState" in data["panelId"]:
            ist_state = data["panelId"]["istState"]
            ist_state_upper = ist_state.upper()

            if "DISARM" in ist_state_upper:
                return ArmStatus.DISARMED
            if "PARTIAL" in ist_state_upper or "PART" in ist_state_upper:
                return ArmStatus.ARMED_HOME
            if "ARM" in ist_state_upper:
                return ArmStatus.ARMED_AWAY
            if "ARMING" in ist_state_upper or "COUNTDOWN" in ist_state_upper:
                return ArmStatus.ARMING
            if "ALARM" in ist_state_upper or "TRIGGER" in ist_state_upper:
                return ArmStatus.TRIGGERED

        _LOGGER.warning("Could not determine status from response: %s", data)
        return ArmStatus.UNKNOWN

    async def arm_total(self) -> bool:
        await self._ensure_authenticated()

        if self._session is None:
            msg = "Session not initialized"
            raise RuntimeError(msg)

        _LOGGER.info("Arming system in total/away mode")

        arm_url = (
            f"{self.base_url}/applicationservice/domoweb/panel/commands/arm"
            "?isBusy=true&checkCompletion=true"
        )

        return await self._send_command(arm_url, "arm total")

    async def arm_partial(self) -> bool:
        await self._ensure_authenticated()

        if self._session is None:
            msg = "Session not initialized"
            raise RuntimeError(msg)

        _LOGGER.info("Arming system in partial/home mode")

        arm_url = (
            f"{self.base_url}/applicationservice/domoweb/panel/commands/partialarm"
            "?isBusy=true&checkCompletion=true"
        )

        return await self._send_command(arm_url, "arm partial")

    async def disarm(self, code: str = "") -> bool:
        await self._ensure_authenticated()

        if self._session is None:
            msg = "Session not initialized"
            raise RuntimeError(msg)

        _LOGGER.info("Disarming system")

        disarm_url = (
            f"{self.base_url}/applicationservice/domoweb/panel/commands/disarm"
            "?isBusy=true&checkCompletion=true"
        )

        payload = {"key": "disarmCode", "value": code}

        return await self._send_command(disarm_url, "disarm", payload)

    async def logout(self) -> bool:
        if self._session is None:
            msg = "Session not initialized"
            raise RuntimeError(msg)

        _LOGGER.info("Logging out from Total Connect system")

        try:
            jsessionid = None
            for cookie in self._session.cookie_jar:
                if cookie.key == "JSESSIONID":
                    jsessionid = cookie.value
                    break

            if not jsessionid:
                _LOGGER.debug("No JSESSIONID found, skipping logout")
                return True

            cookie_parts = [
                "dw_c_contextpath=",
                "binstallationscreen=false",
                "dw_c_clientName=",
                "dw_c_defaultLocale=en",
                "dw_c_defaultLocaleIndex=1",
                f"JSESSIONID={jsessionid}",
                "clickedLogoutBtn=true",
            ]

            cookie_string = "; ".join(cookie_parts)

            headers = {
                "Cookie": cookie_string,
                "Referer": f"{self.base_url}/go/home",
            }

            if self._home_session_id:
                headers["x-session-token"] = self._home_session_id

            logout_url = f"{self.base_url}/logout"
            _LOGGER.debug("Sending logout request to %s", logout_url)

            async with self._session.get(
                logout_url, headers=headers, allow_redirects=False
            ) as response:
                if response.status in (HTTP_OK, 302, 303):
                    _LOGGER.info("Logout successful")
                    self._is_authenticated = False
                    self._home_session_id = None
                    return True
                _LOGGER.warning("Logout returned status %s", response.status)
                self._is_authenticated = False
                self._home_session_id = None
                return False

        except Exception:  # noqa: BLE001
            _LOGGER.exception("Logout error")
            self._is_authenticated = False
            self._home_session_id = None
            return False

    async def _send_command(
        self,
        url: str,
        command_name: str,
        payload: dict[str, str] | None = None,
    ) -> bool:
        if self._session is None:
            msg = "Session not initialized"
            raise RuntimeError(msg)

        headers = self._get_api_headers()
        if payload is None:
            payload = {"key": "", "value": ""}

        try:
            async with self._session.put(
                url, headers=headers, json=payload
            ) as response:
                if response.status in {401, 403}:
                    _LOGGER.warning(
                        "Session expired during %s, re-authenticating", command_name
                    )
                    self._is_authenticated = False
                    await self.authenticate()
                    return await self._send_command(url, command_name, payload)

                if response.status not in (HTTP_OK, HTTP_CREATED):
                    msg = f"{command_name} command failed: {response.status}"
                    raise ApiError(msg)

                _LOGGER.info("%s command sent successfully", command_name)
                return True

        except aiohttp.ClientError as err:
            _LOGGER.exception("Error sending %s command", command_name)
            msg = f"Failed to send {command_name} command: {err}"
            raise ApiError(msg) from err
