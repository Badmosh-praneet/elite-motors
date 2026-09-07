import json, urllib.request, urllib.error, time

BASE = "http://127.0.0.1:8000/api/v1"

def call(method, path, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            payload = json.loads(r.read())
            return r.status, payload, (time.time()-t0)*1000
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read()), (time.time()-t0)*1000

docs = json.load(urllib.request.urlopen(BASE + "/docs"))
SAMPLES = {
  "/leads/test-drive": {"first_name":"A","last_name":"B","email":"a@b.com","mobile":"9876543210","model":"Golf GTI"},
  "/leads/service": {"name":"A B","mobile":"9876543210","model":"Volkswagen Taigun","service_centre":"Hosur Road"},
  "/leads/insurance": {"full_name":"A B","mobile":"9876543210","email":"a@b.com","registration_number":"KA01AB1234"},
  "/leads/contact": {"name":"A B","email":"a@b.com","mobile":"9876543210","message":"Hello"},
  "/careers/apply": {"name":"A B","email":"a@b.com","mobile":"9876543210","job_id":"sales-consultant"},
  "/finance/emi": {"principal":1500000,"down_payment":300000,"rate":9.25,"tenure_months":60},
}

ok = bad = 0
print(f"{'STATUS':<7} {'MS':>6}  METHOD PATH")
print("-"*72)
for ep in docs["endpoints"]:
    path = ep["path"].replace("{slug}","golf-gti").replace("{id}","hosur-road-showroom")
    if ep["method"] == "GET":
        if path == "/search": path += "?q=gti"
        if path == "/models": path += "?body=SUV&sort=price_asc&limit=2"
        if path == "/finance/quote": path += "?model=taigun-sport&down_payment=200000"
        status, payload, ms = call("GET", path)
    else:
        status, payload, ms = call("POST", path, SAMPLES.get(ep["path"], {}))
    good = status in (200, 201)
    ok, bad = (ok+1, bad) if good else (ok, bad+1)
    print(f"{'  OK  ' if good else ' FAIL '} {ms:6.1f}  {ep['method']:<5} {path}")
    if not good: print(f"         -> {payload}")

print("-"*72)
print(f"{ok} passed, {bad} failed\n")

# error-path checks
print("Error handling")
print("-"*72)
checks = [
    ("GET",  "/models/nope",        None, 404),
    ("GET",  "/outlets/nope",       None, 404),
    ("GET",  "/careers/jobs/nope",  None, 404),
    ("GET",  "/bogus",              None, 404),
    ("GET",  "/search",             None, 422),
    ("POST", "/leads/contact",      {},   422),
    ("POST", "/careers/apply",      {"name":"A","email":"a@b.com","mobile":"9876543210","job_id":"ghost"}, 422),
    ("POST", "/bogus",              {},   404),
]
for method, path, body, want in checks:
    status, payload, _ = call(method, path, body)
    mark = "  OK  " if status == want else " FAIL "
    if status != want: bad += 1
    print(f"{mark} expected {want}, got {status}  {method} {path}")
print("-"*72)
print("ALL GREEN" if bad == 0 else f"{bad} FAILURES")
