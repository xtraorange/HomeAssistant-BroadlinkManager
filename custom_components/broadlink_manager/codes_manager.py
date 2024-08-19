import os
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from homeassistant.helpers.storage import Store
from .const import DOMAIN


class CodesManager:
    def __init__(self, hass, mac_address):
        self.hass = hass
        self.mac_address = mac_address
        self.store = Store(hass, 1, f"broadlink_remote_{mac_address}_codes")
        self.file_path = self.store.path
        self.file_name = os.path.basename(self.file_path)
        self.data = None
        self.last_modified = None
        self._start_file_watcher()

    async def async_initialize(self):
        await self._load_data()

    async def _load_data(self):
        data = await self.store.async_load()
        if data is None:
            # Initialize an empty structure if nothing is loaded
            data = {
                "version": 1,
                "minor_version": 1,
                "key": f"broadlink_remote_{self.mac_address}_codes",
                "data": {},
            }
        elif not isinstance(data, dict) or "data" not in data:
            # If the structure is flat (i.e., devices are at the top level), assume it's only the devices
            data = {
                "version": 1,
                "minor_version": 1,
                "key": f"broadlink_remote_{self.mac_address}_codes",
                "data": data,  # Place the flat data into the "data" key
            }
        self.data = data
        self.last_modified = os.path.getmtime(self.file_path)

    async def save_data(self):
        await self.store.async_save(self.data)
        self.last_modified = os.path.getmtime(self.file_path)

    def _start_file_watcher(self):
        event_handler = self._FileChangeHandler(self)
        observer = Observer()
        observer.schedule(
            event_handler, path=os.path.dirname(self.file_path), recursive=False
        )
        observer.start()

    class _FileChangeHandler(FileSystemEventHandler):
        def __init__(self, manager):
            self.manager = manager

        def on_modified(self, event):
            if event.src_path == self.manager.file_path:
                self.manager.hass.async_create_task(self.manager._load_data())
                print(f"Codes file {self.manager.file_name} has been updated.")

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
        # Ensure DOMAIN is initialized in hass.data
        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {}

        if mac_address not in hass.data[DOMAIN]:
            codes_manager = CodesManager(hass, mac_address)
            await codes_manager.async_initialize()
            hass.data[DOMAIN][mac_address] = codes_manager
        else:
            codes_manager = hass.data[DOMAIN][mac_address]

        return codes_manager
