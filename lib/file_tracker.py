#!/usr/bin/env python3
import sys
import os
import time
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from database import log_change, init_db

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, db_path, snapshots_dir):
        self.db_path = db_path
        self.snapshots_dir = snapshots_dir
        init_db(db_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.handle_change(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self.handle_change(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            log_change(self.db_path, event.src_path, time.strftime('%Y-%m-%d-%H:%M:%S'), '', '')

    def handle_change(self, path):
        timestamp = time.strftime('%Y-%m-%d-%H:%M:%S')
        hash_md5 = hashlib.md5()
        try:
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            file_hash = hash_md5.hexdigest()
            snapshot_path = os.path.join(self.snapshots_dir, f"{os.path.basename(path)}_{timestamp}.snap")
            with open(path, 'rb') as src, open(snapshot_path, 'wb') as dst:
                dst.write(src.read())
            log_change(self.db_path, path, timestamp, file_hash, snapshot_path)
        except Exception as e:
            print(f"Error processing {path}: {e}")

def start_monitoring(directory, db_path, snapshots_dir):
    event_handler = FileChangeHandler(db_path, snapshots_dir)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()
    print(f"Monitoring {directory}...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def stop_monitoring():
    print("Stopping monitor (use Ctrl+C in the monitoring process)")

if __name__ == "__main__":
    command = sys.argv[1]
    if command == "start":
        start_monitoring(sys.argv[2], sys.argv[3], sys.argv[4])
    elif command == "stop":
        stop_monitoring()