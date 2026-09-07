---
title: Finance and EMI
summary: How EMI is calculated, accepted ranges and lending partners.
source: https://www.volkswagenbangalore.in/
dealership: Volkswagen Elite Motors
tags: [finance, emi, loan, api]
updated: 2026-08-31
---

# Finance and EMI

Model your EMI before you walk in. Adjust the loan amount, tenure and rate to see exactly what your Volkswagen costs each month.

## Defaults

| Field | Value |
|---|---|
| Principal | ₹15,00,000 |
| Rate | 9.25% p.a. |
| Tenure | 60 months |
| Down payment | 20% |

## Accepted ranges

| Field | Minimum | Maximum |
|---|---|---|
| Principal | ₹3,00,000 | ₹80,00,000 |
| Rate | 6% | 18% |
| Tenure | 12 months | 84 months |

## Lending partners

- HDFC Bank
- ICICI Bank
- Axis Bank
- State Bank of India
- Kotak Mahindra Prime
- Volkswagen Finance

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
curl -X POST http://localhost:8000/api/finance/emi \
  -H 'Content-Type: application/json' \
  -d '{"principal":1500000,"down_payment":300000,"rate":9.25,"tenure_months":60}'
```

- `GET /api/finance` — configuration and partners
- `GET /api/finance/quote` — quote via query string, optionally priced against `model_id`
- `POST /api/finance/emi` — EMI plus the first 12 instalments
- `POST /api/finance/amortisation` — full repayment schedule

> Indicative only. Not an offer of credit. Final rates depend on the customer's
> credit profile and the lending partner.
