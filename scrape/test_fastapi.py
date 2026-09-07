# -*- coding: utf-8 -*-
"""Walk /openapi.json and call every operation."""
import json, urllib.request, urllib.error, time

BASE = "http://127.0.0.1:8000"

def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read() or b"null"), (time.time()-t0)*1000
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"null"), (time.time()-t0)*1000

spec = json.load(urllib.request.urlopen(BASE + "/openapi.json"))

PATH_PARAMS = {
    "model_id": "golf-gti",
    "outlet_id": "hosur-road-showroom",
    "job_id": "senior-technician",
    "package_id": "svp-hi5",
    "variant_id": "taigun-gt-line-1-0l-tsi-6-speed-mt",
    "id": "1",
}

# Rentals reject overlapping dates for the same car, so each run needs a slot of
# its own or the second run legitimately 409s against the first.
_RUN = int(time.time()) % 900
REQUIRED_QUERY = {
    "/api/search": "?q=gti",
    "/api/compare": "?ids=golf-gti,taigun-sport,virtus-sport",
}
BODIES = {
    "/api/leads/rent": {"first_name":"Praneet","last_name":"Gogoi","email":"p@example.com",
        "mobile":"9876543210","model":"Golf GTI",
        "start_date":f"2027-01-{_RUN%27+1:02d}","end_date":f"2027-01-{_RUN%27+1:02d}"},
    "/api/leads/test-drive": {"first_name":"Praneet","last_name":"Gogoi","email":"p@example.com","mobile":"9876543210","model":"Golf GTI"},
    "/api/leads/service": {"name":"Praneet Gogoi","mobile":"9876543210","model":"Volkswagen Taigun","service_centre":"Hosur Road"},
    "/api/leads/insurance": {"full_name":"Praneet Gogoi","mobile":"9876543210","email":"p@example.com","registration_number":"KA01AB1234"},
    "/api/leads/contact": {"name":"Praneet Gogoi","email":"p@example.com","mobile":"9876543210","message":"Hello"},
    "/api/careers/apply": {"name":"Praneet Gogoi","email":"p@example.com","mobile":"9876543210","job_id":"sales-consultant"},
    "/api/finance/emi": {"principal":1500000,"down_payment":300000,"rate":9.25,"tenure_months":60},
    "/api/finance/amortisation": {"principal":1500000,"down_payment":300000,"rate":9.25,"tenure_months":60},
}

ok = bad = 0
print(f"{'':7}{'MS':>7}  OPERATION")
print("-"*74)
for path, ops in sorted(spec["paths"].items()):
    for verb, op in ops.items():
        url = path
        for name, val in PATH_PARAMS.items():
            url = url.replace("{"+name+"}", val)
        url += REQUIRED_QUERY.get(path, "")
        body = BODIES.get(path) if verb in ("post", "patch") else None
        if verb == "patch" and body is None:
            body = {"status": "CONFIRMED"}
        status, payload, ms = call(verb.upper(), url, body)
        good = status in (200, 201)
        ok, bad = (ok+1, bad) if good else (ok, bad+1)
        print(f"{'  OK  ' if good else ' FAIL '} {ms:6.1f}  {verb.upper():<5} {url}")
        if not good:
            print(f"            -> {status} {json.dumps(payload)[:220]}")
print("-"*74)
print(f"{ok} passed, {bad} failed\n")

print("Error handling")
print("-"*74)
checks = [
    ("GET",  "/api/cars/nope", None, 404),
    ("GET",  "/api/variants/nope", None, 404),
    ("GET",  "/api/outlets/nope", None, 404),
    ("GET",  "/api/careers/jobs/nope", None, 404),
    ("GET",  "/api/service-packages/nope", None, 404),
    ("GET",  "/api/compare?ids=golf-gti", None, 422),
    ("GET",  "/api/compare?ids=golf-gti,ghost", None, 404),
    ("GET",  "/api/search", None, 422),
    ("GET",  "/api/finance/quote?model_id=ghost", None, 404),
    ("POST", "/api/leads/contact", {}, 422),
    ("POST", "/api/leads/contact", {"name":"A","email":"bad","mobile":"1","message":"x"}, 422),
    ("POST", "/api/careers/apply", {"name":"A","email":"a@b.com","mobile":"9876543210","job_id":"ghost"}, 422),
    ("POST", "/api/finance/emi", {"principal":100000,"down_payment":200000}, 422),
]
for method, path, body, want in checks:
    status, payload, _ = call(method, path, body)
    mark = "  OK  " if status == want else " FAIL "
    if status != want:
        bad += 1
        print(f"{mark} expected {want}, got {status}  {method} {path}  -> {json.dumps(payload)[:160]}")
    else:
        print(f"{mark} expected {want}, got {status}  {method} {path}")

# error shape must stay {"error": {...}} for the frontend
status, payload, _ = call("POST", "/api/leads/contact", {"name":"A","email":"bad","mobile":"1","message":"x"})
shape_ok = isinstance(payload, dict) and "error" in payload and isinstance(payload["error"].get("detail"), dict)
print("-"*74)
print("error envelope:", json.dumps(payload["error"])[:200] if shape_ok else f"UNEXPECTED {payload}")
if not shape_ok: bad += 1
print("-"*74)
print("ALL GREEN" if bad == 0 else f"{bad} FAILURES")
