/* ==========================================================================
   VOLKSWAGEN ELITE MOTORS — core runtime
   Shared across every page: API client, chrome, motion, forms.
   ========================================================================== */

const Elite = (() => {
  'use strict';

  const API = '/api';

  /* -- API client --------------------------------------------------------- */

  async function api(path, options = {}) {
    const res = await fetch(API + path, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });
    let body;
    try { body = await res.json(); } catch { body = null; }
    if (!res.ok) {
      const err = new Error((body && body.error && body.error.message) || `Request failed (${res.status})`);
      err.status = res.status;
      err.detail = body && body.error && body.error.detail;
      throw err;
    }
    return body;
  }

  const get = (path) => api(path);
  const post = (path, data) => api(path, { method: 'POST', body: JSON.stringify(data) });

  /* -- formatting --------------------------------------------------------- */

  function inr(n) {
    if (n == null || isNaN(n)) return '—';
    if (n >= 1e7) return `₹${(n / 1e7).toFixed(2)} Cr`;
    if (n >= 1e5) return `₹${(n / 1e5).toFixed(2)} L`;
    return `₹${Math.round(n).toLocaleString('en-IN')}`;
  }

  function inrFull(n) {
    if (n == null || isNaN(n)) return '—';
    return `₹${Math.round(n).toLocaleString('en-IN')}`;
  }

  function priceLabel(price) {
    if (!price) return '—';
    return price.min === price.max ? inr(price.min) : `${inr(price.min)} – ${inr(price.max)}`;
  }

  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));

  const initials = (name) => String(name || '').trim().split(/\s+/).slice(0, 2).map((w) => w[0]).join('').toUpperCase();

  /* -- icons -------------------------------------------------------------- */

  const ICON = {
    phone: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg>',
    arrow: '<svg class="btn-arrow" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>',
    up: '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M5 12l7-7 7 7"/></svg>',
    wa: '<svg width="19" height="19" viewBox="0 0 24 24" fill="currentColor"><path d="M17.5 14.4c-.3-.2-1.7-.9-2-1-.3-.1-.5-.1-.7.1-.2.3-.7 1-.9 1.2-.2.2-.3.2-.6.1-.3-.2-1.2-.5-2.3-1.4-.9-.8-1.4-1.7-1.6-2-.2-.3 0-.5.1-.6l.5-.5c.1-.2.2-.3.3-.5v-.5c0-.2-.7-1.6-.9-2.2-.2-.5-.5-.5-.7-.5h-.5c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.4s1 2.8 1.2 3c.1.2 2 3.1 5 4.3.7.3 1.2.5 1.6.6.7.2 1.3.2 1.8.1.6-.1 1.7-.7 1.9-1.4.2-.7.2-1.3.2-1.4-.1-.1-.3-.2-.6-.3zM12 2a10 10 0 0 0-8.6 15L2 22l5.2-1.4A10 10 0 1 0 12 2zm0 18.2c-1.5 0-3-.4-4.3-1.2l-.3-.2-3.1.8.8-3-.2-.3A8.2 8.2 0 1 1 12 20.2z"/></svg>',
    fb: '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M14 9h3V6h-3c-2.2 0-4 1.8-4 4v2H8v3h2v7h3v-7h3l1-3h-4v-2c0-.6.4-1 1-1z"/></svg>',
    ig: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="3.6"/><circle cx="17.4" cy="6.6" r="1" fill="currentColor"/></svg>',
    yt: '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M22 12s0-3.2-.4-4.7a2.5 2.5 0 0 0-1.7-1.8C18.3 5 12 5 12 5s-6.3 0-7.9.5a2.5 2.5 0 0 0-1.7 1.8C2 8.8 2 12 2 12s0 3.2.4 4.7c.2.9.9 1.6 1.7 1.8C5.7 19 12 19 12 19s6.3 0 7.9-.5a2.5 2.5 0 0 0 1.7-1.8c.4-1.5.4-4.7.4-4.7zM10 15V9l5.2 3-5.2 3z"/></svg>',
    li: '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M6.9 8H4v12h2.9V8zM5.4 3.5a1.7 1.7 0 1 0 0 3.4 1.7 1.7 0 0 0 0-3.4zM20 13.4c0-3.2-1.7-4.7-4-4.7-1.8 0-2.6 1-3.1 1.7V8H10v12h2.9v-6.7c0-1.4.8-2.2 1.9-2.2s1.8.7 1.8 2.2V20H20v-6.6z"/></svg>',
    pin: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></svg>',
    clock: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    mail: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2.5" y="4.5" width="19" height="15" rx="2"/><path d="m3 6 9 7 9-7"/></svg>',
    wrench: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a4 4 0 1 0 5 5L21 12l-9 9-3-3 9-9z"/><path d="M6 18 3 21"/></svg>',
    spray: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><rect x="7" y="9" width="8" height="12" rx="2"/><path d="M9 9V5a2 2 0 0 1 2-2h1M18 5h.01M20 8h.01M18 11h.01M21 12h.01"/></svg>',
    chip: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M10 3v4M14 3v4M10 17v4M14 17v4M3 10h4M3 14h4M17 10h4M17 14h4"/></svg>',
    truck: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M2 7h11v9H2zM13 10h4l3 3v3h-7z"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/></svg>',
    box: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="m3 8 9-5 9 5v8l-9 5-9-5z"/><path d="m3 8 9 5 9-5M12 13v8"/></svg>',
    shield: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l8 3v6c0 4.5-3.2 8.3-8 9.5-4.8-1.2-8-5-8-9.5V6z"/><path d="m9 12 2 2 4-4"/></svg>',
    star: '<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="m12 2 3 6.6 7 .8-5.2 4.8 1.4 7L12 17.8 5.8 21.2l1.4-7L2 9.4l7-.8z"/></svg>',
    plus: '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>',
    close: '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>',
    left: '<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>',
    right: '<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/></svg>',
  };

  /* -- navigation --------------------------------------------------------- */

  const NAV = [
    { label: 'Models', href: '/models.html' },
    { label: 'Service', href: '/service.html' },
    { label: 'Finance', href: '/finance.html' },
    { label: 'Rentals', href: '/rent.html' },
    { label: 'Outlets', href: '/outlets.html' },
    { label: 'About', href: '/about.html' },
    { label: 'Careers', href: '/careers.html' },
    { label: 'API', href: '/api-explorer.html' },
  ];

  const DEALER_FALLBACK = {
    contact: {
      phone: '080 4013 8004',
      phone_e164: '+918040138004',
      sales_email: 'crm@vw-elitemotors.co.in',
      service_email: 'crhead@vw-elitemotors.co.in',
    },
    hours: {
      sales: [{ days: 'Mon - Sat', open: '09:45', close: '19:10' }, { days: 'Sun', open: '10:00', close: '19:10' }],
      service: [{ days: 'Mon - Sat', open: '08:45', close: '18:30' }, { days: 'Sun', open: '08:45', close: '18:30' }],
    },
  };

  function brandMark() {
    return `<a class="brand" href="/" aria-label="Volkswagen Elite Motors home">
      <img class="brand-mark" src="/assets/img/vw-logo.png" alt="Volkswagen Logo" width="42" height="42">
      <span class="brand-txt"><b>Elite Motors</b><span>Volkswagen</span></span>
    </a>`;
  }

  function mountNav() {
    const here = location.pathname.replace(/\/$/, '') || '/index.html';
    const isActive = (href) => here === href || (href !== '/' && here.startsWith(href.replace('.html', '')));

    const links = NAV.map((n) => {
      const on = isActive(n.href);
      return `<a class="nav-link${on ? ' active' : ''}" href="${n.href}"${on ? ' aria-current="page"' : ''}>${n.label}</a>`;
    }).join('');

    const nav = document.createElement('header');
    nav.className = 'nav';
    nav.innerHTML = `<div class="nav-inner">
      ${brandMark()}
      <nav class="nav-links" aria-label="Primary">${links}</nav>
      <div class="nav-cta">
        <a class="nav-phone" href="tel:+918040138004">${ICON.phone}<span>080 4013 8004</span></a>
        <a class="btn btn-sm" href="/contact.html#test-drive">Book a Test Drive</a>
        <button class="burger" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
      </div>
    </div>`;
    document.body.prepend(nav);

    const drawer = document.createElement('div');
    drawer.className = 'drawer';
    drawer.innerHTML = `<nav>${NAV.map((n) => `<a href="${n.href}">${n.label}</a>`).join('')}
      <a href="/contact.html#test-drive">Book a Test Drive</a>
      <a href="tel:+918040138004">080 4013 8004</a></nav>`;
    document.body.appendChild(drawer);

    const burger = nav.querySelector('.burger');
    const setDrawer = (open) => {
      drawer.classList.toggle('open', open);
      burger.classList.toggle('open', open);
      burger.setAttribute('aria-expanded', String(open));
      drawer.setAttribute('aria-hidden', String(!open));
      document.body.style.overflow = open ? 'hidden' : '';
      if (open) drawer.querySelector('a').focus();
      else burger.focus();
    };

    drawer.setAttribute('aria-hidden', 'true');
    burger.addEventListener('click', () => setDrawer(!drawer.classList.contains('open')));
    drawer.addEventListener('click', (e) => { if (e.target.tagName === 'A') setDrawer(false); });

    // Escape closes the drawer, and focus stays inside it while it is open.
    document.addEventListener('keydown', (e) => {
      if (!drawer.classList.contains('open')) return;
      if (e.key === 'Escape') { setDrawer(false); return; }
      if (e.key !== 'Tab') return;
      const focusables = [...drawer.querySelectorAll('a')];
      const first = focusables[0], last = focusables[focusables.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });

    const onScroll = () => nav.classList.toggle('stuck', window.scrollY > 40);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  function hoursHtml(rows) {
    return rows.map((r) => `<span>${r.days}: ${r.open} – ${r.close}</span>`).join('<br>');
  }

  function mountFooter(dealer) {
    const d = dealer || DEALER_FALLBACK;
    const c = d.contact;
    const el = document.createElement('footer');
    el.className = 'footer';
    el.innerHTML = `<div class="wrap">
      <div class="foot-grid">
        <div>
          ${brandMark()}
          <p class="lede" style="margin-top:20px;font-size:.92rem">An authorised Volkswagen dealership on Hosur Road, Bengaluru — built around the highest level of customer satisfaction.</p>
          <div class="socials">
            <a class="social" href="https://www.facebook.com/" target="_blank" rel="noopener noreferrer" aria-label="Facebook">${ICON.fb}</a>
            <a class="social" href="https://www.instagram.com/" target="_blank" rel="noopener noreferrer" aria-label="Instagram">${ICON.ig}</a>
            <a class="social" href="https://www.youtube.com/" target="_blank" rel="noopener noreferrer" aria-label="YouTube">${ICON.yt}</a>
            <a class="social" href="https://www.linkedin.com/" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">${ICON.li}</a>
          </div>
        </div>
        <div>
          <div class="foot-h">Explore</div>
          <ul class="foot-links">
            <li><a href="/models.html">All Models</a></li>
            <li><a href="/about.html">About Us</a></li>
            <li><a href="/outlets.html">Outlets</a></li>
            <li><a href="/finance.html">Finance Calculator</a></li>
            <li><a href="/careers.html">Careers</a></li>
            <li><a href="/contact.html">Contact</a></li>
          </ul>
        </div>
        <div>
          <div class="foot-h">Ownership</div>
          <ul class="foot-links">
            <li><a href="/service.html">Book a Service</a></li>
            <li><a href="/service.html#packages">Service Value Packages</a></li>
            <li><a href="/service.html#warranty">Extended Warranty</a></li>
            <li><a href="/service.html#roadside">Roadside Assistance</a></li>
            <li><a href="/service.html#insurance">Insurance</a></li>
            <li><a href="/docs">API Docs (Swagger)</a></li>
          </ul>
        </div>
        <div>
          <div class="foot-h">Visit Us</div>
          <div class="foot-hours">
            <div class="foot-hour"><b>${ICON.pin} Showroom &amp; Service</b>
              <span>SY No. 49/8-9, 10, Hosur Rd, Singasandra, Bengaluru, Karnataka 560100</span></div>
            <div class="foot-hour"><b>${ICON.clock} Sales</b><span>${hoursHtml(d.hours.sales)}</span></div>
            <div class="foot-hour"><b>${ICON.clock} Service</b><span>${hoursHtml(d.hours.service)}</span></div>
            <div class="foot-hour"><b>${ICON.phone} Contact</b>
              <span><a href="tel:${c.phone_e164}">${c.phone}</a><br><a href="mailto:${c.sales_email}">${c.sales_email}</a></span></div>
          </div>
        </div>
      </div>

      <div class="foot-word" aria-hidden="true">ELITE MOTORS</div>

      <div class="foot-bot">
        <span>© 2026 Volkswagen Elite Motors. All rights reserved.</span>
        <div class="foot-legal">
          <a href="/terms.html">Terms &amp; Conditions</a>
          <a href="/privacy.html">Privacy Policy</a>
          <a href="/api-explorer.html">API v1</a>
        </div>
      </div>
      <p class="disclaimer">Actual features, accessories and specification may vary depending on variant. Prices shown are indicative ex-showroom Bengaluru — please contact the dealership for on-road pricing and complete details. This is a demonstration site built for Volkswagen Elite Motors.</p>
    </div>`;
    document.body.appendChild(el);
  }

  function mountFabs() {
    const el = document.createElement('div');
    el.className = 'fabs';
    el.innerHTML = `
      <button class="fab" id="toTop" aria-label="Back to top">${ICON.up}</button>`;
    document.body.appendChild(el);

    const btn = el.querySelector('#toTop');
    btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
    window.addEventListener('scroll', () => btn.classList.toggle('show', window.scrollY > 600), { passive: true });
  }

  /* -- page chrome -------------------------------------------------------- */

  function skipLink() {
    const target = document.querySelector('main') || document.querySelector('.phead, .hero');
    if (!target) return;
    if (!target.id) target.id = 'main';
    target.setAttribute('tabindex', '-1');

    const link = document.createElement('a');
    link.className = 'skip-link';
    link.href = `#${target.id}`;
    link.textContent = 'Skip to content';
    link.addEventListener('click', () => setTimeout(() => target.focus(), 0));
    document.body.prepend(link);
  }

  function scrollProgress() {
    const bar = document.createElement('div');
    bar.className = 'progress';
    bar.setAttribute('aria-hidden', 'true');
    document.body.appendChild(bar);

    let ticking = false;
    const paint = () => {
      ticking = false;
      const max = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.transform = `scaleX(${max > 0 ? Math.min(1, window.scrollY / max) : 0})`;
    };
    window.addEventListener('scroll', () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(paint);
    }, { passive: true });
    window.addEventListener('resize', paint, { passive: true });
    paint();
  }

  /* -- motion ------------------------------------------------------------- */

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function preloader() {
    const el = document.createElement('div');
    el.id = 'preloader';
    el.innerHTML = `<div class="pre-inner">
      <div class="pre-ring">
        <svg viewBox="0 0 92 92"><circle class="bg" cx="46" cy="46" r="42"/><circle class="fg" cx="46" cy="46" r="42"/></svg>
        <img class="pre-logo-img" src="/assets/img/vw-logo.png" alt="Volkswagen Logo" width="56" height="56">
      </div>
      <div class="pre-label">Elite Motors</div>
      <div class="pre-pct">0%</div>
    </div>`;
    document.body.appendChild(el);

    const arc = el.querySelector('.fg');
    const pct = el.querySelector('.pre-pct');

    /* This used to run a fixed random timer with no connection to the page, so
       every reload sat on a black screen for a second or more however fast the
       page was actually ready. Now it creeps to 90% for feedback and finishes
       on the real load event — with a floor so it cannot flash, and a ceiling
       so a slow asset can never trap anyone behind it. */
    const MIN_MS = 240;
    const MAX_MS = 2500;
    const start = performance.now();
    let n = 0;
    let finished = false;

    const paint = (value) => {
      n = value;
      arc.style.strokeDashoffset = String(264 - (264 * n) / 100);
      pct.textContent = `${Math.round(n)}%`;
    };

    const creep = setInterval(() => {
      if (!finished) paint(Math.min(90, n + Math.random() * 14 + 5));
    }, 90);

    const finish = () => {
      if (finished) return;
      finished = true;
      clearInterval(creep);
      paint(100);
      setTimeout(() => {
        el.classList.add('done');
        document.body.classList.add('loaded');
        setTimeout(() => el.remove(), 800);
      }, Math.max(0, MIN_MS - (performance.now() - start)));
    };

    if (document.readyState === 'complete') finish();
    else window.addEventListener('load', finish, { once: true });
    setTimeout(finish, MAX_MS);
  }

  function cursor() {
    if (reduced || window.matchMedia('(pointer: coarse)').matches) return;
    const dot = document.createElement('div');
    const ring = document.createElement('div');
    dot.className = 'cursor-dot';
    ring.className = 'cursor-ring';
    document.body.append(dot, ring);

    let rx = 0, ry = 0, tx = 0, ty = 0;
    document.addEventListener('mousemove', (e) => {
      tx = e.clientX; ty = e.clientY;
      dot.style.transform = `translate(${tx}px, ${ty}px)`;
    });
    (function loop() {
      rx += (tx - rx) * 0.16;
      ry += (ty - ry) * 0.16;
      ring.style.transform = `translate(${rx}px, ${ry}px)`;
      requestAnimationFrame(loop);
    })();

    const hot = 'a, button, .pill, .swatch, .gal-item, input[type=range], .card, .api-ep, .acc-head';
    document.addEventListener('mouseover', (e) => {
      if (e.target.closest(hot)) ring.classList.add('grow');
    });
    document.addEventListener('mouseout', (e) => {
      if (e.target.closest(hot)) ring.classList.remove('grow');
    });
  }

  function reveal(scope = document) {
    // Every page calls reveal() after injecting content, so hanging the other
    // enhancements off it keeps dynamic content in step without new call sites.
    splitHeadings(scope);   // must run first — it creates [data-reveal] nodes
    sheen(scope);
    magnetic(scope);

    const items = [...scope.querySelectorAll('[data-reveal]:not(.in)')];
    if (!items.length) return;

    if (reduced || !('IntersectionObserver' in window)) {
      items.forEach((el) => el.classList.add('in'));
      return;
    }

    // Choreograph siblings. Items that come into view together get an
    // incremental delay so a grid arrives as a sequence rather than a slab.
    // Anything the page already staggered by hand is left alone.
    const groups = new Map();
    items.forEach((el) => {
      if (el.style.getPropertyValue('--d')) return;
      const parent = el.parentElement;
      if (!parent) return;
      if (!groups.has(parent)) groups.set(parent, []);
      groups.get(parent).push(el);
    });
    groups.forEach((list) => {
      if (list.length < 2) return;
      list.forEach((el, idx) => {
        el.style.setProperty('--d', `${Math.min(idx, 6) * 70}ms`);  // cap the tail
      });
    });

    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) { entry.target.classList.add('in'); io.unobserve(entry.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    items.forEach((el) => io.observe(el));

    /* Failsafe. [data-reveal] starts at opacity:0, so if the observer never
       delivers — a throttled/background tab, a paused compositor, a browser
       that reports IO support but stalls it — the page would read as blank.
       Sweep anything that has reached the viewport and reveal it directly. */
    let sweeping = false;
    const sweep = () => {
      sweeping = false;
      let remaining = 0;
      items.forEach((el) => {
        if (el.classList.contains('in')) return;
        if (el.getBoundingClientRect().top < window.innerHeight * 1.05) {
          el.classList.add('in');
          io.unobserve(el);
        } else { remaining++; }
      });
      if (!remaining) {
        window.removeEventListener('scroll', onMove);
        window.removeEventListener('resize', onMove);
      }
    };
    const onMove = () => {
      if (sweeping) return;
      sweeping = true;
      setTimeout(sweep, 150);
    };

    window.addEventListener('scroll', onMove, { passive: true });
    window.addEventListener('resize', onMove, { passive: true });
    setTimeout(sweep, 1400);
  }

  function counters(scope = document) {
    const els = [...scope.querySelectorAll('[data-count]:not([data-counted])')];
    if (!els.length) return;

    const finalValue = (el) => {
      const target = parseFloat(el.getAttribute('data-count')) || 0;
      return target.toLocaleString('en-IN') + (el.getAttribute('data-suffix') || '');
    };

    const settle = (el) => {
      el.setAttribute('data-counted', '1');
      el.textContent = finalValue(el);
    };

    const run = (el) => {
      el.setAttribute('data-counted', '1');
      const target = parseFloat(el.getAttribute('data-count')) || 0;
      const suffix = el.getAttribute('data-suffix') || '';
      if (reduced) { el.textContent = finalValue(el); return; }
      const dur = 1700;
      const t0 = performance.now();
      (function step(now) {
        const p = Math.min(1, (now - t0) / dur);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(target * eased).toLocaleString('en-IN') + suffix;
        if (p < 1) requestAnimationFrame(step);
      })(t0);
    };

    if (reduced || !('IntersectionObserver' in window)) {
      els.forEach(settle);
      return;
    }

    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        io.unobserve(entry.target);
        run(entry.target);
      });
    }, { threshold: 0.5 });
    els.forEach((el) => io.observe(el));

    /* Same failsafe as reveal(): a stalled observer would otherwise leave every
       statistic reading "0". Settle to the final number without animating. */
    let sweeping = false;
    const sweep = () => {
      sweeping = false;
      let remaining = 0;
      els.forEach((el) => {
        if (el.hasAttribute('data-counted')) return;
        if (el.getBoundingClientRect().top < window.innerHeight) {
          io.unobserve(el);
          settle(el);
        } else { remaining++; }
      });
      if (!remaining) {
        window.removeEventListener('scroll', onMove);
        window.removeEventListener('resize', onMove);
      }
    };
    const onMove = () => {
      if (sweeping) return;
      sweeping = true;
      setTimeout(sweep, 150);
    };

    window.addEventListener('scroll', onMove, { passive: true });
    window.addEventListener('resize', onMove, { passive: true });
    setTimeout(sweep, 1400);
  }

  /**
   * Split a heading on its <br> tags into masked lines that rise in sequence.
   * Marked [data-reveal="text"] so the existing reveal observer — and its
   * failsafe sweep — drive it, which means it can never be left hidden.
   */
  function splitHeadings(scope = document) {
    const targets = scope.querySelectorAll(
      '.hero-title, .phead h1, .section-head h2, .m-hero h1'
    );
    targets.forEach((el) => {
      if (el.dataset.split) return;
      el.dataset.split = '1';

      const parts = el.innerHTML.split(/<br\s*\/?>/i).map((s) => s.trim()).filter(Boolean);
      if (!parts.length) return;

      // The <br> that separated the lines carried a word boundary. Without it
      // textContent runs the lines together ("Volkswagenwe"), so keep a space —
      // it collapses visually inside a block, but assistive tech still hears it.
      el.innerHTML = parts
        .map((line, i) => {
          const gap = i < parts.length - 1 ? ' ' : '';
          return `<span class="ln"><i style="--i:${i}">${line}${gap}</i></span>`;
        })
        .join('');
      el.setAttribute('data-reveal', 'text');
    });
  }

  /** Pointer-tracked highlight on cards. */
  function sheen(scope = document) {
    if (reduced || window.matchMedia('(pointer: coarse)').matches) return;
    scope.querySelectorAll('.card').forEach((card) => {
      if (card.dataset.sheen) return;
      card.dataset.sheen = '1';
      card.addEventListener('pointermove', (e) => {
        const r = card.getBoundingClientRect();
        card.style.setProperty('--mx', `${((e.clientX - r.left) / r.width) * 100}%`);
        card.style.setProperty('--my', `${((e.clientY - r.top) / r.height) * 100}%`);
      });
    });
  }

  /** Buttons lean a few pixels toward the pointer. */
  function magnetic(scope = document) {
    if (reduced || window.matchMedia('(pointer: coarse)').matches) return;
    scope.querySelectorAll('.btn:not(.btn-block)').forEach((btn) => {
      if (btn.dataset.mag) return;
      btn.dataset.mag = '1';
      const strength = 0.22;
      btn.addEventListener('pointermove', (e) => {
        const r = btn.getBoundingClientRect();
        const dx = (e.clientX - (r.left + r.width / 2)) * strength;
        const dy = (e.clientY - (r.top + r.height / 2)) * strength;
        btn.style.transform = `translate(${dx}px, ${dy - 2}px)`;
      });
      btn.addEventListener('pointerleave', () => { btn.style.transform = ''; });
    });
  }

  function tilt(scope = document) {
    if (reduced || window.matchMedia('(pointer: coarse)').matches) return;
    scope.querySelectorAll('.tilt').forEach((el) => {
      if (el.dataset.tiltOn) return;
      el.dataset.tiltOn = '1';
      el.addEventListener('mousemove', (e) => {
        const r = el.getBoundingClientRect();
        const px = (e.clientX - r.left) / r.width - 0.5;
        const py = (e.clientY - r.top) / r.height - 0.5;
        el.style.transform = `perspective(1000px) rotateX(${-py * 7}deg) rotateY(${px * 9}deg) translateY(-6px)`;
      });
      el.addEventListener('mouseleave', () => { el.style.transform = ''; });
    });
  }

  /* -- toasts ------------------------------------------------------------- */

  let toastHost;
  function toast(title, message, kind = '') {
    if (!toastHost) {
      toastHost = document.createElement('div');
      toastHost.className = 'toasts';
      document.body.appendChild(toastHost);
    }
    const el = document.createElement('div');
    el.className = `toast ${kind}`;
    el.innerHTML = `<div><b>${esc(title)}</b><p>${esc(message)}</p></div>`;
    toastHost.appendChild(el);
    setTimeout(() => {
      el.classList.add('out');
      setTimeout(() => el.remove(), 420);
    }, 5200);
  }

  /* -- lightbox ----------------------------------------------------------- */

  function lightbox(images, label = 'Image') {
    const el = document.createElement('div');
    el.className = 'lightbox';
    el.setAttribute('role', 'dialog');
    el.setAttribute('aria-modal', 'true');
    el.setAttribute('aria-label', `${label} gallery`);
    el.setAttribute('aria-hidden', 'true');
    el.innerHTML = `<button class="lb-close" aria-label="Close gallery">${ICON.close}</button>
      <button class="lb-nav lb-prev" aria-label="Previous image">${ICON.left}</button>
      <img alt="" hidden>
      <button class="lb-nav lb-next" aria-label="Next image">${ICON.right}</button>
      <p class="lb-count mono" aria-live="polite"></p>`;
    document.body.appendChild(el);

    const img = el.querySelector('img');
    const count = el.querySelector('.lb-count');
    const closeBtn = el.querySelector('.lb-close');
    let i = 0;
    let lastFocused = null;

    const show = (n) => {
      i = (n + images.length) % images.length;
      img.src = images[i];
      img.alt = `${label}, image ${i + 1} of ${images.length}`;
      img.hidden = false;
      count.textContent = `${i + 1} / ${images.length}`;
    };

    const close = () => {
      el.classList.remove('open');
      el.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
      if (lastFocused) lastFocused.focus();
    };

    closeBtn.addEventListener('click', close);
    el.querySelector('.lb-prev').addEventListener('click', (e) => { e.stopPropagation(); show(i - 1); });
    el.querySelector('.lb-next').addEventListener('click', (e) => { e.stopPropagation(); show(i + 1); });
    el.addEventListener('click', (e) => { if (e.target === el) close(); });

    document.addEventListener('keydown', (e) => {
      if (!el.classList.contains('open')) return;
      if (e.key === 'Escape') return close();
      if (e.key === 'ArrowLeft') return show(i - 1);
      if (e.key === 'ArrowRight') return show(i + 1);
      if (e.key !== 'Tab') return;
      // keep focus inside the dialog
      const f = [...el.querySelectorAll('button')];
      const first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });

    return (n) => {
      lastFocused = document.activeElement;
      show(n);
      el.classList.add('open');
      el.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
      closeBtn.focus();
    };
  }

  /* -- accordion ---------------------------------------------------------- */

  function accordion(scope = document) {
    scope.querySelectorAll('.acc-head').forEach((head) => {
      if (head.dataset.accOn) return;
      head.dataset.accOn = '1';
      head.addEventListener('click', () => {
        const item = head.closest('.acc-item');
        const open = item.classList.contains('open');
        item.parentElement.querySelectorAll('.acc-item.open').forEach((o) => o.classList.remove('open'));
        item.classList.toggle('open', !open);
      });
    });
  }

  /* -- forms -------------------------------------------------------------- */

  /**
   * Wire a form to an API endpoint.
   * Shows per-field messages from the API's 422 `detail` map.
   */
  function bindForm(form, endpoint, opts = {}) {
    if (!form) return;
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      form.querySelectorAll('.field.err').forEach((f) => f.classList.remove('err'));

      const btn = form.querySelector('[type=submit]');
      const label = btn ? btn.innerHTML : '';
      if (btn) { btn.disabled = true; btn.innerHTML = 'Sending…'; }

      const data = Object.fromEntries(new FormData(form).entries());
      if (opts.transform) opts.transform(data);

      try {
        const res = await post(endpoint, data);
        toast(res.message || 'Submitted', `${res.next_step || ''} Reference: ${res.reference}`.trim(), 'ok');
        form.reset();
        if (opts.onSuccess) opts.onSuccess(res);
      } catch (err) {
        if (err.status === 422 && err.detail) {
          Object.entries(err.detail).forEach(([name, msg]) => {
            const input = form.querySelector(`[name="${name}"]`);
            const field = input && input.closest('.field');
            if (field) {
              field.classList.add('err');
              let hint = field.querySelector('.field-msg');
              if (!hint) {
                hint = document.createElement('div');
                hint.className = 'field-msg';
                field.appendChild(hint);
              }
              hint.textContent = msg;
            }
          });
          toast('Check the form', 'Some fields need your attention.', 'err');
        } else {
          toast('Something went wrong', err.message, 'err');
        }
      } finally {
        if (btn) { btn.disabled = false; btn.innerHTML = label; }
      }
    });
  }

  /* -- boot --------------------------------------------------------------- */

  async function boot() {
    preloader();
    skipLink();
    mountNav();
    scrollProgress();
    cursor();
    mountFabs();
    reveal();          // also runs splitHeadings, sheen and magnetic
    counters();
    tilt();
    accordion();

    let dealer = null;
    try { dealer = await get('/dealer'); } catch { /* footer falls back */ }
    mountFooter(dealer);
    reveal();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

  return {
    api, get, post, inr, inrFull, priceLabel, esc, initials,
    ICON, toast, reveal, counters, tilt, sheen, magnetic, splitHeadings,
    accordion, lightbox, bindForm, reduced,
  };
})();
