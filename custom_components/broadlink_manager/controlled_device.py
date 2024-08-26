import logging
from homeassistant.helpers import device_registry as dr

_LOGGER = logging.getLogger(__name__)


class ControlledDevice:
    def __init__(self, hass, mac_address, device_name):
        self.hass = hass
        self.mac_address = mac_address
        self.device_name = device_name

    async def register(self, config_entry):
        device_registry = dr.async_get(self.hass)
        unique_id = f"{self.mac_address}_{self.device_name}"
        device_registry.async_get_or_create(
            config_entry_id=config_entry.entry_id,
            identifiers={(dr.CONNECTION_NETWORK_MAC, unique_id)},
            manufacturer="Broadlink-Controlled",
            model=self.device_name,
            name=self.device_name,
        )
        _LOGGER.debug(f"Registered controlled device: {self.device_name}")

    async def unregister(self):
        device_registry = dr.async_get(self.hass)
        unique_id = f"{self.mac_address}_{self.device_name}"
        device_entry = device_registry.async_get((dr.CONNECTION_NETWORK_MAC, unique_id))
        if device_entry:
            device_registry.async_remove_device(device_entry.id)
            _LOGGER.debug(f"Unregistered controlled device: {self.device_name}")

    def exists(self):
        device_registry = dr.async_get(self.hass)
        unique_id = f"{self.mac_address}_{self.device_name}"
        return (
            device_registry.async_get_device(
                identifiers={(dr.CONNECTION_NETWORK_MAC, unique_id)}
            )
            is not None
        )
