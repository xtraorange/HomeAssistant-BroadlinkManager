import broadlink
import logging
from homeassistant.helpers import device_registry as dr

_LOGGER = logging.getLogger(__name__)


class BroadlinkHub:
    @staticmethod
    async def discover_devices(hass):
        """Discover Broadlink devices."""
        devices = broadlink.discover(timeout=5)
        _LOGGER.debug("Network-discovered devices: %s", devices)
        return devices

    @staticmethod
    def find_registered_devices(hass):
        """Find Broadlink devices in the Home Assistant device registry."""
        device_registry = dr.async_get(hass)
        devices = []

        for device_entry in device_registry.devices.values():
            _LOGGER.debug(f"Device Entry: {device_entry.identifiers}")
            for identifier in device_entry.identifiers:
                if "broadlink" in identifier[0]:
                    _LOGGER.debug(f"Broadlink Device Found: {device_entry.name}")
                    devices.append(
                        {
                            "name": device_entry.name
                            or identifier[1],  # Use MAC if no name
                            "id": device_entry.id,
                            "mac_address": identifier[1],  # Capture the MAC address
                        }
                    )

        return devices
