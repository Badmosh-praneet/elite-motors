"""Lead capture — test drives, service, insurance, contact and job applications."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import time

from .. import store
from ..database import get_db
from ..db_models import TestDrive, Rental, CarBooking
from ..schemas import (
    ApplicationRequest, Collection, ContactRequest, ErrorResponse, InsuranceRequest,
    Lead, LeadAccepted, ServiceRequest, TestDriveRequest, RentalRequest, LeadStatusUpdate, CarBookingRequest
)

router = APIRouter(prefix="/api", tags=["Enquiries"])

CREATED = status.HTTP_201_CREATED
VALIDATION = {422: {"model": ErrorResponse, "description": "Validation failed."}}


def _simulate_email(email: str, subject: str):
    time.sleep(2)
    print(f"--- SIMULATED EMAIL SENT TO {email} ---")
    print(f"Subject: {subject}")
    print("---------------------------------------")

def _accept(kind: str, payload: dict, message: str, next_step: str) -> dict:
    lead = store.append_lead(kind, payload)
    return {"message": message, "reference": lead["id"], "next_step": next_step, "lead": lead}


@router.post("/leads/test-drive", response_model=LeadAccepted, status_code=CREATED,
             responses=VALIDATION, summary="Book Test Drive")
def book_test_drive(body: TestDriveRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Request a test drive. A Sales Consultant confirms the slot."""
    new_td = TestDrive(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        mobile=body.mobile,
        model=body.model,
        preferred_date=body.preferred_date,
        preferred_time=body.preferred_time
    )
    db.add(new_td)
    db.commit()
    db.refresh(new_td)
    
    background_tasks.add_task(_simulate_email, body.email, f"Test Drive Request: {body.model}")
    
    return _accept(
        "test-drive", body.model_dump(exclude_none=True),
        "Your request submitted successfully.",
        "A Sales Consultant from Elite Motors will call you within one working day.",
    )

@router.post("/leads/rent", response_model=LeadAccepted, status_code=CREATED,
             responses=VALIDATION, summary="Book Car Rental")
def book_rental(body: RentalRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Request a car rental."""
    conflict = db.query(Rental).filter(
        Rental.model == body.model,
        Rental.status.in_(["PENDING", "CONFIRMED"]),
        Rental.start_date <= body.end_date,
        Rental.end_date >= body.start_date
    ).first()
    
    if conflict:
        raise HTTPException(status_code=409, detail=f"The {body.model} is already booked for these dates.")

    new_rent = Rental(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        mobile=body.mobile,
        model=body.model,
        start_date=body.start_date,
        end_date=body.end_date
    )
    db.add(new_rent)
    db.commit()
    db.refresh(new_rent)
    
    background_tasks.add_task(_simulate_email, body.email, f"Rental Request Confirmed: {body.model}")
    
    return _accept(
        "rent", body.model_dump(exclude_none=True),
        "Your rental request submitted successfully.",
        "Our team will confirm your booking and arrange the handover.",
    )

@router.post("/leads/advance-booking", response_model=LeadAccepted, status_code=CREATED,
             responses=VALIDATION, summary="Advance Car Booking")
def advance_car_booking(body: CarBookingRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Request an advance booking for a new car."""
    new_booking = CarBooking(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        mobile=body.mobile,
        model=body.model,
        variant=body.variant,
        color=body.color,
        dealership_id=body.dealership_id
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    background_tasks.add_task(_simulate_email, body.email, f"Advance Booking Received: {body.model}")
    
    return _accept(
        "advance-booking", body.model_dump(exclude_none=True),
        "Your advance booking request submitted successfully.",
        "A Sales Consultant will call you to confirm payment and allocation details.",
    )

@router.get("/leads/test-drive", summary="Get Test Drives (Admin)")
def get_test_drives(db: Session = Depends(get_db)):
    """Get all test drives from the database."""
    rows = db.query(TestDrive).order_by(TestDrive.id.desc()).all()
    return [
        {
            "id": r.id, "first_name": r.first_name, "last_name": r.last_name,
            "email": r.email, "mobile": r.mobile, "model": r.model,
            "preferred_date": r.preferred_date, "preferred_time": r.preferred_time,
            "created_at": str(r.created_at) if r.created_at else None,
            "status": r.status,
        }
        for r in rows
    ]

@router.patch("/leads/test-drive/{id}", summary="Update Test Drive Status (Admin)")
def update_test_drive(id: int, body: LeadStatusUpdate, db: Session = Depends(get_db)):
    """Update status of a test drive."""
    td = db.query(TestDrive).filter(TestDrive.id == id).first()
    if not td:
        raise HTTPException(status_code=404, detail="Test Drive not found.")
    td.status = body.status
    db.commit()
    return {"message": "Status updated successfully.", "status": td.status}

@router.get("/leads/rent", summary="Get Rentals (Admin)")
def get_rentals(db: Session = Depends(get_db)):
    """Get all rentals from the database."""
    rows = db.query(Rental).order_by(Rental.id.desc()).all()
    return [
        {
            "id": r.id, "first_name": r.first_name, "last_name": r.last_name,
            "email": r.email, "mobile": r.mobile, "model": r.model,
            "start_date": r.start_date, "end_date": r.end_date,
            "created_at": str(r.created_at) if r.created_at else None,
            "status": r.status,
        }
        for r in rows
    ]

@router.patch("/leads/rent/{id}", summary="Update Rental Status (Admin)")
def update_rental(id: int, body: LeadStatusUpdate, db: Session = Depends(get_db)):
    """Update status of a rental."""
    rent = db.query(Rental).filter(Rental.id == id).first()
    if not rent:
        raise HTTPException(status_code=404, detail="Rental not found.")
    rent.status = body.status
    db.commit()
    return {"message": "Status updated successfully.", "status": rent.status}

@router.get("/leads/advance-booking", summary="Get Advance Bookings (Admin)")
def get_advance_bookings(db: Session = Depends(get_db)):
    """Get all advance car bookings from the database."""
    rows = db.query(CarBooking).order_by(CarBooking.id.desc()).all()
    return [
        {
            "id": r.id, "first_name": r.first_name, "last_name": r.last_name,
            "email": r.email, "mobile": r.mobile, "model": r.model,
            "variant": r.variant, "color": r.color, "dealership_id": r.dealership_id,
            "created_at": str(r.created_at) if r.created_at else None,
            "status": r.status,
        }
        for r in rows
    ]

@router.patch("/leads/advance-booking/{id}", summary="Update Advance Booking Status (Admin)")
def update_advance_booking(id: int, body: LeadStatusUpdate, db: Session = Depends(get_db)):
    """Update status of an advance booking."""
    booking = db.query(CarBooking).filter(CarBooking.id == id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Advance Booking not found.")
    booking.status = body.status
    db.commit()
    return {"message": "Status updated successfully.", "status": booking.status}


@router.post("/leads/service", response_model=LeadAccepted, status_code=CREATED,
             responses=VALIDATION, summary="Book Service")
def book_service(body: ServiceRequest):
    """Book a workshop slot for any Volkswagen, including older generations."""
    return _accept(
        "service", body.model_dump(exclude_none=True),
        "Service booking received.",
        "Our Service Advisor will confirm your slot and pick-up window.",
    )


@router.post("/leads/insurance", response_model=LeadAccepted, status_code=CREATED,
             responses=VALIDATION, summary="Request Insurance Quote")
def request_insurance_quote(body: InsuranceRequest):
    """Ask for a comparative motor insurance renewal quote."""
    return _accept(
        "insurance", body.model_dump(exclude_none=True),
        "Insurance enquiry received.",
        "You will receive a comparative quote within 24 hours.",
    )


@router.post("/leads/contact", response_model=LeadAccepted, status_code=CREATED,
             responses=VALIDATION, summary="Send Enquiry")
def send_enquiry(body: ContactRequest):
    """A general enquiry to the dealership."""
    return _accept(
        "contact", body.model_dump(exclude_none=True),
        "Thank you for reaching out. We are here to help you!",
        "Someone from the relevant department will reply shortly.",
    )


@router.post("/careers/apply", response_model=LeadAccepted, status_code=CREATED,
             responses=VALIDATION, summary="Apply For Job")
def apply_for_job(body: ApplicationRequest):
    """Apply for an open role. `job_id` must match `/api/careers/jobs`."""
    if store.job_by_id(body.job_id) is None:
        known = ", ".join(j["id"] for j in store.jobs())
        raise HTTPException(422, {"message": "Validation failed",
                                  "detail": {"job_id": f"Unknown role. Valid options: {known}."}})
    return _accept(
        "career", body.model_dump(exclude_none=True),
        "Your request submitted successfully.",
        "Our HR team reviews every application within five working days.",
    )


@router.get("/leads", response_model=Collection[Lead], tags=["Enquiries"], summary="Get Leads")
def get_leads(
    type: str | None = Query(None, description="`test-drive`, `service`, `insurance`, `contact` or `career`."),
    limit: int = Query(50, ge=1, le=500),
):
    """The demo inbox — every lead submitted, newest first."""
    leads = store.read_leads()
    if type:
        leads = [l for l in leads if l["type"] == type]
    leads = list(reversed(leads))[:limit]
    return {"count": len(leads), "items": leads}
