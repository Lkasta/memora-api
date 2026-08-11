# Memora Backend

Flask API for Memora — user accounts and dated "memories" (title, content,
event date, image URL).

## Stack

- Flask 3 (application factory in [`app.py`](app.py))
- Flask-SQLAlchemy + Flask-Migrate (Alembic) on PostgreSQL
- Flask-JWT-Extended for auth (bearer tokens, 8h expiry by default)
- bcrypt for password hashing ([`security/password_handler.py`](security/password_handler.py))

## Setup

```bash
python -m venv venv
venv/Scripts/activate        # source venv/bin/activate on macOS/Linux
pip install -r requirements.txt
cp .env.example .env         # fill in DATABASE_URL at least
flask --app app:create_app db upgrade
python app.py
```

`GET /health` should return `{"status": "ok"}` once it's running.

## Configuration

All environment variables are read in [`config.py`](config.py); see
[`.env.example`](.env.example) for the full list and defaults. `DATABASE_URL`
is the only one without a fallback — the app fails fast on startup if it's
missing.

## Project layout

```
app.py              application factory, CORS/JWT setup, error handlers
config.py            env-driven Config class
models/               SQLAlchemy models (User, Memory)
routes/               blueprints: auth, memory, user
security/             password hashing
utils.py              small helpers shared across routes
migrations/            Alembic migration history (Flask-Migrate)
scripts/               one-off admin/debug scripts, run directly with python
```

## API overview

| Route | Method | Auth | Notes |
|---|---|---|---|
| `/health` | GET | - | liveness check |
| `/auth/register` | POST | - | `{username, email, password}` |
| `/auth/login` | POST | - | `{email, password}` -> JWT |
| `/user/<id>` | GET, PUT | JWT (self only) | profile, `profile_image_url` |
| `/memories` | GET, POST | JWT | list / create, scoped to the caller |
| `/memories/<id>` | GET, PUT, DELETE | JWT | scoped to the caller |

## Admin scripts

Run from the repo root, e.g.:

```bash
python scripts/list_users.py
python scripts/create_user.py --username Jonas --email jonas@memora.com
python scripts/check_db.py
```
