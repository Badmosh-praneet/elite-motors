from typing import Any
import httpx

API_BASE = "http://localhost:8000/api"

async def book_advance_car(
    first_name: str,
    last_name: str,
    email: str,
    mobile: str,
    model: str,
    dealership_id: str,
    variant: str = None,
    color: str = None
) -> dict[str, Any]:
    """Request an advance booking for a new car."""
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "mobile": mobile,
        "model": model,
        "variant": variant,
        "color": color,
        "dealership_id": dealership_id
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_BASE}/leads/advance-booking", json=payload)
        response.raise_for_status()
        return response.json()

async def get_advance_bookings() -> list[dict[str, Any]]:
    """Get all advance car bookings (Admin)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/leads/advance-booking")
        response.raise_for_status()
        return response.json()

async def update_booking_status(id: int, status: str) -> dict[str, Any]:
    """Update status of an advance booking. Status should be PENDING, CONFIRMED, COMPLETED, or CANCELLED."""
    payload = {"status": status}
    async with httpx.AsyncClient() as client:
        response = await client.patch(f"{API_BASE}/leads/advance-booking/{id}", json=payload)
        response.raise_for_status()
        return response.json()

async def get_dealership_full() -> dict[str, Any]:
    """Returns the full dealership profile and all outlets in a single response."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/dealership-full")
        response.raise_for_status()
        return response.json()

async def get_cars(q: str = None, body_type: str = None, family: str = None, limit: int = 50) -> dict[str, Any]:
    """Every car Elite Motors sells, with filtering, sorting and pagination."""
    params = {"limit": limit}
    if q:
        params["q"] = q
    if body_type:
        params["body_type"] = body_type
    if family:
        params["family"] = family
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/cars", params=params)
        response.raise_for_status()
        return response.json()

async def get_car(model_id: str) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/cars/{model_id}")
        response.raise_for_status()
        return response.json()

async def compare_cars(ids: str) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/compare", params={"ids": ids})
        response.raise_for_status()
        return response.json()

async def list_variants(model_id: str = None, trim: str = None, transmission: str = None, limit: int = 50) -> dict[str, Any]:
    params = {"limit": limit}
    if model_id:
        params["model_id"] = model_id
    if trim:
        params["trim"] = trim
    if transmission:
        params["transmission"] = transmission
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/variants", params=params)
        response.raise_for_status()
        return response.json()

async def book_test_drive(
    first_name: str, last_name: str, email: str, mobile: str, 
    model: str, preferred_date: str, preferred_time: str
) -> dict[str, Any]:
    payload = {
        "first_name": first_name, "last_name": last_name, "email": email, 
        "mobile": mobile, "model": model, 
        "preferred_date": preferred_date, "preferred_time": preferred_time
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_BASE}/leads/test-drive", json=payload)
        response.raise_for_status()
        return response.json()

async def book_service(
    first_name: str, last_name: str, email: str, mobile: str, 
    model: str, registration_number: str, service_type: str, preferred_date: str
) -> dict[str, Any]:
    payload = {
        "first_name": first_name, "last_name": last_name, "email": email, 
        "mobile": mobile, "model": model, "registration_number": registration_number,
        "service_type": service_type, "preferred_date": preferred_date
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_BASE}/leads/service", json=payload)
        response.raise_for_status()
        return response.json()

async def book_rental(
    first_name: str, last_name: str, email: str, mobile: str, 
    model: str, start_date: str, end_date: str
) -> dict[str, Any]:
    payload = {
        "first_name": first_name, "last_name": last_name, "email": email, 
        "mobile": mobile, "model": model, 
        "start_date": start_date, "end_date": end_date
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_BASE}/leads/rent", json=payload)
        response.raise_for_status()
        return response.json()
