"""Open roles at the dealership."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Path, Query

from .. import store
from ..schemas import Careers, Collection, ErrorResponse, Job

router = APIRouter(prefix="/api/careers", tags=["Careers"])


@router.get("", response_model=Careers, summary="Get Careers")
def get_careers():
    """Careers overview and every open role."""
    return store.DB["careers"]


@router.get("/jobs", response_model=Collection[Job], summary="Get Jobs")
def get_jobs(
    department: str | None = Query(None, description="Filter by department, e.g. `Service`."),
):
    """Open roles, optionally filtered by department."""
    items = store.jobs()
    if department:
        items = [j for j in items if j["department"].lower() == department.lower()]
    return {"count": len(items), "items": items}


@router.get("/jobs/{job_id}", response_model=Job,
            responses={404: {"model": ErrorResponse}}, summary="Get Job")
def get_job(job_id: str = Path(..., description="Job id.", examples=["senior-technician"])):
    """One role by id."""
    job = store.job_by_id(job_id)
    if job is None:
        known = ", ".join(j["id"] for j in store.jobs())
        raise HTTPException(404, {"message": f"No job with id '{job_id}'.",
                                  "detail": {"known_ids": known}})
    return job
