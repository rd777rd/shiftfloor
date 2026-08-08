# ShiftFloor

On-demand staffing marketplace connecting Indianapolis-area warehouse and
distribution facilities with pre-vetted, certified workers for short-notice
shift coverage. Built as a portfolio project — see
`shiftfloor_project_plan.md` for the full Design, SEO, Coding, Deployment,
and Maintenance & Scaling plans, plus the 50-point audit rubric used to
check this codebase against them.

## Tech stack

Django 5.2+ · PostgreSQL (prod) / SQLite (local) · hand-written CSS +
vanilla JS · Stripe Checkout & Connect (test mode) · Cloudinary (media) ·
Brevo via django-anymail (email) · pytest-django · Render (hosting).

---

## 1. Local setup

**Requirements:** Python **3.12** recommended. (3.14 is Django 5.2's newest
supported version on paper, but this project has specifically hit a
migration-generation quirk on 3.14 in practice — see Troubleshooting
below. 3.12 is the tested, reliable choice.)

```bash
# 1. Clone and enter the project
git clone <your-repo-url> shiftfloor
cd shiftfloor

# 2. Create and activate a virtual environment (use Python 3.12 specifically)
py -3.12 -m venv venv            # Windows, if multiple Python versions are installed
# or: python3.12 -m venv venv    # macOS/Linux
source venv/bin/activate         # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy the environment template and fill in what you need
cp .env.example .env
# Local dev works out of the box with the defaults — SQLite, console
# email backend, no Cloudinary/Stripe keys required to browse the site.

# 5. Generate migrations (first time only — see note below)
python manage.py makemigrations

# 6. Apply migrations and create an admin account
python manage.py migrate
python manage.py createsuperuser

# 7. Run the dev server
python manage.py runserver
```

**About step 5:** if you're working from a copy of this repo where the
`*/migrations/` folders are already committed (i.e. someone already ran
this once and pushed the result), `makemigrations` will correctly say "No
changes detected" and you can skip straight to step 6 — that's the normal,
expected case going forward. Step 5 only matters the *first* time this
project's migrations are generated from scratch. See **Troubleshooting**
below if you hit "No changes detected" on a repo that genuinely has no
migration files yet.

Visit `http://127.0.0.1:8000/`. Sign up once as a facility and once as a
worker (two different browser sessions, or a private window) to try both
sides of the marketplace. Use the admin at `/admin/` (your superuser
login) to verify a certification once a worker uploads one — a worker
can't claim a certified shift until you do.

### Running tests

```bash
pytest
```

The suite specifically covers the shift-claim race condition (including a
real multi-threaded concurrency test), server-side certification
gate enforcement, role-based access denial across every dashboard, valid
`JobPosting` structured data, and the post-shift review gate.

---

## 2. Deploying to Render

All four Render services below are on Render's **free tier** — this
deployment costs $0.

**Before anything else: commit your migrations.** Render's build command
only runs `migrate` (applies existing migration files) — it deliberately
does **not** run `makemigrations` (see Troubleshooting below for why
that's a bad idea in an automated build). That means the migration files
generated in Local Setup step 5 above must already be committed to git
*before* you push, or the production database will have no tables to work
with. Confirm this before deploying:

```bash
git status
# You should see */migrations/*.py files either already committed,
# or listed here ready to be added:
git add */migrations/*.py
git commit -m "Add migrations"
```

### a. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

(If you already have a local repo from working through setup above,
skip straight to `git push -u origin main` once a remote is added.)

### b. Create the Render services

1. **PostgreSQL** — Render dashboard → New → PostgreSQL → free tier. Copy
   both the **Internal Database URL** (for the web service) and the
   **External Database URL** (for GitHub Actions, in step d below —
   GitHub's runners are outside Render's private network, so they can't
   reach the internal one).
2. **Web Service** — New → Web Service → connect your GitHub repo.
   - **Build Command:**
     `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command:** `gunicorn shiftfloor_project.wsgi:application`
   - **Environment variables:** set every key from `.env.example` in the
     Render dashboard's Environment tab. Set `DEBUG=False`,
     `DJANGO_SETTINGS_MODULE=shiftfloor_project.settings.production`, and
     `DATABASE_URL` to the Postgres **Internal** Database URL from step 1.

Render auto-deploys on every push to `main` once connected — no extra CI
setup needed.

### c. (Not used) Render Cron Jobs

Render's cron jobs now bill a minimum of $1/month per job, which breaks
this project's free-tools constraint — see "Known free-tier limitations"
below. Scheduled tasks run via GitHub Actions instead (step d).

### d. Set up the free scheduled tasks (GitHub Actions)

The two management commands (`expire_shifts`, `send_shift_reminders`) run
on a schedule via `.github/workflows/scheduled_tasks.yml`, already
included in this repo — no extra setup on GitHub's side beyond adding
secrets. In your GitHub repo: **Settings → Secrets and variables →
Actions → New repository secret**, and add:

- `DATABASE_URL` — the Postgres **External** Database URL from step 1
  (not the internal one)
- `SECRET_KEY` — same value as your Render web service
- `ANYMAIL_BREVO_API_KEY` — same value as your Render web service
- `DEFAULT_FROM_EMAIL` — same value as your Render web service

That's it — the workflow is already committed and will start running on
its schedule once the secrets are set. You can trigger a manual test run
anytime from the repo's **Actions** tab → "Scheduled Tasks" → **Run
workflow**.

Two honest caveats worth knowing:
- GitHub doesn't guarantee scheduled workflows fire at the exact minute —
  they can be delayed a few minutes during periods of high platform load.
  Fine for shift-expiry and reminder emails; not fine if you ever needed
  second-precision scheduling.
- GitHub Actions gives unlimited free minutes on **public** repositories,
  but private repos get a monthly free-minutes budget. At this project's
  schedule (hourly + every 15 minutes), a private repo could realistically
  approach that free limit. Keeping the repo public sidesteps this
  entirely — worth considering for a portfolio project anyway.

### e. Set up the other free third-party services

- **Cloudinary** — free account at cloudinary.com, copy the `CLOUDINARY_URL`
  from your dashboard into Render's environment variables.
- **Brevo** (email) — free account at brevo.com, generate an API key,
  set `ANYMAIL_BREVO_API_KEY`.
- **Stripe** — use your **test-mode** keys only (`sk_test_...`,
  `pk_test_...`). This demo deployment never processes real charges.
  Register the webhook endpoint at
  `https://<your-app>.onrender.com/payments/webhooks/stripe/` in the
  Stripe dashboard and copy the signing secret into
  `STRIPE_WEBHOOK_SECRET`.

### f. Fonts (optional polish)

The design system references self-hosted Barlow Condensed and Inter font
files. See `static/fonts/README.md` for the two-file download step — the
site works fine without them (falls back to system fonts) if you'd rather
skip it.

---

## 3. Troubleshooting

Real issues hit while first setting this project up, documented here so
nobody has to rediscover them:

**`makemigrations` says "No changes detected" even though no migration
files exist anywhere.** This happened specifically when generating
migrations for all 8 apps from a completely clean slate at once — a much
less common scenario than the usual "one new app in an already-migrated
project" case most Django tooling is optimized for. Because several of
this project's apps have foreign keys into each other
(`workers_app`→`accounts_app`, `shifts_app`→`facilities_app`,
`matching_app`→`shifts_app`+`workers_app`, etc.), Django's automatic
detection didn't reliably resolve that whole dependency graph starting
from zero history. The fix: name every app explicitly in one command,
which forces Django to generate each one's initial migration directly
rather than relying on automatic detection:

```bash
python manage.py makemigrations accounts_app core_app facilities_app workers_app shifts_app matching_app reviews_app payments_app -v 3
```

This is a **one-time** fix — once `0001_initial.py` exists for every app
and is committed, plain `python manage.py makemigrations` behaves
normally for any future model changes.

**Never run `makemigrations` as part of an automated build command
(Render's Build Command, a Dockerfile, CI, etc.).** It's tempting, but a
fresh checkout has no memory of previous builds — if migration files
aren't already committed to git, `makemigrations` running at build time
regenerates a "new" `0001_initial.py` from current models every single
deploy. Render's `migrate` then sees a migration with a name it already
marked applied from a previous deploy and **skips it**, silently
discarding any model changes made since — while the build logs look
completely clean. Always run `makemigrations` locally, review the
generated file, and commit it like any other code change. Automated
builds should only ever run `migrate`.

**`django.db.migrations.exceptions.InconsistentMigrationHistory`**
(`admin.0001_initial is applied before its dependency accounts_app.0001_initial`).
This happens when a local `db.sqlite3` file has history from *before*
`accounts_app`'s migration existed — for example, right after fixing the
"No changes detected" issue above. The fix is simply to delete the local
dev database and let `migrate` recreate it fresh: `db.sqlite3` is
gitignored, personal to your machine, and never touches production.
```bash
del db.sqlite3       # Windows; use `rm db.sqlite3` on macOS/Linux
python manage.py migrate
```

**A 500 error in production with no useful detail in Render's logs.**
Django's default logging configuration only prints request tracebacks to
the console when `DEBUG=True` — with `DEBUG=False` (correct for
production), a 500 error produces *no* traceback in Render's logs by
default. Two ways to see what's actually happening:
- **Fast/temporary:** set `DEBUG=True` in Render's environment variables,
  reload the failing page to see Django's full debug page, then **set it
  back to `False` immediately** — leaving debug mode on in production
  exposes settings, source snippets, and request data to anyone who
  triggers an error.
- **Permanent/recommended:** set `SENTRY_DSN` (free tier at sentry.io) as
  documented in `.env.example` — every unhandled exception then reports
  automatically to Sentry with a full traceback, no `DEBUG` toggling
  required.

---

## 4. Known free-tier limitations

This project is intentionally built entirely on free tools, per the
project's restrictions. That comes with a few honest trade-offs, all
documented here so nothing is a surprise:

| Limitation | Impact | Workaround |
|---|---|---|
| **Render free Postgres expires after 30 days** | The database (and all data in it) is deleted automatically | Recreate the free DB and re-run `migrate` + re-seed, or upgrade to Render's cheapest paid Postgres tier for real persistence |
| **Render free web service spins down after ~15 min idle** | First request after idle takes 30–60s (cold start) | Acceptable for a portfolio demo; upgrade to a paid web service tier to eliminate this if ever needed |
| **Render Cron Jobs are no longer free** (min. $1/mo per job as of Render's 2026 pricing) | Would break the free-tools constraint if used | Scheduled tasks run via GitHub Actions instead — see the Deployment section above. $0 on a public repo. |
| **Cloudinary free tier (~25 credits/month)** | Uploads/transformations pause once the monthly cap is hit | Upgrade Cloudinary's plan, or clear unused media |
| **Brevo free tier (300 emails/day)** | Notification emails beyond the cap queue/fail | Upgrade Brevo's plan if volume grows |
| **No automated backups by default** | Data loss risk beyond the 30-day Postgres window | Add a `pg_dump` step to a scheduled GitHub Actions workflow, writing to external storage, before relying on this for real data |

---

## 5. Project structure

```
shiftfloor_project/   settings, root urls, sitemaps
core_app/              marketing pages, shared SEO/JSON-LD tags, email/geo utilities
accounts_app/          custom User model, role-based signup/auth
facilities_app/        Facility & FacilityLocation, facility dashboard
workers_app/           WorkerProfile & Certification, verification pipeline
shifts_app/            Shift model, browse/post/detail, JobPosting schema, cron commands
matching_app/          ShiftApplication, race-condition-safe claim, offers
reviews_app/           post-shift two-way ratings
payments_app/          Stripe Checkout (facility billing) + Connect (worker payouts)
templates/              project-level base templates + shared partials
static/                 hand-written CSS, vanilla JS, fonts
```

See `shiftfloor_project_plan.md` for the full reasoning behind every
architectural decision above.