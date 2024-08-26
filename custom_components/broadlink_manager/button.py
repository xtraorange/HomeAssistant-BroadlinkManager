import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .device_manager import DeviceManager
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities
):
    """Set up Broadlink Manager button entities."""
    device_manager = hass.data[DOMAIN][config_entry.entry_id]
    await device_manager.initialize_entities(
        async_add_entities
    )  # Use the correct method name
