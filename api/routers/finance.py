"""EMI maths and lending configuration."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from .. import store
from ..schemas import AmortRow, Collection, EmiRequest, EmiResponse, ErrorResponse, FinanceConfig

router = APIRouter(prefix="/api/finance", tags=["Finance"])


@router.get("", response_model=FinanceConfig, summary="Get Finance Config")
def get_finance_config():
    """Default figures, slider limits and the lending partners we work with."""
    return store.DB["finance"]


@router.get("/quote", response_model=EmiResponse,
            responses={404: {"model": ErrorResponse}}, summary="Get Finance Quote")
def get_finance_quote(
    principal: float | None = Query(None, gt=0, description="Vehicle price. Defaults to the car's starting price."),
    rate: float = Query(9.25, ge=0, le=36, description="Annual interest rate, percent."),
    tenure_months: int = Query(60, ge=1, le=120, description="Loan tenure in months."),
    down_payment: float = Query(0, ge=0, description="Amount paid upfront."),
    model_id: str | None = Query(None, description="Price the quote against a car slug.", examples=["taigun-sport"]),
):
    """An EMI quote via query string — handy for linking straight to a figure."""
    car_ref = None
    if model_id:
        car = store.model_by_slug(model_id)
        if car is None:
            raise HTTPException(404, {"message": f"No car with id '{model_id}'."})
        car_ref = {"slug": car["slug"], "name": car["name"], "price": car["price"]}
        if principal is None:
            principal = float(car["price"]["min"])

    if principal is None:
        principal = float(store.DB["finance"]["defaults"]["principal"])

    if down_payment >= principal:
        raise HTTPException(422, {"message": "Validation failed",
                                  "detail": {"down_payment": "Must be less than the vehicle price."}})

    financed = principal - down_payment
    result = store.emi(financed, rate, tenure_months)
    result["on_road_price"] = round(principal, 2)
    result["down_payment"] = round(down_payment, 2)
    result["car"] = car_ref
    result["schedule_preview"] = store.amortisation(financed, rate, tenure_months, limit=12)
    return result


@router.post("/emi", response_model=EmiResponse, summary="Calculate Emi")
def calculate_emi(body: EmiRequest):
    """Reducing-balance EMI, with the first year of the repayment schedule."""
    financed = body.principal - body.down_payment
    result = store.emi(financed, body.rate, body.tenure_months)
    result["on_road_price"] = round(body.principal, 2)
    result["down_payment"] = round(body.down_payment, 2)
    result["car"] = None
    result["schedule_preview"] = store.amortisation(financed, body.rate, body.tenure_months, limit=12)
    return result


@router.post("/amortisation", response_model=Collection[AmortRow], summary="Get Amortisation Schedule")
def get_amortisation_schedule(
    body: EmiRequest,
    months: int = Query(12, ge=1, le=120, description="How many instalments to return."),
):
    """The full repayment schedule, instalment by instalment."""
    financed = body.principal - body.down_payment
    rows = store.amortisation(financed, body.rate, body.tenure_months, limit=months)
    return {"count": len(rows), "items": rows}
