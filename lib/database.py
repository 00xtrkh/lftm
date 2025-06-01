#!/usr/bin/env python3
import sqlite3
import os
import sys

def init_db(db_path):
    """Initialize the SQLite database."""
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS files
                     (path TEXT, timestamp TEXT, hash TEXT, snapshot_path TEXT, branch TEXT DEFAULT 'main')''')
        c.execute('''CREATE TABLE IF NOT EXISTS timeline
                     (timestamp TEXT PRIMARY KEY, branch TEXT, description TEXT)''')
        conn.commit()
        conn.close()
    else:
        # Ensure tables exist even if DB file exists but is empty
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS files (path TEXT, timestamp TEXT, hash TEXT, snapshot_path TEXT, branch TEXT DEFAULT 'main')")
        c.execute("CREATE TABLE IF NOT EXISTS timeline (timestamp TEXT PRIMARY KEY, branch TEXT, description TEXT)")
        conn.commit()
        conn.close()

def log_change(db_path, path, timestamp, file_hash, snapshot_path, branch='main'):
    """Log a file change in the database."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO files (path, timestamp, hash, snapshot_path, branch) VALUES (?, ?, ?, ?, ?)",
              (path, timestamp, file_hash, snapshot_path, branch))
    c.execute("INSERT OR IGNORE INTO timeline (timestamp, branch, description) VALUES (?, ?, ?)",
              (timestamp, branch, f"Change to {path}"))
    conn.commit()
    conn.close()

def get_timeline(db_path, branch='main'):
    """Retrieve the timeline for a branch."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT timestamp, description FROM timeline WHERE branch = ? ORDER BY timestamp DESC", (branch,))
    timeline = c.fetchall()
    conn.close()
    return timeline

def get_state(db_path, timestamp, branch='main'):
    """Get file state at a specific timestamp."""
    print(f"Accessing database: {db_path}")  # Debug output
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("PRAGMA table_info(files)")  # Check if table exists
    if not c.fetchall():
        print("Warning: 'files' table not found in database")
    c.execute("SELECT path, hash, snapshot_path FROM files WHERE timestamp <= ? AND branch = ? ORDER BY timestamp DESC",
              (timestamp, branch))
    state = c.fetchall()
    conn.close()
    return state

def get_branches(db_path):
    """Get all branches."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT DISTINCT branch FROM timeline")
    branches = c.fetchall()
    conn.close()
    return [b[0] for b in branches]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: database.py <command> [args]")
        sys.exit(1)
    command = sys.argv[1]
    if command == "init":
        db_path = sys.argv[2]
        init_db(db_path)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)