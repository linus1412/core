"""Tests for evohome-security-async."""

import pytest
from aioresponses import aioresponses

from evohome_security_async import (
    ArmStatus,
    AuthenticationError,
    EvohomeSecurityClient,
)


@pytest.fixture
async def client():
    """Create a test client."""
    client = EvohomeSecurityClient(
        username="test@example.com",
        password="testpass",
    )
    async with client:
        yield client


@pytest.mark.asyncio
async def test_authentication_success():
    """Test successful authentication."""
    with aioresponses() as m:
        base_url = "https://tc20e.total-connect.eu"

        # Mock main page request
        m.get(base_url, status=200)

        # Mock validation request
        m.get(f"{base_url}/validate", status=200)

        # Mock home page request with homeSessionId
        home_html = """
        <html>
        <script>
            var homeSessionId = "test-session-id-123";
        </script>
        </html>
        """
        m.get(f"{base_url}/go/home", status=200, body=home_html)

        async with EvohomeSecurityClient(
            username="test@example.com",
            password="testpass",
        ) as client:
            result = await client.authenticate()
            assert result is True
            assert client.is_authenticated


@pytest.mark.asyncio
async def test_authentication_failure():
    """Test authentication failure."""
    with aioresponses() as m:
        base_url = "https://tc20e.total-connect.eu"

        # Mock main page request
        m.get(base_url, status=200)

        # Mock validation request with 401
        m.get(f"{base_url}/validate", status=401)

        async with EvohomeSecurityClient(
            username="test@example.com",
            password="badpass",
        ) as client:
            with pytest.raises(AuthenticationError):
                await client.authenticate()


@pytest.mark.asyncio
async def test_get_status():
    """Test getting system status."""
    with aioresponses() as m:
        base_url = "https://tc20e.total-connect.eu"

        # Mock authentication
        m.get(base_url, status=200)
        m.get(f"{base_url}/validate", status=200)
        home_html = '<script>var homeSessionId = "test-session-id-123";</script>'
        m.get(f"{base_url}/go/home", status=200, body=home_html)

        # Mock status request
        status_url = f"{base_url}/applicationservice/domoweb/panel/commands/status"
        m.put(
            status_url,
            status=200,
            payload={"statusCode": 0},
        )

        async with EvohomeSecurityClient(
            username="test@example.com",
            password="testpass",
        ) as client:
            await client.authenticate()
            status = await client.get_status()
            assert status == ArmStatus.DISARMED


@pytest.mark.asyncio
async def test_arm_total():
    """Test arming system in total mode."""
    with aioresponses() as m:
        base_url = "https://tc20e.total-connect.eu"

        # Mock authentication
        m.get(base_url, status=200)
        m.get(f"{base_url}/validate", status=200)
        home_html = '<script>var homeSessionId = "test-session-id-123";</script>'
        m.get(f"{base_url}/go/home", status=200, body=home_html)

        # Mock arm command
        arm_url = f"{base_url}/applicationservice/domoweb/panel/commands/arm"
        m.put(arm_url, status=200)

        async with EvohomeSecurityClient(
            username="test@example.com",
            password="testpass",
        ) as client:
            await client.authenticate()
            result = await client.arm_total()
            assert result is True
