---
title: General Enquiry
summary: How a general contact enquiry is submitted.
source: https://www.volkswagenbangalore.in/
dealership: Volkswagen Elite Motors
tags: [bookings, contact, leads, api]
updated: 2026-08-31
---

# General Enquiry

A general enquiry to the dealership.

## API

```
POST /api/leads/contact
```

### Request fields

| Field | Type | Required | Example |
|---|---|---|---|
| name | string | yes | Praneet Gogoi |
| email | string | yes | you@example.com |
| mobile | string | yes | 9876543210 |
| message | string | yes | What is the waiting period on the Tayron R-Line? |
| subject | string | no | General enquiry |

## Storage

Appended to `data/leads.json` with `type: "contact"`.
