---
title: Service Booking
summary: How a workshop booking is requested and stored.
source: https://www.volkswagenbangalore.in/
dealership: Volkswagen Elite Motors
tags: [bookings, service, leads, api]
updated: 2026-08-31
---

# Service Booking

A customer books their car into the workshop.

## Where it is offered

The **Service** page (`/service.html#book`).

## API

```
POST /api/leads/service
```

### Request fields

| Field | Type | Required | Example |
|---|---|---|---|
| name | string | yes | Praneet Gogoi |
| mobile | string | yes | 9876543210 |
| model | string | yes | Volkswagen Taigun |
| service_centre | string | yes | Volkswagen Elite Motors Service — Hosur Road |
| email | string | no | you@example.com |
| registration_number | string | no | KA 01 AB 1234 |
| preferred_date | string (YYYY-MM-DD) | no | 2026-09-12 |
| message | string | no | Rattle from the rear on rough roads. |

`model` accepts any entry from [serviceable-models.md](../04-ownership/serviceable-models.md),
including discontinued generations. `service_centre` should match an outlet
from [outlets.md](../01-dealership/outlets.md).

## Storage

Appended to `data/leads.json` with `type: "service"`. **Not** written to SQLite —
only test drives and rentals have database tables so far.

## Follow-up

A Service Advisor confirms the slot and the pick-up window.
