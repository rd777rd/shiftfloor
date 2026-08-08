# ShiftFloor — Project Plan

**Idea:** On-Demand Staffing for Warehouse & Distribution Workers
**Niche:** Indianapolis's bulk distribution market (193M+ sq ft) and its forklift-certified labor shortage
**Concept:** A hyperlocal, two-sided gig-shift marketplace connecting warehouse/DC facilities with pre-vetted, certified workers for short-notice shift coverage — "Instacart for warehouse labor."

---

## STEP 2.1 — DESIGN PLAN

### 1. Project Overview & Positioning

ShiftFloor is a **two-sided marketplace**, not a content site — every design decision has to serve either:
- **Facilities** (ops managers, HR staffing coordinators) who need a shift filled in hours, not weeks, or
- **Workers** (forklift operators, pickers/packers, RF-scanner operators, general labor) who want to see and claim open shifts fast, mostly from a phone.

Brand personality: **reliable, fast, no-nonsense, industrial-modern.** This is not a playful consumer brand — it should feel closer to a dispatch board than a lifestyle app. Trust signals (certification badges, verified facility badges, ratings) carry as much visual weight as the CTA buttons.

Positioning line: *"Open shifts, filled by lunch."*

### 2. User Personas

| Persona | Goal | Device | Key friction to remove |
|---|---|---|---|
| **Dana, DC Shift Supervisor** | Post an open shift for tomorrow's overnight pick wave in under 3 minutes | Desktop (office) + mobile (floor) | Doesn't want to write a job description — wants a fast structured form |
| **Marcus, Certified Forklift Operator** | Find a same-day or next-day shift near the FedEx hub / I-70 corridor that pays well and matches his cert | Mobile (Android-first) | Needs to *trust* the facility and see pay/cert requirements instantly, no back-and-forth |
| **Priya, Staffing Coordinator (multi-site)** | Manage recurring shift coverage across 3 facilities, track fill rate | Desktop | Needs a dashboard view, not a single-post flow |
| **Admin (ShiftFloor ops)** | Vet new workers' certifications, resolve disputes, monitor fill rates | Desktop (Django admin + custom ops views) | Needs fast approve/reject queues |

### 3. Information Architecture / Sitemap

```
/                          Home (marketing + role-based CTA: "I need workers" / "I want shifts")
/how-it-works/             Split explainer (facility track vs worker track)
/certifications/           Explainer of accepted certs (forklift classes, OSHA 10, etc.)
/pricing/                  Facility-side pricing (worker side is always free to browse/apply)
/faq/
/contact/

/accounts/
  /signup/facility/        Facility registration
  /signup/worker/          Worker registration + cert upload
  /login/  /logout/
  /password-reset/
  /profile/                Role-aware: worker profile OR facility profile

/facilities/
  /dashboard/              Facility home: open shifts, fill rate, upcoming shifts
  /<facility_slug>/        Public facility profile (verified badge, ratings, past fill history)
  /locations/              Manage multiple site locations (multi-site staffing coordinators)

/workers/
  /dashboard/               Worker home: matched/recommended shifts, upcoming shifts, earnings summary
  /<worker_id>/profile/     Worker public profile (certs, ratings, completed shifts) — visible to facilities only
  /certifications/          Upload/manage certifications, verification status

/shifts/
  /post/                    Facility: create a shift (structured form, not free text)
  /browse/                  Worker: browse/filter open shifts (map + list view)
  /<shift_id>/              Shift detail (pay, cert requirements, location, facility rating)
  /<shift_id>/apply/        Worker: one-tap apply / instant-claim
  /<shift_id>/manage/       Facility: view applicants, confirm worker, cancel/edit

/matching/
  /offers/                  Worker: pending offers requiring accept/decline
  /applicants/<shift_id>/   Facility: applicant queue for a shift

/reviews/
  /<shift_id>/review/       Post-shift two-way rating (facility rates worker, worker rates facility)

/payments/
  /facility/billing/        Facility invoicing / payment method (Stripe)
  /worker/payouts/          Worker payout history (Stripe Connect)

/notifications/             In-app notification center (new shift match, offer, reminder)

/admin/                     Django admin — cert verification queue, dispute resolution, facility verification
```

### 4. Core User Flows

**Flow A — Facility posts a shift (target: under 3 minutes)**
1. Login → Dashboard → "Post a Shift"
2. Structured form: role type (forklift/picker/packer/RF-scan/general), shift date/time, pay rate, required certs (checkbox list), headcount needed, location (defaults to facility's saved address)
3. Preview → Publish → shift instantly visible to matching workers within radius + cert match
4. Real-time applicant counter on the shift card in the dashboard

**Flow B — Worker claims a shift (target: under 60 seconds on mobile)**
1. Login → Dashboard shows shifts ranked by: cert match → distance → pay → start time
2. Tap shift card → detail view (pay, address, facility rating, required certs already shown as "✓ You qualify")
3. Tap "Claim Shift" → if facility has auto-accept enabled, instant confirmation; otherwise "Applied — pending confirmation"
4. Push/email notification on confirmation with directions + facility contact

**Flow C — Certification verification (trust backbone of the whole platform)**
1. Worker uploads cert (photo/PDF) during signup or from profile
2. Status shown as **Pending Review** (yellow), **Verified** (green badge), or **Rejected** (with reason)
3. Admin ops queue reviews and approves — worker only appears as "qualified" for a shift once verified
4. Facilities can filter shift applicants by verified-only

**Flow D — Post-shift close-out**
1. Facility marks shift as "Completed" (or "No-show")
2. Both sides prompted for a 5-star rating + short comment
3. Ratings feed into worker/facility public profiles and future matching rank

### 5. Visual Design System

**Concept:** industrial dispatch-board meets modern SaaS — hi-vis safety-orange as the single accent color against a graphite/steel neutral palette, echoing warehouse signage without looking like a caution label.

- **Primary:** Graphite `#1E2328` (headers, nav, dark UI chrome)
- **Secondary / Base:** Steel Gray `#4A5560`, Cool White `#F7F8F9` (backgrounds)
- **Accent (safety-orange):** `#FF6B1A` — used *only* for primary CTAs, active states, and the "Verified" cert badge glow — never decoratively, so it stays meaningful
- **Success (verified/confirmed):** `#2E9E5B`
- **Warning (pending):** `#E8A93B`
- **Error (rejected/no-show):** `#D64545`
- **Typography:**
  - Headings: **Barlow Condensed** (bold, industrial, high-legibility at small sizes — reads like signage) — via Google Fonts, self-hosted for performance/privacy
  - Body/UI: **Inter** — excellent mobile legibility, wide weight range for dense dashboard data
- **Iconography:** Line icons for nav/UI; solid filled badge icons for certifications (forklift class icon, OSHA hard-hat icon, hi-vis vest icon) so they read instantly on a shift card
- **Imagery style:** Real-feeling warehouse/DC photography (not stock-cheesy handshake photos) — pallets, forklifts, loading docks — desaturated slightly and duotoned with graphite/orange to stay on-brand

### 6. Page-Level Wireframe Descriptions

- **Home:** Split hero — left "I need workers today" (facility CTA), right "Find a shift near you" (worker CTA). Below: live stat bar (e.g., "X shifts filled this week near the FedEx hub"), how-it-works 3-step strip, trust section (cert types accepted, verification process), testimonials from real Indy warehouse roles.
- **Shift Browse (worker):** Sticky filter bar (cert type, distance, pay range, date), toggle between list and map view, each shift card shows role badge, pay, distance, facility star rating, "✓ You qualify" or "Cert required: Forklift Class III" inline.
- **Facility Dashboard:** Top KPI strip (open shifts, fill rate %, upcoming shifts this week), shift cards with live applicant counts, quick "Repost last shift" action for recurring coverage.
- **Shift Detail:** Pay and cert requirements above the fold, map + address, facility profile snippet with rating, single prominent claim/apply button (orange), sticky on mobile scroll.
- **Worker Profile (facility-facing):** Cert badges row at top (green = verified), completed shifts count, star rating, no-show rate — the trust snapshot a facility needs in 5 seconds.

### 7. Component Library (hand-written CSS, no framework)

Buttons (primary/secondary/danger), shift card, cert badge (3 states), star rating display + input, filter chip, status pill (pending/verified/confirmed/completed/no-show), KPI stat card, structured multi-step form stepper (reused pattern from prior progressive-disclosure work), toast notification, empty-state illustration blocks.

### 8. Responsive Strategy

**Mobile-first**, `min-width` media queries, breakpoints at 480px / 768px / 1024px / 1280px. Worker-facing flows (browse, claim, profile) are designed and tested mobile-first since that's the primary device for hourly workers. Facility dashboard is designed desktop-first but remains fully usable on tablet/mobile for floor supervisors.

### 9. Accessibility

WCAG 2.1 AA target: color contrast checked for the orange-on-graphite and orange-on-white combinations (orange as CTA-fill will use white text; orange as text-only will be avoided due to contrast), full keyboard navigation for the shift-post and shift-claim flows, semantic form labels, `aria-live` regions for real-time applicant counters and toast notifications, alt text for all cert badge icons.

### 10. Design-Driven App Architecture (preview — finalized in Coding Plan)

Mapping UI zones to a Django app boundary so navigation and templates stay modular:

`core_app` (home, static/marketing pages, shared templates/context processors) · `accounts_app` (auth, role-based profiles) · `facilities_app` (facility profiles, locations, dashboard) · `workers_app` (worker profiles, certifications) · `shifts_app` (shift CRUD, browse/filter) · `matching_app` (applications, offers, accept/decline logic) · `reviews_app` (post-shift ratings) · `payments_app` (Stripe billing for facilities, Stripe Connect payouts for workers)

Notifications will be handled as a shared utility (email via a free-tier transactional provider) rather than a dedicated paid SMS service, to keep the stack fully free-tier — confirmed further in the Coding Plan.

---

## STEP 2.2 — SEO PLAN

### 1. Strategy Overview & Goals

ShiftFloor has **three distinct SEO audiences**, and the strategy has to serve all three without diluting any:

1. **Facilities searching for staffing solutions** ("warehouse staffing agency Indianapolis," "same-day forklift operators near me") — high commercial intent, low volume, high value.
2. **Workers searching for shifts** ("forklift jobs Indianapolis today," "warehouse gig work near me") — high volume, and critically, this audience is best captured through **Google for Jobs**, not just organic blue links.
3. **Local/organic discovery of the brand itself** in the Indy industrial corridor (Plainfield, Whitestown, Greenwood, the airport/FedEx hub submarket) — building topical + geographic authority.

Primary goal: rank shift listing pages in **Google for Jobs** (via `JobPosting` structured data) — this is by far the highest-leverage SEO move available to a shift marketplace and effectively free distribution once implemented correctly.

### 2. Keyword Strategy

| Segment | Example targets | Intent | Primary landing page |
|---|---|---|---|
| Facility-side, high intent | "on-demand warehouse staffing indianapolis", "forklift staffing agency near fedex hub", "same day warehouse labor indy" | Commercial | `/`, `/how-it-works/` (facility track), `/pricing/` |
| Facility-side, informational | "how to cover last-minute warehouse shifts", "warehouse turnover indianapolis" | Top-of-funnel | Blog/resource hub |
| Worker-side, high intent | "forklift jobs indianapolis today", "warehouse shifts near me", "picker packer jobs plainfield in" | Transactional (job-seeking) | Individual `/shifts/<id>/` pages + `/shifts/browse/` |
| Worker-side, certification | "OSHA 10 certification indianapolis", "forklift certification class III near me" | Informational, funnel into signup | `/certifications/` + blog guides |
| Local/geo modifiers | "warehouse jobs whitestown in", "distribution center jobs greenwood indiana" | Local transactional | Geo-filtered `/shifts/browse/?location=` and future geo-landing pages |

Longtail worker-intent queries are the volume driver; individual shift pages are the conversion surface **if and only if** they're indexed and eligible for Google for Jobs — which depends entirely on correct `JobPosting` schema (Section 4).

### 3. Local SEO & Google Business Profile

- Claim and fully build out a **Google Business Profile** (free) categorized as a staffing agency, with service-area coverage across the Indy industrial corridor rather than a single storefront address (this is a marketplace, not a retail location).
- NAP (name/address/phone) consistency across the site footer, Business Profile, and any free local directory listings (BBB, Chamber of Commerce, industry-specific directories).
- Facility public profile pages (`/facilities/<slug>/`) double as local landing pages — each includes the facility's neighborhood/submarket, reinforcing geo-relevance site-wide.
- Consider a lightweight `/locations/` hub page listing served submarkets (Plainfield, Whitestown, Greenwood, Airport/FedEx hub) each linking to a filtered shift-browse view — gives Google clear geo-signals without building out full duplicate landing pages prematurely.

### 4. Structured Data / Schema Strategy (highest-leverage item)

- **`JobPosting` schema on every open shift detail page** (`/shifts/<id>/`) — required fields: `title`, `description`, `datePosted`, `validThrough` (shift start time), `employmentType` (TEMPORARY), `hiringOrganization` (facility), `jobLocation`, and `baseSalary`. This is what makes shifts eligible to surface in Google for Jobs.
  - **Critical technical detail:** when a shift is filled or expires, the page must return proper status (410 Gone or updated schema with no `validThrough` in the past) — stale `JobPosting` data violates Google's guidelines and can suppress the whole site's job-posting eligibility. This gets a dedicated cron/signal-based job in the Maintenance Plan.
- **`Organization` schema** on the homepage (logo, name, sameAs social links).
- **`LocalBusiness`** (or `EmploymentAgency` subtype) schema for the org, supporting local pack visibility.
- **`BreadcrumbList`** schema across all deep pages (shift detail, facility profile, worker profile, certifications) — reusing the templatetag/partial pattern proven on prior builds.
- **`AggregateRating`** on facility public profiles once review volume supports it (post-reviews_app launch).
- **`FAQPage`** schema on `/faq/` and `/certifications/` to capture featured-snippet real estate for certification questions.

### 5. On-Page SEO / Meta Strategy

- Per-page dynamic `<title>` and meta description templates: shift pages auto-generate from role + location + pay (e.g., *"Forklift Operator Shift — Plainfield, IN — $19/hr | ShiftFloor"*), rather than a static template, since uniqueness across hundreds of shift pages is what drives long-tail indexing.
- Per-page Open Graph/Twitter cards (pattern already proven on prior projects) — shift cards should look good when shared into local Facebook jobs/community groups, a real distribution channel for hourly work.
- Semantic heading hierarchy enforced in templates (one `<h1>` per page, no skipped levels) — checked in the rubric.
- Descriptive, human-readable URL slugs (`/shifts/forklift-plainfield-aug-12-4382/` rather than raw IDs alone) for both users and crawlers.

### 6. Technical SEO

- `django.contrib.sitemaps` for an auto-generated XML sitemap covering static pages, active shift listings, and facility/worker public profiles — **excluding** expired shifts to avoid crawl budget waste and thin/stale content signals.
- `robots.txt` disallowing dashboard, checkout, and account-management paths; allowing all public marketing and shift/facility pages.
- Canonical tags on all paginated/filtered browse views to consolidate ranking signal onto the base `/shifts/browse/` URL.
- Core Web Vitals: hand-written CSS (no framework bloat), lazy-loaded images below the fold, minimal render-blocking JS (vanilla JS, deferred), self-hosted fonts (Barlow Condensed + Inter) to avoid third-party font-loading latency — directly ties back to the Design Plan's framework-free approach.
- Mobile-first indexing is the default assumption, not an afterthought, since the worker-facing shift pages are the highest-volume indexed surface and are mobile-first by design already.

### 7. Content Strategy / Resource Hub

A lightweight `/resources/` or blog section (kept inside `core_app`, no separate app needed) targeting the informational keyword segment:
- "Certification guides" (what OSHA 10 covers, forklift class differences) — funnels directly into worker signup and the `/certifications/` explainer.
- "Employer guides" (how to reduce last-minute shift gaps, seasonal staffing planning for peak season around the FedEx hub) — funnels into facility signup.
- Local labor-market content (e.g., periodic "State of Indy Warehouse Staffing" posts) — link-earning content aimed at local business press and industry newsletters.

This is deliberately kept small at launch (a handful of cornerstone pages) rather than a large content operation — the marketplace listings themselves are the primary long-tail SEO engine.

### 8. URL Structure

Confirmed structure from the Design Plan's sitemap is already SEO-sound (flat, descriptive, role-segmented). No changes needed beyond adding slugs to shift and facility URLs as noted in Section 5.

### 9. Analytics & Measurement (free tools only)

- **Google Search Console** — monitor JobPosting indexing status/errors specifically (Search Console has a dedicated Job Postings report — this is the primary health check for the whole SEO strategy).
- **Google Analytics 4** (free tier) — funnel tracking for both signup tracks (facility vs worker) as separate conversion events.
- **Plausible or GA4 event tracking** for shift-claim conversion rate — free/low-cost, privacy-respecting option noted as an alternative if GA4 feels heavy for a portfolio-scale project.

### 10. Django Implementation Notes

- `django.contrib.sitemaps` + a small `seo` utility module (templatetags for JSON-LD partials, OG/meta partials) — reusing the proven pattern of per-page meta blocks and structured-data partials rather than a new app; lives inside `core_app`.
- `JobPosting` JSON-LD rendered directly in `shifts_app`'s detail template, populated from the `Shift` model — `validThrough` and status handled via a model property + the scheduled maintenance job (detailed in the Maintenance Plan).
- All schema partials unit-tested for valid JSON output as part of the pytest suite (ties into the Coding Plan's testing strategy).

---

## STEP 2.3 — CODING PLAN

### 1. Tech Stack Summary

| Layer | Choice | Notes |
|---|---|---|
| Framework | Django 5.2+ | Matches Python 3.14 compatibility lesson learned on prior builds |
| DB (prod) | PostgreSQL | Render free Postgres instance |
| DB (local) | SQLite | Zero-setup local dev |
| Templates | Django built-in templates (DTL) | No Jinja2 — restriction honored |
| CSS/JS | Hand-written CSS, vanilla JS | No frontend framework, per Design Plan |
| Payments | Stripe Checkout (facility billing) + Stripe Connect Express (worker payouts) | Stripe's free to integrate; fees are transactional, not platform cost |
| Media storage | Cloudinary free tier via `django-cloudinary-storage` | **Critical:** Render's free web service disk is ephemeral — cert uploads/profile photos would be lost on every redeploy without external storage. Flagging this now so it's not discovered at deployment time. |
| Email | Django email backend + free-tier transactional provider (e.g., Brevo/Sendinblue free tier — 300 emails/day free) via `django-anymail` | No paid SMS; email is the notification channel |
| Testing | pytest-django + `factory_boy` | Matches proven testing approach |
| Static files | WhiteNoise | Free, no external dependency, works cleanly on Render |
| Deployment | Render (web service + free Postgres + cron job for maintenance tasks) | Per hosting restriction |

### 2. Project & App Structure

```
shiftfloor_project/
├── shiftfloor_project/          # settings package
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py / asgi.py
├── core_app/                    # home, static pages, seo utils, shared templatetags, notifications utility
├── accounts_app/                # custom User model, role-based auth, profile routing
├── facilities_app/              # Facility, FacilityLocation models + dashboard views
├── workers_app/                 # WorkerProfile, Certification models + profile/cert management
├── shifts_app/                  # Shift model, browse/filter, post/edit, JobPosting schema
├── matching_app/                # ShiftApplication, Offer models, claim/accept/decline logic
├── reviews_app/                 # Review model, post-shift two-way rating flow
├── payments_app/                # Stripe Checkout + Connect integration, invoices, payouts
├── templates/                   # project-level base templates, shared partials (nav, footer, JSON-LD)
├── static/
├── requirements.txt
├── manage.py
└── README.md
```

Each app follows standard Django conventions (`models.py`, `views.py`, `urls.py`, `forms.py`, `admin.py`, `apps.py`, `templates/<app_name>/`, `tests/`).

### 3. Data Model (core schema by app)

**`accounts_app`**
- `User` (extends `AbstractUser`): adds `role` (choices: `WORKER`, `FACILITY_ADMIN`, `ADMIN`), `phone_number`, `email_verified`.

**`workers_app`**
- `WorkerProfile`: OneToOne→User, `bio`, `home_address`, `lat`/`lng` (for distance matching), `avg_rating` (denormalized, updated on review save), `completed_shifts_count`, `no_show_count`.
- `Certification`: FK→WorkerProfile, `cert_type` (choices: Forklift Class I–VII, OSHA 10, OSHA 30, general), `document` (Cloudinary file field), `status` (`PENDING`/`VERIFIED`/`REJECTED`), `reviewed_by` (FK→User, admin), `reviewed_at`, `rejection_reason`.

**`facilities_app`**
- `Facility`: OneToOne→User (facility admin account owner), `name`, `slug`, `description`, `verified` (bool), `avg_rating` (denormalized).
- `FacilityLocation`: FK→Facility, `address`, `lat`/`lng`, `label` (e.g. "Plainfield DC 3") — supports multi-site staffing coordinators from the Design Plan personas.

**`shifts_app`**
- `Shift`: FK→FacilityLocation, `role_type` (choices matching cert types), `required_cert` (nullable FK→cert type enum, null = general labor), `start_datetime`, `end_datetime`, `pay_rate`, `headcount_needed`, `headcount_filled` (denormalized counter), `status` (`OPEN`/`FILLED`/`IN_PROGRESS`/`COMPLETED`/`CANCELLED`/`EXPIRED`), `slug`, `auto_accept` (bool), `created_at`.
  - Property: `spots_remaining = headcount_needed - headcount_filled`.
  - Property: `is_job_posting_eligible` → drives whether JSON-LD `JobPosting` renders / page returns 410.

**`matching_app`**
- `ShiftApplication`: FK→Shift, FK→WorkerProfile, `status` (`APPLIED`/`OFFERED`/`ACCEPTED`/`DECLINED`/`CONFIRMED`/`COMPLETED`/`NO_SHOW`/`CANCELLED`), `applied_at`, `responded_at`. Unique-together (`shift`, `worker`) to prevent duplicate applications.

**`reviews_app`**
- `Review`: FK→ShiftApplication (one review pair per completed shift-application), `rating` (1–5), `comment`, `direction` (`FACILITY_TO_WORKER` / `WORKER_TO_FACILITY`), `created_at`.

**`payments_app`**
- `FacilityBillingProfile`: OneToOne→Facility, `stripe_customer_id`.
- `WorkerPayoutProfile`: OneToOne→WorkerProfile, `stripe_connect_account_id`, `payouts_enabled` (bool, synced from Stripe webhook).
- `Invoice` / `Payout` records for history views.

### 4. Authentication & Role-Based Access

- Custom `User` model with a `role` field set at signup (`/accounts/signup/facility/` vs `/accounts/signup/worker/` create the role-appropriate profile in the same transaction).
- A small `role_required` decorator / `RoleRequiredMixin` (CBV mixin) used across `facilities_app`, `workers_app`, `matching_app` views to gate dashboards — e.g., a worker can never reach `/shifts/post/`.
- Django's built-in auth views (login/logout/password reset) reused as-is per the "use built-in unless absolutely necessary" restriction — only templates are customized, not the view logic.

### 5. Core Business Logic

- **Shift claim race condition:** claiming a shift wraps the headcount check + `ShiftApplication` creation in `transaction.atomic()` with `select_for_update()` on the `Shift` row, so two workers claiming the last open spot simultaneously can't both succeed. This is a correctness-critical detail flagged now for the rubric.
- **Cert gate:** a worker can only see "✓ You qualify" and submit a claim if they have a `Certification` with matching `cert_type` and `status=VERIFIED`. Enforced both in the UI (template conditional) and server-side in the view/form `clean()` — never trust the client.
- **Matching/ranking:** shift browse queryset ordered by (cert match → distance via lat/lng haversine calculation in Python, no paid geocoding API beyond a one-time free-tier geocode on address save → pay rate desc → soonest start time), matching the Design Plan's Flow B ranking.
- **Offer/auto-accept:** if `Shift.auto_accept=True`, application status jumps straight to `CONFIRMED`; otherwise it sits at `APPLIED` until the facility manually confirms from `/matching/applicants/<shift_id>/`, moving it to `OFFERED` → worker accepts → `CONFIRMED`.
- **Shift lifecycle signals:** Django signals (`post_save` on `ShiftApplication`) update `Shift.headcount_filled` and flip `Shift.status` to `FILLED` automatically when `headcount_filled == headcount_needed`.
- **Review gate:** review form only reachable once `ShiftApplication.status == COMPLETED`, and only once per direction (enforced via unique constraint).

### 6. Views & URL Architecture

Mix of Django CBVs for standard CRUD-shaped views (`ListView`, `DetailView`, `CreateView`, `UpdateView` for shifts/facilities/certifications) and function-based views for the multi-step/business-logic-heavy flows (shift claim, offer accept/decline, review submission) where explicit control over the transaction/atomicity is clearer than fitting into a generic CBV.

### 7. Forms & Templates

- Shift posting uses the same **progressive-disclosure stepper pattern** already proven (vanilla JS + `_step_field.html`-style partials) rather than one long form, matching Design Plan Flow A's "under 3 minutes" goal.
- Base templates split by context: `base.html` (marketing/public), `base_dashboard.html` (facility, extends base with dashboard nav), `base_worker.html` (worker, extends base with mobile-optimized bottom nav bar for on-the-go use).
- Shared partials for JSON-LD blocks (`_jobposting_jsonld.html`, `_breadcrumb_jsonld.html`), reused from the templatetag pattern established on prior projects and wired per the SEO Plan.

### 8. Third-Party Integrations

- **Stripe Checkout**: facility billing (per-shift placement fee or monthly subscription — final pricing model decided at rubric/business-logic level, technically implemented as a Checkout Session + webhook handler updating `FacilityBillingProfile`).
- **Stripe Connect Express**: worker payout onboarding link generated from `/payments/worker/payouts/`; webhook listener updates `payouts_enabled`.
- **Cloudinary free tier**: all `ImageField`/`FileField` uploads (cert documents, profile photos) routed through `django-cloudinary-storage` so uploaded files survive Render redeploys.
- **Brevo (or equivalent free-tier ESP) via `django-anymail`**: transactional emails for shift confirmation, offer notifications, cert verification status changes.

### 9. Testing Strategy

pytest-django with `factory_boy` factories for `User`, `Facility`, `WorkerProfile`, `Shift`, `ShiftApplication`. Coverage priorities: the shift-claim race condition (concurrency test), cert-gate enforcement (server-side, not just template), role-based access denial, JobPosting JSON-LD validity, and the full Flow A/B/C/D happy paths from the Design Plan. This test list becomes direct input into the Step 3 rubric.

### 10. Settings & Environment Configuration

`django-environ` for `.env`-based config; `base.py`/`local.py`/`production.py` split (proven pattern). All secrets (Stripe keys, Cloudinary credentials, email API key, `SECRET_KEY`, `DATABASE_URL`) via environment variables — none committed to git, `.env.example` provided in the repo.

### 11. Management Commands

- `expire_shifts`: flips any `Shift` past its `start_datetime` still `OPEN` to `EXPIRED`, directly supporting the SEO Plan's JobPosting freshness requirement — scheduled via Render's free cron job feature.
- `send_shift_reminders`: emails workers with a `CONFIRMED` application ~2 hours before shift start.

### 12. Security Considerations

- CSRF on all forms (Django default), server-side re-validation of the cert gate and headcount on every claim attempt (never trust client-rendered "qualify" state), file-type/size validation on cert uploads, HTTPS enforced in production settings (`SECURE_SSL_REDIRECT`, HSTS), Stripe webhook signature verification, rate-limiting on the claim endpoint to blunt scripted double-claim attempts.

---

## STEP 2.4 — DEPLOYMENT PLAN

### 1. Render Services Overview

| Service | Type | Purpose |
|---|---|---|
| `shiftfloor-web` | Render Web Service (free tier) | Gunicorn-served Django app |
| `shiftfloor-db` | Render PostgreSQL (free tier) | Production database |

**Update:** Render's cron jobs are no longer free — they now bill a
minimum of $1/month per job with per-second execution billing on top,
which breaks this project's free-tools constraint. Scheduled tasks
(`expire_shifts`, `send_shift_reminders`) run via a **GitHub Actions
scheduled workflow** instead (`.github/workflows/scheduled_tasks.yml`),
genuinely free on a public repository. This keeps the whole deployment at
$0 as originally intended — see §6 below.

### 2. Environment & Secrets Management

All secrets set via Render's dashboard **Environment** tab (never committed to git):
`SECRET_KEY`, `DEBUG=False`, `DATABASE_URL` (auto-populated by Render when the Postgres service is linked), `ALLOWED_HOSTS`, `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_CONNECT_CLIENT_ID`, `CLOUDINARY_URL`, `ANYMAIL_BREVO_API_KEY`, `DEFAULT_FROM_EMAIL`. A `.env.example` in the repo documents every required key without real values, so setup is copy-paste-and-fill on Render.

### 3. Build & Start Configuration

```
Build Command: pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
Start Command: gunicorn shiftfloor_project.wsgi:application
```
Running `migrate` in the build step (rather than a separate release step, which Render's free tier doesn't support) keeps deploys single-step and reliable — a lesson carried over from prior deployment troubleshooting.

### 4. Static & Media Files in Production

- **Static** (CSS/JS/self-hosted fonts): WhiteNoise, `STATICFILES_STORAGE` set to the compressed-manifest backend, served directly by Gunicorn — no separate CDN needed at this scale, and it's free.
- **Media** (cert uploads, profile photos): Cloudinary free tier via `django-cloudinary-storage`, as locked in during the Coding Plan — this is the fix for Render's ephemeral disk and is treated as a hard requirement, not an optimization.

### 5. Database Strategy & Free-Tier Constraint

**Important caveat to flag explicitly:** Render's free PostgreSQL instances are automatically deleted after 30 days. For a portfolio project this is acceptable, but the README will document this clearly with two options: (a) recreate the free DB and re-run migrations/seed data every ~30 days, or (b) upgrade to Render's cheapest paid Postgres tier if long-term persistence is needed. This is called out up front so it's never a surprise mid-demo.

### 6. Scheduled Tasks — GitHub Actions (revised from original Render Cron Job plan)

**This section supersedes the original plan below.** Render's cron pricing changed to a minimum of $1/month per job with per-second execution billing on top — incompatible with this project's free-tools constraint. The two management commands from the Coding Plan (`expire_shifts`, `send_shift_reminders`) instead run via a GitHub Actions scheduled workflow (`.github/workflows/scheduled_tasks.yml`), triggered on the same schedule (hourly / every 15 minutes) via GitHub's native `schedule:` cron trigger, authenticating to Render's Postgres over its external connection string since GitHub's runners sit outside Render's private network. This still directly supports the SEO Plan's requirement that expired shifts stop being crawlable/eligible for `JobPosting` rich results — only the trigger mechanism changed, not the underlying guarantee. Two trade-offs versus Render's native cron, worth naming rather than glossing over: GitHub doesn't guarantee scheduled workflows fire at the exact minute (runs can be delayed a few minutes under high platform load), and GitHub Actions free minutes are unlimited on public repositories but capped on private ones — at this project's schedule frequency a private repo could approach that cap, so keeping the repo public sidesteps it entirely.

*(Original plan, superseded above: Render's free Cron Job service runs the two management commands from the Coding Plan on their own containers on a schedule, independent of the web service.)*

### 7. Stripe Webhook Configuration

Production webhook endpoint (`/payments/webhooks/stripe/`) registered in the Stripe Dashboard pointing at the Render web service's public URL, with the signing secret stored as `STRIPE_WEBHOOK_SECRET`. Stripe test mode used throughout development and demo (no real charges) — kept in **test mode** for the portfolio deployment so the live demo never processes real payments, documented clearly in the README.

### 8. Free-Tier Cold Start — UX Consideration

Render's free web services spin down after ~15 minutes of inactivity and take 30–60 seconds to wake on the next request. For a portfolio demo this is a known, acceptable trade-off, but it's worth naming explicitly since the product's whole value prop is *speed* ("filled by lunch") — the README will note this limitation candidly and mention the upgrade path (Render's cheapest paid web service tier eliminates spin-down) if this ever moves beyond portfolio use.

### 9. Custom Domain

Default deployment uses Render's free `shiftfloor.onrender.com`-style subdomain — no cost. A custom domain is optional and out of scope by default since domain registration isn't free; the README notes the two-step process (buy domain elsewhere → add as custom domain in Render, free on Render's side) if desired later.

### 10. Deploy Flow (CI/CD)

GitHub → Render's native **auto-deploy on push to `main`** (built into Render's free tier, no separate CI service needed). This satisfies Step 7/8 of your loop directly: once the repo is pushed, Render deploys automatically without a manual trigger step.

### 11. Health Checks & Monitoring

Render's built-in health check hits `/` by default; Django's `ALLOWED_HOSTS` and `DEBUG=False` verified as part of the deploy checklist. Google Search Console (already set up per the SEO Plan) doubles as the ongoing production health signal specifically for the JobPosting/sitemap surface, which a generic uptime check wouldn't catch.

---

## STEP 2.5 — MAINTENANCE & SCALING PLAN

### 1. Routine Maintenance

- **Dependency updates:** GitHub's free **Dependabot** enabled on the repo for automated security-patch PRs (Python packages + GitHub Actions if any are added later) — zero-cost vulnerability monitoring.
- **`pip-audit`** run periodically (documented as a README maintenance step) to catch known CVEs in pinned dependencies before they're flagged elsewhere.
- **Django/Python version currency:** given the Python 3.14 / Django 5.2 compatibility lesson from prior builds, the README documents the minimum-supported-version pairing explicitly so future upgrades don't silently break `psycopg2`/`Pillow`-style binary dependencies again.

### 2. Free-Tier Usage Monitoring

Every free-tier service in this stack has a cap — tracked explicitly so none becomes a surprise outage:

| Service | Free limit | What happens at the cap |
|---|---|---|
| Cloudinary | ~25 monthly credits (storage+bandwidth) | New uploads/transformations blocked until next cycle or upgrade |
| Brevo (email) | 300 emails/day | Emails queue/fail past the daily cap |
| Render Postgres | 30-day auto-expiry (free tier) | DB deleted — requires the recreate/re-seed process from the Deployment Plan |
| Render Web Service | Spin-down after ~15 min idle | Cold start on next request, no data loss |

These are documented in the README's "Known Free-Tier Limitations" section so the project stays honest about what it is: a fully-functional portfolio deployment, with a clear, named upgrade path for each limit if it ever needed to run at real production scale.

### 3. Backups

Given the free Postgres 30-day expiry, **no long-term backup is assumed on the free tier by default** — this is stated plainly rather than glossed over. For anyone extending this project past portfolio use: a simple `pg_dump` export via a scheduled Render Cron Job (writing to a free-tier object store, e.g., Cloudinary's raw file storage or a manually-triggered local export) is documented as the recommended first upgrade before relying on the deployment for real data.

### 4. Monitoring & Error Tracking

- **Sentry free tier** (5k errors/month) wired in via `sentry-sdk` for production exception tracking — catches issues like Stripe webhook failures or cert-upload errors in real time rather than waiting for a user report.
- **Google Search Console** continues as the SEO-specific health check (JobPosting indexing errors, sitemap coverage), as established in the SEO Plan.

### 5. Data Maintenance Jobs

Building on the two cron jobs from the Deployment Plan, two more are noted as straightforward additions if usage grows: `flag_stale_certifications` (prompt re-verification after a configurable expiry window — forklift certs do expire in reality) and `archive_completed_shifts` (move very old completed shifts out of the hot query path to keep the browse/dashboard queries fast).

### 6. Scaling Plan (path beyond portfolio scale)

Presented as a **staged upgrade path**, not a rewrite:

1. **Database indexing (do this first, free):** indexes on `Shift.status`, `Shift.start_datetime`, `Shift.facility_location`, and the lat/lng fields — the shift-browse query is the hottest path in the app and should be indexed from day one, not retrofitted.
2. **Caching (free, in-app):** Django's cache framework (local-memory or file-based cache, no Redis required at this scale) applied to the largely-static marketing pages and the facility/worker public profile pages.
3. **Background task queue (first paid step, if ever needed):** synchronous email sending and Stripe webhook handling are fine at portfolio scale; if shift volume grew significantly, Celery + a small Redis instance (Render's paid tier, since Redis isn't part of Render's free offering) would move notification sending off the request/response cycle — explicitly marked as a **future upgrade, not part of the initial build**, keeping the free-tools restriction intact for launch.
4. **Read scaling:** upgrade Render Postgres to a paid tier with more connections/storage before considering read replicas — noted as the natural next step, not implemented now.
5. **Geo scaling:** if ShiftFloor expanded beyond the Indy industrial corridor, the `/locations/` hub pattern from the SEO Plan extends cleanly to new metros without a data model change (`FacilityLocation` is already city-agnostic).

### 7. Feature Roadmap (documented, not built)

Noted in the README as logical next features rather than built now, to keep this deployment focused and true to the approved plans: SMS notifications (once budget allows a paid provider), a facility recurring-shift template feature, and worker shift-streak/loyalty badges tied into the ratings system already in place.

### 8. Change Management

Standard `main`-protected branching with feature branches per change, conventional commit messages, and this plan document (`shiftfloor_project_plan.md`) kept as the living source of truth — updated if any material deviation from an approved plan happens during coding.

---

## STEP 3 — UNIQUE AUDIT RUBRIC (50 CRITERIA)

Derived directly from decisions locked in across the five plans above. Each item is scored 1 point (pass) or 0 (fail) during the Step 5 audit — target is 50/50 before code is handed back for review.

### A. Design & UX (9 pts)
1. Mobile-first CSS confirmed via `min-width` media queries only (no `max-width` overrides)
2. Role-based base templates (`base.html` / `base_dashboard.html` / `base_worker.html`) used correctly, no cross-bleed between roles
3. Shift posting uses the progressive-disclosure stepper pattern, not a single long form
4. Safety-orange accent used only for CTAs and the Verified badge — never decoratively elsewhere
5. Cert badge component renders all 3 states (pending/verified/rejected) with distinct visual treatment
6. Shift card shows cert-match indicator ("✓ You qualify" / required cert) inline
7. Facility dashboard KPI strip present (open shifts, fill rate %, upcoming shifts)
8. WCAG AA contrast verified for orange-on-graphite and orange-on-white combinations
9. Fonts (Barlow Condensed, Inter) self-hosted, not loaded from an external CDN

### B. SEO & Structured Data (9 pts)
10. Valid `JobPosting` JSON-LD present on every open shift detail page with all required fields
11. Expired/filled shifts correctly drop `JobPosting` eligibility (410 or updated schema) — no stale data
12. XML sitemap excludes expired shifts and all dashboard/account/checkout URLs
13. `robots.txt` disallows dashboard/checkout/account paths, allows public pages
14. Per-shift `<title>`/meta description dynamically generated from role + location + pay (unique per page)
15. `BreadcrumbList` JSON-LD present on shift/facility/worker/cert deep pages
16. `FAQPage` schema present on `/faq/` and `/certifications/`
17. `Organization`/`LocalBusiness` schema present on homepage
18. Canonical tags present on paginated/filtered shift-browse views

### C. Data Model & Business Logic (9 pts)
19. Shift claim wrapped in `transaction.atomic()` + `select_for_update()` — race-condition safe
20. Cert gate enforced server-side in view/form `clean()`, not just a template conditional
21. `ShiftApplication` unique-together (`shift`, `worker`) constraint enforced
22. `Shift.headcount_filled` auto-updates via signal; status flips to `FILLED` correctly
23. Auto-accept vs. manual-confirm branching matches the Coding Plan's flow exactly
24. Review submission gated to `COMPLETED` applications only, one review per direction enforced
25. Denormalized `avg_rating` fields update correctly on `Review` save
26. Worker/Facility role + profile created atomically together at signup
27. Shift-browse ranking order matches spec (cert match → distance → pay → soonest start)

### D. Code Quality & Architecture (8 pts)
28. All 8 apps present, named with `_app` suffix; project folder is `shiftfloor_project`
29. Django built-in templates used throughout (DTL only, no Jinja2)
30. Django's built-in auth views reused for login/logout/password reset, not reimplemented
31. No business logic embedded in templates — logic lives in views/models/forms
32. JSON-LD/meta partials implemented as reusable templatetags/includes, not duplicated per template
33. CBVs used for CRUD-shaped views, FBVs for complex transactional flows, per plan
34. Human-readable slugs used for shift/facility URLs, not raw IDs alone
35. `requirements.txt` pinned to specific, compatible versions

### E. Security & Auth (8 pts)
36. Role-required mixin/decorator correctly blocks all cross-role view access
37. CSRF protection present on every form
38. File-type/size validation enforced on certification document uploads
39. Stripe webhook signature verification implemented
40. All secrets loaded via environment variables — none hardcoded or committed
41. HTTPS enforced in production settings (`SECURE_SSL_REDIRECT`, HSTS)
42. Rate-limiting or equivalent safeguard present on the shift-claim endpoint
43. Media uploads routed through Cloudinary in production, never local disk

### F. Testing & Deployment Readiness (7 pts)
44. pytest-django suite covers: claim race condition, cert-gate enforcement, role-based access denial, JobPosting schema validity
45. Settings split (base/local/production) works correctly with `django-environ`
46. Build command runs `collectstatic` + `migrate`; start command correctly invokes `gunicorn`
47. Both cron jobs (`expire_shifts`, `send_shift_reminders`) documented/configured for Render
48. README documents setup, deployment steps, and a "Known Free-Tier Limitations" table
49. `.env.example` provided with all required keys, no real secrets committed
50. Stripe kept in test mode for the live demo, clearly documented

**Total: 50 points — target 50/50 before Step 6 review.**

---

*Status: Rubric complete. Proceeding to Step 4: full code generation.*