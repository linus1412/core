"""Enums for Evohome Security."""

from enum import Enum


class ArmStatus(Enum):
    """Enum representing the possible arm statuses of the security system."""

    DISARMED = "disarmed"
    ARMED_HOME = "armed_home"
    ARMED_AWAY = "armed_away"
    ARMING = "arming"
    TRIGGERED = "triggered"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        """Return string representation."""
        return self.value
