"""
Volkswagen Elite Motors API.

    uvicorn api.main:app --reload
    python run.py

Swagger UI  /docs
ReDoc       /redoc
Schema      /openapi.json
Website     /
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import store
from .routers import careers, catalogue, dealership, enquiries, finance, ownership, system
from .database import engine
from . import db_models

db_models.Base.metadata.create_all(bind=engine)

DESCRIPTION = """\
A read API over a scraped knowledge base of **volkswagenbangalore.in** — the site of
**Volkswagen Elite Motors**, an authorised Volkswagen dealership on Hosur Road, Bengaluru.

Seven cars, nineteen variants and their prices, ownership services, finance maths and
full-text search across every page in the catalogue.

Content, imagery and specifications are scraped from the dealership's live site.
Pricing is indicative ex-showroom Bengaluru — the source site does not publish prices.
"""

TAGS = [
    {"name": "Catalogue",
     "description": "Cars, variants, specifications, colours, galleries, FAQs and side-by-side comparison."},
    {"name": "Dealership",
     "description": "Who Elite Motors are — profile, outlets, opening hours, offers and testimonials."},
    {"name": "Ownership",
     "description": "Life after the handover: servicing, value packages, warranty, roadside assistance and insurance."},
    {"name": "Finance",
     "description": "Reducing-balance EMI maths, repayment schedules and lending partners."},
    {"name": "Careers",
     "description": "Open roles at the dealership."},
    {"name": "Enquiries",
     "description": "Lead capture — test drives, service bookings, insurance quotes, enquiries and job applications."},
    {"name": "Search & System",
     "description": "Full-text search across the knowledge base, and service health."},
]

app = FastAPI(
    title="Volkswagen Elite Motors API",
    description=DESCRIPTION,
    version="2.0.0",
    openapi_tags=TAGS,
    contact={"name": "Volkswagen Elite Motors", "email": "crm@vw-elitemotors.co.in"},
    license_info={"name": "Demonstration build"},
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_parameters={"docExpansion": "list", "defaultModelsExpandDepth": 0},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------
# error contract: every API failure is {"error": {status, message, detail?}}
# --------------------------------------------------------------------------

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    detail = exc.detail
    if isinstance(detail, dict):
        message = detail.get("message", "Error")
        extra = detail.get("detail")
    else:
        message = str(detail)
        extra = None

    payload: dict = {"status": exc.status_code, "message": message}
    if extra:
        payload["detail"] = extra
    return JSONResponse(status_code=exc.status_code, content={"error": payload},
                        headers=getattr(exc, "headers", None))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Flatten pydantic errors into {field: message}, which is what the site renders."""
    detail: dict[str, str] = {}
    for err in exc.errors():
        parts = [str(p) for p in err["loc"] if p not in ("body", "query", "path")]
        field = ".".join(parts) or "body"
        detail.setdefault(field, err["msg"].removeprefix("Value error, "))
    return JSONResponse(
        status_code=422,
        content={"error": {"status": 422, "message": "Validation failed", "detail": detail}},
    )


# --------------------------------------------------------------------------
# routes
# --------------------------------------------------------------------------

for module in (catalogue, dealership, ownership, finance, careers, enquiries, system):
    app.include_router(module.router)


@app.get("/api", include_in_schema=False)
def api_index():
    return {
        "name": app.title,
        "version": app.version,
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "cars": len(store.models()),
        "variants": len(store.all_variants()),
    }


# --------------------------------------------------------------------------
# static site — mounted last so it never shadows the API
# --------------------------------------------------------------------------

class SiteFiles(StaticFiles):
    """StaticFiles with extensionless URLs (`/models` -> `models.html`), a styled 404,
    and cache headers so edited markup/CSS/JS is picked up on refresh."""

    LONG_LIVED = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".mp4", ".woff2", ".ico"}

    @staticmethod
    def _with_cache_headers(response, path: str):
        # Assets are content-stable and worth caching; markup, CSS and JS must
        # revalidate or a refresh keeps serving the previous build.
        ext = Path(path).suffix.lower()
        response.headers["Cache-Control"] = (
            "public, max-age=86400" if ext in SiteFiles.LONG_LIVED else "no-cache"
        )
        return response

    async def get_response(self, path: str, scope):
        # With html=True Starlette *returns* a 404.html response rather than
        # raising, so a miss has to be detected by status as well as by exception.
        try:
            response = await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code != 404:
                raise
            response = None

        if response is not None and response.status_code != 404:
            return self._with_cache_headers(response, path)

        leaf = path.rsplit("/", 1)[-1]
        if leaf and "." not in leaf:
            try:
                alt = await super().get_response(f"{path}.html", scope)
                if alt.status_code == 200:
                    return self._with_cache_headers(alt, f"{path}.html")
            except StarletteHTTPException:
                pass

        if response is not None:
            return response  # already the styled 404 page

        fallback = Path(self.directory) / "404.html"
        if fallback.is_file():
            return FileResponse(fallback, status_code=404)
        raise StarletteHTTPException(status_code=404)


app.mount("/", SiteFiles(directory=str(store.WEB_DIR), html=True), name="site")
