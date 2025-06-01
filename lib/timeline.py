#!/usr/bin/env python3
import sys
import os
import shutil
from database import get_timeline, get_state, get_branches, init_db

def display_timeline(db_path, branch='main'):
    timeline = get_timeline(db_path, branch)
    if not timeline:
        print("No timeline entries found.")
        return
    for timestamp, description in timeline:
        print(f"{timestamp}: {description}")

def view_state(db_path, timestamp, branch='main'):
    state = get_state(db_path, timestamp, branch)
    for path, hash_val, snapshot_path in state:
        if snapshot_path:
            print(f"{path} (Snapshot: {snapshot_path}, Hash: {hash_val})")
        else:
            print(f"{path} (Deleted)")

def restore_state(db_path, timestamp, snapshots_dir, branch='main'):
    state = get_state(db_path, timestamp, branch)
    backup_dir = f"{snapshots_dir}/backup_{time.strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    for path, _, snapshot_path in state:
        if snapshot_path and os.path.exists(snapshot_path):
            target_path = os.path.expanduser(path)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            shutil.copy(snapshot_path, target_path)
            print(f"Restored {path} from {snapshot_path}")
        elif not snapshot_path and os.path.exists(path):
            os.remove(path)
            print(f"Deleted {path}")

def show_diff(db_path, t1, t2, branch='main'):
    state1 = get_state(db_path, t1, branch)
    state2 = get_state(db_path, t2, branch)
    files1 = {p[0]: p for p in state1}
    files2 = {p[0]: p for p in state2}
    all_paths = set(files1.keys()) | set(files2.keys())
    for path in all_paths:
        if path not in files2:
            print(f"- {path} (Deleted)")
        elif path not in files1:
            print(f"+ {path} (Added)")
        elif files1[path][1] != files2[path][1]:
            print(f"~ {path} (Modified)")

def create_branch(db_path, branch_name):
    current_timestamp = time.strftime('%Y-%m-%d-%H:%M:%S')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT INTO timeline (timestamp, branch, description) VALUES (?, ?, ?)",
              (current_timestamp, branch_name, f"Branch {branch_name} created"))
    conn.commit()
    conn.close()
    print(f"Created branch {branch_name} at {current_timestamp}")

def switch_branch(db_path, branch_name):
    if branch_name not in get_branches(db_path):
        print(f"Branch {branch_name} does not exist")
        return
    # For now, just update the active branch context (future enhancement for full switch)
    print(f"Switched to branch {branch_name}")

if __name__ == "__main__":
    import time
    import sqlite3
    command = sys.argv[1]
    db_path = sys.argv[2]
    # Ensure database is initialized
    init_db(db_path)
    if command == "timeline":
        display_timeline(db_path)
    elif command == "goto":
        view_state(db_path, sys.argv[3])
    elif command == "restore":
        restore_state(db_path, sys.argv[3], sys.argv[4])
    elif command == "diff":
        show_diff(db_path, sys.argv[3], sys.argv[4])
    elif command == "branch":
        create_branch(db_path, sys.argv[3])
    elif command == "switch":
        switch_branch(db_path, sys.argv[3])