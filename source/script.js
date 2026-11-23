(() => {
  const $ = id => document.getElementById(id);
  const ANALYTICS_ID = 'G-8V28F53XS9'; // verify against your GA4 property
  const CONSENT_KEY = 'teki_analytics_consent';
  const leadEndpoint = 'https://script.google.com/macros/s/AKfycbw3CDbGXl9nsWYww-cOfCFovLpkXUqRQ92NyCnglmnXxIY4g4OXaFl3y9gI6BlhywCz/exec';

  /* ---------- navigation ---------- */
  const menuButton = $('menuButton');
  const mobileNav = $('mobileNav');
  function closeMenu() {
    if (!menuButton) return;
    menuButton.classList.remove('open');
    menuButton.setAttribute('aria-expanded', 'false');
    menuButton.setAttribute('aria-label', 'Open navigation');
    mobileNav.hidden = true;
  }
  if (menuButton && mobileNav) {
    menuButton.addEventListener('click', () => {
      const open = mobileNav.hidden;
      mobileNav.hidden = !open;
      menuButton.classList.toggle('open', open);
      menuButton.setAttribute('aria-expanded', String(open));
      menuButton.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    });
    mobileNav.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
  }

  /* ---------- scroll reveal (content stays visible without JS) ---------- */
  const reveals = document.querySelectorAll('.reveal, .diamond-line');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) { e.target.classList.add('is-visible'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12 });
    reveals.forEach(el => io.observe(el));
  } else {
    reveals.forEach(el => el.classList.add('is-visible'));
  }

  /* ---------- analytics consent (GA4 loads only after opt-in) ---------- */
  const banner = $('cookieBanner');
  const panel = $('cookieSettingsPanel');
  const status = $('analyticsStatus');

  function loadGoogleAnalytics() {
    if (document.getElementById('google-analytics-script')) return;
    gtag('consent', 'update', { analytics_storage: 'granted', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
    const s = document.createElement('script');
    s.id = 'google-analytics-script';
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + ANALYTICS_ID;
    document.head.appendChild(s);
    gtag('js', new Date());
    gtag('config', ANALYTICS_ID, { anonymize_ip: true });
  }
  function removeAnalyticsCookies() {
    document.cookie.split(';').forEach(c => {
      const name = c.split('=')[0].trim();
      if (name === '_ga' || name.indexOf('_ga_') === 0) document.cookie = name + '=; Max-Age=0; path=/';
    });
  }
  function updateCookieUI() {
    const consent = localStorage.getItem(CONSENT_KEY);
    if (banner) banner.hidden = consent === 'granted' || consent === 'denied';
    if (status) status.textContent = consent === 'granted' ? 'On' : 'Off';
  }
  function setAnalyticsConsent(value) {
    localStorage.setItem(CONSENT_KEY, value);
    if (value === 'granted') loadGoogleAnalytics();
    else {
      gtag('consent', 'update', { analytics_storage: 'denied', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
      removeAnalyticsCookies();
    }
    updateCookieUI();
  }
  function openCookieSettings() { if (panel) { panel.hidden = false; document.body.classList.add('modal-open'); $('cookieSettingsClose')?.focus(); } }
  function closeCookieSettings() { if (panel) { panel.hidden = true; document.body.classList.remove('modal-open'); } }

  $('cookieAccept')?.addEventListener('click', () => setAnalyticsConsent('granted'));
  $('cookieReject')?.addEventListener('click', () => setAnalyticsConsent('denied'));
  $('cookieManage')?.addEventListener('click', openCookieSettings);
  document.querySelectorAll('.cookie-settings-trigger').forEach(b => b.addEventListener('click', openCookieSettings));
  $('cookieSettingsClose')?.addEventListener('click', closeCookieSettings);
  $('cookieSettingsAccept')?.addEventListener('click', () => { setAnalyticsConsent('granted'); closeCookieSettings(); });
  $('cookieSettingsReject')?.addEventListener('click', () => { setAnalyticsConsent('denied'); closeCookieSettings(); });
  panel?.addEventListener('mousedown', e => { if (e.target === panel) closeCookieSettings(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeCookieSettings(); });

  if (localStorage.getItem(CONSENT_KEY) === 'granted') loadGoogleAnalytics();
  updateCookieUI();

  /* ---------- analytics events (only after consent; never any personal data) ---------- */
  function track(name, params) {
    if (localStorage.getItem(CONSENT_KEY) !== 'granted') return;
    gtag('event', name, params || {});
  }
  const productPage = document.querySelector('[data-product-id]');
  if (productPage) {
    track('view_product', { product_id: productPage.dataset.productId, product_name: productPage.dataset.productName, product_category: productPage.dataset.productCategory });
  }
  document.querySelectorAll('[data-store-link]').forEach(a => a.addEventListener('click', () => {
    const p = { product_id: a.dataset.productId, product_name: a.dataset.productName, store: a.dataset.store };
    track('click_external_store', p);
    track('click_purchase', p);
  }));

  /* ---------- contact form: same endpoint, field names and payload as the original site ---------- */
  const form = $('contactForm');
  if (form) {
    const formError = $('formError');
    const submitButton = $('submitButton');
    const label = submitButton.querySelector('.btn-label');
    const successMessage = $('successMessage');
    const msg = form.message, count = $('c-msg');
    const formOpenedAt = Date.now();
    const emailOk = v => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v);

    // one rule per field, checked on blur and again on submit
    const rules = {
      name: () => form.name.value.trim() ? '' : 'Please add your name.',
      email: () => !form.email.value.trim() ? 'Please add your email so we can reply.' : emailOk(form.email.value.trim()) ? '' : 'That email doesn’t look quite right.',
      message: () => { const n = msg.value.trim().length; return !n ? 'Please tell us a little about it.' : n < 10 ? 'A little more detail, please (10 characters minimum).' : ''; },
      privacyAcknowledgement: () => form.privacyAcknowledgement.checked ? '' : 'Please confirm you’ve read the Privacy Policy.'
    };
    const errIds = { name: 'e-name', email: 'e-email', message: 'e-msg', privacyAcknowledgement: 'e-consent' };
    const check = (k, show = true) => {
      const m = rules[k](), field = form[k], box = field.closest('.field');
      if (show) { $(errIds[k]).textContent = m; box.classList.toggle('invalid', !!m); field.setAttribute('aria-invalid', m ? 'true' : 'false'); }
      if (!m && field.value) box.classList.add('valid'); else box.classList.remove('valid');
      return m;
    };
    Object.keys(rules).forEach(k => {
      const f = form[k];
      f.addEventListener('blur', () => { if (f.type === 'checkbox' || f.value) check(k); });
      f.addEventListener('input', () => { if (f.closest('.field').classList.contains('invalid')) check(k); else check(k, false); });
      f.addEventListener('change', () => { if (f.type === 'checkbox') check(k); });
    });
    const updateCount = () => { const n = msg.value.length; count.textContent = `${n} / 2000`; count.classList.toggle('near', n > 1800); };
    msg.addEventListener('input', updateCount);

    const showError = m => { formError.textContent = m; formError.hidden = false; };
    const showSuccess = (name, email) => {
      $('successText').textContent = name && email ? `Thanks, ${name}. We’ll reply to ${email}.` : 'Thanks. We’ll reply to the email you gave us.';
      form.hidden = true; successMessage.hidden = false; successMessage.focus();
    };
    $('sendAnother').addEventListener('click', () => {
      successMessage.hidden = true; form.hidden = false;
      form.querySelectorAll('.field').forEach(f => f.classList.remove('valid', 'invalid'));
      updateCount(); form.name.focus();
    });

    form.addEventListener('submit', async event => {
      event.preventDefault();
      formError.hidden = true;
      const bad = Object.keys(rules).filter(k => check(k));
      if (bad.length) { form[bad[0]].focus(); return; }

      const data = new FormData(form);
      const payload = {
        name: form.name.value.trim(),
        email: form.email.value.trim(),
        businessName: form.businessName.value.trim(),
        trackInterest: data.get('trackInterest') || 'Not sure',
        message: msg.value.trim(),
        privacyAcknowledgement: form.privacyAcknowledgement.checked
      };

      if (String(data.get('website') || '').trim()) return showSuccess();          // honeypot: quietly drop bots
      if (Date.now() - formOpenedAt < 1200) return showError('Please take a moment to check your details before sending.');

      submitButton.disabled = true;
      submitButton.classList.add('is-sending');
      label.textContent = 'Sending…';
      try {
        await fetch(leadEndpoint, {
          method: 'POST',
          mode: 'no-cors',
          headers: { 'Content-Type': 'text/plain;charset=utf-8' },
          body: JSON.stringify(payload)
        });
        form.reset();
        showSuccess(payload.name, payload.email);
        track('lead_form_submit', {});
      } catch (error) {
        showError('That didn’t send, probably a connection problem. Your message is still here, so please try again.');
      } finally {
        submitButton.disabled = false;
        submitButton.classList.remove('is-sending');
        label.textContent = 'Send message';
      }
    });
    form.addEventListener('focusin', () => { if (!form.dataset.started) { form.dataset.started = '1'; track('lead_form_start', {}); } });
  }
})();

/* guardian parallax (skipped for reduced motion) */
(() => {
  const band = document.querySelector('.guardian');
  if (!band || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const img = band.querySelector('img');
  let ticking = false;
  const update = () => {
    const r = band.getBoundingClientRect();
    const p = (r.top + r.height / 2 - innerHeight / 2) / innerHeight;
    img.style.setProperty('--py', (p * -48).toFixed(1) + 'px');
    ticking = false;
  };
  addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
  update();

  /* ---------- 3D: pointer tilt on the hero art, pause spinning scenes when off-screen ---------- */
  (function () {
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const fine = matchMedia('(pointer: fine)').matches;
    const art = document.querySelector('.tilt3d');
    if (art && fine && !reduce) {
      const hero = art.closest('.hero') || art;
      let raf = 0;
      hero.addEventListener('pointermove', e => {
        if (raf) return;
        raf = requestAnimationFrame(() => {
          raf = 0;
          const r = hero.getBoundingClientRect();
          const x = (e.clientX - r.left) / r.width - 0.5;
          const y = (e.clientY - r.top) / r.height - 0.5;
          art.style.setProperty('--ry', (x * 10).toFixed(2) + 'deg');
          art.style.setProperty('--rx', (-y * 8).toFixed(2) + 'deg');
          hero.style.setProperty('--mx', (e.clientX - r.left) + 'px');
          hero.style.setProperty('--my', (e.clientY - r.top) + 'px');
        });
      });
      hero.addEventListener('pointerleave', () => { art.style.setProperty('--rx', '0deg'); art.style.setProperty('--ry', '0deg'); hero.style.setProperty('--spot', '0'); });
      hero.addEventListener('pointerenter', () => hero.style.setProperty('--spot', '1'));
    }
    if ('IntersectionObserver' in window) {
      const scenes = document.querySelectorAll('.ldia-wrap, .c3');
      const io3 = new IntersectionObserver(entries => {
        entries.forEach(en => { en.target.dataset.inview = en.isIntersecting ? '1' : ''; en.target.classList.toggle('is-paused', !en.isIntersecting || document.hidden); });
      }, { threshold: 0 });
      scenes.forEach(el => io3.observe(el));
      document.addEventListener('visibilitychange', () => scenes.forEach(el => el.classList.toggle('is-paused', document.hidden || !el.dataset.inview)));
    }
  })();

  /* ---------- game UI: inventory-card tilt + glint ---------- */
  (function () {
    if (matchMedia('(prefers-reduced-motion: reduce)').matches || !matchMedia('(pointer: fine)').matches) return;
    document.querySelectorAll('.product-card').forEach(card => {
      card.addEventListener('pointermove', e => {
        const r = card.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
        card.style.setProperty('--ty', ((x - 0.5) * 10).toFixed(2) + 'deg');
        card.style.setProperty('--tx', ((0.5 - y) * 8).toFixed(2) + 'deg');
        card.style.setProperty('--gx', (x * 100).toFixed(1) + '%');
        card.style.setProperty('--gy', (y * 100).toFixed(1) + '%');
      });
      card.addEventListener('pointerleave', () => { card.style.setProperty('--tx', '0deg'); card.style.setProperty('--ty', '0deg'); });
    });
  })();

  /* ---------- game UI level 2: reticle, magnetic buttons, decode text, drag-to-spin hologram, achievement ---------- */
  (function () {
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const fine = matchMedia('(pointer: fine)').matches;

    // targeting reticle that trails the cursor and locks onto links and buttons
    const ret = document.getElementById('reticle');
    if (ret && fine && !reduce) {
      let tx = 0, ty = 0, x = 0, y = 0, running = false;
      const step = () => {
        x += (tx - x) * 0.22; y += (ty - y) * 0.22;
        ret.style.transform = `translate3d(${x}px,${y}px,0)`;
        if (Math.abs(tx - x) + Math.abs(ty - y) > 0.3) requestAnimationFrame(step); else running = false;
      };
      addEventListener('pointermove', e => {
        tx = e.clientX; ty = e.clientY; ret.classList.add('on');
        ret.classList.toggle('lock', !!e.target.closest('a, button, .holo'));
        if (!running) { running = true; requestAnimationFrame(step); }
      }, { passive: true });
      document.addEventListener('pointerleave', () => ret.classList.remove('on'));
    }

    // magnetic primary buttons
    if (fine && !reduce) {
      document.querySelectorAll('.btn-primary').forEach(b => {
        b.addEventListener('pointermove', e => {
          const r = b.getBoundingClientRect();
          const dx = (e.clientX - (r.left + r.width / 2)) / r.width, dy = (e.clientY - (r.top + r.height / 2)) / r.height;
          b.style.transform = `translate(${(dx * 8).toFixed(1)}px,${(dy * 6).toFixed(1)}px)`;
        });
        b.addEventListener('pointerleave', () => { b.style.transform = ''; });
      });
    }

    // decode effect on section labels as they come into view
    if (!reduce && 'IntersectionObserver' in window) {
      const glyphs = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/<>#*+';
      const decode = el => {
        const final = el.textContent; el.setAttribute('aria-label', final); el.classList.add('decoding');
        const start = performance.now(), dur = 700;
        const tick = now => {
          const t = Math.min(1, (now - start) / dur), keep = Math.floor(final.length * t);
          el.textContent = final.slice(0, keep) + final.slice(keep).replace(/[^\s/•·]/g, () => glyphs[Math.random() * glyphs.length | 0]);
          if (t < 1) requestAnimationFrame(tick); else { el.textContent = final; el.classList.remove('decoding'); }
        };
        requestAnimationFrame(tick);
      };
      const io = new IntersectionObserver(es => es.forEach(en => { if (en.isIntersecting) { io.unobserve(en.target); decode(en.target); } }), { threshold: 0.6 });
      document.querySelectorAll('.hero .eyebrow, .section-head .eyebrow, .stack > .eyebrow, .holo-label').forEach(el => io.observe(el));
    }

    // drag (or swipe) the hologram to spin it; a real drag never triggers the link
    const holo = document.querySelector('.holo');
    if (holo) {
      const wrap = holo.querySelector('.c3-drag');
      let startX = 0, base = 0, drag = 0, moved = false, down = false;
      holo.addEventListener('pointerdown', e => { down = true; moved = false; startX = e.clientX; base = drag; holo.setPointerCapture(e.pointerId); });
      holo.addEventListener('pointermove', e => {
        if (!down) return;
        const dx = e.clientX - startX;
        if (Math.abs(dx) > 6) { moved = true; holo.classList.add('dragging'); }
        if (moved) { drag = base + dx * 0.45; wrap.style.setProperty('--drag', drag.toFixed(1) + 'deg'); }
      });
      const end = () => { down = false; holo.classList.remove('dragging'); };
      holo.addEventListener('pointerup', end); holo.addEventListener('pointercancel', end);
      holo.addEventListener('click', e => { if (moved) { e.preventDefault(); moved = false; } });
      holo.addEventListener('dragstart', e => e.preventDefault());
    }

    // achievement: shown once per session when someone reaches the bottom of a page
    const toast = document.getElementById('achv');
    if (toast) {
      let seen = false; try { seen = sessionStorage.getItem('teki-achv') === '1'; } catch (e) {}
      const check = () => {
        if (seen) return;
        const h = document.documentElement;
        if (h.scrollTop + innerHeight >= h.scrollHeight * 0.92 && h.scrollHeight > innerHeight * 1.6) {
          seen = true; try { sessionStorage.setItem('teki-achv', '1'); } catch (e) {}
          toast.hidden = false; requestAnimationFrame(() => toast.classList.add('show'));
          setTimeout(() => { toast.classList.remove('show'); setTimeout(() => { toast.hidden = true; }, 600); }, 6000);
          removeEventListener('scroll', check);
        }
      };
      addEventListener('scroll', check, { passive: true });
    }
  })();

  /* ---------- signature splash: fade out once the page has loaded (min 650ms, max 1.6s) ---------- */
  (function () {
    const html = document.documentElement;
    if (!html.classList.contains('splash')) return;
    const t0 = performance.now();
    let done = false;
    const out = () => {
      if (done) return; done = true;
      const wait = Math.max(0, 650 - (performance.now() - t0));
      setTimeout(() => { html.classList.add('splash-out'); setTimeout(() => html.classList.remove('splash', 'splash-out'), 600); }, wait);
    };
    if (document.readyState === 'complete') out(); else addEventListener('load', out);
    setTimeout(out, 1600);
    document.querySelector('.tk-splash')?.addEventListener('click', out);
  })();
})();
/* footer social tiles power on when they scroll into view */
(() => {
  const s = document.querySelector('.socials');
  if (!s || !('IntersectionObserver' in window)) return;
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { s.classList.add('in'); io.disconnect(); } }), { threshold: .4 });
  io.observe(s);
})();
