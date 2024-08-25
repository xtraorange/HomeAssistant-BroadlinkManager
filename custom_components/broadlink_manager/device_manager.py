import logging
from homeassistant.helpers import device_registry as dr, entity_registry as er
from .codes_manager import CodesManager
from .command_button import CommandButton

_LOGGER = logging.getLogger(__name__)


class DeviceManager:
    def __init__(self, hass, mac_address, config_entry):
        self.hass = hass
        self.mac_address = self._normalize_mac(mac_address)
        self.config_entry = config_entry
        self.codes_manager = None  # Will be initialized in initialize()

    async def initialize(self):
        self.codes_manager = await CodesManager.get_or_create(
            self.hass, self.mac_address
        )
        self.codes_manager.set_on_change_callback(self.reload_devices_and_commands)

    async def setup_all_entities(self, async_add_entities):
        entities = []

        for device_name in self.codes_manager.get_all_devices():
            commands = self.codes_manager.get_device_codes(device_name)
            for command_name, command_data in commands.items():
                unique_id = f"{self.mac_address}_{device_name}_{command_name}"
                entities.append(
                    CommandButton(
                        mac_address=self.mac_address,
                        device_name=device_name,
                        command_name=command_name,
                        command_data=command_data,
                        unique_id=unique_id,
                        config_entry=self.config_entry,
                    )
                )

        if entities:
            async_add_entities(entities)

    async def cleanup_entities(self):
        """Clean up existing entities related to the Broadlink device."""
        _LOGGER.debug("Cleaning up devices and buttons for MAC: %s", self.mac_address)

        device_registry = dr.async_get(self.hass)
        entity_registry = er.async_get(self.hass)

        # Find and remove devices and their entities
        devices_to_remove = [
            device_entry
            for device_entry in device_registry.devices.values()
            if any(
                self.mac_address in identifier[1]
                for identifier in device_entry.identifiers
            )
        ]

        for device_entry in devices_to_remove:
            _LOGGER.debug("Removing device: %s", device_entry.name)
            device_registry.async_remove_device(device_entry.id)

        entities_to_remove = [
            entity_entry
            for entity_entry in entity_registry.entities.values()
            if entity_entry.unique_id.startswith(self.mac_address)
        ]

        for entity_entry in entities_to_remove:
            _LOGGER.debug("Removing entity: %s", entity_entry.entity_id)
            entity_registry.async_remove(entity_entry.entity_id)

        _LOGGER.debug(
            "Finished cleaning up devices and buttons for MAC: %s", self.mac_address
        )

    async def reload_devices_and_commands(self):
        """Reload devices and commands when the codes file changes."""
        _LOGGER.info(
            "Reloading devices and commands due to file change for MAC: %s",
            self.mac_address,
        )
        await self.cleanup_entities()

        platforms = self.hass.helpers.entity_platform.async_get_platforms(
            self.hass, "broadlink_manager"
        )
        for platform in platforms:
            await platform.async_setup_entry(self.config_entry)

    @staticmethod
    def _normalize_mac(mac: str) -> str:
        """Normalize a MAC address by removing colons and converting to lowercase."""
        return mac.replace(":", "").lower()
