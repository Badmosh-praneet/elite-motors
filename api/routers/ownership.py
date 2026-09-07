"""Service, warranty, roadside assistance and insurance."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Path

from .. import store
from ..schemas import (
    Collection, ErrorResponse, Insurance, RoadsideAssistance, ServiceItem,
    ServicePackage, ServicePackages, Warranty,
)

router = APIRouter(prefix="/api", tags=["Ownership"])


@router.get("/services", response_model=Collection[ServiceItem], summary="Get Services")
def get_services():
    """What the workshop offers."""
    items = store.DB["services"]
    return {"count": len(items), "items": items}


@router.get("/service-packages", response_model=ServicePackages, summary="Get Service Packages")
def get_service_packages():
    """Volkswagen Service Value Packages — 1 Year, 2 Year and Hi5."""
    return store.DB["service_packages"]


@router.get("/service-packages/{package_id}", response_model=ServicePackage,
            responses={404: {"model": ErrorResponse}}, summary="Get Service Package")
def get_service_package(package_id: str = Path(..., description="Package id.", examples=["svp-hi5"])):
    """One Service Value Package by id."""
    for p in store.DB["service_packages"]["packages"]:
        if p["id"] == package_id:
            return p
    raise HTTPException(404, {"message": f"No service package with id '{package_id}'."})


@router.get("/service-models", response_model=Collection[str], summary="Get Service Models")
def get_service_models():
    """Every Volkswagen accepted for service, including discontinued generations."""
    items = store.DB["service_models"]
    return {"count": len(items), "items": items}


@router.get("/warranty", response_model=Warranty, summary="Get Warranty")
def get_warranty():
    """Standard manufacturer warranty and the extended cover options."""
    return store.DB["warranty"]


@router.get("/roadside-assistance", response_model=RoadsideAssistance, summary="Get Roadside Assistance")
def get_roadside_assistance():
    """Volkswagen Assistance cover and what it includes."""
    return store.DB["roadside_assistance"]


@router.get("/insurance", response_model=Insurance, summary="Get Insurance")
def get_insurance():
    """Motor insurance benefits and the fields the renewal form collects."""
    return store.DB["insurance"]
