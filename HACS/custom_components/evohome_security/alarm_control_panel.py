"""Alarm control panel platform for Honeywell Evohome Security."""

from __future__ import annotations

from datetime import timedelta
import logging

from evohome_security_async import ArmStatus, EvohomeSecurityClient
from evohome_security_async.exceptions import ApiError, AuthenticationError

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
    AlarmControlPanelState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import CONF_BASE_URL, DEFAULT_BASE_URL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

STATE_MAP = {
    ArmStatus.DISARMED: AlarmControlPanelState.DISARMED,
    ArmStatus.ARMED_HOME: AlarmControlPanelState.ARMED_HOME,
    ArmStatus.ARMED_AWAY: AlarmControlPanelState.ARMED_AWAY,
    ArmStatus.ARMING: AlarmControlPanelState.ARMING,
    ArmStatus.TRIGGERED: AlarmControlPanelState.TRIGGERED,
    ArmStatus.UNKNOWN: None,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Honeywell Evohome Security alarm control panel."""
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    base_url = entry.data.get(CONF_BASE_URL, DEFAULT_BASE_URL)

    coordinator = EvohomeSecurityCoordinator(hass, username, password, base_url)

    await coordinator.async_config_entry_first_refresh()

    async_add_entities([EvohomeSecurityAlarm(coordinator, entry)])


class EvohomeSecurityCoordinator(DataUpdateCoordinator[ArmStatus]):
    """Coordinator to manage data updates with login/logout per operation."""

    def __init__(
        self, hass: HomeAssistant, username: str, password: str, base_url: str
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.username = username
        self.password = password
        self.base_url = base_url

    async def _async_update_data(self) -> ArmStatus:
        """Fetch data from API with login/logout."""
        async with EvohomeSecurityClient(
            username=self.username,
            password=self.password,
            base_url=self.base_url,
        ) as client:
            await client.authenticate()
            return await client.get_status()


class EvohomeSecurityAlarm(
    CoordinatorEntity[EvohomeSecurityCoordinator], AlarmControlPanelEntity
):
    """Representation of a Honeywell Evohome Security alarm."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = (
        AlarmControlPanelEntityFeature.ARM_HOME
        | AlarmControlPanelEntityFeature.ARM_AWAY
    )

    def __init__(
        self, coordinator: EvohomeSecurityCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the alarm control panel."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_alarm"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Evohome Security",
            "manufacturer": "Honeywell",
            "model": "Total Connect",
        }

    @property
    def state(self) -> AlarmControlPanelState | None:
        """Return the state of the device."""
        if self.coordinator.data is None:
            return None
        return STATE_MAP.get(self.coordinator.data)

    async def _execute_command(self, command_func) -> None:
        """Execute a command with login/logout to prevent blocking other users."""
        try:
            async with EvohomeSecurityClient(
                username=self.coordinator.username,
                password=self.coordinator.password,
                base_url=self.coordinator.base_url,
            ) as client:
                await client.authenticate()
                await command_func(client)

            await self.coordinator.async_request_refresh()
        except AuthenticationError as err:
            _LOGGER.error("Authentication failed: %s", err)
            raise
        except ApiError as err:
            _LOGGER.error("Command failed: %s", err)
            raise

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Send disarm command."""
        await self._execute_command(lambda client: client.disarm(code or ""))

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        """Send arm home command."""
        await self._execute_command(lambda client: client.arm_partial())

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        """Send arm away command."""
        await self._execute_command(lambda client: client.arm_total())
