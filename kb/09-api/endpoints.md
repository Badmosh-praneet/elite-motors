---
title: API Reference
summary: All 47 endpoints grouped by tag.
source: https://www.volkswagenbangalore.in/
dealership: Volkswagen Elite Motors
tags: [api, reference, endpoints]
updated: 2026-08-31
---

# API Reference

47 operations, OpenAPI 3.1.0, version 2.0.0.

- Swagger UI — `http://localhost:8000/docs`
- ReDoc — `http://localhost:8000/redoc`
- Schema — `http://localhost:8000/openapi.json`

## Catalogue

| Method | Path | Summary | Description |
|---|---|---|---|
| GET | `/api/cars/{model_id}` | Get Car Details | One car in full — specs, features, colours, gallery, variants and FAQs. |
| GET | `/api/cars` | Get Cars | Every car Elite Motors sells, with filtering, sorting and pagination. |
| GET | `/api/compare` | Compare | Compare cars attribute by attribute, ready to drop into a table. |
| GET | `/api/lineup` | Get Lineup | The whole range grouped by body style — the shape the showroom uses. |
| GET | `/api/models/{model_id}/colours` | Get Model Colours | Paint options with hex values, ready to render as swatches. |
| GET | `/api/models/{model_id}/faqs` | Get Model Faqs | Frequently asked questions for one car, answered from dealership data. |
| GET | `/api/models/{model_id}/gallery` | Get Model Gallery | Gallery image paths for one car. |
| GET | `/api/models/{model_id}/specs` | Get Model Specs | The specification block on its own. |
| GET | `/api/models/{model_id}/variants` | Get Model Variants | Every variant of one car, cheapest first. |
| GET | `/api/models/{model_id}` | Get Model | Alias of `/api/cars/{model_id}`, kept for callers that think in models. |
| GET | `/api/variants/{variant_id}` | Get Variant | One variant by id. |
| GET | `/api/variants` | Get Variants | Every variant across the whole range, with its own price. |

## Dealership

| Method | Path | Summary | Description |
|---|---|---|---|
| GET | `/api/about` | Get About | The About Us copy as published, with opening hours and contact details alongside. |
| GET | `/api/dealer` | Get Dealer | Everything about Volkswagen Elite Motors — contact, hours, social, statistics. |
| GET | `/api/hero-slides` | Get Hero Slides | Homepage hero slides, in display order. |
| GET | `/api/offers` | Get Offers | Offers currently running at the dealership. |
| GET | `/api/outlets/{outlet_id}` | Get Outlet | One outlet by id. |
| GET | `/api/outlets` | Get Outlets | Showrooms and service centres. |
| GET | `/api/stats` | Get Stats | Headline dealership numbers used on the site. |
| GET | `/api/testimonials` | Get Testimonials | What owners say about Elite Motors. |

## Ownership

| Method | Path | Summary | Description |
|---|---|---|---|
| GET | `/api/insurance` | Get Insurance | Motor insurance benefits and the fields the renewal form collects. |
| GET | `/api/roadside-assistance` | Get Roadside Assistance | Volkswagen Assistance cover and what it includes. |
| GET | `/api/service-models` | Get Service Models | Every Volkswagen accepted for service, including discontinued generations. |
| GET | `/api/service-packages/{package_id}` | Get Service Package | One Service Value Package by id. |
| GET | `/api/service-packages` | Get Service Packages | Volkswagen Service Value Packages — 1 Year, 2 Year and Hi5. |
| GET | `/api/services` | Get Services | What the workshop offers. |
| GET | `/api/warranty` | Get Warranty | Standard manufacturer warranty and the extended cover options. |

## Finance

| Method | Path | Summary | Description |
|---|---|---|---|
| POST | `/api/finance/amortisation` | Get Amortisation Schedule | The full repayment schedule, instalment by instalment. |
| POST | `/api/finance/emi` | Calculate Emi | Reducing-balance EMI, with the first year of the repayment schedule. |
| GET | `/api/finance/quote` | Get Finance Quote | An EMI quote via query string — handy for linking straight to a figure. |
| GET | `/api/finance` | Get Finance Config | Default figures, slider limits and the lending partners we work with. |

## Careers

| Method | Path | Summary | Description |
|---|---|---|---|
| GET | `/api/careers/jobs/{job_id}` | Get Job | One role by id. |
| GET | `/api/careers/jobs` | Get Jobs | Open roles, optionally filtered by department. |
| GET | `/api/careers` | Get Careers | Careers overview and every open role. |

## Enquiries

| Method | Path | Summary | Description |
|---|---|---|---|
| POST | `/api/careers/apply` | Apply For Job | Apply for an open role. `job_id` must match `/api/careers/jobs`. |
| POST | `/api/leads/contact` | Send Enquiry | A general enquiry to the dealership. |
| POST | `/api/leads/insurance` | Request Insurance Quote | Ask for a comparative motor insurance renewal quote. |
| PATCH | `/api/leads/rent/{id}` | Update Rental Status (Admin) | Update status of a rental. |
| GET | `/api/leads/rent` | Get Rentals (Admin) | Get all rentals from the database. |
| POST | `/api/leads/rent` | Book Car Rental | Request a car rental. |
| POST | `/api/leads/service` | Book Service | Book a workshop slot for any Volkswagen, including older generations. |
| PATCH | `/api/leads/test-drive/{id}` | Update Test Drive Status (Admin) | Update status of a test drive. |
| GET | `/api/leads/test-drive` | Get Test Drives (Admin) | Get all test drives from the database. |
| POST | `/api/leads/test-drive` | Book Test Drive | Request a test drive. A Sales Consultant confirms the slot. |
| GET | `/api/leads` | Get Leads | The demo inbox — every lead submitted, newest first. |

## Search & System

| Method | Path | Summary | Description |
|---|---|---|---|
| GET | `/api/health` | Health | Liveness probe and a count of what is loaded. |
| GET | `/api/search` | Search | Search cars, variants, outlets, services, packages, jobs and FAQs in one call. |

## Error contract

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
