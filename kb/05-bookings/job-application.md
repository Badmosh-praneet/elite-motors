---
title: Job Application
summary: How a career application is submitted and validated.
source: https://www.volkswagenbangalore.in/
dealership: Volkswagen Elite Motors
tags: [bookings, careers, leads, api]
updated: 2026-08-31
---

# Job Application

An application for one of the open roles.

## API

```
POST /api/careers/apply
```

### Request fields

| Field | Type | Required | Example |
|---|---|---|---|
| name | string | yes | Praneet Gogoi |
| email | string | yes | you@example.com |
| mobile | string | yes | 9876543210 |
| job_id | string | yes | sales-consultant |
| experience | integer (0–60) | no | 4 |
| cv_filename | string | no | praneet-gogoi-cv.pdf |
| message | string | no | A short note about why this role. |

`job_id` must be one of: `sales-consultant`, `front-office-executive`, `crm`, `senior-technician`. An unknown id returns `422` with the valid options
listed in `error.detail.job_id`.

## Storage

Appended to `data/leads.json` with `type: "career"`. The CV **filename** is recorded;
the file itself is not uploaded in this build.

## Follow-up

HR reviews every application within five working days.
