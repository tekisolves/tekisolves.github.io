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
    const successMessage = $('successMessage');
    const formOpenedAt = Date.now();

    const showError = m => { formError.textContent = m; formError.hidden = false; };
    const showSuccess = () => { form.hidden = true; successMessage.hidden = false; successMessage.focus?.(); };

    form.addEventListener('submit', async event => {
      event.preventDefault();
      formError.hidden = true;
      if (!form.checkValidity()) { form.reportValidity(); return; }

      const data = new FormData(form);
      const website = String(data.get('website') || '').trim();
      const payload = {
        name: form.name.value.trim(),
        email: form.email.value.trim(),
        businessName: form.businessName.value.trim(),
        trackInterest: form.trackInterest.value,
        message: form.message.value.trim(),
        privacyAcknowledgement: form.privacyAcknowledgement.checked
      };

      if (website) return showSuccess();
      if (Date.now() - formOpenedAt < 1200) return showError('Please take a moment to check your details before sending.');
      if (!payload.name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(payload.email)) return showError('Please add your name and a valid email address.');

      submitButton.disabled = true;
      submitButton.textContent = 'Sending…';
      try {
        await fetch(leadEndpoint, {
          method: 'POST',
          mode: 'no-cors',
          headers: { 'Content-Type': 'text/plain;charset=utf-8' },
          body: JSON.stringify(payload)
        });
        form.reset();
        showSuccess();
        track('lead_form_submit', {});
      } catch (error) {
        showError('Something went wrong while sending that. Your details are still here — please try again.');
      } finally {
        submitButton.disabled = false;
        submitButton.innerHTML = 'Send it over <span aria-hidden="true">→</span>';
      }
    });
    form.addEventListener('focusin', () => { if (!form.dataset.started) { form.dataset.started = '1'; track('lead_form_start', {}); } }, { once: false });
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
})();
