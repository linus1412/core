"""Exceptions for Evohome Security."""


class EvohomeSecurityException(Exception):
    """Base exception for Evohome Security."""


class AuthenticationError(EvohomeSecurityException):
    """Exception raised when authentication fails."""


class SessionExpiredError(EvohomeSecurityException):
    """Exception raised when session has expired."""


class ApiError(EvohomeSecurityException):
    """Exception raised when API returns an error."""
