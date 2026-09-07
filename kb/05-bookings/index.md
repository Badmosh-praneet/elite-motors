---
title: Bookings and Enquiries
summary: All six submission types, their endpoints and where each is stored.
source: https://www.volkswagenbangalore.in/
dealership: Volkswagen Elite Motors
tags: [bookings, leads, api, index]
updated: 2026-08-31
---

# Bookings and Enquiries

Every way a customer can submit something to the dealership.

| Booking type | Endpoint | Stored in SQLite | Document |
|---|---|---|---|
| Test drive | `POST /api/leads/test-drive` | yes — `test_drives` | [test-drive.md](./test-drive.md) |
| Car rental | `POST /api/leads/rent` | yes — `rentals` | [rentals.md](./rentals.md) |
| Service booking | `POST /api/leads/service` | no | [service-booking.md](./service-booking.md) |
| Insurance enquiry | `POST /api/leads/insurance` | no | [insurance-enquiry.md](./insurance-enquiry.md) |
| General enquiry | `POST /api/leads/contact` | no | [contact-enquiry.md](./contact-enquiry.md) |
| Job application | `POST /api/careers/apply` | no | [job-application.md](./job-application.md) |

## Shared behaviour

Every endpoint above:

- returns **`201 Created`** on success with a `reference` the customer can quote;
- returns **`422`** with a `{field: message}` map in `error.detail` listing *every*
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
