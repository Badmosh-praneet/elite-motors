"""Dealer profile, outlets and showroom-floor content."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Path, Query

from .. import store
from ..schemas import (
    AboutResponse, Collection, Dealer, ErrorResponse, HeroSlide, Offer, Outlet, Stat, Testimonial,
)

router = APIRouter(prefix="/api", tags=["Dealership"])


@router.get("/dealer", response_model=Dealer, summary="Get Dealer")
def get_dealer():
    """Everything about Volkswagen Elite Motors — contact, hours, social, statistics."""
    return store.DB["dealer"]


@router.get("/about", response_model=AboutResponse, summary="Get About")
def get_about():
    """The About Us copy as published, with opening hours and contact details alongside."""
    dealer = store.DB["dealer"]
    return {
        **dealer["about"],
        "dealer": dealer["legal_name"],
        "display_name": dealer["trading_as"],
        "hours": dealer["hours"],
        "contact": dealer["contact"],
    }


@router.get("/dealership-full", response_model=dict, summary="Get Full Dealership Info")
def get_dealership_full():
    """Returns the full dealership profile and all outlets in a single response."""
    return {
        "dealer": store.DB["dealer"],
        "outlets": store.outlets()
    }


@router.get("/stats", response_model=Collection[Stat], summary="Get Stats")
def get_stats():
    """Headline dealership numbers used on the site."""
    items = store.DB["dealer"]["stats"]
    return {"count": len(items), "items": items}


@router.get("/outlets", response_model=Collection[Outlet], summary="Get Outlets")
def get_outlets(
    type: str | None = Query(
        None, description="Filter by capability: `sales`, `service` or `bodyshop`.", examples=["service"]
    ),
):
    """Showrooms and service centres."""
    items = store.outlets()
    if type:
        needle = type.lower()
        items = [o for o in items if needle in [t.lower() for t in o["types"]] or needle == o["type"]]
    return {"count": len(items), "items": items}


@router.get("/outlets/{outlet_id}", response_model=Outlet,
            responses={404: {"model": ErrorResponse}}, summary="Get Outlet")
def get_outlet(outlet_id: str = Path(..., description="Outlet id.", examples=["hosur-road-showroom"])):
    """One outlet by id."""
    outlet = store.outlet_by_id(outlet_id)
    if outlet is None:
        raise HTTPException(404, {"message": f"No outlet with id '{outlet_id}'."})
    return outlet


@router.get("/offers", response_model=Collection[Offer], summary="Get Offers")
def get_offers():
    """Offers currently running at the dealership."""
    items = store.DB["offers"]
    return {"count": len(items), "items": items}


@router.get("/testimonials", response_model=Collection[Testimonial], summary="Get Testimonials")
def get_testimonials(
    min_rating: int = Query(1, ge=1, le=5, description="Only testimonials at or above this rating."),
):
    """What owners say about Elite Motors."""
    items = [t for t in store.DB["testimonials"] if t["rating"] >= min_rating]
    return {"count": len(items), "items": items}


@router.get("/hero-slides", response_model=Collection[HeroSlide], summary="Get Hero Slides")
def get_hero_slides():
    """Homepage hero slides, in display order."""
    items = store.DB["hero_slides"]
    return {"count": len(items), "items": items}
