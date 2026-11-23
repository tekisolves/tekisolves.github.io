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

  /* ---- sound: synthesized with Web Audio, no audio files ---- */
  const sfx = (() => {
    let ac = null, master = null, on = true, noiseBuf = null;
    const init = () => {
      if (ac) return ac.state === 'suspended' ? ac.resume() : null;
      const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return;
      ac = new AC(); master = ac.createGain(); master.gain.value = 0.32; master.connect(ac.destination);
      noiseBuf = ac.createBuffer(1, ac.sampleRate, ac.sampleRate); const d = noiseBuf.getChannelData(0);
      for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
    };
    const env = (g, t, a, peak, dec) => { g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(peak, t + a); g.gain.exponentialRampToValueAtTime(0.0001, t + a + dec); };
    const tone = (type, f0, f1, dur, vol, at = 0) => {
      if (!ac || !on) return; const t = ac.currentTime + at, o = ac.createOscillator(), g = ac.createGain(), lp = ac.createBiquadFilter();
      o.type = type; o.frequency.setValueAtTime(f0, t); o.frequency.exponentialRampToValueAtTime(Math.max(20, f1), t + dur);
      lp.type = 'lowpass'; lp.frequency.value = 5200; env(g, t, 0.004, vol, dur);
      o.connect(lp).connect(g).connect(master); o.start(t); o.stop(t + dur + 0.05);
    };
    const noise = (dur, vol, ftype, f0, f1, at = 0) => {
      if (!ac || !on) return; const t = ac.currentTime + at, src = ac.createBufferSource(), f = ac.createBiquadFilter(), g = ac.createGain();
      src.buffer = noiseBuf; f.type = ftype; f.frequency.setValueAtTime(f0, t); f.frequency.exponentialRampToValueAtTime(f1, t + dur); f.Q.value = 1.2;
      env(g, t, 0.005, vol, dur); src.connect(f).connect(g).connect(master); src.start(t); src.stop(t + dur + 0.05);
    };
    return {
      init, toggle: v => { on = v; },
      pistol: () => { tone('sawtooth', 1400, 180, 0.16, 0.5); tone('square', 2600, 900, 0.05, 0.12); },
      rifle: () => { tone('sawtooth', 1900, 300, 0.09, 0.42); noise(0.05, 0.15, 'highpass', 3000, 6000); },
      shotgun: () => { noise(0.22, 0.6, 'bandpass', 2400, 400); tone('sawtooth', 900, 90, 0.2, 0.35); },
      blade: () => { noise(0.28, 0.45, 'bandpass', 600, 4200); tone('sine', 520, 1200, 0.22, 0.12); },
      throw: () => { tone('sine', 300, 520, 0.12, 0.3); },
      boom: () => { noise(0.7, 0.9, 'lowpass', 1400, 120); tone('sine', 110, 38, 0.6, 0.7); },
      hit: () => { tone('sine', 1320, 1320, 0.12, 0.35); tone('sine', 1980, 1980, 0.18, 0.25, 0.06); },
      tier: n => { tone('square', [440, 554, 659][n], [440, 554, 659][n] * 1.5, 0.09, 0.18); },
      pick: () => { tone('triangle', 660, 880, 0.06, 0.2); },
      start: () => { [523, 659, 784, 1047].forEach((f, i) => tone('triangle', f, f, 0.16, 0.25, i * 0.07)); }
    };
  })();

  let data = null, imgs = {}, w = 0, h = 0, dpr = 1, started = false;
  let weapon = 0, tier = 0, aim = 0, flipped = false, hits = 0;
  let holding = false;
  const buzz = ms => { try { if (navigator.vibrate && matchMedia('(pointer: coarse)').matches) navigator.vibrate(ms); } catch (e) {} };
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
  const scale = () => Math.min(w, h * 1.6) / (w < 560 ? 1500 : 2300); // sprite px -> screen px

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
    if (!started || cooldown > 0 || !root.classList.contains('started')) return;
    sfx.init(); buzz(8);
    const { type } = frameData(), m = muzzleWorld(), name = WEAPONS[weapon];
    const speed = name === 'rifle' ? 1500 : 1000;
    if (type === 'gun') {
      const spread = name === 'shotgun' ? [-0.14, -0.07, 0, 0.07, 0.14] : [0];
      spread.forEach(a => shots.push({ x: m.x, y: m.y, vx: Math.cos(aim + a) * speed, vy: Math.sin(aim + a) * speed, life: 1.2, kind: 'bolt' }));
      flash = 0.08; cooldown = name === 'rifle' ? 0.12 : name === 'shotgun' ? 0.5 : 0.22;
      sfx[name]();
    } else if (type === 'blade') {
      swing = 0.25; cooldown = 0.3; sfx.blade();
      targets.forEach(t => { if (Math.hypot(t.x - m.x, t.y - m.y) < t.r + w * 0.12) hit(t); });
    } else {
      shots.push({ x: m.x, y: m.y, vx: Math.cos(aim) * 650, vy: Math.sin(aim) * 650 - 200, life: 1.1, kind: 'nade' });
      cooldown = 0.7; sfx.throw();
    }
  }

  function hit(t) {
    if (t.hp <= 0) return;
    t.hp = 0; t.pop = 0.5; hits++; sfx.hit(); buzz(25); hud.hits.textContent = String(hits).padStart(3, '0');
    for (let i = 0; i < 14; i++) { const a = Math.random() * 6.28, v = 80 + Math.random() * 220; sparks.push({ x: t.x, y: t.y, vx: Math.cos(a) * v, vy: Math.sin(a) * v, life: 0.5 + Math.random() * 0.3 }); }
    setTimeout(() => { t.hp = 1; t.x = w * (0.55 + Math.random() * 0.38); t.y = h * (0.15 + Math.random() * 0.55); }, 900);
  }
  function boom(x, y) {
    sfx.boom(); buzz([30, 20, 40]);
    for (let i = 0; i < 26; i++) { const a = Math.random() * 6.28, v = 60 + Math.random() * 320; sparks.push({ x, y, vx: Math.cos(a) * v, vy: Math.sin(a) * v, life: 0.6 + Math.random() * 0.4, gold: true }); }
    targets.forEach(t => { if (Math.hypot(t.x - x, t.y - y) < t.r + w * 0.09) hit(t); });
  }

  function setWeapon(i) { weapon = (i + WEAPONS.length) % WEAPONS.length; updateHud(); sfx.pick(); }
  function setTier(i) {
    tier = (i + 3) % 3; updateHud(); sfx.tier(tier);
    hud.note.textContent = 'Same pivot, same muzzle point: the sprite swaps without moving.'; notice = 2.5;
  }
  function updateHud() {
    hud.weapon.textContent = NAMES[WEAPONS[weapon]].toUpperCase();
    hud.tier.textContent = data[WEAPONS[weapon]][TIERS[tier]].tier.toUpperCase();
    const fsb = root.querySelector('[data-fs]');
  const fsEl = root.requestFullscreen ? 'requestFullscreen' : root.webkitRequestFullscreen ? 'webkitRequestFullscreen' : null;
  if (fsb && fsEl) {
    fsb.hidden = false;
    fsb.addEventListener('click', async () => {
      if (document.fullscreenElement || document.webkitFullscreenElement) { (document.exitFullscreen || document.webkitExitFullscreen).call(document); return; }
      try { await root[fsEl](); if (screen.orientation && screen.orientation.lock) screen.orientation.lock('landscape').catch(() => {}); } catch (e) {}
    });
    const onFs = () => { const on = !!(document.fullscreenElement || document.webkitFullscreenElement); fsb.textContent = on ? 'EXIT FULLSCREEN' : 'FULLSCREEN'; setTimeout(() => started && resize(), 120); };
    document.addEventListener('fullscreenchange', onFs); document.addEventListener('webkitfullscreenchange', onFs);
  }
  const sbtn = root.querySelector('[data-sound]');
  if (sbtn) sbtn.addEventListener('click', () => { const on = sbtn.getAttribute('aria-pressed') !== 'true'; sbtn.setAttribute('aria-pressed', String(on)); sbtn.textContent = on ? 'SOUND ON' : 'SOUND OFF'; sfx.toggle(on); if (on) { sfx.init(); sfx.pick(); } });
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
    if (holding && cooldown <= 0) fire();
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
    const bar = root.querySelector('.tk-range-load .tk-bar'), startBtn = root.querySelector('[data-start]');
    const total = 16; let done = 0;
    const tickLoad = () => { done++; bar.style.setProperty('--p', (done / total).toFixed(3)); if (done >= total) ready(); };
    const ready = () => { startBtn.hidden = false; startBtn.focus({ preventScroll: true }); };
    fetch(root.dataset.data).then(r => r.json()).then(d => {
      data = d; tickLoad();
      WEAPONS.forEach(wn => TIERS.forEach(t => { const im = new Image(); im.decoding = 'async'; im.onload = im.onerror = tickLoad; im.src = `${root.dataset.base}${wn}-${t}.webp`; imgs[wn + t] = im; }));
      resize(); pointer = { x: w * 0.8, y: h * 0.45 }; updateHud(); root.classList.add('live');
      if (visible && !running) { running = true; requestAnimationFrame(loop); }
    });
    startBtn.addEventListener('click', () => { sfx.init(); sfx.start(); root.classList.add('started'); canvas.focus({ preventScroll: true }); });
  }
  new IntersectionObserver(es => es.forEach(e => {
    visible = e.isIntersecting;
    if (visible) { start(); if (data && !running) { running = true; last = performance.now(); requestAnimationFrame(loop); } }
  }), { threshold: 0.15 }).observe(root);

  addEventListener('resize', () => started && resize());
  const setPointer = e => { const r = canvas.getBoundingClientRect(); pointer = { x: e.clientX - r.left, y: e.clientY - r.top }; };
  canvas.addEventListener('pointermove', setPointer);
  canvas.addEventListener('pointerdown', e => { setPointer(e); holding = true; canvas.setPointerCapture(e.pointerId); fire(); });
  const release = () => { holding = false; };
  canvas.addEventListener('pointerup', release); canvas.addEventListener('pointercancel', release); canvas.addEventListener('lostpointercapture', release);
  canvas.addEventListener('contextmenu', e => e.preventDefault());
  root.querySelectorAll('[data-w]').forEach(b => b.addEventListener('click', () => setWeapon(+b.dataset.w)));
  root.querySelectorAll('[data-t]').forEach(b => b.addEventListener('click', () => setTier(+b.dataset.t)));
  root.addEventListener('keydown', e => {
    if (e.key >= '1' && e.key <= '5') { setWeapon(+e.key - 1); e.preventDefault(); }
    else if (e.key === 't' || e.key === 'T') { setTier(tier + 1); e.preventDefault(); }
    else if (e.key === ' ' || e.key === 'Enter') { if (e.target === canvas) { fire(); e.preventDefault(); } }
  });
})();
