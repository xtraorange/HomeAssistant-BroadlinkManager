import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .device_manager import DeviceManager
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Broadlink Manager from a config entry."""
    device_manager = DeviceManager(hass, entry.data.get("mac_address"), entry)
    await device_manager.initialize()

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    hass.data[DOMAIN][entry.entry_id] = device_manager

    # Forward entry setup to the button platform
    await hass.config_entries.async_forward_entry_setup(entry, "button")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    _LOGGER.debug("Unloading Broadlink Manager for entry: %s", entry.title)

    await hass.config_entries.async_forward_entry_unload(entry, "button")

    device_manager = hass.data[DOMAIN].pop(entry.entry_id, None)
    if device_manager:
        await device_manager.remove_entities()

    return True
