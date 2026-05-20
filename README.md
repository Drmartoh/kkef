# Kiambu-Karai Empowerment Forum (KKEF)

Premium, modular Django 5 + Django REST Framework platform for uniting community groups, SACCOs, environmental clusters, county stakeholders, donors, and members beneath a single transparency-grade operating model.

## Highlights

- TailwindCSS (CDN) + Alpine.js + Animate.css + Font Awesome front-end with dark/light modes, glass panels, animated counters, dashboards, and GIS (Leaflet).
- Domain apps for organizations, projects (kanban + milestones), proposals, donors, events (RSVP/ticketing scaffolding), community engagement, archival documents, media/news, and realtime notifications (Django Channels + Redis).
- JWT + session authentication, granular role permissions, audit logging, throttled AI assist endpoints, Stripe/M-Pesa webhook stubs, and Docker/Nginx/Gunicorn-ready assets.
- Management command `seed_demo` boots sample groups, projects, proposals, donations, and admin-ready accounts.

## Requirements

- Python 3.12+
- PostgreSQL 16+ for production
- Redis 7+ for Channel layers / notification fan-out

## Local development (SQLite bootstrap)

```powershell
cd C:\Users\pc\KKEF
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

> **Channels note:** the default `REDIS_URL` points to `redis://127.0.0.1:6379/0`. Start Redis locally or export a reachable URL before exercising `/ws/notifications/`.

### Demo credentials (change immediately)

| Username        | Role hint        | Password          |
|----------------|-----------------|-------------------|
| `kkef.super`   | Super admin     | `ChangeMe!2026`   |
| `forum.admin`  | Forum admin     | `ForumAdmin!2026` |
| `amaiagi.leader` | Group leader  | `LeaderDemo!2026` |
| `county.partner` | Stakeholder   | `StakeDemo!2026`  |
| `livingwaters.donor` | Donor   | `DonorDemo!2026`  |

## Quality checks

```powershell
python manage.py check
python manage.py test  # add tests as you harden modules
```

## API surface (v1)

REST routes are registered under `/api/v1/` (see `apps/integrations/api_urls.py`). Notable paths:

- `/api/v1/orgs/groups/`, `/api/v1/projects/`, `/api/v1/proposals/`
- `/api/v1/funding/donations/` + `/api/v1/funding/donations/rollup/`
- `/api/v1/events/` (+ `calendar/`, `register/`)
- `/api/v1/community/*`, `/api/v1/media/*`, `/api/v1/documents/`
- `/api/v1/analytics/tiles/` (public) & `/api/v1/analytics/executive/` (forum admins)
- `/api/v1/ai/*` proposal drafting, summariser, chatbot, and recommendation helpers (guarded by API keys + throttles)
- JWT lifecycle: `/api/auth/jwt/create/` & `/api/auth/jwt/refresh/`

## Docker & production

```powershell
copy .env.example .env
docker compose up --build
```

Services:

- `db` — PostgreSQL (`POSTGRES_*` env knobs in `docker-compose.yml`)
- `redis` — Channels + cache fan-out
- `web` — Daphne serving `config.asgi:application` (HTTP + WebSockets)
- `nginx` — Terminates traffic, serves `/static/` + `/media/`

### Manual production layout

1. Export `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, trusted hosts, HTTPS flags, and Stripe/M-Pesa secrets.
2. Build static files: `python manage.py collectstatic`.
3. Run migrations: `python manage.py migrate`.
4. Launch `gunicorn config.wsgi:application` or `daphne config.asgi:application` behind Nginx (see `deploy/nginx/nginx.conf`).

## Integration checklist

- Stripe: set `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, forward webhooks to `/payments/stripe/webhook/`.
- M-Pesa: implement signature validation inside `mpesa_callback_stub`.
- SMS/WhatsApp: extend `apps/integrations/services/outbound.py` with your approved gateways.
- AI: supply `OPENAI_API_KEY` (+ optional `OPENAI_MODEL`) for live completions; otherwise local heuristics activate.

## Accessibility & SEO

Semantic HTML landmarks, high-contrast palettes, keyboard navigable shells, and descriptive metadata blocks are included — continue adding alt text for uploads and structured data as media grows.

## Licensing

Proprietary to Kiambu-Karai Empowerment Forum unless otherwise released.
