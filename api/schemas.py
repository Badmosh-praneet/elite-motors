"""Pydantic schemas — these drive the OpenAPI 3.1 document."""

from __future__ import annotations

import re
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, Field, field_validator

T = TypeVar("T")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^[+\d][\d\s\-()]{7,17}$")


# ==========================================================================
# shared
# ==========================================================================

class Page(BaseModel, Generic[T]):
    """A paged collection."""
    count: int = Field(..., description="Items in this page.", examples=[7])
    total: int = Field(..., description="Items matching the filter.", examples=[7])
    offset: int = Field(0, description="Items skipped.", examples=[0])
    limit: int = Field(50, description="Page size.", examples=[50])
    items: list[T]


class Collection(BaseModel, Generic[T]):
    """A complete, unpaged collection."""
    count: int = Field(..., examples=[6])
    items: list[T]


class ErrorDetail(BaseModel):
    status: int = Field(..., examples=[404])
    message: str = Field(..., examples=["No car with id 'polo'."])
    detail: dict[str, Any] | None = Field(
        None, description="Field-level problems, keyed by field name.",
        examples=[{"email": "Enter a valid email address."}],
    )


class ErrorResponse(BaseModel):
    error: ErrorDetail


# ==========================================================================
# catalogue
# ==========================================================================

class Price(BaseModel):
    min: int = Field(..., description="Lowest variant price.", examples=[1170000])
    max: int = Field(..., description="Highest variant price.", examples=[1940000])
    currency: str = Field("INR", examples=["INR"])
    note: str = Field(..., examples=["Indicative ex-showroom, Bengaluru"])


class Specs(BaseModel):
    engine: str = Field(..., examples=["1.5L TSI EVO (ACT) / 1.0L TSI"])
    power: str = Field(..., examples=["150 PS / 115 PS"])
    torque: str = Field(..., examples=["250 Nm / 178 Nm"])
    transmission: str = Field(..., examples=["6-speed MT or 7-speed DSG"])
    drivetrain: str = Field(..., examples=["FWD"])
    fuel: str = Field(..., examples=["Petrol"])
    zero_to_hundred: str | None = Field(None, examples=["5.9 s"])
    mileage_record: str | None = None
    seating: str | None = Field(None, examples=["5-seater"])
    boot: str | None = Field(None, examples=["385 L"])


class ColourOption(BaseModel):
    name: str = Field(..., examples=["Curcuma Yellow"])
    hex: str = Field(..., examples=["#D8A51D"])


class Variant(BaseModel):
    id: str = Field(..., examples=["taigun-gt-line-1-0l-tsi-6-speed-mt"])
    model_slug: str = Field(..., examples=["taigun-sport"])
    model_name: str = Field(..., examples=["Taigun Sport"])
    name: str = Field(..., examples=["Taigun GT Line 1.0 TSI MT"])
    trim: str = Field(..., examples=["GT Line"])
    engine: str = Field(..., examples=["1.0L TSI"])
    power: str = Field(..., examples=["115 PS"])
    torque: str = Field(..., examples=["178 Nm"])
    transmission: str = Field(..., examples=["6-speed MT"])
    drivetrain: str = Field(..., examples=["FWD"])
    fuel: str = Field(..., examples=["Petrol"])
    seats: int = Field(..., examples=[5])
    body_type: str = Field(..., examples=["SUV"])
    price: int = Field(..., examples=[1170000])
    currency: str = Field("INR", examples=["INR"])
    price_note: str = Field(..., examples=["Indicative ex-showroom, Bengaluru"])


class FAQ(BaseModel):
    question: str = Field(..., examples=["What warranty does the Taigun Sport carry?"])
    answer: str = Field(..., examples=[
        "Your Volkswagen is secured with a 4 year (100,000 kilometers) manufacturer's warranty."
    ])


class CarSummary(BaseModel):
    """A car as it appears in listings."""
    slug: str = Field(..., examples=["taigun-sport"])
    name: str = Field(..., examples=["Taigun Sport"])
    family: str = Field(..., examples=["Taigun"])
    variant_label: str = Field(..., examples=["GT Plus Sport / GT Line"])
    body_type: str = Field(..., examples=["SUV"])
    segment: str = Field(..., examples=["core"])
    seats: int = Field(..., examples=[5])
    status: str = Field(..., examples=["available"])
    badge: str | None = Field(None, examples=["29.8 km/l record"])
    tagline: str = Field(..., examples=["Built for the ones who go looking."])
    price: Price
    specs: Specs
    hero_image: str = Field(..., examples=["/assets/img/ourmodels/taigun-sport.png"])
    variant_count: int = Field(..., examples=[4])


class CarDetail(CarSummary):
    """A car with everything the catalogue holds."""
    description: str
    highlights: list[str]
    features: dict[str, list[str]] = Field(
        ..., description="Feature lists grouped by category.",
        examples=[{"Safety": ["6 airbags as standard", "Electronic Stability Control"]}],
    )
    colors: list[ColourOption]
    gallery: list[str]
    intro_image: str
    variants: list[Variant]
    faqs: list[FAQ]


class LineupGroup(BaseModel):
    body_type: str = Field(..., examples=["SUV"])
    count: int = Field(..., examples=[4])
    cars: list[CarSummary]


class Lineup(BaseModel):
    total_cars: int = Field(..., examples=[7])
    total_variants: int = Field(..., examples=[19])
    groups: list[LineupGroup]


class ComparisonRow(BaseModel):
    attribute: str = Field(..., examples=["Power"])
    values: dict[str, str] = Field(
        ..., description="Attribute value keyed by car slug.",
        examples=[{"golf-gti": "265 hp", "taigun-sport": "150 PS / 115 PS"}],
    )


class Comparison(BaseModel):
    cars: list[CarSummary]
    rows: list[ComparisonRow]


# ==========================================================================
# dealership
# ==========================================================================

class HoursRow(BaseModel):
    days: str = Field(..., examples=["Mon - Sat"])
    open: str = Field(..., examples=["09:45"])
    close: str = Field(..., examples=["19:10"])


class Hours(BaseModel):
    sales: list[HoursRow]
    service: list[HoursRow]


class Contact(BaseModel):
    phone: str = Field(..., examples=["080 4013 8004"])
    phone_e164: str = Field(..., examples=["+918040138004"])
    sales_email: str = Field(..., examples=["crm@vw-elitemotors.co.in"])
    service_email: str = Field(..., examples=["crhead@vw-elitemotors.co.in"])
    whatsapp: str | None = None


class Stat(BaseModel):
    label: str = Field(..., examples=["Cars delivered"])
    value: int = Field(..., examples=[12480])
    suffix: str = Field("", examples=["+"])


class AboutBlock(BaseModel):
    headline: str
    paragraphs: list[str]


class AboutResponse(AboutBlock):
    """About copy plus the details an About page needs alongside it."""
    dealer: str = Field(..., examples=["Elite Motors"])
    display_name: str = Field(..., examples=["Volkswagen Elite Motors"])
    hours: "Hours"
    contact: "Contact"


class Dealer(BaseModel):
    id: str = Field(..., examples=["elite-motors-blr"])
    legal_name: str = Field(..., examples=["Elite Motors"])
    trading_as: str = Field(..., examples=["Volkswagen Elite Motors"])
    brand: str = Field(..., examples=["Volkswagen"])
    city: str = Field(..., examples=["Bengaluru"])
    state: str
    country: str
    tagline: str
    authorised: bool = Field(..., examples=[True])
    about: AboutBlock
    contact: Contact
    hours: Hours
    social: dict[str, str]
    stats: list[Stat]


class Outlet(BaseModel):
    id: str = Field(..., examples=["hosur-road-showroom"])
    name: str = Field(..., examples=["Volkswagen Elite Motors — Hosur Road"])
    type: Literal["showroom", "service"] = Field(..., examples=["showroom"])
    types: list[str] = Field(..., examples=[["sales"]])
    address_line: str
    city: str
    state: str
    pincode: str = Field(..., examples=["560100"])
    full_address: str
    phone: str
    email: str
    map_url: str
    lat: float = Field(..., examples=[12.8797])
    lng: float = Field(..., examples=[77.6408])
    hours: list[HoursRow]


class Offer(BaseModel):
    id: str
    title: str = Field(..., examples=["Exchange Bonus"])
    value: str = Field(..., examples=["Up to ₹60,000"])
    description: str
    valid_till: str = Field(..., examples=["2026-09-30"])


class Testimonial(BaseModel):
    name: str
    location: str
    model: str
    rating: int = Field(..., ge=1, le=5, examples=[5])
    quote: str


class HeroSlide(BaseModel):
    image: str
    mobile: str
    eyebrow: str
    title: str
    subtitle: str
    cta: str
    href: str


# ==========================================================================
# ownership
# ==========================================================================

class ServiceItem(BaseModel):
    id: str = Field(..., examples=["periodic"])
    name: str = Field(..., examples=["Periodic Maintenance"])
    icon: str
    description: str


class ServicePackage(BaseModel):
    id: str = Field(..., examples=["svp-hi5"])
    name: str = Field(..., examples=["Hi5 Package"])
    duration: str = Field(..., examples=["5 Years"])
    image: str
    featured: bool = False
    benefits: list[str]


class ServicePackages(BaseModel):
    intro: str
    guarantees: list[str]
    packages: list[ServicePackage]


class StandardWarranty(BaseModel):
    title: str
    description: str
    years: int = Field(..., examples=[4])
    kilometers: int = Field(..., examples=[100000])
    image: str


class ExtendedOption(BaseModel):
    term: str = Field(..., examples=["5th Year"])
    kilometers: int = Field(..., examples=[125000])


class ExtendedWarranty(BaseModel):
    title: str
    description: str
    options: list[ExtendedOption]


class Warranty(BaseModel):
    standard: StandardWarranty
    extended: ExtendedWarranty


class RoadsideAssistance(BaseModel):
    title: str
    description: str
    assistance_note: str
    image: str
    coverage: list[str]


class Insurance(BaseModel):
    title: str
    description: str
    benefits: list[str]
    form_fields: list[str]


# ==========================================================================
# careers
# ==========================================================================

class Job(BaseModel):
    id: str = Field(..., examples=["sales-consultant"])
    title: str = Field(..., examples=["Sales Consultant"])
    department: str = Field(..., examples=["Sales"])
    location: str = Field(..., examples=["Hosur Road, Bengaluru"])
    type: str = Field(..., examples=["Full-time"])
    description: str


class Careers(BaseModel):
    title: str
    description: str
    image: str
    upload_formats: list[str]
    jobs: list[Job]


# ==========================================================================
# finance
# ==========================================================================

class FinanceDefaults(BaseModel):
    principal: int
    rate: float
    tenure_months: int
    down_payment_pct: int


class FinanceLimits(BaseModel):
    principal_min: int
    principal_max: int
    rate_min: float
    rate_max: float
    tenure_min: int
    tenure_max: int


class FinanceConfig(BaseModel):
    title: str
    description: str
    defaults: FinanceDefaults
    limits: FinanceLimits
    partners: list[str]


class AmortRow(BaseModel):
    month: int = Field(..., examples=[1])
    emi: float = Field(..., examples=[20253.5])
    interest: float = Field(..., examples=[7479.17])
    principal: float = Field(..., examples=[12774.33])
    balance: float = Field(..., examples=[957225.67])


class EmiRequest(BaseModel):
    principal: float = Field(..., gt=0, description="On-road or ex-showroom price.", examples=[1500000])
    rate: float = Field(9.25, ge=0, le=36, description="Annual interest rate, percent.", examples=[9.25])
    tenure_months: int = Field(60, ge=1, le=120, description="Loan tenure in months.", examples=[60])
    down_payment: float = Field(0, ge=0, description="Amount paid upfront.", examples=[300000])

    @field_validator("down_payment")
    @classmethod
    def _under_principal(cls, v: float, info):
        principal = info.data.get("principal")
        if principal is not None and v >= principal:
            raise ValueError("Down payment must be less than the principal.")
        return v


class CarRef(BaseModel):
    slug: str
    name: str
    price: Price


class EmiResponse(BaseModel):
    principal: float = Field(..., description="Amount financed, after down payment.", examples=[1200000])
    annual_rate: float = Field(..., examples=[9.25])
    tenure_months: int = Field(..., examples=[60])
    monthly_emi: float = Field(..., examples=[25055.88])
    total_payable: float = Field(..., examples=[1503352.8])
    total_interest: float = Field(..., examples=[303352.8])
    currency: str = Field("INR", examples=["INR"])
    on_road_price: float | None = None
    down_payment: float | None = None
    car: CarRef | None = None
    schedule_preview: list[AmortRow] = Field(default_factory=list, description="First 12 instalments.")


# ==========================================================================
# enquiries
# ==========================================================================

class _ContactBase(BaseModel):
    @field_validator("email", check_fields=False)
    @classmethod
    def _email(cls, v: str) -> str:
        if not EMAIL_RE.match(v):
            raise ValueError("Enter a valid email address.")
        return v

    @field_validator("mobile", check_fields=False)
    @classmethod
    def _mobile(cls, v: str) -> str:
        if not PHONE_RE.match(v):
            raise ValueError("Enter a valid phone number.")
        return v


class TestDriveRequest(_ContactBase):
    first_name: str = Field(..., min_length=1, examples=["Praneet"])
    last_name: str = Field(..., min_length=1, examples=["Gogoi"])
    email: str = Field(..., examples=["you@example.com"])
    mobile: str = Field(..., examples=["9876543210"])
    model: str = Field(..., min_length=1, examples=["Golf GTI"])
    preferred_date: str | None = Field(None, examples=["2026-09-15"])
    preferred_time: str | None = Field(None, examples=["Morning (10:00 – 13:00)"])


class RentalRequest(_ContactBase):
    first_name: str = Field(..., min_length=1, examples=["Praneet"])
    last_name: str = Field(..., min_length=1, examples=["Gogoi"])
    email: str = Field(..., examples=["you@example.com"])
    mobile: str = Field(..., examples=["9876543210"])
    model: str = Field(..., min_length=1, examples=["Volkswagen Virtus"])
    start_date: str = Field(..., examples=["2026-09-10"])
    end_date: str = Field(..., examples=["2026-09-15"])


class CarBookingRequest(_ContactBase):
    first_name: str = Field(..., min_length=1, examples=["Praneet"])
    last_name: str = Field(..., min_length=1, examples=["Gogoi"])
    email: str = Field(..., examples=["you@example.com"])
    mobile: str = Field(..., examples=["9876543210"])
    model: str = Field(..., min_length=1, examples=["Volkswagen Virtus"])
    variant: str | None = Field(None, examples=["GT Plus"])
    color: str | None = Field(None, examples=["Wild Cherry Red"])
    dealership_id: str = Field(..., examples=["hosur-road-showroom"])


class ServiceRequest(_ContactBase):
    name: str = Field(..., min_length=1, examples=["Praneet Gogoi"])
    mobile: str = Field(..., examples=["9876543210"])
    email: str | None = None
    model: str = Field(..., min_length=1, examples=["Volkswagen Taigun"])
    service_centre: str = Field(..., min_length=1, examples=["Volkswagen Elite Motors Service — Hosur Road"])
    registration_number: str | None = Field(None, examples=["KA 01 AB 1234"])
    preferred_date: str | None = None
    message: str | None = None


class InsuranceRequest(_ContactBase):
    full_name: str = Field(..., min_length=1, examples=["Praneet Gogoi"])
    mobile: str = Field(..., examples=["9876543210"])
    email: str = Field(..., examples=["you@example.com"])
    registration_number: str = Field(..., min_length=1, examples=["KA 01 AB 1234"])
    model: str | None = None
    registration_year: str | None = Field(None, examples=["2023"])
    registration_month: str | None = Field(None, examples=["March"])
    insurance_company: str | None = Field(None, examples=["HDFC ERGO"])
    policy_number: str | None = None
    insurance_expiry: str | None = None


class ContactRequest(_ContactBase):
    name: str = Field(..., min_length=1, examples=["Praneet Gogoi"])
    email: str = Field(..., examples=["you@example.com"])
    mobile: str = Field(..., examples=["9876543210"])
    subject: str | None = Field(None, examples=["General enquiry"])
    message: str = Field(..., min_length=1, examples=["What is the waiting period on the Tayron R-Line?"])


class ApplicationRequest(_ContactBase):
    name: str = Field(..., min_length=1, examples=["Praneet Gogoi"])
    email: str = Field(..., examples=["you@example.com"])
    mobile: str = Field(..., examples=["9876543210"])
    job_id: str = Field(..., description="Must match an id from /api/careers/jobs.", examples=["sales-consultant"])
    experience: int | None = Field(None, ge=0, le=60, examples=[4])
    cv_filename: str | None = Field(None, examples=["praneet-gogoi-cv.pdf"])
    message: str | None = None


class LeadStatusUpdate(BaseModel):
    status: Literal["PENDING", "CONFIRMED", "COMPLETED", "CANCELLED"] = Field(..., examples=["CONFIRMED"])

class Lead(BaseModel):
    id: str = Field(..., examples=["test-drive-a1b2c3d4e5"])
    type: str = Field(..., examples=["test-drive"])
    received_at: str = Field(..., examples=["2026-08-31T05:22:41+00:00"])
    status: str = Field(..., examples=["new"])
    data: dict[str, Any]


class LeadAccepted(BaseModel):
    message: str = Field(..., examples=["Your request submitted successfully."])
    reference: str = Field(..., examples=["test-drive-a1b2c3d4e5"])
    next_step: str | None = Field(
        None, examples=["A Sales Consultant from Elite Motors will call you within one working day."]
    )
    lead: Lead


# ==========================================================================
# search & system
# ==========================================================================

class SearchHit(BaseModel):
    type: Literal["car", "variant", "outlet", "service", "package", "job", "faq"]
    id: str
    title: str
    subtitle: str
    url: str
    image: str | None = None


class SearchResponse(BaseModel):
    query: str = Field(..., examples=["gti"])
    count: int = Field(..., examples=[3])
    results: list[SearchHit]


class Health(BaseModel):
    status: Literal["ok"] = "ok"
    service: str = Field(..., examples=["vw-elite-motors-api"])
    version: str = Field(..., examples=["2.0.0"])
    uptime_seconds: float = Field(..., examples=[128.4])
    cars_loaded: int = Field(..., examples=[7])
    variants_loaded: int = Field(..., examples=[19])
    timestamp: str
