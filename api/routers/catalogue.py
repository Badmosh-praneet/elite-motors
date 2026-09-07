"""Cars, variants, specifications, FAQs and comparison."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Path, Query

from .. import store
from ..schemas import (
    CarDetail, CarSummary, Collection, ColourOption, Comparison, ComparisonRow,
    ErrorResponse, FAQ, Lineup, LineupGroup, Page, Specs, Variant,
)

router = APIRouter(prefix="/api", tags=["Catalogue"])

NOT_FOUND = {404: {"model": ErrorResponse, "description": "No such car."}}

MODEL_ID = Path(
    ...,
    description="Car slug, e.g. `golf-gti`, `taigun-sport`, `virtus-chrome`.",
    examples=["golf-gti"],
)


def _car_or_404(model_id: str) -> dict:
    car = store.model_by_slug(model_id)
    if car is None:
        known = ", ".join(m["slug"] for m in store.models())
        raise HTTPException(404, {"message": f"No car with id '{model_id}'.",
                                  "detail": {"known_ids": known}})
    return car


@router.get("/cars", response_model=Page[CarSummary], summary="Get Cars")
def get_cars(
    q: str | None = Query(None, description="Free-text match on name, family, tagline and description.", examples=["gti"]),
    body_type: str | None = Query(None, description="Filter by body style, e.g. `SUV`, `Sedan`, `Hot Hatch`."),
    family: str | None = Query(None, description="Filter by model family, e.g. `Taigun`."),
    segment: str | None = Query(None, description="`core`, `premium`, `performance` or `flagship`."),
    fuel: str | None = Query(None, description="Substring match on fuel type."),
    seats: int | None = Query(None, ge=2, le=9, description="Exact seat count."),
    price_min: int | None = Query(None, ge=0, description="Only cars whose range reaches this price."),
    price_max: int | None = Query(None, ge=0, description="Only cars starting at or below this price."),
    sort: str = Query("default", pattern="^(default|price_asc|price_desc|name)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Every car Elite Motors sells, with filtering, sorting and pagination."""
    items = list(store.models())

    if q:
        needle = q.lower()
        items = [m for m in items if needle in " ".join([
            m["name"], m["family"], m["body_type"], m["tagline"], m["description"],
            " ".join(m["highlights"]),
        ]).lower()]

    for value, key in ((body_type, "body_type"), (family, "family"), (segment, "segment")):
        if value:
            items = [m for m in items if m[key].lower() == value.lower()]

    if fuel:
        items = [m for m in items if fuel.lower() in m["specs"]["fuel"].lower()]
    if seats is not None:
        items = [m for m in items if m["seats"] == seats]
    if price_min is not None:
        items = [m for m in items if m["price"]["max"] >= price_min]
    if price_max is not None:
        items = [m for m in items if m["price"]["min"] <= price_max]

    if sort == "price_asc":
        items.sort(key=lambda m: m["price"]["min"])
    elif sort == "price_desc":
        items.sort(key=lambda m: m["price"]["min"], reverse=True)
    elif sort == "name":
        items.sort(key=lambda m: m["name"])

    total = len(items)
    page = [store.model_summary(m) for m in items[offset:offset + limit]]
    return {"count": len(page), "total": total, "offset": offset, "limit": limit, "items": page}


@router.get("/cars/{model_id}", response_model=CarDetail, responses=NOT_FOUND, summary="Get Car Details")
def get_car_details(model_id: str = MODEL_ID):
    """One car in full — specs, features, colours, gallery, variants and FAQs."""
    car = _car_or_404(model_id)
    return {**store.model_summary(car), **car}


@router.get("/lineup", response_model=Lineup, summary="Get Lineup")
def get_lineup():
    """The whole range grouped by body style — the shape the showroom uses."""
    groups: dict[str, list[dict]] = {}
    for m in store.models():
        groups.setdefault(m["body_type"], []).append(store.model_summary(m))
    return {
        "total_cars": len(store.models()),
        "total_variants": len(store.all_variants()),
        "groups": [
            LineupGroup(body_type=body, count=len(cars), cars=cars)
            for body, cars in sorted(groups.items())
        ],
    }


@router.get("/models/{model_id}", response_model=CarDetail, responses=NOT_FOUND, summary="Get Model")
def get_model(model_id: str = MODEL_ID):
    """Alias of `/api/cars/{model_id}`, kept for callers that think in models."""
    car = _car_or_404(model_id)
    return {**store.model_summary(car), **car}


@router.get("/models/{model_id}/faqs", response_model=Collection[FAQ], responses=NOT_FOUND,
            summary="Get Model Faqs")
def get_model_faqs(model_id: str = MODEL_ID):
    """Frequently asked questions for one car, answered from dealership data."""
    car = _car_or_404(model_id)
    return {"count": len(car["faqs"]), "items": car["faqs"]}


@router.get("/models/{model_id}/specs", response_model=Specs, responses=NOT_FOUND, summary="Get Model Specs")
def get_model_specs(model_id: str = MODEL_ID):
    """The specification block on its own."""
    return _car_or_404(model_id)["specs"]


@router.get("/models/{model_id}/colours", response_model=Collection[ColourOption], responses=NOT_FOUND,
            summary="Get Model Colours")
def get_model_colours(model_id: str = MODEL_ID):
    """Paint options with hex values, ready to render as swatches."""
    car = _car_or_404(model_id)
    return {"count": len(car["colors"]), "items": car["colors"]}


@router.get("/models/{model_id}/gallery", response_model=Collection[str], responses=NOT_FOUND,
            summary="Get Model Gallery")
def get_model_gallery(model_id: str = MODEL_ID):
    """Gallery image paths for one car."""
    car = _car_or_404(model_id)
    return {"count": len(car["gallery"]), "items": car["gallery"]}


@router.get("/models/{model_id}/variants", response_model=Collection[Variant], responses=NOT_FOUND,
            summary="Get Model Variants")
def get_model_variants(model_id: str = MODEL_ID):
    """Every variant of one car, cheapest first."""
    car = _car_or_404(model_id)
    items = sorted(car["variants"], key=lambda v: v["price"])
    return {"count": len(items), "items": items}


@router.get("/variants", response_model=Page[Variant], summary="Get Variants")
def get_variants(
    model_id: str | None = Query(None, description="Restrict to one car slug.", examples=["taigun-sport"]),
    trim: str | None = Query(None, description="Filter by trim, e.g. `GT Line`."),
    transmission: str | None = Query(None, description="Substring match, e.g. `DSG`, `MT`."),
    price_max: int | None = Query(None, ge=0, description="Only variants at or below this price."),
    sort: str = Query("price_asc", pattern="^(price_asc|price_desc|name)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Every variant across the whole range, with its own price."""
    items = store.all_variants()

    if model_id:
        items = [v for v in items if v["model_slug"] == model_id.lower()]
    if trim:
        items = [v for v in items if v["trim"].lower() == trim.lower()]
    if transmission:
        items = [v for v in items if transmission.lower() in v["transmission"].lower()]
    if price_max is not None:
        items = [v for v in items if v["price"] <= price_max]

    if sort == "price_asc":
        items = sorted(items, key=lambda v: v["price"])
    elif sort == "price_desc":
        items = sorted(items, key=lambda v: v["price"], reverse=True)
    else:
        items = sorted(items, key=lambda v: v["name"])

    total = len(items)
    return {"count": len(items[offset:offset + limit]), "total": total,
            "offset": offset, "limit": limit, "items": items[offset:offset + limit]}


@router.get("/variants/{variant_id}", response_model=Variant,
            responses={404: {"model": ErrorResponse, "description": "No such variant."}},
            summary="Get Variant")
def get_variant(variant_id: str = Path(..., description="Variant id from `/api/variants`.",
                                       examples=["taigun-gt-line-1-0l-tsi-6-speed-mt"])):
    """One variant by id."""
    variant = store.variant_by_id(variant_id)
    if variant is None:
        raise HTTPException(404, {"message": f"No variant with id '{variant_id}'."})
    return variant


@router.get("/compare", response_model=Comparison,
            responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
            summary="Compare")
def compare(
    ids: str = Query(..., description="Two to four car slugs, comma separated.",
                     examples=["golf-gti,tiguan-r-line,taigun-sport"]),
):
    """Compare cars attribute by attribute, ready to drop into a table."""
    slugs = [s.strip().lower() for s in ids.split(",") if s.strip()]
    if not 2 <= len(slugs) <= 4:
        raise HTTPException(422, {"message": "Compare between two and four cars.",
                                  "detail": {"ids": f"Received {len(slugs)}."}})

    cars = [_car_or_404(s) for s in slugs]

    def spec(car: dict, key: str) -> str:
        return str(car["specs"].get(key) or "—")

    rows = [
        ComparisonRow(attribute="Body", values={c["slug"]: c["body_type"] for c in cars}),
        ComparisonRow(attribute="Engine", values={c["slug"]: spec(c, "engine") for c in cars}),
        ComparisonRow(attribute="Power", values={c["slug"]: spec(c, "power") for c in cars}),
        ComparisonRow(attribute="Torque", values={c["slug"]: spec(c, "torque") for c in cars}),
        ComparisonRow(attribute="Transmission", values={c["slug"]: spec(c, "transmission") for c in cars}),
        ComparisonRow(attribute="Drivetrain", values={c["slug"]: spec(c, "drivetrain") for c in cars}),
        ComparisonRow(attribute="0-100 km/h", values={c["slug"]: spec(c, "zero_to_hundred") for c in cars}),
        ComparisonRow(attribute="Boot", values={c["slug"]: spec(c, "boot") for c in cars}),
        ComparisonRow(attribute="Seats", values={c["slug"]: str(c["seats"]) for c in cars}),
        ComparisonRow(attribute="Variants", values={c["slug"]: str(len(c["variants"])) for c in cars}),
        ComparisonRow(attribute="Starting price",
                      values={c["slug"]: f"INR {c['price']['min']:,}" for c in cars}),
    ]
    return {"cars": [store.model_summary(c) for c in cars], "rows": rows}
