# Volkswagen Elite Motors — FastAPI backend + demo website

A **FastAPI** REST API and a matching demo site for **Volkswagen Elite Motors**, the authorised
Volkswagen dealership on Hosur Road, Bengaluru. Content and imagery are scraped from the client's
live site at <https://www.volkswagenbangalore.in/> and rebranded from generic "VW Bangalore" to
**Volkswagen Elite Motors** throughout.

> The client's own About page already refers to itself as Elite Motors — *"Elite Motors features a
> state-of-the-art auto showroom"* — and their outlet contacts are `crm@vw-elitemotors.co.in` /
> `crhead@vw-elitemotors.co.in`. The Elite Motors identity used here is the dealership's own.

---

## Run it

```bash
pip install -r requirements.txt
python run.py
```

Or with uvicorn directly:

```bash
uvicorn api.main:app --reload
```

| URL | What it is |
| --- | --- |
| <http://localhost:8000> | The website |
| <http://localhost:8000/docs> | **Swagger UI — interactive, try any endpoint** |
| <http://localhost:8000/redoc> | ReDoc reference |
| <http://localhost:8000/openapi.json> | OpenAPI 3.1 schema |
| <http://localhost:8000/api-explorer.html> | Branded endpoint index (reads the live schema) |

```bash
python run.py --port 9000 --reload
python run.py --host 0.0.0.0          # demo from a phone on the same network
```

---

## Layout

```
volkswagon elite/
├── run.py                  Launcher (uvicorn wrapper)
├── requirements.txt
├── api/
│   ├── main.py             App, tag metadata, error contract, static mount
│   ├── store.py            Catalogue loading, lookups, lead persistence, EMI maths
│   ├── schemas.py          Pydantic models — these generate the OpenAPI schema
│   └── routers/
│       ├── catalogue.py    Cars, variants, specs, FAQs, compare
│       ├── dealership.py   Dealer, outlets, offers, testimonials
│       ├── ownership.py    Services, packages, warranty, roadside, insurance
│       ├── finance.py      EMI and amortisation
│       ├── careers.py      Open roles
│       ├── enquiries.py    Lead capture
│       └── system.py       Search and health
├── data/
│   ├── catalog.json        The whole scraped knowledge base — single source of truth
│   └── leads.json          Submitted leads land here
├── web/                    The website (13 pages, vanilla JS, no build step)
│   └── assets/img/         96 images scraped from the client's site
├── kb/                     Markdown knowledge base — generated, see below
└── scrape/                 Raw scraped HTML + the scripts that produced the dataset
```

## Knowledge base

`kb/` holds the whole dataset as 32 Markdown files — dealership, cars, variants,
ownership, bookings (test drives and rentals included), finance, careers, FAQs and the
API reference. Each file carries YAML front matter (`title`, `summary`, `source`, `tags`,
`updated`) so it drops straight into a RAG pipeline or a docs site.

It is **generated**, never hand-edited — from `data/catalog.json`, the SQLAlchemy models
and the OpenAPI document — so it cannot drift from what the app serves:

```bash
python scrape/build_kb.py
```

Start at [`kb/README.md`](kb/README.md).

---

## The API

**42 operations**, grouped into seven tags, all documented in Swagger UI with typed request and
response schemas and worked examples.

### Catalogue
| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/cars` | All cars — filter, sort, paginate |
| GET | `/api/cars/{model_id}` | One car in full |
| GET | `/api/lineup` | The range grouped by body style |
| GET | `/api/models/{model_id}` | Alias of `/api/cars/{model_id}` |
| GET | `/api/models/{model_id}/faqs` | FAQs for one car |
| GET | `/api/models/{model_id}/specs` | Specification block |
| GET | `/api/models/{model_id}/colours` | Paint options with hex values |
| GET | `/api/models/{model_id}/gallery` | Gallery images |
| GET | `/api/models/{model_id}/variants` | Variants of one car |
| GET | `/api/variants` | All 19 variants with their prices |
| GET | `/api/variants/{variant_id}` | One variant |
| GET | `/api/compare` | Compare 2–4 cars attribute by attribute |

`/api/cars` accepts `q`, `body_type`, `family`, `segment`, `fuel`, `seats`, `price_min`,
`price_max`, `sort`, `limit`, `offset`.

### Dealership
`/api/dealer` · `/api/about` · `/api/stats` · `/api/outlets` · `/api/outlets/{outlet_id}` ·
`/api/offers` · `/api/testimonials` · `/api/hero-slides`

### Ownership
`/api/services` · `/api/service-packages` · `/api/service-packages/{package_id}` ·
`/api/service-models` (39 models incl. discontinued) · `/api/warranty` ·
`/api/roadside-assistance` · `/api/insurance`

### Finance
`GET /api/finance` · `GET /api/finance/quote` · `POST /api/finance/emi` ·
`POST /api/finance/amortisation`

### Careers
`/api/careers` · `/api/careers/jobs` · `/api/careers/jobs/{job_id}`

### Enquiries
`POST /api/leads/test-drive` · `POST /api/leads/service` · `POST /api/leads/insurance` ·
`POST /api/leads/contact` · `POST /api/careers/apply` · `GET /api/leads`

Leads are appended to `data/leads.json` and read back via `GET /api/leads`, so a form submitted
during a demo can be shown landing in the inbox.

### Search & System
`/api/search` (cars, variants, outlets, services, packages, jobs and FAQs in one call) · `/api/health`

### Examples

```bash
curl "http://localhost:8000/api/cars?body_type=SUV&sort=price_asc"
curl "http://localhost:8000/api/variants?model_id=taigun-sport"
curl "http://localhost:8000/api/compare?ids=golf-gti,tiguan-r-line,taigun-sport"
```

```bash
curl -X POST http://localhost:8000/api/finance/emi \
  -H 'Content-Type: application/json' \
  -d '{"principal":1500000,"down_payment":300000,"rate":9.25,"tenure_months":60}'
```

### Errors

Every failure returns the same envelope — never an HTML error page:

```json
{
  "error": {
    "status": 422,
    "message": "Validation failed",
    "detail": {
      "email": "Enter a valid email address.",
      "mobile": "Enter a valid phone number."
    }
  }
}
```

FastAPI's `RequestValidationError` is flattened into that `detail` map, and the website paints each
message under the offending input rather than showing one generic error.

---

## The website

13 pages, vanilla JS, no build step. Dark and cinematic, built to be looked at on a showroom screen.

**Design system** — tokens in `elite.css` drive everything: a five-step surface ramp
(`--ink` … `--ink-5`) that gains blue chroma as it lightens, full colour ramps rather than single
values (`--blue-700` … `--blue-300`, `--elite-600` … `--elite-2`), a four-step layered elevation
scale (`--e-1` … `--e-4`), spacing (`--s-1` … `--s-9`), and one shared focus treatment (`--ring`).
Archivo for display, Inter for text, JetBrains Mono for spec readouts.

Every brand tint is **derived from the tokens** via relative colour syntax
(`rgb(from var(--blue) r g b / .22)`), with literal fallbacks in an `@supports` pair — so changing
`--blue`, `--elite` or `--ink-1` re-tints every glow, ring, gradient and wash across the site.
Reusable atmospheric washes (`--wash-blue`, `--wash-navy`) give gradients a hue path to travel
instead of fading one colour to nothing.

- **Depth** — cards carry a hairline top highlight, a layered shadow and a pointer-tracked sheen;
  model shots sit on a lit stage with a contact shadow instead of floating in a box.
- **Motion** — five easing curves picked per job (`--ease`, `--ease-in`, `--ease-soft`,
  `--ease-smooth`, `--ease-spring`) and a duration scale. Headings rise line by line from behind a
  mask, hero slides cross-fade with a defocus and push, grids self-stagger, buttons lean toward the
  pointer, plus a scroll-progress bar, animated counters, marquee and a glass nav that morphs on
  scroll.
- **Everything is API-driven.** No content is hardcoded — cars, variants, FAQs, offers, outlets,
  packages, testimonials, hero slides and EMI figures are all fetched from `/api` at runtime.
  Edit `data/catalog.json` and the whole site updates.
- **Interactive** — live filter/search/sort, comparison table, variant price table, FAQ accordion,
  colour switcher that tints the hero, gallery lightbox, sticky in-page section nav with scroll-spy
  on the model page, and an EMI calculator with an animated donut and amortisation schedule.

**Accessibility**

- `:focus-visible` ring on every interactive element, a skip-to-content link, and a `<main>`
  landmark on all 13 pages.
- Text clears WCAG AA on its own surface — `--fg-3` at 6.5:1 and `--red` at 7.5:1 (both previously
  failed at 4.2:1 and 3.3:1). No label sits below 11.2px.
- Form errors carry a glyph as well as colour, so they do not rely on hue alone.
- Gallery tiles are buttons; the lightbox and mobile drawer trap focus, close on `Escape` and
  restore focus to where it came from.
- Tap targets reach 44px under `(pointer: coarse)`; `prefers-reduced-motion` and
  `prefers-contrast: more` are both honoured.
- Responsive to 375px. Reveal and counter animations fail open, so content is never left invisible
  if `IntersectionObserver` stalls.

---

## Notes on the data

- Copy, model names, features, specs, service packages, warranty terms, job roles, outlet
  addresses, phone numbers, emails and opening hours are **verbatim** from the client's site.
- 96 images were downloaded from the client's CDN and are served locally from `web/assets/img/`.
- **Prices are indicative.** The source site publishes none, so ex-showroom Bengaluru figures are
  used as realistic placeholders, labelled as such on every page and in the API (`price.note`,
  `price_note`). Variant prices are interpolated across each model's range. Swap them for real
  numbers in `data/catalog.json` before any public use.
- **Variants** follow the real Volkswagen India trim ladder (GT Line / GT Plus Sport, Comfortline /
  Highline / Topline). **FAQ answers** are composed from facts scraped from the dealership site —
  warranty term, service hours, NCAP rating, engines, features — not invented.
- Testimonials, statistics and current offers are illustrative demo content. Everything else is real.

## Scripts

```bash
python scrape/fetch_assets.py     # re-download imagery from the client's site
python scrape/enrich_catalog.py   # regenerate variants and FAQs (idempotent)
python scrape/test_fastapi.py     # call all 42 operations + 13 error paths
```

`scrape/` also holds the raw HTML that was parsed, kept as provenance for the extracted content.
