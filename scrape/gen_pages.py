# -*- coding: utf-8 -*-
import os

HEAD = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Volkswagen Elite Motors</title>
<meta name="description" content="{desc}">
<meta name="robots" content="{robots}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;700;800;900&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/elite.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><circle cx='16' cy='16' r='14' fill='none' stroke='%2300B0F0' stroke-width='2'/><text x='16' y='21' font-size='11' font-family='sans-serif' font-weight='bold' fill='%2300B0F0' text-anchor='middle'>VW</text></svg>">
</head>
<body>
'''

FOOT = '''
<script src="/assets/js/core.js"></script>
</body>
</html>
'''

def legal_section(title, crumb, blocks):
    items = "\n".join(
        f'      <div class="acc-item{" open" if i == 0 else ""}">\n'
        f'        <button class="acc-head">{h} <span class="acc-ico"></span></button>\n'
        f'        <div class="acc-body"><div><p>{b}</p></div></div>\n'
        f'      </div>' for i, (h, b) in enumerate(blocks))
    return f'''
<header class="phead">
  <div class="wrap">
    <div class="crumbs"><a href="/">Home</a> / <span>{crumb}</span></div>
    <div class="eyebrow">Legal</div>
    <h1 class="h-lg">{title}</h1>
    <p class="lede">Last updated 31 August 2026. This is a demonstration website built for Volkswagen Elite Motors.</p>
  </div>
</header>

<section class="section">
  <div class="wrap" style="max-width:900px">
{items}
  </div>
</section>
'''

PAGES = {}

# ---------- 404 ----------
PAGES["404.html"] = HEAD.format(
    title="Page not found", desc="The page you were looking for is not here.", robots="noindex"
) + '''
<section class="section" style="min-height:78vh;display:grid;place-items:center;text-align:center;padding-top:calc(var(--nav-h) + 60px)">
  <div class="wrap">
    <div class="eyebrow center">Error 404</div>
    <h1 class="h-xl grad-text" style="margin:22px 0 20px">Wrong turn.</h1>
    <p class="lede" style="margin:0 auto 38px">That page has left the showroom floor. Let's get you back on the road.</p>
    <div style="display:flex;gap:14px;justify-content:center;flex-wrap:wrap">
      <a class="btn btn-lg" href="/">Back to Home</a>
      <a class="btn btn-lg btn-ghost" href="/models.html">Browse the Range</a>
    </div>
  </div>
</section>
''' + FOOT

# ---------- terms ----------
PAGES["terms.html"] = HEAD.format(
    title="Terms & Conditions", desc="Terms and conditions for the Volkswagen Elite Motors website.", robots="index"
) + legal_section("Terms &amp; Conditions", "Terms", [
    ("Using this website",
     "By accessing this website you agree to these terms. Volkswagen Elite Motors is an authorised Volkswagen dealership operating in Bengaluru, Karnataka. This site is provided for information and enquiry purposes."),
    ("Vehicle information and pricing",
     "Actual features, accessories and specification may vary depending on variant. Prices shown are indicative ex-showroom Bengaluru and exclude registration, insurance, road tax and accessories. Prices, offers and specifications are subject to change without notice. Please contact the dealership for confirmed on-road pricing and availability."),
    ("Images and colours",
     "Vehicle images are for illustration only. Paint colours reproduced on screen may differ from the actual finish. Alloy wheels, trim and equipment shown may not be available on all variants."),
    ("Offers",
     "Offers are valid for the period stated, apply to select variants and cannot be combined unless expressly stated. All offers are subject to stock availability and to the terms set by Volkswagen India and the participating finance or insurance partner."),
    ("Finance calculations",
     "The finance calculator provides an indicative EMI using a standard reducing-balance method. It is not an offer of credit. Final rates, processing fees and eligibility are determined by the lending partner based on your credit profile."),
    ("Enquiries and test drives",
     "Submitting an enquiry does not guarantee a booking, an allocation or a delivery date. A representative will contact you to confirm availability."),
    ("Liability",
     "While we take care to keep information accurate, Volkswagen Elite Motors accepts no liability for errors, omissions or for decisions taken on the basis of information published here."),
    ("Governing law",
     "These terms are governed by the laws of India, with jurisdiction in the courts of Bengaluru, Karnataka."),
    ("Demonstration notice",
     "This site is a demonstration build. Form submissions are stored locally by the demo server and are not routed to a live CRM."),
]) + FOOT

# ---------- privacy ----------
PAGES["privacy.html"] = HEAD.format(
    title="Privacy Policy", desc="Privacy policy for the Volkswagen Elite Motors website.", robots="index"
) + legal_section("Privacy Policy", "Privacy", [
    ("What we collect",
     "When you submit a test drive, service, insurance, careers or contact form we collect the details you provide — typically your name, mobile number, email address, vehicle model of interest and any message or registration number you supply."),
    ("Why we collect it",
     "We use your details solely to respond to your enquiry: confirming a test drive slot, scheduling a service, preparing an insurance or finance quote, or reviewing a job application."),
    ("Who sees it",
     "Enquiry details are shared with the relevant Elite Motors department and, where required to fulfil your request, with Volkswagen India or the finance or insurance partner you asked us to quote. We do not sell your data."),
    ("Cookies and analytics",
     "This demonstration build sets no advertising or tracking cookies. Only technically necessary requests are made to the local server that hosts the site."),
    ("Retention",
     "Enquiry records are retained only as long as needed to service your request and to meet statutory record-keeping obligations."),
    ("Your rights",
     "You may ask us to confirm what personal data we hold about you, correct it, or delete it. Write to crm@vw-elitemotors.co.in and we will respond within a reasonable period."),
    ("Contact",
     "Volkswagen Elite Motors, SY No. 49/8-9, 10, Hosur Rd, Singasandra, Bengaluru, Karnataka 560100. Phone 080 4013 8004."),
    ("Demonstration notice",
     "This site is a demonstration build. Data submitted through its forms is written to a local JSON file on the machine running the demo server and is not transmitted anywhere else."),
]) + FOOT

for name, html in PAGES.items():
    path = os.path.join("web", name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"wrote web/{name}  ({len(html)} bytes)")
