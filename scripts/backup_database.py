"""
Database Backup Script
Run: python scripts/backup_database.py

SQLite database backup करतो.
"""

import os
import shutil
import datetime


def backup_database():
    db_path = "license.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    # Backup folder create करा
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Timestamp with backup filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"license.db.backup.{timestamp}")
    
    shutil.copy2(db_path, backup_path)
    size = os.path.getsize(backup_path)
    
    print(f"✅ Backup created: {backup_path} ({size:,} bytes)")
    
    # Old backups cleanup (keep last 10)
    backups = sorted([
        f for f in os.listdir(backup_dir)
        if f.startswith("license.db.backup.")
    ])
    
    if len(backups) > 10:
        for old in backups[:-10]:
            os.remove(os.path.join(backup_dir, old))
            print(f"🗑️  Removed old backup: {old}")
    
    return True


if __name__ == "__main__":
    backup_database()
