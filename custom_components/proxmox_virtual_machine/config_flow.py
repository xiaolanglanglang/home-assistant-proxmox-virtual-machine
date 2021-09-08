from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_NODE,
    CONF_MACHINE,
)
import voluptuous as vol

SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT, default=8006): cv.positive_int,
        vol.Required(CONF_USERNAME, default="root@pam"): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_NODE): cv.string,
        vol.Required(CONF_MACHINE): cv.string,
    }
)


class ProxmoxVirtualMachineConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""

    async def async_step_user(self, info):
        if info is not None:
            print("async_step_user:" + str(info))
            return self.async_create_entry(title="Proxmox Virtural Machine", data=info)
        return self.async_show_form(step_id="user", data_schema=SCHEMA)
