# Voice Slideshow Maker

The page runs in the browser: slides, recordings, noise removal and video all stay on the user's device.
The server only handles accounts (name, email, hashed password, timestamps).

## Run it on your computer
    python -m venv venv && venv\Scripts\activate        (Windows)   |   source venv/bin/activate   (Mac/Linux)
    pip install -r requirements.txt
    copy .env.example .env                              (cp on Mac/Linux), then set ADMIN_TOKEN
    python server.py                                    -> http://127.0.0.1:5000

## How many users do I have?
- On the server:   python stats.py
- From anywhere:   curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" https://your-site/api/admin/stats
  Returns total users, new today / 7 / 30 days, active in 24 h / 7 / 30 days, and sign-ups per day.
  "Active" means the person opened the app while signed in (checked at most once an hour).

## Put it online
    APP_ENV=production SECRET_KEY=<long random> ADMIN_TOKEN=<long random> TRUSTED_PROXIES=1 \
    DATABASE_PATH=/data/users.db gunicorn -w 2 -b 0.0.0.0:$PORT server:app
- Use https (the microphone needs it on phones).
- Put DATABASE_PATH on a persistent disk, or the user list is lost on every redeploy.
- Run one or two workers on SQLite. If you grow past that, move the users table to Postgres.
- The failed-login limiter is kept in memory per worker; use Redis or your host's firewall for stricter limits.

## Files
- server.py        accounts API + serves the page
- templates/index.html   the whole app (page, noise-removal model, video maker)
- stats.py         prints user counts
- legacy_backend/  the earlier all-server version, not used any more
