"""
Production Safe SQLite Backup Script for Spin & Win SaaS Platform.
Uses SQLite's online backup API to ensure a 100% consistent, non-corrupted database snapshot even during active writes.
"""

import os
import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'db.sqlite3'
BACKUP_DIR = BASE_DIR / 'backups'

def create_safe_sqlite_backup():
    if not DB_PATH.exists():
        print(f"[ERROR] Database file not found at {DB_PATH}")
        return False

    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = BACKUP_DIR / f'spinplus_backup_{timestamp}.sqlite3'

    print(f"[INFO] Initiating safe SQLite online backup...")
    try:
        src_conn = sqlite3.connect(DB_PATH)
        dst_conn = sqlite3.connect(backup_file)

        with dst_conn:
            src_conn.backup(dst_conn, pages=100, progress=None)

        src_conn.close()
        dst_conn.close()

        file_size_mb = backup_file.stat().st_size / (1024 * 1024)
        print(f"[SUCCESS] Consistent backup saved to: {backup_file} ({file_size_mb:.2f} MB)")
        return True
    except Exception as e:
        print(f"[ERROR] SQLite backup failed: {e}")
        return False

if __name__ == '__main__':
    create_safe_sqlite_backup()
