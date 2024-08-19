import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import (
    entity_registry as er,
)  # Correct import for entity registry

_LOGGER = logging.getLogger(__name__)


def normalize_mac(mac: str) -> str:
    """Normalize a MAC address by removing colons and converting to uppercase."""
    return mac.replace(":", "").upper()


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities
):
    """Set up Broadlink Manager devices and their commands."""

    devices = hass.data[DOMAIN][config_entry.entry_id]
    mac_address = config_entry.data.get("mac_address")
    entities = []

    for device_name, commands in devices.items():
        _LOGGER.debug(f"Setting up buttons for device: {device_name}")

        if not commands:
            _LOGGER.error(f"No commands found for device: {device_name}")
            continue

        for command_name, command_data in commands.items():
            # Create a unique ID for the button entity
            unique_id = f"{mac_address}_{device_name}_{command_name}"
            entities.append(
                BroadlinkButtonEntity(
                    mac_address,
                    device_name,
                    command_name,
                    command_data,
                    unique_id,
                    config_entry,
                )
            )

    async_add_entities(entities)


class BroadlinkButtonEntity(ButtonEntity):
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
            "identifiers": {(DOMAIN, f"{mac_address}_{device_name}")}
        }
        self._config_entry = config_entry

    async def async_press(self):
        """Handle the button press asynchronously."""
        _LOGGER.debug(
            f"Sending command '{self._command_name}' for device '{self._device_name}' via hub '{self._mac_address}'"
        )

        normalized_mac = normalize_mac(self._mac_address)

        # Retrieve the device registry
        device_registry = dr.async_get(self.hass)
        device = None

        # Look up the device using the normalized MAC address
        for device_entry in device_registry.devices.values():
            for identifier in device_entry.identifiers:
                test_value = normalize_mac(identifier[1])
                _LOGGER.debug(
                    f"Checking {test_value} against {normalized_mac} - details: {identifier}"
                )

                if "broadlink" in identifier[0] and test_value == normalized_mac:
                    device = device_entry
                    _LOGGER.debug(f"Found device entry: {device_entry}")
                    break

        if not device:
            _LOGGER.error(
                f"No device found in the registry for MAC address: {self._mac_address}"
            )
            return

        # Find the associated remote entity for this device
        entity_registry = er.async_get(self.hass)  # Use entity registry
        remote_entity_id = None

        for entity_entry in entity_registry.entities.values():
            if entity_entry.device_id == device.id and entity_entry.domain == "remote":
                remote_entity_id = entity_entry.entity_id
                _LOGGER.debug(f"Found remote entity: {remote_entity_id}")
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

        # Log the service call data for debugging
        _LOGGER.debug(f"Calling service remote.send_command with data: {service_data}")

        # Call the remote.send_command service
        await self.hass.services.async_call(
            domain="remote",
            service="send_command",
            service_data=service_data,
            blocking=True,
        )
