# PostgreSQL Setup Guide

Your Voice Slideshow Maker app now supports **both SQLite and PostgreSQL**!

## Why PostgreSQL for Production?

- ✅ Supports unlimited concurrent users
- ✅ Enterprise-grade security
- ✅ Better performance at scale
- ✅ Built-in backup/recovery
- ✅ Multiple user permissions
- ✅ No file access vulnerabilities

## Quick Start: Using PostgreSQL

### Option 1: Using Render.com (Easiest - Free Tier Available)

1. **Sign up** at https://render.com
2. **Create PostgreSQL Database**:
   - Go to Dashboard → New+ → PostgreSQL
   - Name: `slideshow-maker-db`
   - Region: Pick closest to you
   - PostgreSQL Version: 15 or higher
3. **Copy the Internal Database URL**
4. **Set environment variable**:
   ```
   set DATABASE_URL=postgresql://user:password@host:port/dbname
   ```
5. **Run your app**:
   ```
   py server.py
   ```

### Option 2: Using AWS RDS

1. Go to AWS RDS Console
2. Create DB instance → PostgreSQL
3. Copy connection string
4. Set:
   ```
   set DATABASE_URL=postgresql://user:password@host:port/dbname
   ```

### Option 3: Local PostgreSQL (Windows)

1. **Download** from https://www.postgresql.org/download/windows/
2. **Install** (keep default settings)
3. **Open pgAdmin** or command prompt
4. **Create database**:
   ```sql
   CREATE DATABASE slideshow_maker;
   ```
5. **Set environment variable**:
   ```
   set DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/slideshow_maker
   ```

### Option 4: Docker (Recommended for Testing)

```bash
docker run --name postgres-slideshow \
  -e POSTGRES_DB=slideshow_maker \
  -e POSTGRES_PASSWORD=yourpassword \
  -p 5432:5432 \
  -d postgres:15
```

Then set:
```
set DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/slideshow_maker
```

## Environment Setup

### On Windows (Command Prompt):
```cmd
set DATABASE_URL=postgresql://username:password@hostname:port/database_name
py server.py
```

### On Windows (PowerShell):
```powershell
$env:DATABASE_URL="postgresql://username:password@hostname:port/database_name"
py server.py
```

### On Mac/Linux (Terminal):
```bash
export DATABASE_URL="postgresql://username:password@hostname:port/database_name"
python server.py
```

### Using .env file (Recommended):
Create/edit `.env`:
```
DATABASE_URL=postgresql://username:password@hostname:port/database_name
APP_ENV=production
SECRET_KEY=your-long-random-secret-key-here
ADMIN_TOKEN=your-admin-token-here
```

Then just run:
```
py server.py
```

## How It Works

The app now automatically detects:

- **If DATABASE_URL is set** → Uses PostgreSQL
- **If DATABASE_URL is not set** → Falls back to SQLite (default)

## Connection String Format

```
postgresql://username:password@hostname:port/database_name
```

### Example:
```
postgresql://postgres:mypassword@localhost:5432/slideshow_maker
postgresql://admin:secure123@render-prod.com:5432/vsm_db
```

## Migrating from SQLite to PostgreSQL

Your data in SQLite (`instance/users.db`) needs to be migrated. Here's the simple way:

### Step 1: Export data from SQLite
```python
# Run this one-time script
import sqlite3
import json
from pathlib import Path

# Read from SQLite
sqlite_con = sqlite3.connect("instance/users.db")
sqlite_con.row_factory = sqlite3.Row
users = sqlite_con.execute("SELECT * FROM users").fetchall()
sqlite_con.close()

# Save to JSON for backup
with open("users_backup.json", "w") as f:
    json.dump([dict(u) for u in users], f, indent=2)

print(f"✓ Exported {len(users)} users to users_backup.json")
```

### Step 2: Set up PostgreSQL
- Create database (see options above)
- Set DATABASE_URL environment variable

### Step 3: Run the app
```
py server.py
```

The app will:
1. Connect to PostgreSQL
2. Create the `users` table automatically
3. Be ready for new users

**Important**: Old SQLite users will need to create new accounts in PostgreSQL (or you can manually import them using the backup file).

## Verifying Connection

When the app starts, you'll see:
```
✓ PostgreSQL database initialized
```

Or with SQLite:
```
✓ SQLite database initialized
```

## Testing the Connection

### Using psql (command line):
```bash
psql postgresql://username:password@hostname:port/database_name
```

Then run:
```sql
SELECT * FROM users;
```

### Using Python:
```python
import psycopg2
conn = psycopg2.connect("postgresql://user:pass@host:port/db")
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM users")
print(cur.fetchone())
conn.close()
```

## Troubleshooting

### "could not connect to server"
- Check hostname is correct
- Check port (usually 5432)
- Verify credentials
- Ensure database exists

### "relation 'users' does not exist"
- App will create it automatically on first run
- Check the startup log for "PostgreSQL database initialized"

### "SSL connection error"
- Try adding `?sslmode=require` to your connection string
- Or remove it to disable SSL (not for production!)

### "too many connections"
- Reduce connection pool or restart app
- PostgreSQL limits concurrent connections

## Production Deployment

### Render.com

1. Push code to GitHub
2. Create new service → GitHub Repo
3. Select your repo
4. Environment: Python 3.8+
5. Build: `pip install -r requirements.txt`
6. Start: `gunicorn server:app`
7. Add `DATABASE_URL` from PostgreSQL instance
8. Deploy!

### AWS / Heroku / Railway

Similar process:
1. Push to git
2. Connect git repo to platform
3. Add `DATABASE_URL` environment variable
4. Platform automatically deploys

## Performance Tips

- **Connection pooling**: PostgreSQL handles this automatically
- **Indexes**: Already created on `created_at` and `last_seen_at`
- **Backups**: Set up automated backups in your provider
- **Monitoring**: Use provider's built-in monitoring tools

## Reverting to SQLite (if needed)

1. Remove `DATABASE_URL` from environment
2. Restart the app
3. It will use SQLite automatically

## Need Help?

1. **Connection issues**: Test with `psql` command
2. **Database issues**: Check PostgreSQL logs
3. **App issues**: Check app startup messages
4. **Performance**: Monitor with provider's dashboard

---

**Summary:**
- ✅ SQLite: Great for local development
- ✅ PostgreSQL: Required for production scale
- ✅ App: Supports both automatically
- ✅ Migration: Simple, one environment variable

You're ready to scale! 🚀
