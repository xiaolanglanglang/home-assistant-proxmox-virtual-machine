from homeassistant.components.switch import SwitchEntity
from homeassistant.const import STATE_ON, STATE_OFF
from .const import CONF_NODE, CONF_MACHINE, DOMAIN, LOGGER, CLIENT


async def async_setup_entry(hass, entry, async_add_devices):
    logger = hass.data[DOMAIN][LOGGER]
    logger.info("setup switch")
    client = hass.data[DOMAIN][CLIENT]
    node = entry.data[CONF_NODE]
    machine = entry.data[CONF_MACHINE]
    unique_id = node + "_" + machine
    switch = ProxmoxVirtualMachineSwaitch(
        unique_id=unique_id,
        hass=hass,
        logger=logger,
        node=node,
        machine=machine,
        client=client,
    )
    await switch.async_update()
    async_add_devices([switch])
    return True


class ProxmoxVirtualMachineSwaitch(SwitchEntity):
    def __init__(
        self, unique_id, hass, logger, node, machine, client, state=STATE_ON
    ) -> None:
        super().__init__()
        self._hass = hass
        self._unique_id = unique_id
        self._logger = logger
        self._node = node
        self._machine = machine
        self._client = client
        self._state = state

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def is_on(self):
        return self._state == STATE_ON

    async def async_turn_on(self):
        """Turn the entity on."""
        self._logger.info(f"switch on, node: ({self._node}), vm: ({self._machine})")
        self._hass.loop.create_task(self._client.start(self._node, self._machine))
        self._state = STATE_ON

    async def async_turn_off(self):
        """Turn the entity off."""
        self._logger.info(f"switch off, node: ({self._node}), vm: ({self._machine})")
        self._hass.loop.create_task(
            self._client.shutdown_by_agent(self._node, self._machine)
        )
        self._state = STATE_OFF

    async def async_update(self):
        self._logger.debug("async upadte")
        status = await self._client.status(self._node, self._machine)
        if status == "running":
            self._state = STATE_ON
        else:
            self._state = STATE_OFF
