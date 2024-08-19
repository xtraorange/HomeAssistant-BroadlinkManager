# Broadlink Manager

**Broadlink Manager** is a custom integration for Home Assistant that extends the existing Broadlink integration. It allows users to manage their Broadlink IR/RF devices with enhanced capabilities, including:

- Automatic discovery of Broadlink devices.
- Adding, renaming, and deleting devices directly from the Home Assistant UI.
- Creating buttons for each learned remote command.
- Renaming commands with automatic updates to Home Assistant entities.

## Installation

1. **Via HACS:**
   - Go to HACS in your Home Assistant UI.
   - Click on "Integrations" and search for "Broadlink Manager."
   - Click "Install" and follow the prompts to add the integration.

2. **Manual Installation:**
   - Download the latest release from [GitHub](https://github.com/yourusername/broadlink_manager).
   - Copy the `broadlink_manager` folder to your `custom_components` directory.
   - Restart Home Assistant.

## Configuration

1. Go to "Settings" -> "Devices & Services."
2. Click on "Add Integration" and search for "Broadlink Manager."
3. Follow the setup process to add your Broadlink devices.

## Features

- **Device Management**: Easily add, rename, and delete Broadlink devices.
- **Command Control**: Manage IR/RF commands with buttons created in Home Assistant.
- **Renaming Support**: Seamlessly rename devices and commands, reflecting changes in Home Assistant.

## Support

For issues, questions, or feature requests, please open an issue on [GitHub](https://github.com/yourusername/broadlink_manager/issues).
