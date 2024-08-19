import logging
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.storage import Store
from homeassistant.config_entries import ConfigEntry


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

    # Construct the path to the codes file within the .storage directory
    store = Store(hass, 1, f"broadlink_remote_{mac_address}_codes")
    _LOGGER.debug("Attempting to access %s", store.path)

    # Attempt to read the codes file asynchronously
    codes = await store.async_load()
    if codes:
        _LOGGER.debug("Codes have successfully loaded.")
        _LOGGER.debug(codes)

        # Register each controlled device as a separate device
        device_registry = dr.async_get(hass)
        for device_name, commands in codes.items():
            unique_id = f"{mac_address}_{device_name}"
            device_registry.async_get_or_create(
                config_entry_id=entry.entry_id,
                identifiers={(DOMAIN, unique_id)},
                manufacturer="Broadlink-Controlled",
                model=device_name,
                name=device_name,
            )
            _LOGGER.debug(f"Registered controlled device: {device_name}")

        # Save the loaded codes in hass.data for use by the button entity
        hass.data[DOMAIN][entry.entry_id] = codes

    else:
        _LOGGER.error("Failed to load codes from %s", store.path)
        return False

    # Forward entry setup for the button platform
    await hass.config_entries.async_forward_entry_setups(entry, ["button"])

    return True
