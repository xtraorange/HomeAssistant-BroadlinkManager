import logging
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
import voluptuous as vol
from .const import DOMAIN
from .codes_manager import CodesManager  # Import the CodesManager

_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class BroadlinkManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Broadlink Manager."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step where the user selects a Broadlink device."""

        # Access the device registry
        device_registry = dr.async_get(self.hass)

        # Find Broadlink devices that match the desired criteria
        devices = []
        for device_entry in device_registry.devices.values():
            _LOGGER.debug(f"Device Entry: {device_entry.identifiers}")
            for identifier in device_entry.identifiers:
                if "broadlink" in identifier:
                    _LOGGER.debug(f"Broadlink Device Found: {device_entry.name}")
                    devices.append(
                        {
                            "name": device_entry.name
                            or identifier[1],  # Use MAC if no name
                            "id": device_entry.id,
                            "mac_address": identifier[1],  # Capture the MAC address
                        }
                    )

        if not devices:
            return self.async_abort(reason="no_broadlink_devices_found")

        devices_dict = {device["name"]: device for device in devices}

        if user_input is not None:
            selected_device = devices_dict[user_input["device_name"]]

            # Initialize the CodesManager if it doesn't exist
            mac_address = selected_device["mac_address"]
            codes_manager = await CodesManager.get_or_create(self.hass, mac_address)

            _LOGGER.debug(f"Loaded codes for device: {codes_manager.get_all_devices()}")

            # Store the selected device's information and create an entry
            return self.async_create_entry(
                title=selected_device["name"],
                data={
                    "device_name": selected_device["name"],
                    "mac_address": selected_device["mac_address"],
                },
            )

        data_schema = vol.Schema(
            {
                vol.Required(
                    "device_name", default=list(devices_dict.keys())[0]
                ): vol.In(devices_dict.keys())
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema, errors={})


class BroadlinkManagerOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema(
            {
                vol.Optional("rename_device", default=""): str,
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)
