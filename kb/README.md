---
title: Volkswagen Elite Motors — Knowledge Base
summary: Generated Markdown knowledge base covering the dealership, cars, ownership, bookings and API.
source: https://www.volkswagenbangalore.in/
dealership: Volkswagen Elite Motors
tags: [index, knowledge-base, overview]
updated: 2026-08-31
---

# Volkswagen Elite Motors — Knowledge Base

Knowledge base for **Volkswagen Elite Motors**, an authorised Volkswagen
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
| [`02-cars/`](./02-cars/) | The 7 cars, one file each, plus a lineup index |
| [`03-variants/`](./03-variants/) | All 19 variants with individual pricing |
| [`04-ownership/`](./04-ownership/) | Servicing, value packages, warranty, roadside, insurance |
| [`05-bookings/`](./05-bookings/) | **Test drives, rentals**, service, insurance, enquiries, applications |
| [`06-finance/`](./06-finance/) | EMI maths, lending partners, current offers |
| [`07-careers/`](./07-careers/) | Open roles and how to apply |
| [`08-faqs/`](./08-faqs/) | All 52 FAQs, grouped by car |
| [`09-api/`](./09-api/) | Full endpoint reference |

## Quick facts

| Field | Value |
|---|---|
| Dealership | Volkswagen Elite Motors |
| Brand | Volkswagen |
| Location | Bengaluru, Karnataka, India |
| Phone | 080 4013 8004 |
| Sales email | crm@vw-elitemotors.co.in |
| Service email | crhead@vw-elitemotors.co.in |
| Cars | 7 |
| Variants | 19 |
| Outlets | 2 |
| Serviceable models | 39 |
| Open roles | 4 |
| FAQs | 52 |

## Bookings at a glance

The two booking flows backed by a database table:

- **[Test drive](./05-bookings/test-drive.md)** — `POST /api/leads/test-drive` → table `test_drives`
- **[Car rental](./05-bookings/rentals.md)** — `POST /api/leads/rent` → table `rentals`

The other four (service, insurance, contact, careers) are recorded in `data/leads.json`
only. See [05-bookings/index.md](./05-bookings/index.md).

## Provenance and caveats

- Copy, specifications, features, service packages, warranty terms, job roles, outlet
  addresses, phone numbers and opening hours are taken **verbatim** from
  https://www.volkswagenbangalore.in/.
- **Pricing is indicative** ex-showroom Bengaluru. The source site publishes none.
  Variant prices are interpolated across each model's range.
- **Testimonials, statistics and offers are illustrative demo content.**
- FAQ answers are composed from scraped facts, not invented claims.

Pages scraped: `/`, `/about-us`, `/models`, `/outlets`, `/service`, `/insurance`, `/careers`, `/finance-calculator`, `/service-value-package`, `/roadside-assistance`, `/extended-warranty`, `/booking`, `/contact-us`, `/tayron-r-line`, `/golf-gti`, `/tiguan-r-line`, `/virtus-sport`, `/virtus-chrome`, `/taigun-sport`, `/taigun-chrome`
