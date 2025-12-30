"""Helper function to get credentials from environment variables."""

import os


def get_credentials() -> tuple[str, str]:
    """Get credentials from environment variables.

    Returns:
        Tuple of (username, password)

    Raises:
        ValueError: If credentials are not set
    """
    username = os.environ.get("EVOHOME_USERNAME")
    password = os.environ.get("EVOHOME_PASSWORD")

    if not username or not password:
        msg = (
            "Credentials not found. Set environment variables:\n"
            "  export EVOHOME_USERNAME='your-email'\n"
            "  export EVOHOME_PASSWORD='your-password'"
        )
        raise ValueError(msg)

    return username, password
