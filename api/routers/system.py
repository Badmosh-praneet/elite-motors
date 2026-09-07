"""Full-text search across the knowledge base, plus service health."""

from __future__ import annotations

import time
from datetime import datetime, timezone

from fastapi import APIRouter, Query

from .. import store
from ..schemas import Health, SearchResponse

router = APIRouter(prefix="/api", tags=["Search & System"])

STARTED_AT = time.time()


@router.get("/search", response_model=SearchResponse, summary="Search")
def search(
    q: str = Query(..., min_length=1, description="What to look for.", examples=["gti"]),
    limit: int = Query(25, ge=1, le=100),
):
    """Search cars, variants, outlets, services, packages, jobs and FAQs in one call."""
    needle = q.strip().lower()
    hits: list[dict] = []

    for m in store.models():
        blob = f"{m['name']} {m['family']} {m['body_type']} {m['tagline']} {m['description']}".lower()
        if needle in blob:
            hits.append({"type": "car", "id": m["slug"], "title": m["name"],
                         "subtitle": m["tagline"], "url": f"/model.html?slug={m['slug']}",
                         "image": m["hero_image"]})

    for v in store.all_variants():
        if needle in f"{v['name']} {v['trim']} {v['engine']} {v['transmission']}".lower():
            hits.append({"type": "variant", "id": v["id"], "title": v["name"],
                         "subtitle": f"{v['power']} · {v['transmission']} · INR {v['price']:,}",
                         "url": f"/model.html?slug={v['model_slug']}", "image": None})

    for o in store.outlets():
        if needle in f"{o['name']} {o['full_address']} {o['type']}".lower():
            hits.append({"type": "outlet", "id": o["id"], "title": o["name"],
                         "subtitle": o["full_address"], "url": "/outlets.html", "image": None})

    for s in store.DB["services"]:
        if needle in f"{s['name']} {s['description']}".lower():
            hits.append({"type": "service", "id": s["id"], "title": s["name"],
                         "subtitle": s["description"], "url": "/service.html", "image": None})

    for p in store.DB["service_packages"]["packages"]:
        if needle in f"{p['name']} {' '.join(p['benefits'])}".lower():
            hits.append({"type": "package", "id": p["id"], "title": p["name"],
                         "subtitle": p["duration"], "url": "/service.html#packages",
                         "image": p.get("image")})

    for j in store.jobs():
        if needle in f"{j['title']} {j['department']} {j['description']}".lower():
            hits.append({"type": "job", "id": j["id"], "title": j["title"],
                         "subtitle": f"{j['department']} · {j['location']}",
                         "url": "/careers.html", "image": None})

    for m in store.models():
        for i, f in enumerate(m["faqs"]):
            if needle in f"{f['question']} {f['answer']}".lower():
                hits.append({"type": "faq", "id": f"{m['slug']}-faq-{i}", "title": f["question"],
                             "subtitle": f["answer"][:140],
                             "url": f"/model.html?slug={m['slug']}", "image": None})

    return {"query": needle, "count": len(hits[:limit]), "results": hits[:limit]}


@router.get("/health", response_model=Health, summary="Health")
def health():
    """Liveness probe and a count of what is loaded."""
    return {
        "status": "ok",
        "service": "vw-elite-motors-api",
        "version": "2.0.0",
        "uptime_seconds": round(time.time() - STARTED_AT, 1),
        "cars_loaded": len(store.models()),
        "variants_loaded": len(store.all_variants()),
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
