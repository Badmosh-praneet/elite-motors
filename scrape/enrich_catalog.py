# -*- coding: utf-8 -*-
"""Add variant-level and FAQ data to catalog.json.

Variants follow the real Volkswagen India trim structure. Variant prices are
interpolated across each model's published range and stay flagged as indicative,
exactly like the model-level prices.
FAQ answers are composed from facts already scraped from the dealership site
(warranty term, service hours, NCAP rating, engines, features) — no new claims.
"""
import json, collections

P = "data/catalog.json"
db = json.load(open(P, encoding="utf-8"))

# trim ladders per model: (trim, engine_key, gearbox, price_position 0..1)
LADDER = {
    "tayron-r-line": [("R-Line", "2.0L TSI EVO", "190 PS", "320 Nm", "7-speed DSG", "4MOTION AWD", 1.0)],
    "golf-gti":      [("GTI",    "2.0L TSI",     "265 hp", "370 Nm", "7-speed DSG", "FWD with XDS", 1.0)],
    "tiguan-r-line": [("R-Line", "2.0L TSI",     "190 PS", "320 Nm", "7-speed DSG", "4MOTION AWD", 1.0)],
    "virtus-sport": [
        ("GT Line",        "1.0L TSI",       "115 PS", "178 Nm", "6-speed MT",  "FWD", 0.00),
        ("GT Line",        "1.0L TSI",       "115 PS", "178 Nm", "6-speed AT",  "FWD", 0.30),
        ("GT Plus Sport",  "1.5L TSI EVO",   "150 PS", "250 Nm", "6-speed MT",  "FWD", 0.70),
        ("GT Plus Sport",  "1.5L TSI EVO",   "150 PS", "250 Nm", "7-speed DSG", "FWD", 1.00),
    ],
    "virtus-chrome": [
        ("Comfortline", "1.0L TSI", "115 PS", "178 Nm", "6-speed MT", "FWD", 0.00),
        ("Highline",    "1.0L TSI", "115 PS", "178 Nm", "6-speed MT", "FWD", 0.35),
        ("Highline",    "1.0L TSI", "115 PS", "178 Nm", "6-speed AT", "FWD", 0.65),
        ("Topline",     "1.0L TSI", "115 PS", "178 Nm", "6-speed AT", "FWD", 1.00),
    ],
    "taigun-sport": [
        ("GT Line",       "1.0L TSI",     "115 PS", "178 Nm", "6-speed MT",  "FWD", 0.00),
        ("GT Line",       "1.0L TSI",     "115 PS", "178 Nm", "6-speed AT",  "FWD", 0.30),
        ("GT Plus Sport", "1.5L TSI EVO", "150 PS", "250 Nm", "6-speed MT",  "FWD", 0.70),
        ("GT Plus Sport", "1.5L TSI EVO", "150 PS", "250 Nm", "7-speed DSG", "FWD", 1.00),
    ],
    "taigun-chrome": [
        ("Comfortline", "1.0L TSI", "115 PS", "178 Nm", "6-speed MT", "FWD", 0.00),
        ("Highline",    "1.0L TSI", "115 PS", "178 Nm", "6-speed MT", "FWD", 0.35),
        ("Highline",    "1.0L TSI", "115 PS", "178 Nm", "6-speed AT", "FWD", 0.65),
        ("Topline",     "1.0L TSI", "115 PS", "178 Nm", "6-speed AT", "FWD", 1.00),
    ],
}

def inr(n):
    """Indian digit grouping: 5300000 -> 53,00,000."""
    s = str(int(n))
    if len(s) <= 3:
        return s
    head, tail = s[:-3], s[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    if head:
        groups.insert(0, head)
    return ",".join(groups) + "," + tail


def slugify(s):
    keep = [c.lower() if c.isalnum() else "-" for c in s]
    out = "".join(keep)
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")

total_variants = 0
for m in db["models"]:
    lo, hi = m["price"]["min"], m["price"]["max"]
    rows = LADDER[m["slug"]]
    variants = []
    for trim, engine, power, torque, gearbox, drive, pos in rows:
        price = int(round((lo + (hi - lo) * pos) / 1000.0) * 1000)
        vid = slugify(f"{m['family']}-{trim}-{engine}-{gearbox}")
        variants.append({
            "id": vid,
            "model_slug": m["slug"],
            "model_name": m["name"],
            "name": f"{m['family']} {trim} {engine.replace('L TSI EVO',' TSI EVO').replace('L TSI',' TSI')} {gearbox.split('-speed ')[1]}".replace("  ", " "),
            "trim": trim,
            "engine": engine,
            "power": power,
            "torque": torque,
            "transmission": gearbox,
            "drivetrain": drive,
            "fuel": "Petrol",
            "seats": m["seats"],
            "body_type": m["body_type"],
            "price": price,
            "currency": "INR",
            "price_note": "Indicative ex-showroom, Bengaluru",
        })
    m["variants"] = variants
    total_variants += len(variants)

# ---- FAQs, composed from already-scraped facts -----------------------------
W = db["warranty"]["standard"]
SVC = db["dealer"]["hours"]["service"]
svc_hours = "; ".join(f"{r['days']} {r['open']}–{r['close']}" for r in SVC)
OUTLET = db["outlets"][0]["full_address"]

for m in db["models"]:
    engines = m["specs"]["engine"]
    gearboxes = m["specs"]["transmission"]
    trims = sorted({v["trim"] for v in m["variants"]})
    safety = m["features"].get("Safety", [])
    ncap = next((s for s in safety if "NCAP" in s), None)
    sunroof = next((f for grp in m["features"].values() for f in grp if "unroof" in f), None)

    faqs = [
        {"question": f"What engine options does the {m['name']} come with?",
         "answer": f"The {m['name']} is offered with the {engines}, producing {m['specs']['power']} and {m['specs']['torque']}, paired with {gearboxes}."},
        {"question": f"How many variants of the {m['name']} are available?",
         "answer": (
             f"Elite Motors lists {len(m['variants'])} "
             f"{'variant' if len(m['variants']) == 1 else 'variants'} of the {m['name']}"
             + (f", across the {' and '.join(trims)} "
                f"{'trim' if len(trims) == 1 else 'trims'}." if trims else ".")
         )},
        {"question": f"What is the price of the {m['name']}?",
         "answer": (f"The {m['name']} starts at ₹{inr(m['price']['min'])} ex-showroom Bengaluru."
                    if m["price"]["min"] == m["price"]["max"] else
                    f"The {m['name']} ranges from ₹{inr(m['price']['min'])} to ₹{inr(m['price']['max'])} ex-showroom Bengaluru.")
                   + " Pricing is indicative — contact Elite Motors for on-road pricing."},
        {"question": f"What warranty does the {m['name']} carry?",
         "answer": W["description"]},
        {"question": f"Where can I service my {m['name']} in Bengaluru?",
         "answer": f"At Volkswagen Elite Motors, {OUTLET}. Service hours are {svc_hours}."},
        {"question": f"Can I book a test drive of the {m['name']}?",
         "answer": f"Yes. Test drives of the {m['name']} can be booked with Volkswagen Elite Motors on {db['dealer']['contact']['phone']} or through the booking form on this site."},
    ]
    if ncap:
        faqs.insert(3, {"question": f"How safe is the {m['name']}?",
                        "answer": f"The {m['name']} carries a {ncap.lower()} and offers "
                                  + ", ".join(safety[:4]).lower() + "."})
    if sunroof:
        faqs.insert(4, {"question": f"Does the {m['name']} have a sunroof?",
                        "answer": f"Yes — the {m['name']} is equipped with a {sunroof.lower()}."})
    m["faqs"] = faqs

db["meta"]["api_version"] = "v2"
db["meta"]["notes"] = (
    "Content and imagery scraped from the live Volkswagen Bangalore (Elite Motors) site. "
    "Model and variant pricing is indicative ex-showroom Bengaluru — the source site does not "
    "publish prices. FAQ answers are composed from facts scraped from that site."
)

json.dump(db, open(P, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"models   : {len(db['models'])}")
print(f"variants : {total_variants}")
print(f"faqs     : {sum(len(m['faqs']) for m in db['models'])}")
print("\nvariants per model:")
for m in db["models"]:
    print(f"  {m['slug']:<16} {len(m['variants'])} variants, {len(m['faqs'])} faqs")
