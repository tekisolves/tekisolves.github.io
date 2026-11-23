/* Retro Arsenal weapon range: try every weapon and tier in the browser.
   Vanilla canvas, no libraries. Uses the pack's real pivot and muzzle data,
   so what you see here is exactly how the sprites line up in a game. */
(function () {
  const root = document.getElementById('range');
  if (!root) return;
  const canvas = root.querySelector('canvas');
  const ctx = canvas.getContext('2d');
  const hud = { weapon: root.querySelector('[data-hud=weapon]'), tier: root.querySelector('[data-hud=tier]'), hits: root.querySelector('[data-hud=hits]'), note: root.querySelector('[data-hud=note]') };
  const WEAPONS = ['pistol', 'rifle', 'shotgun', 'blade', 'grenade'];
  const NAMES = { pistol: 'Laser Pistol', rifle: 'Laser Rifle', shotgun: 'Laser Shotgun', blade: 'Energy Blade', grenade: 'Plasma Grenade' };
  const TIERS = ['t1', 't2', 't3'];
  const SRC = 1024, IMG = 400; // sprite data is in 1024px space, images are 400px
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  let data = null, imgs = {}, w = 0, h = 0, dpr = 1, started = false;
  let weapon = 0, tier = 0, aim = 0, flipped = false, hits = 0;
  let pointer = { x: 0, y: 0 }, last = 0, cooldown = 0, flash = 0, swing = 0, notice = 0;
  const shots = [], sparks = [], targets = [];

  function resize() {
    const r = canvas.getBoundingClientRect();
    dpr = Math.min(2, devicePixelRatio || 1);
    w = r.width; h = r.height;
    canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    if (!targets.length) spawnTargets();
  }
  const gunPos = () => ({ x: w * 0.24, y: h * 0.62 });
  const scale = () => Math.min(w, h * 1.6) / 2300; // sprite px -> screen px

  function spawnTargets() {
    targets.length = 0;
    for (let i = 0; i < 3; i++) targets.push({ x: w * (0.6 + i * 0.13), y: h * (0.25 + (i % 2) * 0.3), r: Math.max(16, w * 0.025), t: Math.random() * 6, hp: 1, pop: 0 });
  }

  function frameData() { const d = data[WEAPONS[weapon]]; return { type: d.type, f: d[TIERS[tier]] }; }
  function muzzleWorld() {
    const { f } = frameData(), s = scale(), g = gunPos();
    const dx = (f.muzzle[0] - f.pivot[0]) * s, dy = (f.muzzle[1] - f.pivot[1]) * s * (flipped ? -1 : 1);
    const c = Math.cos(aim), n = Math.sin(aim);
    return { x: g.x + dx * c - dy * n, y: g.y + dx * n + dy * c };
  }

  function fire() {
    if (!started || cooldown > 0) return;
    const { type } = frameData(), m = muzzleWorld(), name = WEAPONS[weapon];
    const speed = name === 'rifle' ? 1500 : 1000;
    if (type === 'gun') {
      const spread = name === 'shotgun' ? [-0.14, -0.07, 0, 0.07, 0.14] : [0];
      spread.forEach(a => shots.push({ x: m.x, y: m.y, vx: Math.cos(aim + a) * speed, vy: Math.sin(aim + a) * speed, life: 1.2, kind: 'bolt' }));
      flash = 0.08; cooldown = name === 'rifle' ? 0.12 : name === 'shotgun' ? 0.5 : 0.22;
    } else if (type === 'blade') {
      swing = 0.25; cooldown = 0.3;
      targets.forEach(t => { if (Math.hypot(t.x - m.x, t.y - m.y) < t.r + w * 0.12) hit(t); });
    } else {
      shots.push({ x: m.x, y: m.y, vx: Math.cos(aim) * 650, vy: Math.sin(aim) * 650 - 200, life: 1.1, kind: 'nade' });
      cooldown = 0.7;
    }
  }

  function hit(t) {
    if (t.hp <= 0) return;
    t.hp = 0; t.pop = 0.5; hits++; hud.hits.textContent = String(hits).padStart(3, '0');
    for (let i = 0; i < 14; i++) { const a = Math.random() * 6.28, v = 80 + Math.random() * 220; sparks.push({ x: t.x, y: t.y, vx: Math.cos(a) * v, vy: Math.sin(a) * v, life: 0.5 + Math.random() * 0.3 }); }
    setTimeout(() => { t.hp = 1; t.x = w * (0.55 + Math.random() * 0.38); t.y = h * (0.15 + Math.random() * 0.55); }, 900);
  }
  function boom(x, y) {
    for (let i = 0; i < 26; i++) { const a = Math.random() * 6.28, v = 60 + Math.random() * 320; sparks.push({ x, y, vx: Math.cos(a) * v, vy: Math.sin(a) * v, life: 0.6 + Math.random() * 0.4, gold: true }); }
    targets.forEach(t => { if (Math.hypot(t.x - x, t.y - y) < t.r + w * 0.09) hit(t); });
  }

  function setWeapon(i) { weapon = (i + WEAPONS.length) % WEAPONS.length; updateHud(); }
  function setTier(i) {
    tier = (i + 3) % 3; updateHud();
    hud.note.textContent = 'Same pivot, same muzzle point: the sprite swaps without moving.'; notice = 2.5;
  }
  function updateHud() {
    hud.weapon.textContent = NAMES[WEAPONS[weapon]].toUpperCase();
    hud.tier.textContent = data[WEAPONS[weapon]][TIERS[tier]].tier.toUpperCase();
    root.querySelectorAll('[data-w]').forEach(b => b.setAttribute('aria-pressed', String(+b.dataset.w === weapon)));
    root.querySelectorAll('[data-t]').forEach(b => b.setAttribute('aria-pressed', String(+b.dataset.t === tier)));
  }

  function draw(dt) {
    ctx.clearRect(0, 0, w, h);
    // floor grid in perspective
    ctx.strokeStyle = 'rgba(178,221,49,.10)'; ctx.lineWidth = 1;
    const hor = h * 0.78;
    for (let i = -12; i <= 12; i++) { ctx.beginPath(); ctx.moveTo(w / 2 + i * 18, hor); ctx.lineTo(w / 2 + i * w * 0.12, h); ctx.stroke(); }
    for (let j = 0; j < 6; j++) { const y = hor + (h - hor) * (j / 6) ** 1.6; ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke(); }

    // targets: gold diamonds
    targets.forEach(t => {
      t.t += dt; if (t.pop > 0) t.pop -= dt;
      if (t.hp <= 0) return;
      const bob = reduce ? 0 : Math.sin(t.t * 2) * 6;
      ctx.save(); ctx.translate(t.x, t.y + bob);
      ctx.strokeStyle = '#e9c55c'; ctx.lineWidth = 2; ctx.shadowColor = 'rgba(233,197,92,.6)'; ctx.shadowBlur = 12;
      ctx.beginPath(); ctx.moveTo(0, -t.r * 1.3); ctx.lineTo(t.r, 0); ctx.lineTo(0, t.r * 1.3); ctx.lineTo(-t.r, 0); ctx.closePath(); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(-t.r * 0.55, -t.r * 0.25); ctx.lineTo(t.r * 0.55, -t.r * 0.25); ctx.lineTo(0, t.r * 0.6); ctx.closePath(); ctx.stroke();
      ctx.restore();
    });

    // shots
    for (let i = shots.length - 1; i >= 0; i--) {
      const s = shots[i]; s.life -= dt;
      if (s.kind === 'nade') s.vy += 900 * dt;
      s.x += s.vx * dt; s.y += s.vy * dt;
      let gone = s.life <= 0 || s.x > w + 40 || s.y > h + 40 || s.x < -40;
      if (s.kind === 'bolt') {
        targets.forEach(t => { if (t.hp > 0 && Math.hypot(t.x - s.x, t.y - s.y) < t.r) { hit(t); gone = true; } });
        const a = Math.atan2(s.vy, s.vx);
        ctx.save(); ctx.translate(s.x, s.y); ctx.rotate(a);
        ctx.fillStyle = '#b2dd31'; ctx.shadowColor = '#b2dd31'; ctx.shadowBlur = 14; ctx.fillRect(-16, -2, 30, 4); ctx.restore();
      } else {
        if (s.y > hor + 10 || s.life <= 0) { boom(s.x, s.y); gone = true; }
        ctx.save(); ctx.fillStyle = '#7fffd4'; ctx.shadowColor = '#7fffd4'; ctx.shadowBlur = 16; ctx.beginPath(); ctx.arc(s.x, s.y, 6, 0, 6.28); ctx.fill(); ctx.restore();
      }
      if (gone) shots.splice(i, 1);
    }
    // sparks
    for (let i = sparks.length - 1; i >= 0; i--) {
      const p = sparks[i]; p.life -= dt; p.x += p.vx * dt; p.y += p.vy * dt; p.vy += 300 * dt;
      if (p.life <= 0) { sparks.splice(i, 1); continue; }
      ctx.fillStyle = p.gold ? `rgba(233,197,92,${p.life})` : `rgba(178,221,49,${p.life})`; ctx.fillRect(p.x, p.y, 3, 3);
    }

    // the weapon, drawn from its pivot exactly as a game engine would
    const { type, f } = frameData(), img = imgs[WEAPONS[weapon] + TIERS[tier]], s = scale(), g = gunPos(), k = IMG / SRC;
    if (img && img.complete) {
      ctx.save(); ctx.translate(g.x, g.y);
      let rot = aim; if (type === 'blade' && swing > 0) rot += Math.sin((swing / 0.25) * Math.PI) * -0.9 * (flipped ? -1 : 1);
      ctx.rotate(rot); if (flipped) ctx.scale(1, -1);
      ctx.drawImage(img, -f.pivot[0] * s, -f.pivot[1] * s, SRC * s, SRC * s);
      ctx.restore();
      void k;
    }
    // hand marker at the pivot
    ctx.fillStyle = 'rgba(233,197,92,.9)'; ctx.beginPath(); ctx.arc(g.x, g.y, 3, 0, 6.28); ctx.fill();
    if (flash > 0) { const m = muzzleWorld(); ctx.save(); ctx.fillStyle = 'rgba(220,255,140,.9)'; ctx.shadowColor = '#b2dd31'; ctx.shadowBlur = 25; ctx.beginPath(); ctx.arc(m.x, m.y, 9, 0, 6.28); ctx.fill(); ctx.restore(); }
    if (type === 'blade' && swing > 0) { const m = muzzleWorld(); ctx.save(); ctx.strokeStyle = 'rgba(127,255,212,.6)'; ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(g.x, g.y, Math.hypot(m.x - g.x, m.y - g.y), aim - 0.9, aim + 0.4); ctx.stroke(); ctx.restore(); }
  }

  function loop(now) {
    const dt = Math.min(0.05, (now - last) / 1000 || 0); last = now;
    if (cooldown > 0) cooldown -= dt; if (flash > 0) flash -= dt; if (swing > 0) swing -= dt;
    if (notice > 0) { notice -= dt; if (notice <= 0) hud.note.textContent = ''; }
    const g = gunPos();
    aim = Math.atan2(pointer.y - g.y, pointer.x - g.x); flipped = Math.abs(aim) > Math.PI / 2;
    draw(dt);
    if (visible) requestAnimationFrame(loop); else running = false;
  }

  // start only when scrolled into view; stop when off-screen
  let visible = false, running = false;
  function start() {
    if (started) return; started = true;
    fetch(root.dataset.data).then(r => r.json()).then(d => {
      data = d;
      WEAPONS.forEach(wn => TIERS.forEach(t => { const im = new Image(); im.decoding = 'async'; im.src = `${root.dataset.base}${wn}-${t}.webp`; imgs[wn + t] = im; }));
      resize(); pointer = { x: w * 0.8, y: h * 0.45 }; updateHud(); root.classList.add('live');
      if (visible && !running) { running = true; requestAnimationFrame(loop); }
    });
  }
  new IntersectionObserver(es => es.forEach(e => {
    visible = e.isIntersecting;
    if (visible) { start(); if (data && !running) { running = true; last = performance.now(); requestAnimationFrame(loop); } }
  }), { threshold: 0.15 }).observe(root);

  addEventListener('resize', () => started && resize());
  canvas.addEventListener('pointermove', e => { const r = canvas.getBoundingClientRect(); pointer = { x: e.clientX - r.left, y: e.clientY - r.top }; });
  canvas.addEventListener('pointerdown', e => { const r = canvas.getBoundingClientRect(); pointer = { x: e.clientX - r.left, y: e.clientY - r.top }; fire(); });
  root.querySelectorAll('[data-w]').forEach(b => b.addEventListener('click', () => setWeapon(+b.dataset.w)));
  root.querySelectorAll('[data-t]').forEach(b => b.addEventListener('click', () => setTier(+b.dataset.t)));
  root.addEventListener('keydown', e => {
    if (e.key >= '1' && e.key <= '5') { setWeapon(+e.key - 1); e.preventDefault(); }
    else if (e.key === 't' || e.key === 'T') { setTier(tier + 1); e.preventDefault(); }
    else if (e.key === ' ' || e.key === 'Enter') { if (e.target === canvas) { fire(); e.preventDefault(); } }
  });
})();
