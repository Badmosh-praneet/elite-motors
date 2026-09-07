---
title: Insurance Enquiry
summary: How an insurance renewal quote is requested.
source: https://www.volkswagenbangalore.in/
dealership: Volkswagen Elite Motors
tags: [bookings, insurance, leads, api]
updated: 2026-08-31
---

# Insurance Enquiry

A customer asks for a comparative motor insurance renewal quote.

## API

```
POST /api/leads/insurance
```

### Request fields

| Field | Type | Required | Example |
|---|---|---|---|
| full_name | string | yes | Praneet Gogoi |
| mobile | string | yes | 9876543210 |
| email | string | yes | you@example.com |
| registration_number | string | yes | KA 01 AB 1234 |
| model | string | no | Volkswagen Virtus |
| registration_year | string | no | 2023 |
| registration_month | string | no | March |
| insurance_company | string | no | HDFC ERGO |
| policy_number | string | no | P/123456789 |
| insurance_expiry | string (YYYY-MM-DD) | no | 2026-11-30 |

## Storage

Appended to `data/leads.json` with `type: "insurance"`.

## Follow-up

A comparative quote is sent within 24 hours.
