import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers import device_registry as dr, entity_registry as er

_LOGGER = logging.getLogger(__name__)


class CommandButton(ButtonEntity):
    """Representation of a Broadlink command as a button."""

    def __init__(
        self,
        mac_address,
        device_name,
        command_name,
        command_data,
        unique_id,
        config_entry,
    ):
        self._mac_address = mac_address
        self._device_name = device_name
        self._command_name = command_name
        self._command_data = command_data
        self._attr_name = f"{device_name} {command_name} Button"
        self._attr_unique_id = unique_id
        self._attr_device_info = {
            "identifiers": {
                (dr.CONNECTION_NETWORK_MAC, f"{mac_address}_{device_name}")
            },
            "name": device_name,
            "manufacturer": "Broadlink",
            "model": "Controlled Device",
            "sw_version": "1.0",
            "via_device": (dr.CONNECTION_NETWORK_MAC, mac_address),
        }
        self._config_entry = config_entry

    async def async_press(self):
        """Handle the button press asynchronously."""
        _LOGGER.debug(
            f"Sending command '{self._command_name}' for device '{self._device_name}' via hub '{self._mac_address}'"
        )

        # Normalize MAC address for consistent lookup
        normalized_mac = self._normalize_mac(self._mac_address)

        # Retrieve the device from the device registry
        device_registry = dr.async_get(self.hass)
        device = None

        # Look up the device using the normalized MAC address
        for device_entry in device_registry.devices.values():
            for identifier in device_entry.identifiers:
                test_value = self._normalize_mac(identifier[1])
                if "broadlink" in identifier[0] and test_value == normalized_mac:
                    device = device_entry
                    break

        if not device:
            _LOGGER.error(
                f"No device found in the registry for MAC address: {self._mac_address}"
            )
            return

        # Find the associated remote entity for this device
        entity_registry = er.async_get(self.hass)
        remote_entity_id = None

        for entity_entry in entity_registry.entities.values():
            if entity_entry.device_id == device.id and entity_entry.domain == "remote":
                remote_entity_id = entity_entry.entity_id
                break

        if not remote_entity_id:
            _LOGGER.error(f"Could not find remote entity for device: {device.name}")
            return

        # Build the service data
        service_data = {
            "entity_id": remote_entity_id,
            "device": self._device_name,
            "command": self._command_name,
        }

        # Call the remote.send_command service
        await self.hass.services.async_call(
            domain="remote",
            service="send_command",
            service_data=service_data,
            blocking=True,
        )

    @staticmethod
    def _normalize_mac(mac: str) -> str:
        """Normalize a MAC address by removing colons and converting to uppercase."""
        return mac.replace(":", "").upper()
