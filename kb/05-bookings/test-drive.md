---
title: Test Drive Booking
summary: How a test drive is requested, validated, stored and followed up.
source: https://www.volkswagenbangalore.in/
dealership: Volkswagen Elite Motors
tags: [bookings, test-drive, leads, api]
updated: 2026-08-31
---

# Test Drive Booking

A prospective customer asks to drive a specific car before buying.
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

| Field | Type | Required | Example |
|---|---|---|---|
| first_name | string | yes | Praneet |
| last_name | string | yes | Gogoi |
| email | string | yes | you@example.com |
| mobile | string | yes | 9876543210 |
| model | string | yes | Golf GTI |
| preferred_date | string (YYYY-MM-DD) | no | 2026-09-15 |
| preferred_time | string | no | Morning (10:00 – 13:00) |

### Validation

- `email` must match a standard address pattern.
- `mobile` must be 8–18 digits, optionally with `+`, spaces, hyphens or brackets.
- Every failing field is reported at once in `error.detail`.

### Example request

```bash
curl -X POST http://localhost:8000/api/leads/test-drive \
  -H 'Content-Type: application/json' \
  -d '{
    "first_name": "Praneet",
    "last_name": "Gogoi",
    "email": "you@example.com",
    "mobile": "9876543210",
    "model": "Golf GTI",
    "preferred_date": "2026-09-15",
    "preferred_time": "Morning (10:00 – 13:00)"
  }'
```

### Success — `201 Created`

```json
{
  "message": "Your request submitted successfully.",
  "reference": "test-drive-a1b2c3d4e5",
  "next_step": "A Sales Consultant from Elite Motors will call you within one working day.",
  "lead": { "id": "test-drive-a1b2c3d4e5", "type": "test-drive", "status": "new", "data": { } }
}
```

### Validation failure — `422`

```json
{
  "error": {
    "status": 422,
    "message": "Validation failed",
    "detail": { "email": "Enter a valid email address." }
  }
}
```

## Storage

Persisted to SQLite via SQLAlchemy (`volkswagen.db`). The request is also appended to `data/leads.json` with `type: "test-drive"`,
which is what `GET /api/leads` reads.

### Table `test_drives`

| Column | Type | Nullable | PK | Default |
|---|---|---|---|---|
| id | INTEGER | no | yes |  |
| first_name | VARCHAR | no |  |  |
| last_name | VARCHAR | no |  |  |
| email | VARCHAR | no |  |  |
| mobile | VARCHAR | no |  |  |
| model | VARCHAR | no |  |  |
| preferred_date | VARCHAR | yes |  |  |
| preferred_time | VARCHAR | yes |  |  |
| created_at | DATETIME | yes |  | now() |
| status | VARCHAR | yes |  | PENDING |

## Managing test drives

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/leads/test-drive` | Every test drive row from the database |
| `PATCH` | `/api/leads/test-drive/{id}` | Set a booking's `status` |

```bash
curl -X PATCH http://localhost:8000/api/leads/test-drive/1 \
  -H 'Content-Type: application/json' -d '{"status":"CONFIRMED"}'
```

New bookings are created with status `PENDING`. Both endpoints are
**unauthenticated** — anyone who can reach the API can read every customer's
contact details and change any booking.

## Follow-up

A Sales Consultant contacts the customer within one working day to confirm the slot.
Home or office pick-up is available on request.
