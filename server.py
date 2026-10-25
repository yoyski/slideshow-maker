"""
Voice Slideshow Maker - account server.

What it does:   sign up, sign in, sign out, delete account, and a private stats endpoint.
What it stores: name, email, a hashed password, and timestamps. Nothing else.
What it never sees: slides, recordings or videos. Those stay on the user's device.
"""
import os
import re
import secrets
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from flask import Flask, g, jsonify, request, send_from_directory, session
from werkzeug.security import check_password_hash, generate_password_hash

# Database imports - support both SQLite and PostgreSQL
try:
    import psycopg2
    import psycopg2.extras
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

import sqlite3

load_dotenv()

BASE = Path(__file__).parent
INSTANCE = BASE / "instance"
INSTANCE.mkdir(exist_ok=True)
PRODUCTION = os.environ.get("APP_ENV", "development") == "production"
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")

# Database configuration
USE_POSTGRES = os.environ.get("DATABASE_URL") is not None
if USE_POSTGRES and not POSTGRES_AVAILABLE:
    raise RuntimeError("PostgreSQL support requires: pip install psycopg2-binary")

DB_PATH = Path(os.environ.get("DATABASE_PATH", INSTANCE / "users.db")) if not USE_POSTGRES else None


def load_secret_key():
    key = os.environ.get("SECRET_KEY", "")
    if key and key != "change-me":
        return key
    if PRODUCTION:
        raise RuntimeError("Set a long random SECRET_KEY in the environment before running in production.")
    path = INSTANCE / "secret_key"  # development only: generated once and kept
    if not path.exists():
        path.write_text(secrets.token_hex(32))
    return path.read_text().strip()


app = Flask(__name__, static_folder=None)
app.config.update(
    SECRET_KEY=load_secret_key(),
    SESSION_COOKIE_NAME="vsm_session",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=PRODUCTION,  # cookie only travels over https in production
    PERMANENT_SESSION_LIFETIME=timedelta(days=30),
    MAX_CONTENT_LENGTH=16 * 1024,      # account requests are tiny
)
if os.environ.get("TRUSTED_PROXIES"):  # set to 1 when behind nginx, Render, Fly, Railway, etc.
    from werkzeug.middleware.proxy_fix import ProxyFix
    n = int(os.environ["TRUSTED_PROXIES"])
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=n, x_proto=n, x_host=n)

# ---------------------------------------------------------------- database

# SQL schema compatible with both SQLite and PostgreSQL
SCHEMA_SQLITE = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at    TEXT NOT NULL,
    last_login_at TEXT,
    last_seen_at  TEXT
);
CREATE TABLE IF NOT EXISTS projects (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    name          TEXT NOT NULL,
    description   TEXT,
    folder_id     TEXT NOT NULL UNIQUE,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS slideshows (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id    INTEGER NOT NULL,
    user_id       INTEGER NOT NULL,
    name          TEXT NOT NULL,
    data          TEXT NOT NULL,
    thumbnail     TEXT,
    duration      REAL,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_users_created ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_seen ON users(last_seen_at);
CREATE INDEX IF NOT EXISTS idx_projects_user ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_created ON projects(created_at);
CREATE INDEX IF NOT EXISTS idx_slideshows_project ON slideshows(project_id);
CREATE INDEX IF NOT EXISTS idx_slideshows_user ON slideshows(user_id);
CREATE INDEX IF NOT EXISTS idx_slideshows_updated ON slideshows(updated_at);
"""

SCHEMA_POSTGRES = """
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    name          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at    TEXT NOT NULL,
    last_login_at TEXT,
    last_seen_at  TEXT
);
CREATE TABLE IF NOT EXISTS projects (
    id            SERIAL PRIMARY KEY,
    user_id       INTEGER NOT NULL,
    name          TEXT NOT NULL,
    description   TEXT,
    folder_id     TEXT NOT NULL UNIQUE,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS slideshows (
    id            SERIAL PRIMARY KEY,
    project_id    INTEGER NOT NULL,
    user_id       INTEGER NOT NULL,
    name          TEXT NOT NULL,
    data          TEXT NOT NULL,
    thumbnail     TEXT,
    duration      REAL,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_users_created ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_seen ON users(last_seen_at);
CREATE INDEX IF NOT EXISTS idx_projects_user ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_created ON projects(created_at);
CREATE INDEX IF NOT EXISTS idx_slideshows_project ON slideshows(project_id);
CREATE INDEX IF NOT EXISTS idx_slideshows_user ON slideshows(user_id);
CREATE INDEX IF NOT EXISTS idx_slideshows_updated ON slideshows(updated_at);
"""


def init_db():
    if USE_POSTGRES:
        conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
        cur = conn.cursor()
        cur.execute(SCHEMA_POSTGRES)
        conn.commit()
        cur.close()
        conn.close()
        print("✓ PostgreSQL database initialized")
    else:
        con = sqlite3.connect(DB_PATH)
        con.execute("PRAGMA journal_mode=WAL")
        con.executescript(SCHEMA_SQLITE)
        con.commit()
        con.close()
        print("✓ SQLite database initialized")


def get_db_connection():
    """Get database connection - returns different types for SQLite vs PostgreSQL"""
    if USE_POSTGRES:
        conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
        conn.set_session(autocommit=False)
        return conn
    else:
        return sqlite3.connect(DB_PATH, timeout=10)


def db():
    if "db" not in g:
        if USE_POSTGRES:
            g.db = get_db_connection()
        else:
            g.db = sqlite3.connect(DB_PATH, timeout=10)
            g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    con = g.pop("db", None)
    if con is not None:
        con.close()


def now():
    return datetime.now(timezone.utc)


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------- helpers
def reply(ok, message="", status=200, **extra):
    return jsonify({"success": ok, "message": message, **extra}), status


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DUMMY_HASH = generate_password_hash("not-a-real-password")  # keeps timing equal for unknown emails

_attempts = {}
_lock = threading.Lock()


def limited(key, limit, window):
    """True when `key` already used up `limit` tries in the last `window` seconds."""
    t = time.time()
    with _lock:
        hits = [x for x in _attempts.get(key, []) if t - x < window]
        _attempts[key] = hits
        return len(hits) >= limit


def record(key):
    with _lock:
        _attempts.setdefault(key, []).append(time.time())


def clear_attempts(key):
    with _lock:
        _attempts.pop(key, None)


def current_user():
    uid = session.get("uid")
    if not uid:
        return None
    if USE_POSTGRES:
        cur = db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM users WHERE id = %s", (uid,))
        row = cur.fetchone()
    else:
        row = db().execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
    if row is None:
        session.clear()
    return row


def public(row):
    return {"name": row["name"], "email": row["email"]}


@app.before_request
def guard():
    if request.path.startswith("/api/") and request.method in ("POST", "PUT", "PATCH"):
        if not request.is_json:
            return reply(False, "Send the request as JSON.", 415)
    if request.path.startswith("/api/") and request.method == "DELETE":
        if request.data and not request.is_json:
            return reply(False, "Send the request as JSON.", 415)
    if request.path.startswith("/api/"):
        origin = request.headers.get("Origin")
        if origin and urlparse(origin).netloc != request.host:
            return reply(False, "Request blocked.", 403)


@app.after_request
def headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Permissions-Policy"] = "microphone=(self), camera=(), geolocation=()"
    if request.path.startswith("/api/"):
        resp.headers["Cache-Control"] = "no-store"
    else:
        resp.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' 'wasm-unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; img-src 'self' blob: data:; media-src 'self' blob:; "
            "connect-src 'self'; worker-src 'self' blob:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
        )
    return resp


# ---------------------------------------------------------------- pages
@app.get("/")
def index():
    resp = send_from_directory(BASE / "templates", "index.html")
    resp.headers["Cache-Control"] = "no-cache"
    return resp


@app.get("/healthz")
def healthz():
    return "ok"


# ---------------------------------------------------------------- accounts
@app.post("/api/auth/signup")
def signup():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    ip = request.remote_addr or "?"

    if limited(f"signup:{ip}", 10, 3600):
        return reply(False, "Too many sign-up attempts. Try again in an hour.", 429)
    if not 1 <= len(name) <= 80:
        return reply(False, "Enter your name (up to 80 characters).", 400)
    if len(email) > 254 or not EMAIL_RE.match(email):
        return reply(False, "Enter a valid email address, like you@example.com.", 400)
    if not 8 <= len(password) <= 128:
        return reply(False, "Use a password with 8 to 128 characters.", 400)

    record(f"signup:{ip}")
    stamp = iso(now())
    
    try:
        if USE_POSTGRES:
            cur = db().cursor()
            cur.execute(
                "INSERT INTO users (name, email, password_hash, created_at, last_login_at, last_seen_at) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
                (name, email, generate_password_hash(password), stamp, stamp, stamp),
            )
            uid = cur.fetchone()[0]
            db().commit()
        else:
            cur = db().execute(
                "INSERT INTO users (name, email, password_hash, created_at, last_login_at, last_seen_at) VALUES (?,?,?,?,?,?)",
                (name, email, generate_password_hash(password), stamp, stamp, stamp),
            )
            db().commit()
            uid = cur.lastrowid
    except (sqlite3.IntegrityError, psycopg2.IntegrityError):
        return reply(False, "An account with this email already exists. Sign in instead.", 409)

    session.clear()
    session["uid"] = uid
    session.permanent = True
    return reply(True, "Account created.", 201, user={"name": name, "email": email})


@app.post("/api/auth/signin")
def signin():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()[:254]
    password = str(data.get("password", ""))[:128]
    ip = request.remote_addr or "?"
    keys = (f"signin-ip:{ip}", f"signin-email:{email}")

    if any(limited(k, 8, 600) for k in keys):
        return reply(False, "Too many failed attempts. Wait 10 minutes and try again.", 429)

    if USE_POSTGRES:
        cur = db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        row = cur.fetchone()
    else:
        row = db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    
    ok = check_password_hash(row["password_hash"] if row else DUMMY_HASH, password)
    if not (row and ok):
        for k in keys:
            record(k)
        return reply(False, "Email or password is incorrect.", 401)

    for k in keys:
        clear_attempts(k)
    stamp = iso(now())
    
    if USE_POSTGRES:
        cur = db().cursor()
        cur.execute("UPDATE users SET last_login_at = %s, last_seen_at = %s WHERE id = %s", (stamp, stamp, row["id"]))
        db().commit()
    else:
        db().execute("UPDATE users SET last_login_at = ?, last_seen_at = ? WHERE id = ?", (stamp, stamp, row["id"]))
        db().commit()
    
    session.clear()
    session["uid"] = row["id"]
    session.permanent = True
    return reply(True, "Signed in.", user=public(row))


@app.post("/api/auth/signout")
def signout():
    session.clear()
    return reply(True, "Signed out.")


@app.get("/api/auth/me")
def me():
    row = current_user()
    if row is None:
        return reply(False, "Not signed in.", 401)
    # remember when we last saw this person (at most once an hour) so "active users" can be counted
    last = row["last_seen_at"] or ""
    if last < iso(now() - timedelta(hours=1)):
        if USE_POSTGRES:
            cur = db().cursor()
            cur.execute("UPDATE users SET last_seen_at = %s WHERE id = %s", (iso(now()), row["id"]))
            db().commit()
        else:
            db().execute("UPDATE users SET last_seen_at = ? WHERE id = ?", (iso(now()), row["id"]))
            db().commit()
    return reply(True, "", user=public(row))


@app.delete("/api/auth/account")
def delete_account():
    row = current_user()
    if row is None:
        return reply(False, "Not signed in.", 401)
    password = str((request.get_json(silent=True) or {}).get("password", ""))[:128]
    key = f"delete:{row['id']}"
    if limited(key, 5, 600):
        return reply(False, "Too many attempts. Wait 10 minutes and try again.", 429)
    if not check_password_hash(row["password_hash"], password):
        record(key)
        return reply(False, "That password is not correct.", 403)
    
    if USE_POSTGRES:
        cur = db().cursor()
        cur.execute("DELETE FROM users WHERE id = %s", (row["id"],))
        db().commit()
    else:
        db().execute("DELETE FROM users WHERE id = ?", (row["id"],))
        db().commit()
    
    session.clear()
    return reply(True, "Account deleted.")


# ---------------------------------------------------------------- projects
@app.post("/api/projects")
def create_project():
    """Create a new project/folder"""
    row = current_user()
    if row is None:
        return reply(False, "Not signed in.", 401)
    
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    description = str(data.get("description", "")).strip()
    
    if not 1 <= len(name) <= 100:
        return reply(False, "Project name must be 1-100 characters.", 400)
    if len(description) > 500:
        return reply(False, "Description must be under 500 characters.", 400)
    
    folder_id = secrets.token_hex(12)
    stamp = iso(now())
    
    try:
        if USE_POSTGRES:
            cur = db().cursor()
            cur.execute(
                "INSERT INTO projects (user_id, name, description, folder_id, created_at, updated_at) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
                (row["id"], name, description, folder_id, stamp, stamp),
            )
            project_id = cur.fetchone()[0]
            db().commit()
        else:
            cur = db().execute(
                "INSERT INTO projects (user_id, name, description, folder_id, created_at, updated_at) VALUES (?,?,?,?,?,?)",
                (row["id"], name, description, folder_id, stamp, stamp),
            )
            db().commit()
            project_id = cur.lastrowid
    except (sqlite3.IntegrityError, psycopg2.IntegrityError):
        return reply(False, "Could not create project. Try again.", 409)
    
    return reply(True, "Project created.", 201, project={"id": project_id, "name": name, "description": description, "folder_id": folder_id, "created_at": stamp})


@app.get("/api/projects")
def list_projects():
    """List all projects for the current user"""
    row = current_user()
    if row is None:
        return reply(False, "Not signed in.", 401)
    
    if USE_POSTGRES:
        cur = db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT p.id, p.name, p.description, p.folder_id, p.created_at, p.updated_at, 
                   COUNT(s.id) as slideshow_count
            FROM projects p
            LEFT JOIN slideshows s ON p.id = s.project_id
            WHERE p.user_id = %s
            GROUP BY p.id
            ORDER BY p.updated_at DESC
        """, (row["id"],))
        projects = cur.fetchall()
        projects = [dict(p) for p in projects]
    else:
        cur = db().execute("""
            SELECT p.id, p.name, p.description, p.folder_id, p.created_at, p.updated_at, 
                   COUNT(s.id) as slideshow_count
            FROM projects p
            LEFT JOIN slideshows s ON p.id = s.project_id
            WHERE p.user_id = ?
            GROUP BY p.id
            ORDER BY p.updated_at DESC
        """, (row["id"],))
        projects = [dict(p) for p in cur.fetchall()]
    
    return reply(True, "", projects=projects)


@app.get("/api/projects/<int:project_id>")
def get_project(project_id):
    """Get a specific project with slideshow count"""
    row = current_user()
    if row is None:
        return reply(False, "Not signed in.", 401)
    
    if USE_POSTGRES:
        cur = db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT p.id, p.name, p.description, p.folder_id, p.created_at, p.updated_at,
                   COUNT(s.id) as slideshow_count
            FROM projects p
            LEFT JOIN slideshows s ON p.id = s.project_id
            WHERE p.id = %s AND p.user_id = %s
            GROUP BY p.id
        """, (project_id, row["id"]))
        project = cur.fetchone()
    else:
        project = db().execute("""
            SELECT p.id, p.name, p.description, p.folder_id, p.created_at, p.updated_at,
                   COUNT(s.id) as slideshow_count
            FROM projects p
            LEFT JOIN slideshows s ON p.id = s.project_id
            WHERE p.id = ? AND p.user_id = ?
            GROUP BY p.id
        """, (project_id, row["id"])).fetchone()
    
    if project is None:
        return reply(False, "Project not found.", 404)
    
    return reply(True, "", project=dict(project) if USE_POSTGRES else dict(project))


@app.patch("/api/projects/<int:project_id>")
def update_project(project_id):
    """Update project name or description"""
    row = current_user()
    if row is None:
        return reply(False, "Not signed in.", 401)
    
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip() if "name" in data else None
    description = str(data.get("description", "")).strip() if "description" in data else None
    
    if USE_POSTGRES:
        cur = db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id, user_id FROM projects WHERE id = %s", (project_id,))
        project = cur.fetchone()
    else:
        project = db().execute("SELECT id, user_id FROM projects WHERE id = ?", (project_id,)).fetchone()
    
    if project is None or project["user_id"] != row["id"]:
        return reply(False, "Project not found or unauthorized.", 404)
    
    if name is not None and not 1 <= len(name) <= 100:
        return reply(False, "Project name must be 1-100 characters.", 400)
    if description is not None and len(description) > 500:
        return reply(False, "Description must be under 500 characters.", 400)
    
    stamp = iso(now())
    
    if name is not None or description is not None:
        if USE_POSTGRES:
            updates = []
            params = []
            if name is not None:
                updates.append("name = %s")
                params.append(name)
            if description is not None:
                updates.append("description = %s")
                params.append(description)
            updates.append("updated_at = %s")
            params.append(stamp)
            params.append(project_id)
            params.append(row["id"])
            
            cur = db().cursor()
            cur.execute(f"UPDATE projects SET {', '.join(updates)} WHERE id = %s AND user_id = %s", params)
            db().commit()
        else:
            updates = []
            params = []
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            updates.append("updated_at = ?")
            params.append(stamp)
            params.append(project_id)
            params.append(row["id"])
            
            db().execute(f"UPDATE projects SET {', '.join(updates)} WHERE id = ? AND user_id = ?", params)
            db().commit()
    
    return reply(True, "Project updated.")


@app.delete("/api/projects/<int:project_id>")
def delete_project(project_id):
    """Delete a project and all its slideshows"""
    row = current_user()
    if row is None:
        return reply(False, "Not signed in.", 401)
    
    if USE_POSTGRES:
        cur = db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id, user_id FROM projects WHERE id = %s", (project_id,))
        project = cur.fetchone()
    else:
        project = db().execute("SELECT id, user_id FROM projects WHERE id = ?", (project_id,)).fetchone()
    
    if project is None or project["user_id"] != row["id"]:
        return reply(False, "Project not found or unauthorized.", 404)
    
    # Delete all slideshows in this project first
    if USE_POSTGRES:
        cur = db().cursor()
        cur.execute("DELETE FROM slideshows WHERE project_id = %s", (project_id,))
        cur.execute("DELETE FROM projects WHERE id = %s AND user_id = %s", (project_id, row["id"]))
        db().commit()
    else:
        db().execute("DELETE FROM slideshows WHERE project_id = ?", (project_id,))
        db().execute("DELETE FROM projects WHERE id = ? AND user_id = ?", (project_id, row["id"]))
        db().commit()
    
    return reply(True, "Project deleted.")


# ---------------------------------------------------------------- slideshows
@app.post("/api/slideshows")
def create_slideshow():
    """Create a new slideshow in a project"""
    row = current_user()
    if row is None:
        return reply(False, "Not signed in.", 401)
    
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    project_id = data.get("project_id")
    slideshow_data = data.get("data", "{}")
    
    if not 1 <= len(name) <= 100:
        return reply(False, "Slideshow name must be 1-100 characters.", 400)
    if not project_id:
        return reply(False, "Project ID is required.", 400)
    
    # Verify user owns the project
    if USE_POSTGRES:
        cur = db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id, user_id FROM projects WHERE id = %s", (project_id,))
        project = cur.fetchone()
    else:
        project = db().execute("SELECT id, user_id FROM projects WHERE id = ?", (project_id,)).fetchone()
    
    if not project or project["user_id"] != row["id"]:
        return reply(False, "Project not found or unauthorized.", 404)
    
    stamp = iso(now())
    
    try:
        if USE_POSTGRES:
            cur = db().cursor()
            cur.execute(
                "INSERT INTO slideshows (project_id, user_id, name, data, created_at, updated_at) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
                (project_id, row["id"], name, str(slideshow_data), stamp, stamp),
            )
            slideshow_id = cur.fetchone()[0]
            db().commit()
        else:
            cur = db().execute(
                "INSERT INTO slideshows (project_id, user_id, name, data, created_at, updated_at) VALUES (?,?,?,?,?,?)",
                (project_id, row["id"], name, str(slideshow_data), stamp, stamp),
            )
            db().commit()
            slideshow_id = cur.lastrowid
    except (sqlite3.IntegrityError, psycopg2.IntegrityError):
        return reply(False, "Could not create slideshow. Try again.", 409)
    
    return reply(True, "Slideshow created.", 201, slideshow={"id": slideshow_id, "name": name, "project_id": project_id, "created_at": stamp})


@app.get("/api/slideshows")
def list_slideshows():
    """List all slideshows for current user, optionally filtered by project"""
    row = current_user()
    if row is None:
        return reply(False, "Not signed in.", 401)
    
    project_id = request.args.get("project_id")
    
    if USE_POSTGRES:
        cur = db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if project_id:
            cur.execute(
                "SELECT id, name, project_id, duration, created_at, updated_at FROM slideshows WHERE user_id = %s AND project_id = %s ORDER BY updated_at DESC",
                (row["id"], project_id)
            )
        else:
            cur.execute(
                "SELECT id, name, project_id, duration, created_at, updated_at FROM slideshows WHERE user_id = %s ORDER BY updated_at DESC",
                (row["id"],)
            )
        slideshows = cur.fetchall()
        slideshows = [dict(s) for s in slideshows]
    else:
        if project_id:
            cur = db().execute(
                "SELECT id, name, project_id, duration, created_at, updated_at FROM slideshows WHERE user_id = ? AND project_id = ? ORDER BY updated_at DESC",
                (row["id"], project_id)
            )
        else:
            cur = db().execute(
                "SELECT id, name, project_id, duration, created_at, updated_at FROM slideshows WHERE user_id = ? ORDER BY updated_at DESC",
                (row["id"],)
            )
        slideshows = [dict(s) for s in cur.fetchall()]
    
    return reply(True, "", slideshows=slideshows)


@app.get("/api/slideshows/<int:slideshow_id>")
def get_slideshow(slideshow_id):
    """Get a specific slideshow with its data"""
    row = current_user()
    if row is None:
        return reply(False, "Not signed in.", 401)
    
    if USE_POSTGRES:
        cur = db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "SELECT id, name, project_id, data, duration, created_at, updated_at FROM slideshows WHERE id = %s AND user_id = %s",
            (slideshow_id, row["id"])
        )
        slideshow = cur.fetchone()
    else:
        slideshow = db().execute(
            "SELECT id, name, project_id, data, duration, created_at, updated_at FROM slideshows WHERE id = ? AND user_id = ?",
            (slideshow_id, row["id"])
        ).fetchone()
    
    if slideshow is None:
        return reply(False, "Slideshow not found.", 404)
    
    return reply(True, "", slideshow=dict(slideshow) if USE_POSTGRES else dict(slideshow))


@app.patch("/api/slideshows/<int:slideshow_id>")
def update_slideshow(slideshow_id):
    """Update slideshow name, data, or duration"""
    row = current_user()
    if row is None:
        return reply(False, "Not signed in.", 401)
    
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip() if "name" in data else None
    slideshow_data = data.get("data") if "data" in data else None
    duration = data.get("duration") if "duration" in data else None
    
    if USE_POSTGRES:
        cur = db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id, user_id FROM slideshows WHERE id = %s", (slideshow_id,))
        slideshow = cur.fetchone()
    else:
        slideshow = db().execute("SELECT id, user_id FROM slideshows WHERE id = ?", (slideshow_id,)).fetchone()
    
    if slideshow is None or slideshow["user_id"] != row["id"]:
        return reply(False, "Slideshow not found or unauthorized.", 404)
    
    if name is not None and not 1 <= len(name) <= 100:
        return reply(False, "Slideshow name must be 1-100 characters.", 400)
    
    stamp = iso(now())
    
    if name is not None or slideshow_data is not None or duration is not None:
        if USE_POSTGRES:
            updates = []
            params = []
            if name is not None:
                updates.append("name = %s")
                params.append(name)
            if slideshow_data is not None:
                updates.append("data = %s")
                params.append(str(slideshow_data))
            if duration is not None:
                updates.append("duration = %s")
                params.append(float(duration) if duration else None)
            updates.append("updated_at = %s")
            params.append(stamp)
            params.append(slideshow_id)
            params.append(row["id"])
            
            cur = db().cursor()
            cur.execute(f"UPDATE slideshows SET {', '.join(updates)} WHERE id = %s AND user_id = %s", params)
            db().commit()
        else:
            updates = []
            params = []
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if slideshow_data is not None:
                updates.append("data = ?")
                params.append(str(slideshow_data))
            if duration is not None:
                updates.append("duration = ?")
                params.append(float(duration) if duration else None)
            updates.append("updated_at = ?")
            params.append(stamp)
            params.append(slideshow_id)
            params.append(row["id"])
            
            db().execute(f"UPDATE slideshows SET {', '.join(updates)} WHERE id = ? AND user_id = ?", params)
            db().commit()
    
    return reply(True, "Slideshow updated.")


@app.delete("/api/slideshows/<int:slideshow_id>")
def delete_slideshow(slideshow_id):
    """Delete a slideshow"""
    row = current_user()
    if row is None:
        return reply(False, "Not signed in.", 401)
    
    if USE_POSTGRES:
        cur = db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id, user_id FROM slideshows WHERE id = %s", (slideshow_id,))
        slideshow = cur.fetchone()
    else:
        slideshow = db().execute("SELECT id, user_id FROM slideshows WHERE id = ?", (slideshow_id,)).fetchone()
    
    if slideshow is None or slideshow["user_id"] != row["id"]:
        return reply(False, "Slideshow not found or unauthorized.", 404)
    
    if USE_POSTGRES:
        cur = db().cursor()
        cur.execute("DELETE FROM slideshows WHERE id = %s AND user_id = %s", (slideshow_id, row["id"]))
        db().commit()
    else:
        db().execute("DELETE FROM slideshows WHERE id = ? AND user_id = ?", (slideshow_id, row["id"]))
        db().commit()
    
    return reply(True, "Slideshow deleted.")



def compute_stats():
    n = now()
    day0 = iso(n.replace(hour=0, minute=0, second=0, microsecond=0))
    
    if USE_POSTGRES:
        con = db()
        cur = con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        def count(sql, *a):
            cur.execute(sql, a)
            return cur.fetchone()[0]
        
        by_day_query = """
            SELECT substr(created_at,1,10) AS day, COUNT(*) AS signups FROM users 
            WHERE created_at >= %s GROUP BY day ORDER BY day
        """
        cur.execute(by_day_query, (iso(n - timedelta(days=13)),))
        by_day = cur.fetchall()
    else:
        con = db()
        def count(sql, *a):
            return con.execute(sql, a).fetchone()[0]
        
        by_day_sql = """SELECT substr(created_at,1,10) AS day, COUNT(*) AS signups FROM users 
            WHERE created_at >= ? GROUP BY day ORDER BY day"""
        by_day = con.execute(by_day_sql, (iso(n - timedelta(days=13)),)).fetchall()
    
    return {
        "total_users": count("SELECT COUNT(*) FROM users"),
        "new_today_utc": count("SELECT COUNT(*) FROM users WHERE created_at >= %s" if USE_POSTGRES else "SELECT COUNT(*) FROM users WHERE created_at >= ?", day0),
        "new_last_7_days": count("SELECT COUNT(*) FROM users WHERE created_at >= %s" if USE_POSTGRES else "SELECT COUNT(*) FROM users WHERE created_at >= ?", iso(n - timedelta(days=7))),
        "new_last_30_days": count("SELECT COUNT(*) FROM users WHERE created_at >= %s" if USE_POSTGRES else "SELECT COUNT(*) FROM users WHERE created_at >= ?", iso(n - timedelta(days=30))),
        "active_last_24_hours": count("SELECT COUNT(*) FROM users WHERE last_seen_at >= %s" if USE_POSTGRES else "SELECT COUNT(*) FROM users WHERE last_seen_at >= ?", iso(n - timedelta(hours=24))),
        "active_last_7_days": count("SELECT COUNT(*) FROM users WHERE last_seen_at >= %s" if USE_POSTGRES else "SELECT COUNT(*) FROM users WHERE last_seen_at >= ?", iso(n - timedelta(days=7))),
        "active_last_30_days": count("SELECT COUNT(*) FROM users WHERE last_seen_at >= %s" if USE_POSTGRES else "SELECT COUNT(*) FROM users WHERE last_seen_at >= ?", iso(n - timedelta(days=30))),
        "signups_by_day": [dict(r) for r in by_day],
    }


@app.get("/api/admin/stats")
def admin_stats():
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if not ADMIN_TOKEN or not secrets.compare_digest(token.encode(), ADMIN_TOKEN.encode()):
        return reply(False, "Not found.", 404)  # same answer whether the token is wrong or unset
    return jsonify({"success": True, **compute_stats()})


# ---------------------------------------------------------------- errors
@app.errorhandler(404)
def not_found(_e):
    return reply(False, "Not found.", 404) if request.path.startswith("/api/") else ("Not found", 404)


@app.errorhandler(405)
def bad_method(_e):
    return reply(False, "Method not allowed.", 405)


@app.errorhandler(413)
def too_big(_e):
    return reply(False, "Request too large.", 413)


@app.errorhandler(500)
def server_error(_e):
    return reply(False, "Something went wrong on the server. Try again.", 500)


init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=not PRODUCTION)
