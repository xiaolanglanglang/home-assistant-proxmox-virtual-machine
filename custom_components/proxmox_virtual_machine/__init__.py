import logging

from homeassistant.core import HomeAssistant
from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
    LOGGER,
    CLIENT,
)
from .switch import ProxmoxVirtualMachineSwaitch
from .client import ProxmoxClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry):
    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][LOGGER] = _LOGGER
    config = entry.data
    remote_url = f"https://{config[CONF_HOST]}:{config[CONF_PORT]}"
    client = ProxmoxClient(
        logger=_LOGGER,
        host=remote_url,
        name=config[CONF_USERNAME],
        password=config[CONF_PASSWORD],
    )
    hass.data[DOMAIN][CLIENT] = client
    hass.async_add_job(hass.config_entries.async_forward_entry_setup(entry, "switch"))
    return True
