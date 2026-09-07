# -*- coding: utf-8 -*-
"""Build the kb/ knowledge base as Markdown.

Everything is generated from the live sources — data/catalog.json, the SQLAlchemy
models and the FastAPI OpenAPI document — so the knowledge base cannot drift from
what the application actually serves. Re-run after changing any of them.

    python scrape/build_kb.py
"""
from __future__ import annotations

import io
import json
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KB = ROOT / "kb"
CATALOG = ROOT / "data" / "catalog.json"
TODAY = date.today().isoformat()

sys.path.insert(0, str(ROOT))

db = json.loads(CATALOG.read_text(encoding="utf-8"))
DEALER = db["dealer"]
META = db["meta"]

written: list[Path] = []


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def inr(n) -> str:
    """Indian digit grouping: 5300000 -> 53,00,000."""
    s = str(int(n))
    if len(s) <= 3:
        return s
    head, tail = s[:-3], s[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    if head:
        groups.insert(0, head)
    return ",".join(groups) + "," + tail


def price_range(p) -> str:
    if p["min"] == p["max"]:
        return f"₹{inr(p['min'])}"
    return f"₹{inr(p['min'])} – ₹{inr(p['max'])}"


def esc(v) -> str:
    """Escape a value for use inside a Markdown table cell."""
    return str(v).replace("|", "\\|").replace("\n", " ")


def table(headers: list[str], rows: list[list]) -> str:
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(esc(c) for c in r) + " |")
    return "\n".join(out)


def write(rel: str, title: str, summary: str, body: str, tags: list[str]) -> None:
    path = KB / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    front = (
        "---\n"
        f"title: {title}\n"
        f"summary: {summary}\n"
        f"source: {META['source_url']}\n"
        f"dealership: {DEALER['trading_as']}\n"
        f"tags: [{', '.join(tags)}]\n"
        f"updated: {TODAY}\n"
        "---\n\n"
    )
    path.write_text(front + f"# {title}\n\n" + body.rstrip() + "\n", encoding="utf-8")
    written.append(path)


def hours_table(rows) -> str:
    return table(["Days", "Open", "Close"], [[r["days"], r["open"], r["close"]] for r in rows])


# --------------------------------------------------------------------------
# 01 — dealership
# --------------------------------------------------------------------------

def build_dealership() -> None:
    a = DEALER["about"]
    body = f"""{a['headline']}

""" + "\n\n".join(a["paragraphs"]) + f"""

## At a glance

{table(["Field", "Value"], [
    ["Legal name", DEALER["legal_name"]],
    ["Trading as", DEALER["trading_as"]],
    ["Brand", DEALER["brand"]],
    ["Authorised dealer", "Yes" if DEALER["authorised"] else "No"],
    ["City", DEALER["city"]],
    ["State", DEALER["state"]],
    ["Country", DEALER["country"]],
    ["Tagline", DEALER["tagline"]],
])}

## Dealership statistics

{table(["Metric", "Value"], [[s["label"], f"{inr(s['value'])}{s['suffix']}"] for s in DEALER["stats"]])}

> Statistics are illustrative demo figures. Everything else on this page is taken
> verbatim from the dealership's published site.
"""
    write("01-dealership/overview.md", "Dealership Overview",
          "Who Volkswagen Elite Motors are, in their own words.", body,
          ["dealership", "about", "company"])

    c = DEALER["contact"]
    body = f"""## Contact

{table(["Channel", "Value"], [
    ["Phone", c["phone"]],
    ["Phone (E.164)", c["phone_e164"]],
    ["Sales email", c["sales_email"]],
    ["Service email", c["service_email"]],
    ["WhatsApp", c.get("whatsapp") or "—"],
])}

## Sales hours

{hours_table(DEALER["hours"]["sales"])}

## Service hours

{hours_table(DEALER["hours"]["service"])}

## Social

{table(["Network", "URL"], [[k.title(), v] for k, v in DEALER["social"].items()])}
"""
    write("01-dealership/contact-and-hours.md", "Contact and Opening Hours",
          "Phone, email and the sales and service hours.", body,
          ["dealership", "contact", "hours"])

    parts = []
    for o in db["outlets"]:
        parts.append(f"""## {o['name']}

{table(["Field", "Value"], [
    ["Outlet ID", o["id"]],
    ["Type", o["type"]],
    ["Capabilities", ", ".join(o["types"])],
    ["Address", o["full_address"]],
    ["City", o["city"]],
    ["State", o["state"]],
    ["Pincode", o["pincode"]],
    ["Phone", o["phone"]],
    ["Email", o["email"]],
    ["Coordinates", f"{o['lat']}, {o['lng']}"],
    ["Map", o["map_url"]],
])}

### Hours

{hours_table(o["hours"])}
""")
    write("01-dealership/outlets.md", "Outlets",
          "Showroom and service centre locations, contacts and hours.",
          "\n".join(parts), ["dealership", "outlets", "locations"])

    rows = [[t["name"], t["location"], t["model"], "★" * t["rating"], t["quote"]]
            for t in db["testimonials"]]
    body = f"""{table(["Customer", "Location", "Model", "Rating", "Quote"], rows)}

> Testimonials are illustrative demo content, not published customer reviews.
"""
    write("01-dealership/testimonials.md", "Customer Testimonials",
          "What owners say about the dealership.", body,
          ["dealership", "testimonials", "reviews"])


# --------------------------------------------------------------------------
# 02 / 03 — cars and variants
# --------------------------------------------------------------------------

def build_cars() -> None:
    rows = [[m["name"], m["body_type"], m["seats"], m["specs"]["engine"],
             m["specs"]["power"], len(m["variants"]), price_range(m["price"])]
            for m in db["models"]]
    body = f"""{len(db['models'])} cars, {sum(len(m['variants']) for m in db['models'])} variants.

{table(["Model", "Body", "Seats", "Engine", "Power", "Variants", "Price range"], rows)}

## By body style

"""
    groups: dict[str, list] = {}
    for m in db["models"]:
        groups.setdefault(m["body_type"], []).append(m)
    for body_type, cars in sorted(groups.items()):
        body += f"### {body_type} ({len(cars)})\n\n"
        for m in cars:
            body += f"- **{m['name']}** — {m['tagline']} → [`{m['slug']}.md`](./{m['slug']}.md)\n"
        body += "\n"

    body += """## Pricing note

All prices are **indicative ex-showroom Bengaluru**. The source site does not publish
pricing. Contact the dealership for on-road pricing.
"""
    write("02-cars/index.md", "Car Lineup",
          "Every car the dealership sells, with prices and variant counts.", body,
          ["cars", "lineup", "catalogue"])

    for m in db["models"]:
        spec_rows = [[k.replace("_", " ").title(), v] for k, v in m["specs"].items()]
        var_rows = [[v["name"], v["trim"], v["engine"], v["power"], v["torque"],
                     v["transmission"], f"₹{inr(v['price'])}"]
                    for v in sorted(m["variants"], key=lambda x: x["price"])]

        feat = ""
        for group, items in m["features"].items():
            feat += f"### {group}\n\n" + "\n".join(f"- {i}" for i in items) + "\n\n"

        faqs = ""
        for f in m["faqs"]:
            faqs += f"**{f['question']}**\n\n{f['answer']}\n\n"

        body = f"""> {m['tagline']}

{m['description']}

## Identity

{table(["Field", "Value"], [
    ["Slug", m["slug"]],
    ["Family", m["family"]],
    ["Variant label", m["variant_label"]],
    ["Body type", m["body_type"]],
    ["Segment", m["segment"]],
    ["Seats", m["seats"]],
    ["Status", m["status"]],
    ["Badge", m["badge"] or "—"],
    ["Price range", price_range(m["price"])],
    ["Price basis", m["price"]["note"]],
])}

## Specifications

{table(["Specification", "Value"], spec_rows)}

## Highlights

""" + "\n".join(f"- {h}" for h in m["highlights"]) + f"""

## Variants ({len(m['variants'])})

{table(["Variant", "Trim", "Engine", "Power", "Torque", "Transmission", "Price"], var_rows)}

## Colours

{table(["Colour", "Hex"], [[c["name"], c["hex"]] for c in m["colors"]])}

## Features

{feat}## Gallery

""" + "\n".join(f"- `{g}`" for g in m["gallery"]) + f"""

## Frequently asked questions

{faqs}## API

- `GET /api/cars/{m['slug']}` — full record
- `GET /api/models/{m['slug']}/specs` — specifications only
- `GET /api/models/{m['slug']}/variants` — variants
- `GET /api/models/{m['slug']}/colours` — colours
- `GET /api/models/{m['slug']}/gallery` — gallery
- `GET /api/models/{m['slug']}/faqs` — FAQs
"""
        write(f"02-cars/{m['slug']}.md", m["name"],
              m["tagline"], body,
              ["cars", m["slug"], m["family"].lower(), m["body_type"].lower().replace(" ", "-")])

    all_variants = [v for m in db["models"] for v in m["variants"]]
    rows = [[v["id"], v["model_name"], v["trim"], v["engine"], v["power"],
             v["transmission"], v["drivetrain"], f"₹{inr(v['price'])}"]
            for v in sorted(all_variants, key=lambda x: x["price"])]
    body = f"""All {len(all_variants)} variants across the range, cheapest first.

{table(["Variant ID", "Model", "Trim", "Engine", "Power", "Transmission", "Drive", "Price"], rows)}

## Pricing note

Variant prices are interpolated across each model's published range and are
**indicative ex-showroom Bengaluru**.

## API

- `GET /api/variants` — all variants (filter by `model_id`, `trim`, `transmission`, `price_max`)
- `GET /api/variants/{{variant_id}}` — a single variant
"""
    write("03-variants/index.md", "All Variants",
          f"Every one of the {len(all_variants)} variants with individual pricing.", body,
          ["variants", "pricing", "catalogue"])


# --------------------------------------------------------------------------
# 04 — ownership
# --------------------------------------------------------------------------

def build_ownership() -> None:
    body = table(["ID", "Service", "Description"],
                 [[s["id"], s["name"], s["description"]] for s in db["services"]])
    write("04-ownership/services.md", "Workshop Services",
          "What the service centre offers.", body, ["ownership", "service", "workshop"])

    svp = db["service_packages"]
    body = f"""{svp['intro']}

## Guarantees

""" + "\n".join(f"- {g}" for g in svp["guarantees"]) + "\n\n"
    for p in svp["packages"]:
        body += f"""## {p['name']} ({p['duration']}){' — best value' if p.get('featured') else ''}

- **Package ID:** `{p['id']}`

""" + "\n".join(f"- {b}" for b in p["benefits"]) + "\n\n"
    body += """## API

- `GET /api/service-packages` — all packages
- `GET /api/service-packages/{package_id}` — a single package
"""
    write("04-ownership/service-packages.md", "Service Value Packages",
          "Prepaid maintenance packages — 1 Year, 2 Year and Hi5.", body,
          ["ownership", "service", "packages", "pricing"])

    w = db["warranty"]
    body = f"""## {w['standard']['title']}

{w['standard']['description']}

{table(["Field", "Value"], [
    ["Years", w["standard"]["years"]],
    ["Distance", f"{inr(w['standard']['kilometers'])} km"],
])}

## {w['extended']['title']}

{w['extended']['description']}

{table(["Term", "Distance covered"],
       [[o["term"], f"{inr(o['kilometers'])} km"] for o in w["extended"]["options"]])}
"""
    write("04-ownership/warranty.md", "Warranty",
          "Standard manufacturer warranty and extended cover options.", body,
          ["ownership", "warranty", "cover"])

    r = db["roadside_assistance"]
    body = f"""{r['description']}

{r['assistance_note']}

## What is covered

""" + "\n".join(f"- {c}" for c in r["coverage"])
    write("04-ownership/roadside-assistance.md", "Roadside Assistance",
          "Volkswagen Assistance cover and what it includes.", body,
          ["ownership", "roadside", "assistance", "emergency"])

    ins = db["insurance"]
    body = f"""{ins['description']}

## Benefits

""" + "\n".join(f"- {b}" for b in ins["benefits"]) + """

## Fields collected on the renewal form

""" + "\n".join(f"- {f}" for f in ins["form_fields"]) + """

See [insurance-enquiry.md](../05-bookings/insurance-enquiry.md) for the submission API.
"""
    write("04-ownership/insurance.md", "Insurance",
          "Motor insurance benefits and the renewal enquiry fields.", body,
          ["ownership", "insurance", "renewal"])

    body = f"""Every Volkswagen accepted for service, including discontinued generations
({len(db['service_models'])} entries).

""" + "\n".join(f"- {m}" for m in db["service_models"]) + """

## API

- `GET /api/service-models`
"""
    write("04-ownership/serviceable-models.md", "Serviceable Models",
          "All Volkswagen models the workshop accepts.", body,
          ["ownership", "service", "models"])


# --------------------------------------------------------------------------
# 05 — bookings (test drive, rentals, service, insurance, contact, careers)
# --------------------------------------------------------------------------

def sqlalchemy_table(model) -> str:
    rows = []
    for col in model.__table__.columns:
        rows.append([
            col.name,
            str(col.type),
            "no" if not col.nullable else "yes",
            "yes" if col.primary_key else "",
            str(col.default.arg) if col.default is not None and not callable(getattr(col.default, "arg", None)) else
            ("now()" if col.server_default is not None else ""),
        ])
    return table(["Column", "Type", "Nullable", "PK", "Default"], rows)


def fields_table(rows) -> str:
    return table(["Field", "Type", "Required", "Example"], rows)


def build_bookings() -> None:
    try:
        from api import db_models
        td_schema = sqlalchemy_table(db_models.TestDrive)
        rent_schema = sqlalchemy_table(db_models.Rental)
        db_note = "Persisted to SQLite via SQLAlchemy (`volkswagen.db`)."
    except Exception as exc:                                   # pragma: no cover
        td_schema = rent_schema = f"_Could not introspect models: {exc}_"
        db_note = "Database models could not be introspected at build time."

    # ---- test drive ----
    body = f"""A prospective customer asks to drive a specific car before buying.
A Sales Consultant confirms the slot and has the car ready at the showroom.

## Where it is offered

- The **Contact** page (`/contact.html#test-drive`)
- Every **model detail** page (`/model.html?slug=…`), pre-filled with that car
- The **Book a Test Drive** button in the site header

## API

```
POST /api/leads/test-drive
Content-Type: application/json
```

### Request fields

{fields_table([
    ["first_name", "string", "yes", "Praneet"],
    ["last_name", "string", "yes", "Gogoi"],
    ["email", "string", "yes", "you@example.com"],
    ["mobile", "string", "yes", "9876543210"],
    ["model", "string", "yes", "Golf GTI"],
    ["preferred_date", "string (YYYY-MM-DD)", "no", "2026-09-15"],
    ["preferred_time", "string", "no", "Morning (10:00 – 13:00)"],
])}

### Validation

- `email` must match a standard address pattern.
- `mobile` must be 8–18 digits, optionally with `+`, spaces, hyphens or brackets.
- Every failing field is reported at once in `error.detail`.

### Example request

```bash
curl -X POST http://localhost:8000/api/leads/test-drive \\
  -H 'Content-Type: application/json' \\
  -d '{{
    "first_name": "Praneet",
    "last_name": "Gogoi",
    "email": "you@example.com",
    "mobile": "9876543210",
    "model": "Golf GTI",
    "preferred_date": "2026-09-15",
    "preferred_time": "Morning (10:00 – 13:00)"
  }}'
```

### Success — `201 Created`

```json
{{
  "message": "Your request submitted successfully.",
  "reference": "test-drive-a1b2c3d4e5",
  "next_step": "A Sales Consultant from Elite Motors will call you within one working day.",
  "lead": {{ "id": "test-drive-a1b2c3d4e5", "type": "test-drive", "status": "new", "data": {{ }} }}
}}
```

### Validation failure — `422`

```json
{{
  "error": {{
    "status": 422,
    "message": "Validation failed",
    "detail": {{ "email": "Enter a valid email address." }}
  }}
}}
```

## Storage

{db_note} The request is also appended to `data/leads.json` with `type: "test-drive"`,
which is what `GET /api/leads` reads.

### Table `test_drives`

{td_schema}

## Managing test drives

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/leads/test-drive` | Every test drive row from the database |
| `PATCH` | `/api/leads/test-drive/{{id}}` | Set a booking's `status` |

```bash
curl -X PATCH http://localhost:8000/api/leads/test-drive/1 \\
  -H 'Content-Type: application/json' -d '{{"status":"CONFIRMED"}}'
```

New bookings are created with status `PENDING`. Both endpoints are
**unauthenticated** — anyone who can reach the API can read every customer's
contact details and change any booking.

## Follow-up

A Sales Consultant contacts the customer within one working day to confirm the slot.
Home or office pick-up is available on request.
"""
    write("05-bookings/test-drive.md", "Test Drive Booking",
          "How a test drive is requested, validated, stored and followed up.", body,
          ["bookings", "test-drive", "leads", "api"])

    # ---- rentals ----
    body = f"""A customer hires a Volkswagen for a fixed period rather than buying one.
The team confirms availability and arranges the handover.

## API

```
POST /api/leads/rent
Content-Type: application/json
```

### Request fields

{fields_table([
    ["first_name", "string", "yes", "Praneet"],
    ["last_name", "string", "yes", "Gogoi"],
    ["email", "string", "yes", "you@example.com"],
    ["mobile", "string", "yes", "9876543210"],
    ["model", "string", "yes", "Volkswagen Virtus"],
    ["start_date", "string (YYYY-MM-DD)", "yes", "2026-09-10"],
    ["end_date", "string (YYYY-MM-DD)", "yes", "2026-09-15"],
])}

### Validation

- `email` and `mobile` use the same patterns as every other lead endpoint.
- `start_date` and `end_date` are **required** — unlike a test drive, where the date is optional.
- **Double bookings are rejected.** Before writing, the endpoint looks for an
  existing rental of the same `model` whose dates overlap the requested window
  and whose status is `PENDING` or `CONFIRMED`. A clash returns `409 Conflict`:

  ```json
  {{"error": {{"status": 409, "message": "The Golf GTI is already booked for these dates."}}}}
  ```
- Dates are compared as strings, so they must be `YYYY-MM-DD` to order correctly.
  The API does not check that `end_date` falls after `start_date`.

### Example request

```bash
curl -X POST http://localhost:8000/api/leads/rent \\
  -H 'Content-Type: application/json' \\
  -d '{{
    "first_name": "Praneet",
    "last_name": "Gogoi",
    "email": "you@example.com",
    "mobile": "9876543210",
    "model": "Taigun Sport",
    "start_date": "2026-09-10",
    "end_date": "2026-09-14"
  }}'
```

### Success — `201 Created`

```json
{{
  "message": "Your rental request submitted successfully.",
  "reference": "rent-e50281919d",
  "next_step": "Our team will confirm your booking and arrange the handover.",
  "lead": {{ "id": "rent-e50281919d", "type": "rent", "status": "new", "data": {{ }} }}
}}
```

## Storage

{db_note} The request is also appended to `data/leads.json` with `type: "rent"`.

### Table `rentals`

{rent_schema}

## Managing rentals

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/leads/rent` | Every rental row from the database |
| `PATCH` | `/api/leads/rent/{{id}}` | Set a rental's `status` |

```bash
curl -X PATCH http://localhost:8000/api/leads/rent/1 \
  -H 'Content-Type: application/json' -d '{{"status":"CONFIRMED"}}'
```

Status drives the conflict check above: only `PENDING` and `CONFIRMED` rentals
block a date range, so cancelling one frees the car.

## Current limitations

- There is **no rental pricing** in the catalogue — daily or weekly rates are not modelled.
- There is **no fleet model**; any `model` string is accepted, and each car is
  treated as a single unit rather than a countable pool.
- The admin endpoints are **unauthenticated** — anyone who can reach the API can
  read every customer's details and change any booking's status.
- `status` is a free-text column with no constraint, so a typo in a `PATCH` (for
  example `CONFIRM`) silently stops that rental blocking its dates.

## Follow-up

The team confirms the booking and arranges the handover.
"""
    write("05-bookings/rentals.md", "Car Rental Booking",
          "How a rental is requested, validated and stored, and what is not yet modelled.", body,
          ["bookings", "rentals", "leads", "api"])

    # ---- service ----
    body = f"""A customer books their car into the workshop.

## Where it is offered

The **Service** page (`/service.html#book`).

## API

```
POST /api/leads/service
```

### Request fields

{fields_table([
    ["name", "string", "yes", "Praneet Gogoi"],
    ["mobile", "string", "yes", "9876543210"],
    ["model", "string", "yes", "Volkswagen Taigun"],
    ["service_centre", "string", "yes", "Volkswagen Elite Motors Service — Hosur Road"],
    ["email", "string", "no", "you@example.com"],
    ["registration_number", "string", "no", "KA 01 AB 1234"],
    ["preferred_date", "string (YYYY-MM-DD)", "no", "2026-09-12"],
    ["message", "string", "no", "Rattle from the rear on rough roads."],
])}

`model` accepts any entry from [serviceable-models.md](../04-ownership/serviceable-models.md),
including discontinued generations. `service_centre` should match an outlet
from [outlets.md](../01-dealership/outlets.md).

## Storage

Appended to `data/leads.json` with `type: "service"`. **Not** written to SQLite —
only test drives and rentals have database tables so far.

## Follow-up

A Service Advisor confirms the slot and the pick-up window.
"""
    write("05-bookings/service-booking.md", "Service Booking",
          "How a workshop booking is requested and stored.", body,
          ["bookings", "service", "leads", "api"])

    # ---- insurance ----
    body = f"""A customer asks for a comparative motor insurance renewal quote.

## API

```
POST /api/leads/insurance
```

### Request fields

{fields_table([
    ["full_name", "string", "yes", "Praneet Gogoi"],
    ["mobile", "string", "yes", "9876543210"],
    ["email", "string", "yes", "you@example.com"],
    ["registration_number", "string", "yes", "KA 01 AB 1234"],
    ["model", "string", "no", "Volkswagen Virtus"],
    ["registration_year", "string", "no", "2023"],
    ["registration_month", "string", "no", "March"],
    ["insurance_company", "string", "no", "HDFC ERGO"],
    ["policy_number", "string", "no", "P/123456789"],
    ["insurance_expiry", "string (YYYY-MM-DD)", "no", "2026-11-30"],
])}

## Storage

Appended to `data/leads.json` with `type: "insurance"`.

## Follow-up

A comparative quote is sent within 24 hours.
"""
    write("05-bookings/insurance-enquiry.md", "Insurance Enquiry",
          "How an insurance renewal quote is requested.", body,
          ["bookings", "insurance", "leads", "api"])

    # ---- contact ----
    body = f"""A general enquiry to the dealership.

## API

```
POST /api/leads/contact
```

### Request fields

{fields_table([
    ["name", "string", "yes", "Praneet Gogoi"],
    ["email", "string", "yes", "you@example.com"],
    ["mobile", "string", "yes", "9876543210"],
    ["message", "string", "yes", "What is the waiting period on the Tayron R-Line?"],
    ["subject", "string", "no", "General enquiry"],
])}

## Storage

Appended to `data/leads.json` with `type: "contact"`.
"""
    write("05-bookings/contact-enquiry.md", "General Enquiry",
          "How a general contact enquiry is submitted.", body,
          ["bookings", "contact", "leads", "api"])

    # ---- careers ----
    jobs = ", ".join(f"`{j['id']}`" for j in db["careers"]["jobs"])
    body = f"""An application for one of the open roles.

## API

```
POST /api/careers/apply
```

### Request fields

{fields_table([
    ["name", "string", "yes", "Praneet Gogoi"],
    ["email", "string", "yes", "you@example.com"],
    ["mobile", "string", "yes", "9876543210"],
    ["job_id", "string", "yes", "sales-consultant"],
    ["experience", "integer (0–60)", "no", "4"],
    ["cv_filename", "string", "no", "praneet-gogoi-cv.pdf"],
    ["message", "string", "no", "A short note about why this role."],
])}

`job_id` must be one of: {jobs}. An unknown id returns `422` with the valid options
listed in `error.detail.job_id`.

## Storage

Appended to `data/leads.json` with `type: "career"`. The CV **filename** is recorded;
the file itself is not uploaded in this build.

## Follow-up

HR reviews every application within five working days.
"""
    write("05-bookings/job-application.md", "Job Application",
          "How a career application is submitted and validated.", body,
          ["bookings", "careers", "leads", "api"])

    # ---- index ----
    body = f"""Every way a customer can submit something to the dealership.

{table(["Booking type", "Endpoint", "Stored in SQLite", "Document"], [
    ["Test drive", "`POST /api/leads/test-drive`", "yes — `test_drives`", "[test-drive.md](./test-drive.md)"],
    ["Car rental", "`POST /api/leads/rent`", "yes — `rentals`", "[rentals.md](./rentals.md)"],
    ["Service booking", "`POST /api/leads/service`", "no", "[service-booking.md](./service-booking.md)"],
    ["Insurance enquiry", "`POST /api/leads/insurance`", "no", "[insurance-enquiry.md](./insurance-enquiry.md)"],
    ["General enquiry", "`POST /api/leads/contact`", "no", "[contact-enquiry.md](./contact-enquiry.md)"],
    ["Job application", "`POST /api/careers/apply`", "no", "[job-application.md](./job-application.md)"],
])}

## Shared behaviour

Every endpoint above:

- returns **`201 Created`** on success with a `reference` the customer can quote;
- returns **`422`** with a `{{field: message}}` map in `error.detail` listing *every*
  invalid field at once, not just the first;
- appends the submission to `data/leads.json`, readable back via `GET /api/leads`
  (filter with `?type=`).

## Reading submissions

```bash
curl "http://localhost:8000/api/leads?type=rent&limit=20"
```

```bash
sqlite3 volkswagen.db "select * from rentals order by created_at desc limit 5;"
```
"""
    write("05-bookings/index.md", "Bookings and Enquiries",
          "All six submission types, their endpoints and where each is stored.", body,
          ["bookings", "leads", "api", "index"])


# --------------------------------------------------------------------------
# 06 / 07 / 08 — finance, careers, faqs
# --------------------------------------------------------------------------

def build_rest() -> None:
    f = db["finance"]
    d, lim = f["defaults"], f["limits"]
    body = f"""{f['description']}

## Defaults

{table(["Field", "Value"], [
    ["Principal", f"₹{inr(d['principal'])}"],
    ["Rate", f"{d['rate']}% p.a."],
    ["Tenure", f"{d['tenure_months']} months"],
    ["Down payment", f"{d['down_payment_pct']}%"],
])}

## Accepted ranges

{table(["Field", "Minimum", "Maximum"], [
    ["Principal", f"₹{inr(lim['principal_min'])}", f"₹{inr(lim['principal_max'])}"],
    ["Rate", f"{lim['rate_min']}%", f"{lim['rate_max']}%"],
    ["Tenure", f"{lim['tenure_min']} months", f"{lim['tenure_max']} months"],
])}

## Lending partners

""" + "\n".join(f"- {p}" for p in f["partners"]) + """

## How the EMI is calculated

Standard reducing-balance amortisation:

```
r    = annual_rate / 12 / 100
EMI  = P × r × (1 + r)^n / ((1 + r)^n − 1)
```

where `P` is the amount financed (price − down payment) and `n` is the tenure in months.
When `r` is zero the EMI is simply `P / n`.

## API

```bash
curl -X POST http://localhost:8000/api/finance/emi \\
  -H 'Content-Type: application/json' \\
  -d '{"principal":1500000,"down_payment":300000,"rate":9.25,"tenure_months":60}'
```

- `GET /api/finance` — configuration and partners
- `GET /api/finance/quote` — quote via query string, optionally priced against `model_id`
- `POST /api/finance/emi` — EMI plus the first 12 instalments
- `POST /api/finance/amortisation` — full repayment schedule

> Indicative only. Not an offer of credit. Final rates depend on the customer's
> credit profile and the lending partner.
"""
    write("06-finance/emi.md", "Finance and EMI",
          "How EMI is calculated, accepted ranges and lending partners.", body,
          ["finance", "emi", "loan", "api"])

    rows = [[o["id"], o["title"], o["value"], o["valid_till"], o["description"]]
            for o in db["offers"]]
    body = f"""{table(["ID", "Offer", "Value", "Valid till", "Details"], rows)}

> Offers are illustrative demo content, not published dealership offers.
"""
    write("06-finance/offers.md", "Current Offers",
          "Running offers with their values and expiry.", body,
          ["finance", "offers", "promotions"])

    c = db["careers"]
    body = f"""{c['description']}

## Open roles

"""
    for j in c["jobs"]:
        body += f"""### {j['title']}

{table(["Field", "Value"], [
    ["Job ID", j["id"]],
    ["Department", j["department"]],
    ["Location", j["location"]],
    ["Type", j["type"]],
])}

{j['description']}

"""
    body += f"""## Applying

Accepted CV formats: {', '.join(c['upload_formats'])}.
See [job-application.md](../05-bookings/job-application.md) for the submission API.
"""
    write("07-careers/open-roles.md", "Open Roles",
          "Every open position at the dealership and how to apply.", body,
          ["careers", "jobs", "hiring"])

    body = f"""Every question in the knowledge base, grouped by car
({sum(len(m['faqs']) for m in db['models'])} in total).

"""
    for m in db["models"]:
        body += f"## {m['name']}\n\n"
        for f_ in m["faqs"]:
            body += f"**{f_['question']}**\n\n{f_['answer']}\n\n"
    body += """> FAQ answers are composed from facts scraped from the dealership's site —
> warranty terms, service hours, NCAP ratings, engines and features.
"""
    write("08-faqs/index.md", "Frequently Asked Questions",
          "All FAQs across the range, grouped by car.", body,
          ["faqs", "questions", "support"])


# --------------------------------------------------------------------------
# 09 — API reference
# --------------------------------------------------------------------------

def build_api() -> None:
    try:
        from api.main import app
        spec = app.openapi()
    except Exception as exc:                                   # pragma: no cover
        write("09-api/endpoints.md", "API Reference",
              "Could not be generated.",
              f"_The OpenAPI document could not be built: {exc}_", ["api"])
        return

    groups: dict[str, list] = {}
    for path, verbs in spec["paths"].items():
        for verb, op in verbs.items():
            tag = (op.get("tags") or ["Other"])[0]
            groups.setdefault(tag, []).append(
                [verb.upper(), f"`{path}`", op.get("summary", ""),
                 (op.get("description") or "").split("\n")[0]])

    ops = sum(len(v) for v in groups.values())
    body = f"""{ops} operations, OpenAPI {spec['openapi']}, version {spec['info']['version']}.

- Swagger UI — `http://localhost:8000/docs`
- ReDoc — `http://localhost:8000/redoc`
- Schema — `http://localhost:8000/openapi.json`

"""
    order = [t["name"] for t in spec.get("tags", [])]
    for tag in sorted(groups, key=lambda t: order.index(t) if t in order else 99):
        rows = sorted(groups[tag], key=lambda r: r[1])
        body += f"## {tag}\n\n{table(['Method', 'Path', 'Summary', 'Description'], rows)}\n\n"

    body += """## Error contract

Every failure returns the same envelope — never an HTML error page:

```json
{
  "error": {
    "status": 422,
    "message": "Validation failed",
    "detail": { "email": "Enter a valid email address." }
  }
}
```
"""
    write("09-api/endpoints.md", "API Reference",
          f"All {ops} endpoints grouped by tag.", body, ["api", "reference", "endpoints"])


# --------------------------------------------------------------------------
# index
# --------------------------------------------------------------------------

def build_index() -> None:
    n_cars = len(db["models"])
    n_var = sum(len(m["variants"]) for m in db["models"])
    n_faq = sum(len(m["faqs"]) for m in db["models"])

    body = f"""Knowledge base for **{DEALER['trading_as']}**, an authorised Volkswagen
dealership on Hosur Road, Bengaluru.

Every file here is **generated** from the live application sources — `data/catalog.json`,
the SQLAlchemy models and the FastAPI OpenAPI document — so the knowledge base cannot
drift from what the site actually serves.

```bash
python scrape/build_kb.py     # regenerate
```

## Contents

| Folder | What is in it |
|---|---|
| [`01-dealership/`](./01-dealership/) | Company overview, contact, hours, outlets, testimonials |
| [`02-cars/`](./02-cars/) | The {n_cars} cars, one file each, plus a lineup index |
| [`03-variants/`](./03-variants/) | All {n_var} variants with individual pricing |
| [`04-ownership/`](./04-ownership/) | Servicing, value packages, warranty, roadside, insurance |
| [`05-bookings/`](./05-bookings/) | **Test drives, rentals**, service, insurance, enquiries, applications |
| [`06-finance/`](./06-finance/) | EMI maths, lending partners, current offers |
| [`07-careers/`](./07-careers/) | Open roles and how to apply |
| [`08-faqs/`](./08-faqs/) | All {n_faq} FAQs, grouped by car |
| [`09-api/`](./09-api/) | Full endpoint reference |

## Quick facts

{table(["Field", "Value"], [
    ["Dealership", DEALER["trading_as"]],
    ["Brand", DEALER["brand"]],
    ["Location", f"{DEALER['city']}, {DEALER['state']}, {DEALER['country']}"],
    ["Phone", DEALER["contact"]["phone"]],
    ["Sales email", DEALER["contact"]["sales_email"]],
    ["Service email", DEALER["contact"]["service_email"]],
    ["Cars", n_cars],
    ["Variants", n_var],
    ["Outlets", len(db["outlets"])],
    ["Serviceable models", len(db["service_models"])],
    ["Open roles", len(db["careers"]["jobs"])],
    ["FAQs", n_faq],
])}

## Bookings at a glance

The two booking flows backed by a database table:

- **[Test drive](./05-bookings/test-drive.md)** — `POST /api/leads/test-drive` → table `test_drives`
- **[Car rental](./05-bookings/rentals.md)** — `POST /api/leads/rent` → table `rentals`

The other four (service, insurance, contact, careers) are recorded in `data/leads.json`
only. See [05-bookings/index.md](./05-bookings/index.md).

## Provenance and caveats

- Copy, specifications, features, service packages, warranty terms, job roles, outlet
  addresses, phone numbers and opening hours are taken **verbatim** from
  {META['source_url']}.
- **Pricing is indicative** ex-showroom Bengaluru. The source site publishes none.
  Variant prices are interpolated across each model's range.
- **Testimonials, statistics and offers are illustrative demo content.**
- FAQ answers are composed from scraped facts, not invented claims.

Pages scraped: {', '.join(f'`{p}`' for p in META['scraped_pages'])}
"""
    write("README.md", f"{DEALER['trading_as']} — Knowledge Base",
          "Generated Markdown knowledge base covering the dealership, cars, ownership, bookings and API.",
          body, ["index", "knowledge-base", "overview"])


# --------------------------------------------------------------------------

def main() -> None:
    if KB.exists():
        for p in sorted(KB.rglob("*.md")):
            p.unlink()
    build_dealership()
    build_cars()
    build_ownership()
    build_bookings()
    build_rest()
    build_api()
    build_index()

    total = sum(p.stat().st_size for p in written)
    print(f"{len(written)} Markdown files written to kb/  ({total / 1024:.1f} KB)\n")
    for p in sorted(written):
        print(f"  {p.relative_to(ROOT).as_posix():<44} {p.stat().st_size / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
