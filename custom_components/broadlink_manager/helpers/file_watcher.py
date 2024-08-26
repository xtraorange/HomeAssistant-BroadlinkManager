from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FileWatcher:
    def __init__(self, file_path, on_change_callback):
        self.file_path = file_path
        self.on_change_callback = on_change_callback
        self._start_watcher()

    def _start_watcher(self):
        event_handler = self._FileChangeHandler(self)
        observer = Observer()
        observer.schedule(event_handler, path=self.file_path, recursive=False)
        observer.start()

    def _on_file_change(self, event):
        if event.src_path == self.file_path:
            self.on_change_callback()

    class _FileChangeHandler(FileSystemEventHandler):
        def __init__(self, watcher):
            self.watcher = watcher

        def on_modified(self, event):
            self.watcher._on_file_change(event)
