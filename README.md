# ShiftFloor

**Live demo:** [shiftfloor.onrender.com](https://shiftfloor.onrender.com)
*(Free-tier hosting spins down after ~15 min idle — the first load can take 30–60s to wake up.)*

An on-demand staffing marketplace connecting Indianapolis-area warehouse
and distribution facilities with pre-vetted, certified workers for
short-notice shift coverage. Built solo as a full-stack portfolio project
to demonstrate production-grade Django patterns beyond CRUD — multi-tenant
access control, correctness under concurrency, real third-party
integrations, and SEO infrastructure — all on a $0/month hosting budget.

## See it in action

- Sign up as a **facility** to post a shift, or as a **worker** to browse
  and claim one — two different accounts (or a private browser window)
  show both sides of the marketplace.
- Facilities pay a flat per-shift placement fee via Stripe Checkout (test
  mode — no real charges); workers get paid out via Stripe Connect.
- Workers upload a certification for verification; a shift requiring that
  certification can't be claimed until it's approved.

## What this project demonstrates

- **Multi-tenant access control** — two distinct roles (Worker / Facility
  Admin) enforced server-side on every view via ownership-scoped
  queries, not just a hidden nav link. Covered by a dedicated test suite
  asserting every cross-role access attempt is actually denied.
- **Correctness under concurrency** — shift claiming uses
  `select_for_update()` inside atomic transactions so a shift's headcount
  can never be overfilled by two workers claiming it at once. Verified
  with a real multi-threaded test that fires simultaneous claims at the
  same shift, not a unit test that just assumes serial execution.
- **Real third-party integrations** — Stripe Checkout & Connect (test
  mode) for facility billing and worker payouts, Cloudinary for media
  storage, Brevo for transactional email — each wired through Django's
  own storage/email abstractions rather than hardcoded API calls.
- **SEO infrastructure** — `sitemap.xml`, `robots.txt`, self-referencing
  canonical tags, Open Graph/Twitter Card previews, and JSON-LD structured
  data (Organization, JobPosting, FAQPage, BreadcrumbList) across the
  site.
- **Automated test discipline** — a real, passing pytest suite covering
  the concurrency guarantee above, role-based access denial across every
  dashboard, server-side data validation (not just client-side form
  constraints), ownership checks on payment and profile-access endpoints,
  and structured-data correctness.
- **Resourceful, honest infrastructure** — the entire deployment runs on
  free tiers end-to-end, including routing scheduled jobs through GitHub
  Actions after Render discontinued free cron jobs. Trade-offs of that
  choice (documented in `SETUP.md`) are written down rather than hidden.

## Tech stack

Django 5.2 · PostgreSQL (prod) / SQLite (local) · hand-written CSS +
vanilla JS (no frontend framework) · Stripe · Cloudinary · Brevo (via
django-anymail) · pytest-django + factory_boy · Render + GitHub Actions.

## Project structure

```
shiftfloor_project/    settings, root urls, sitemaps
core_app/               marketing pages, shared SEO/JSON-LD tags, email/geo utilities
accounts_app/           custom User model, role-based signup/auth
facilities_app/         Facility & FacilityLocation, facility dashboard
workers_app/            WorkerProfile & Certification, verification pipeline
shifts_app/             Shift model, browse/post/detail, JobPosting schema, cron commands
matching_app/           ShiftApplication, race-condition-safe claim, offers
reviews_app/            post-shift two-way ratings
payments_app/           Stripe Checkout (facility billing) + Connect (worker payouts)
templates/               project-level base templates + shared partials
static/                  hand-written CSS, vanilla JS, fonts
```

## Setup, deployment & the reasoning behind it

Full local setup, Render deployment steps, and troubleshooting notes live
in [`SETUP.md`](./SETUP.md). The architectural reasoning behind every
major decision — and the 50-point audit rubric this codebase is checked
against — is in `shiftfloor_project_plan.md`.
