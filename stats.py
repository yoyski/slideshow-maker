"""Print how many people use the app. Run on the server:  python stats.py"""
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
import os

path = Path(os.environ.get("DATABASE_PATH", Path(__file__).parent / "instance" / "users.db"))
if not path.exists():
    sys.exit(f"No database yet at {path}. Start the server once first.")
con = sqlite3.connect(path)
n = datetime.now(timezone.utc)
iso = lambda d: d.strftime("%Y-%m-%dT%H:%M:%SZ")
q = lambda sql, *a: con.execute(sql, a).fetchone()[0]
print(f"Total users:            {q('SELECT COUNT(*) FROM users')}")
print(f"New in last 7 days:     {q('SELECT COUNT(*) FROM users WHERE created_at >= ?', iso(n - timedelta(days=7)))}")
print(f"New in last 30 days:    {q('SELECT COUNT(*) FROM users WHERE created_at >= ?', iso(n - timedelta(days=30)))}")
print(f"Active last 24 hours:   {q('SELECT COUNT(*) FROM users WHERE last_seen_at >= ?', iso(n - timedelta(hours=24)))}")
print(f"Active last 7 days:     {q('SELECT COUNT(*) FROM users WHERE last_seen_at >= ?', iso(n - timedelta(days=7)))}")
print(f"Active last 30 days:    {q('SELECT COUNT(*) FROM users WHERE last_seen_at >= ?', iso(n - timedelta(days=30)))}")
print("\nLatest sign-ups (name, email, date):")
for r in con.execute("SELECT name, email, created_at FROM users ORDER BY id DESC LIMIT 10"):
    print("  ", *r)
