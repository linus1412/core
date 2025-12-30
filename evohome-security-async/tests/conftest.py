"""Pytest configuration."""

import pytest


@pytest.fixture
def anyio_backend():
    """Use asyncio backend for tests."""
    return "asyncio"
