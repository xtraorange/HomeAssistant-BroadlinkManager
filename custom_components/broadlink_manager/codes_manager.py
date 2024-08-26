import os
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from homeassistant.helpers.storage import Store
from .const import DOMAIN
from .helpers.file_watcher import FileWatcher


class CodesManager:
    def __init__(self, hass, mac_address):
        self.hass = hass
        self.mac_address = mac_address.lower()
        self.store = Store(hass, 1, f"broadlink_remote_{self.mac_address}_codes")
        self.file_path = self.store.path
        self.file_name = os.path.basename(self.file_path)
        self.data = None
        self.last_modified = None
        self._on_change_callback = None
        self.file_watcher = FileWatcher(self.file_path, self._on_file_change)

    async def async_initialize(self):
        await self._load_data()

    async def _load_data(self):
        data = await self.store.async_load()
        if data is None:
            data = {
                "version": 1,
                "minor_version": 1,
                "key": f"broadlink_remote_{self.mac_address}_codes",
                "data": {},
            }
        elif not isinstance(data, dict) or "data" not in data:
            data = {
                "version": 1,
                "minor_version": 1,
                "key": f"broadlink_remote_{self.mac_address}_codes",
                "data": data,
            }
        self.data = data
        self.last_modified = os.path.getmtime(self.file_path)
        if self._on_change_callback:
            self.hass.loop.call_soon_threadsafe(
                self.hass.async_create_task, self._on_change_callback()
            )

    def set_on_change_callback(self, callback):
        self._on_change_callback = callback

    async def save_data(self):
        await self.store.async_save(self.data)
        self.last_modified = os.path.getmtime(self.file_path)

    def _on_file_change(self):
        self.hass.loop.call_soon_threadsafe(
            self.hass.async_create_task, self._load_data()
        )

    def get_all_devices(self):
        if self.data is None:
            raise ValueError(
                "Data not loaded. Ensure async_initialize is called first."
            )
        return list(self.data["data"].keys())

    def get_device_codes(self, device_name):
        if self.data is None:
            raise ValueError(
                "Data not loaded. Ensure async_initialize is called first."
            )
        return self.data["data"].get(device_name, {})

    def device_exists(self, device_name):
        if self.data is None:
            raise ValueError("Data not loaded. Ensure _load_data is called first.")
        return device_name in self.data["data"]

    def command_exists(self, device_name, command_name):
        if self.data is None:
            raise ValueError("Data not loaded. Ensure _load_data is called first.")
        return command_name in self.data["data"].get(device_name, {})

    def rename_device(self, old_name, new_name):
        if self.device_exists(old_name):
            self.data["data"][new_name] = self.data["data"].pop(old_name)
            self.hass.async_create_task(self.save_data())

    def rename_command(self, device_name, old_command, new_command):
        if self.command_exists(device_name, old_command):
            self.data["data"][device_name][new_command] = self.data["data"][
                device_name
            ].pop(old_command)
            self.hass.async_create_task(self.save_data())

    def update_command_value(self, device_name, command_name, command_value):
        if self.device_exists(device_name):
            self.data["data"][device_name][command_name] = command_value
            self.hass.async_create_task(self.save_data())

    def create_device(self, device_name):
        if not self.device_exists(device_name):
            self.data["data"][device_name] = {}
            self.hass.async_create_task(self.save_data())

    def create_command(self, device_name, command_name, command_value):
        if self.device_exists(device_name):
            self.data["data"][device_name][command_name] = command_value
            self.hass.async_create_task(self.save_data())

    def delete_device(self, device_name):
        if self.device_exists(device_name):
            del self.data["data"][device_name]
            self.hass.async_create_task(self.save_data())

    def delete_command(self, device_name, command_name):
        if self.command_exists(device_name, command_name):
            del self.data["data"][device_name][command_name]
            self.hass.async_create_task(self.save_data())

    @staticmethod
    async def get_or_create(hass, mac_address):
        mac_address = mac_address.lower()
        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {}
        if mac_address not in hass.data[DOMAIN]:
            codes_manager = CodesManager(hass, mac_address)
            await codes_manager.async_initialize()
            hass.data[DOMAIN][mac_address] = codes_manager
        else:
            codes_manager = hass.data[DOMAIN][mac_address]
        return codes_manager
