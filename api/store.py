"""Catalogue loading, lookups and lead persistence."""

from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
WEB_DIR = ROOT / "web"
CATALOG_FILE = DATA_DIR / "catalog.json"
LEADS_FILE = DATA_DIR / "leads.json"

_lock = threading.Lock()


def _load() -> dict[str, Any]:
    with CATALOG_FILE.open(encoding="utf-8") as fh:
        return json.load(fh)


DB: dict[str, Any] = _load()


def reload_catalog() -> dict[str, Any]:
    """Re-read catalog.json from disk (used by the admin reload endpoint)."""
    global DB
    with _lock:
        DB = _load()
    return DB


# --------------------------------------------------------------------------
# lookups
# --------------------------------------------------------------------------

def models() -> list[dict]:
    return DB["models"]


def model_by_slug(slug: str) -> dict | None:
    slug = slug.lower()
    for m in DB["models"]:
        if m["slug"] == slug:
            return m
    return None


def all_variants() -> list[dict]:
    return [v for m in DB["models"] for v in m["variants"]]


def variant_by_id(variant_id: str) -> dict | None:
    variant_id = variant_id.lower()
    for v in all_variants():
        if v["id"] == variant_id:
            return v
    return None


def outlets() -> list[dict]:
    return DB["outlets"]


def outlet_by_id(outlet_id: str) -> dict | None:
    for o in DB["outlets"]:
        if o["id"] == outlet_id:
            return o
    return None


def jobs() -> list[dict]:
    return DB["careers"]["jobs"]


def job_by_id(job_id: str) -> dict | None:
    for j in jobs():
        if j["id"] == job_id:
            return j
    return None


def model_summary(m: dict) -> dict:
    """Trim a full model record down to the list representation."""
    return {
        "slug": m["slug"],
        "name": m["name"],
        "family": m["family"],
        "variant_label": m["variant_label"],
        "body_type": m["body_type"],
        "segment": m["segment"],
        "seats": m["seats"],
        "status": m["status"],
        "badge": m["badge"],
        "tagline": m["tagline"],
        "price": m["price"],
        "specs": m["specs"],
        "hero_image": m["hero_image"],
        "variant_count": len(m["variants"]),
    }


# --------------------------------------------------------------------------
# leads
# --------------------------------------------------------------------------

def read_leads() -> list[dict]:
    if not LEADS_FILE.exists():
        return []
    try:
        with LEADS_FILE.open(encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, list) else []
    except (ValueError, OSError):
        return []


def append_lead(kind: str, payload: dict) -> dict:
    """Append a lead atomically and return the stored record."""
    record = {
        "id": f"{kind}-{uuid.uuid4().hex[:10]}",
        "type": kind,
        "received_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "new",
        "data": payload,
    }
    with _lock:
        leads = read_leads()
        leads.append(record)
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        tmp = LEADS_FILE.with_suffix(".json.tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(leads, fh, indent=2, ensure_ascii=False)
        tmp.replace(LEADS_FILE)
    return record


# --------------------------------------------------------------------------
# finance maths
# --------------------------------------------------------------------------

def emi(principal: float, annual_rate: float, months: int) -> dict:
    """Standard reducing-balance EMI."""
    r = annual_rate / 12.0 / 100.0
    monthly = principal / months if r == 0 else (
        principal * r * (1 + r) ** months / ((1 + r) ** months - 1)
    )
    total = monthly * months
    return {
        "principal": round(principal, 2),
        "annual_rate": annual_rate,
        "tenure_months": months,
        "monthly_emi": round(monthly, 2),
        "total_payable": round(total, 2),
        "total_interest": round(total - principal, 2),
        "currency": "INR",
    }


def amortisation(principal: float, annual_rate: float, months: int, limit: int = 12) -> list[dict]:
    r = annual_rate / 12.0 / 100.0
    monthly = emi(principal, annual_rate, months)["monthly_emi"]
    balance = principal
    rows: list[dict] = []
    for period in range(1, months + 1):
        interest = balance * r
        principal_part = monthly - interest
        balance = max(0.0, balance - principal_part)
        if period <= limit:
            rows.append({
                "month": period,
                "emi": round(monthly, 2),
                "interest": round(interest, 2),
                "principal": round(principal_part, 2),
                "balance": round(balance, 2),
            })
    return rows
