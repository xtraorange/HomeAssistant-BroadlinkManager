import broadlink
import logging
from homeassistant.helpers import device_registry as dr
from .codes_manager import CodesManager  # Import the CodesManager

_LOGGER = logging.getLogger(__name__)

DOMAIN = "broadlink_manager"


async def discover_devices(hass):
    """Discover Broadlink devices."""
    devices = broadlink.discover(timeout=5)
    _LOGGER.debug("Discovered devices: %s", devices)
    return devices


async def setup_devices(hass, config_entry):
    """Set up Broadlink devices in Home Assistant."""
    devices = await discover_devices(hass)
    device_registry = dr.async_get(hass)

    for device in devices:
        _LOGGER.debug(
            f"Setting up device: {device.name} with MAC: {device.mac_address}"
        )

        device_entry = device_registry.async_get_or_create(
            config_entry_id=config_entry.entry_id,
            connections={(dr.CONNECTION_NETWORK_MAC, device.mac_address)},
            identifiers={(DOMAIN, device.mac_address)},
            manufacturer="Broadlink",
            name=device.name,
            model=device.model,
            sw_version=device.firmware_version,
        )

        codes_manager = await CodesManager.get_or_create(hass, device.mac_address)

        _LOGGER.debug(f"Loaded codes for device: {codes_manager.get_all_devices()}")
