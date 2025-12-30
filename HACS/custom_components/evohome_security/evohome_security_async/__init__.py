"""Async client for Honeywell Evohome (Total Connect) Security Systems."""

from .client import EvohomeSecurityClient
from .enums import ArmStatus
from .exceptions import (
    ApiError,
    AuthenticationError,
    EvohomeSecurityException,
    SessionExpiredError,
)

__version__ = "0.1.0"

__all__ = [
    "ApiError",
    "ArmStatus",
    "AuthenticationError",
    "EvohomeSecurityClient",
    "EvohomeSecurityException",
    "SessionExpiredError",
]
