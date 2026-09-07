---
title: Car Rental Booking
summary: How a rental is requested, validated and stored, and what is not yet modelled.
source: https://www.volkswagenbangalore.in/
dealership: Volkswagen Elite Motors
tags: [bookings, rentals, leads, api]
updated: 2026-08-31
---

# Car Rental Booking

A customer hires a Volkswagen for a fixed period rather than buying one.
The team confirms availability and arranges the handover.

## API

```
POST /api/leads/rent
Content-Type: application/json
```

### Request fields

| Field | Type | Required | Example |
|---|---|---|---|
| first_name | string | yes | Praneet |
| last_name | string | yes | Gogoi |
| email | string | yes | you@example.com |
| mobile | string | yes | 9876543210 |
| model | string | yes | Volkswagen Virtus |
| start_date | string (YYYY-MM-DD) | yes | 2026-09-10 |
| end_date | string (YYYY-MM-DD) | yes | 2026-09-15 |

### Validation

- `email` and `mobile` use the same patterns as every other lead endpoint.
- `start_date` and `end_date` are **required** — unlike a test drive, where the date is optional.
- **Double bookings are rejected.** Before writing, the endpoint looks for an
  existing rental of the same `model` whose dates overlap the requested window
  and whose status is `PENDING` or `CONFIRMED`. A clash returns `409 Conflict`:

  ```json
  {"error": {"status": 409, "message": "The Golf GTI is already booked for these dates."}}
  ```
- Dates are compared as strings, so they must be `YYYY-MM-DD` to order correctly.
  The API does not check that `end_date` falls after `start_date`.

### Example request

```bash
curl -X POST http://localhost:8000/api/leads/rent \
  -H 'Content-Type: application/json' \
  -d '{
    "first_name": "Praneet",
    "last_name": "Gogoi",
    "email": "you@example.com",
    "mobile": "9876543210",
    "model": "Taigun Sport",
    "start_date": "2026-09-10",
    "end_date": "2026-09-14"
  }'
```

### Success — `201 Created`

```json
{
  "message": "Your rental request submitted successfully.",
  "reference": "rent-e50281919d",
  "next_step": "Our team will confirm your booking and arrange the handover.",
  "lead": { "id": "rent-e50281919d", "type": "rent", "status": "new", "data": { } }
}
```

## Storage

Persisted to SQLite via SQLAlchemy (`volkswagen.db`). The request is also appended to `data/leads.json` with `type: "rent"`.

### Table `rentals`

| Column | Type | Nullable | PK | Default |
|---|---|---|---|---|
| id | INTEGER | no | yes |  |
| first_name | VARCHAR | no |  |  |
| last_name | VARCHAR | no |  |  |
| email | VARCHAR | no |  |  |
| mobile | VARCHAR | no |  |  |
| model | VARCHAR | no |  |  |
| start_date | VARCHAR | no |  |  |
| end_date | VARCHAR | no |  |  |
| created_at | DATETIME | yes |  | now() |
| status | VARCHAR | yes |  | PENDING |

## Managing rentals

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/leads/rent` | Every rental row from the database |
| `PATCH` | `/api/leads/rent/{id}` | Set a rental's `status` |

```bash
curl -X PATCH http://localhost:8000/api/leads/rent/1   -H 'Content-Type: application/json' -d '{"status":"CONFIRMED"}'
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
