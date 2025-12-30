"""Config flow for Honeywell Evohome Security integration."""

from __future__ import annotations

import logging
from typing import Any

from evohome_security_async import EvohomeSecurityClient
from evohome_security_async.exceptions import AuthenticationError
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

from .const import CONF_BASE_URL, DEFAULT_BASE_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
    }
)


class EvohomeSecurityConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Honeywell Evohome Security."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                async with EvohomeSecurityClient(
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                    base_url=user_input.get(CONF_BASE_URL, DEFAULT_BASE_URL),
                ) as client:
                    await client.authenticate()
                    await self.async_set_unique_id(user_input[CONF_USERNAME].lower())
                    self._abort_if_unique_id_configured()

                data = {
                    CONF_USERNAME: user_input[CONF_USERNAME],
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                }
                if user_input.get(CONF_BASE_URL, DEFAULT_BASE_URL) != DEFAULT_BASE_URL:
                    data[CONF_BASE_URL] = user_input[CONF_BASE_URL]

                return self.async_create_entry(
                    title=user_input[CONF_USERNAME],
                    data=data,
                )
            except AuthenticationError:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
