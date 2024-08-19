import logging
from homeassistant.helpers import device_registry as dr
from .codes_manager import CodesManager  # Import the new CodesManager

_LOGGER = logging.getLogger(__name__)

DOMAIN = "broadlink_manager"


async def async_setup_entry(hass, entry):
    """Set up Broadlink Manager from a config entry."""
    _LOGGER.debug("Setting up Broadlink Manager for entry: %s", entry.title)

    # Initialize the DOMAIN in hass.data if it does not exist
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    # Get the MAC address of the hub from the config entry data
    mac_address = entry.data.get("mac_address")

    # Check if a CodesManager already exists or create a new one
    codes_manager = await CodesManager.get_or_create(hass, mac_address)

    # Register each controlled device as a separate device in Home Assistant
    device_registry = dr.async_get(hass)
    for device_name in codes_manager.get_all_devices():
        unique_id = f"{mac_address}_{device_name}"
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, unique_id)},
            manufacturer="Broadlink-Controlled",
            model=device_name,
            name=device_name,
        )
        _LOGGER.debug(f"Registered controlled device: {device_name}")

    # Forward entry setup for the button platform
    await hass.config_entries.async_forward_entry_setups(entry, ["button"])

    return True
