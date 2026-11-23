// Retro Arsenal: Phaser 4 weapon demo by Teki Solves
// Every weapon uses the pack's real pivot and muzzle points and behaves like what it is:
//   Pistol  - one shot per click
//   Rifle   - hold to fire, fast and accurate
//   Shotgun - five-pellet spread, short range, big kick, slow pump
//   Blade   - the grip follows your pointer, click to swing, the edge cuts
//   Grenade - click to throw at the pointer, short fuse, area blast
// The canvas fills the window and re-lays itself out on every resize.

const ATLAS = 'arsenal';
const PISTOL_FRAMES = [                          // atlas frame names include ".png"
  'weapon_laser_pistol_t1_scrap.png',
  'weapon_laser_pistol_t2_military.png',
  'weapon_laser_pistol_t3_prototype.png',
];
const TIER_NAMES = ['Scrap', 'Military', 'Prototype'];

// Attachment points in the pack's 1024px frame space (top-left origin).
// "point" is the muzzle for guns, the tip for the blade and the pin for the grenade.
const WEAPONS = {
  pistol:  { kind: 'gun',   pivot: [388, 585], point: [900, 442], rate: 0.16, speed: 2.4, len: 0.05,  spread: 0,    pellets: 1, range: 2,    kick: 0.02 },
  rifle:   { kind: 'gun',   pivot: [320, 639], point: [872, 507], rate: 0.09, speed: 3.4, len: 0.075, spread: 0.03, pellets: 1, range: 2,    kick: 0.012, auto: true },
  shotgun: { kind: 'gun',   pivot: [340, 654], point: [855, 452], rate: 0.7,  speed: 2.1, len: 0.03,  spread: 0.34, pellets: 5, range: 0.55, kick: 0.07 },
  blade:   { kind: 'blade', pivot: [236, 607], point: [900, 632] },
  grenade: { kind: 'throw', pivot: [505, 676], point: [450, 424] },
};
const ORDER = ['pistol', 'rifle', 'shotgun', 'blade', 'grenade'];

const LIME = 0xb2dd31, GOLD = 0xe9c55c, CREAM = 0xf4f3ed, HOT = 0xf2b63d;
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const $ = (id) => document.getElementById(id);

class Demo extends Phaser.Scene {
  preload() {
    this.load.atlas(ATLAS, 'retro_arsenal_sample.png', 'retro_arsenal_sample.json');
    ['rifle', 'shotgun', 'blade', 'grenade'].forEach((w) =>
      [1, 2, 3].forEach((t) => this.load.image(`${w}${t}`, `${w}-t${t}.webp`)));
  }

  create() {
    this.tier = 0;
    this.hits = 0;
    this.weapon = 'pistol';
    this.cool = 0;               // seconds until the weapon can be used again
    this.recoil = 0;             // 0..1, eases back to 0
    this.bolts = [];
    this.targets = [];
    this.nades = [];
    this.debug = false;

    // one image for every hand-held weapon; its texture, origin and scale change with the weapon
    this.held = this.add.image(0, 0, ATLAS, PISTOL_FRAMES[0]).setDepth(3);
    this.hand = this.add.circle(0, 0, 5, LIME).setDepth(4);

    this.bladePos = new Phaser.Math.Vector2();
    this.bladeGoal = new Phaser.Math.Vector2();
    this.restAngle = -0.6;
    this.swing = null;
    this.trail = this.add.graphics().setBlendMode(Phaser.BlendModes.ADD).setDepth(2);
    this.fx = this.add.graphics().setDepth(6);

    this.layout(this.scale.gameSize);
    this.scale.on('resize', (size) => this.layout(size));

    this.input.on('pointermove', (p) => this.onMove(p));
    this.input.on('pointerdown', (p) => { this.onMove(p); this.use(); });
    const kb = this.input.keyboard;
    kb?.on('keydown-SPACE', () => this.nextTier());
    kb?.on('keydown-D', () => this.toggleDebug());
    ['ONE', 'TWO', 'THREE', 'FOUR', 'FIVE'].forEach((k, i) => kb?.on(`keydown-${k}`, () => this.setWeapon(ORDER[i])));

    document.querySelectorAll('.slot').forEach((b) => (b.onclick = () => this.setWeapon(b.dataset.w)));
    $('tier').onclick = () => this.nextTier();
    $('debug').onclick = () => this.toggleDebug();
    // hand keyboard focus back to the game after a HUD click, so Space changes tier, not the last button
    document.querySelectorAll('.hud button, .hotbar button').forEach((b) => b.addEventListener('click', () => b.blur()));

    for (let i = 0; i < 3; i++) this.spawnTarget();
    this.setWeapon('pistol');
  }

  // ---------- layout: everything is sized from the shorter screen side ----------
  layout({ width: w, height: h }) {
    this.cameras.main.setViewport(0, 0, w, h);
    if (this.W) this.bladePos.set(this.bladePos.x * w / this.W, this.bladePos.y * h / this.H);
    this.W = w; this.H = h;
    this.unit = Math.min(w, h);
    this.framePx = Phaser.Math.Clamp(this.unit * 0.42, 130, 340);   // on-screen size of a 1024px frame
    this.handAt = { x: Math.max(w * 0.18, 80), y: h * 0.56 };
    this.hand.setPosition(this.handAt.x, this.handAt.y);
    if (this.bladePos.lengthSq() === 0) this.bladePos.set(w * 0.32, h * 0.56);
    this.bladePos.set(Phaser.Math.Clamp(this.bladePos.x, 40, w - 40), Phaser.Math.Clamp(this.bladePos.y, 40, h - 40));
    this.bladeGoal.copy(this.bladePos);
    this.targets.forEach((t) => this.placeTarget(t, true));
    this.applyWeapon();
    this.aimAt(this.lastAim ?? { x: w * 0.8, y: h * 0.45 });
    $('size').textContent = `${Math.round(w)} × ${Math.round(h)} @${+(window.devicePixelRatio || 1).toFixed(2)}x`;
  }

  // play area for targets, clear of the HUD bars and the hotbar
  bounds() {
    const top = Math.min(90, this.H * 0.16), bot = Math.min(150, this.H * 0.26);
    return { x0: this.W * 0.42, x1: this.W - 40, y0: top + 30, y1: Math.max(top + 60, this.H - bot - 20) };
  }

  // ---------- weapons ----------
  get W8() { return WEAPONS[this.weapon]; }

  setWeapon(w) {
    if (!WEAPONS[w]) return;
    this.weapon = w;
    this.swing = null;
    this.cool = Math.min(this.cool, 0.15);
    this.applyWeapon();
    document.querySelectorAll('.slot').forEach((b) => b.setAttribute('aria-pressed', b.dataset.w === w));
    this.flash(this.held);
  }

  // texture, origin and scale for the current weapon and tier
  applyWeapon() {
    const d = this.W8;
    if (this.weapon === 'pistol') {
      // the pistol comes from the atlas: setFrame with updateOrigin = false keeps our origin
      this.held.setTexture(ATLAS).setFrame(PISTOL_FRAMES[this.tier], false, false);
    } else {
      this.held.setTexture(`${this.weapon}${this.tier + 1}`);
    }
    this.held.texPx = this.held.frame.width;              // 1024 for the atlas, 400 for the webps
    this.held.setOrigin(d.pivot[0] / 1024, d.pivot[1] / 1024);
    this.baseScale = this.framePx / this.held.texPx;
    this.held.setScale(this.baseScale).setRotation(0).setVisible(!(this.weapon === 'grenade' && this.nadeOut));
    this.hand.setVisible(d.kind !== 'blade');
    if (d.kind === 'blade') { this.held.setPosition(this.bladePos.x, this.bladePos.y).setRotation(this.restAngle); }
    else this.held.setPosition(this.handAt.x, this.handAt.y);
    if (d.kind === 'gun') this.aimAt(this.lastAim ?? { x: this.W * 0.8, y: this.H * 0.45 });
  }

  nextTier() {
    this.tier = (this.tier + 1) % 3;
    this.applyWeapon();
    $('tier').innerHTML = `Tier <b>${TIER_NAMES[this.tier]}</b>`;
    this.flash(this.held);
  }

  toggleDebug() {
    this.debug = !this.debug;
    document.body.classList.toggle('debug', this.debug);
    $('debug').setAttribute('aria-pressed', this.debug);
    if (!this.debug) this.fx.clear();
  }

  onMove(p) {
    this.lastAim = { x: p.worldX, y: p.worldY };
    const k = this.W8.kind;
    if (k === 'gun') this.aimAt(this.lastAim);
    else if (k === 'blade') this.bladeGoal.set(p.worldX, p.worldY);
    else this.held.setRotation(Phaser.Math.Clamp((p.worldX - this.handAt.x) / this.W, -0.3, 0.3));
  }

  use() {
    if (this.cool > 0) return;
    const k = this.W8.kind;
    if (k === 'gun') this.fire();
    else if (k === 'blade') this.startSwing();
    else this.throwNade();
  }

  aimAt(p) {
    if (this.W8.kind !== 'gun') return;
    // aim the barrel, not the grip: the muzzle sits above the pivot, so tilt the gun until
    // the line out of the muzzle passes through the pointer
    const d = this.W8, px = p.x - this.handAt.x, py = p.y - this.handAt.y, dist = Math.hypot(px, py);
    const phi = Math.atan2(py, px), flip = Math.abs(phi) > Math.PI / 2 ? -1 : 1;   // pointing left? flip so it isn't upside down
    const off = (d.point[1] - d.pivot[1]) / 1024 * this.framePx * flip;
    const a = dist > Math.abs(off) ? phi - Math.asin(off / dist) : phi;
    this.held.setRotation(a);
    this.held.setScale(this.baseScale, this.baseScale * flip);
  }

  // a point in 1024 frame space -> world space: offset from the pivot, scaled, rotated
  attach(point) {
    const img = this.held, d = this.W8, k = img.texPx / 1024;
    const dx = (point[0] - d.pivot[0]) * k * img.scaleX, dy = (point[1] - d.pivot[1]) * k * img.scaleY;
    const c = Math.cos(img.rotation), s = Math.sin(img.rotation);
    return { x: img.x + dx * c - dy * s, y: img.y + dx * s + dy * c };
  }

  // ---------- guns ----------
  fire() {
    const d = this.W8, m = this.attach(d.point), r = this.held.rotation, u = this.unit;
    for (let i = 0; i < d.pellets; i++) {
      const off = d.pellets > 1 ? (i / (d.pellets - 1) - 0.5) * d.spread : 0;
      const a = r + off + (Math.random() - 0.5) * (d.pellets > 1 ? 0.06 : d.spread);
      const speed = u * d.speed * (d.pellets > 1 ? 0.9 + Math.random() * 0.2 : 1);
      const bolt = this.add.rectangle(m.x, m.y, u * d.len, Math.max(2, u * (d.pellets > 1 ? 0.01 : 0.007)), d.pellets > 1 ? HOT : LIME)
        .setRotation(a).setDepth(2);
      bolt.vx = Math.cos(a) * speed; bolt.vy = Math.sin(a) * speed;
      bolt.life = (d.range * u) / speed;                     // seconds until it fizzles
      this.bolts.push(bolt);
    }
    const f = this.add.circle(m.x, m.y, u * (d.pellets > 1 ? 0.045 : 0.025), CREAM).setBlendMode(Phaser.BlendModes.ADD).setDepth(4);
    this.tweens.add({ targets: f, scale: 0, alpha: 0, duration: d.pellets > 1 ? 180 : 110, onComplete: () => f.destroy() });
    this.cool = d.rate;
    this.recoil = 1;
    if (d.pellets > 1 && !reduceMotion) this.cameras.main.shake(80, 0.003);
  }

  // ---------- blade ----------
  startSwing() {
    if (this.swing) return;
    this.swing = { t: 0, from: this.restAngle - 0.6, to: this.restAngle + 1.9 };
    this.held.setRotation(this.swing.from);
    this.cool = 0.25;
  }

  // ---------- grenade ----------
  throwNade() {
    const d = this.W8, from = { x: this.handAt.x, y: this.handAt.y - this.framePx * 0.1 };
    const goal = this.lastAim ?? { x: this.W * 0.7, y: this.H * 0.5 };
    const max = this.unit * 0.95, dist = Phaser.Math.Distance.BetweenPoints(from, goal);
    const to = dist > max ? { x: from.x + (goal.x - from.x) * max / dist, y: from.y + (goal.y - from.y) * max / dist } : goal;
    const n = this.add.image(from.x, from.y, `grenade${this.tier + 1}`).setDepth(3)
      .setOrigin(d.pivot[0] / 1024, d.pivot[1] / 1024).setScale(this.framePx / 400 * 0.8);
    n.from = from; n.to = to; n.t = 0; n.flight = 0.45 + Math.min(dist, max) / this.unit * 0.35;
    n.arc = this.unit * (0.18 + Math.min(dist, max) / this.unit * 0.2);   // apex height
    n.spin = (to.x >= from.x ? 1 : -1) * 9;
    this.nades.push(n);
    this.nadeOut = true;
    this.held.setVisible(false);
    this.cool = 0.9;
  }

  explode(x, y) {
    const R = this.unit * 0.17;
    const core = this.add.circle(x, y, R * 0.35, CREAM).setBlendMode(Phaser.BlendModes.ADD).setDepth(5);
    const ring = this.add.circle(x, y, R, 0x000000, 0).setStrokeStyle(3, LIME).setDepth(5).setScale(0.2);
    const glow = this.add.circle(x, y, R, HOT, 0.25).setBlendMode(Phaser.BlendModes.ADD).setDepth(4).setScale(0.3);
    this.tweens.add({ targets: core, scale: 1.8, alpha: 0, duration: 260, onComplete: () => core.destroy() });
    this.tweens.add({ targets: ring, scale: 1, alpha: 0, duration: 380, ease: 'Cubic.Out', onComplete: () => ring.destroy() });
    this.tweens.add({ targets: glow, scale: 1.1, alpha: 0, duration: 420, ease: 'Cubic.Out', onComplete: () => glow.destroy() });
    if (!reduceMotion) this.cameras.main.shake(160, 0.008);
    this.targets.filter((t) => Phaser.Math.Distance.Between(x, y, t.x, t.y) < R + t.r).forEach((t) => this.destroyTarget(t));
    // a fresh grenade appears in the hand
    this.nadeOut = false;
    if (this.weapon === 'grenade') {
      this.held.setVisible(true).setAlpha(0);
      this.tweens.add({ targets: this.held, alpha: 1, duration: 200 });
    }
  }

  // ---------- targets ----------
  spawnTarget() {
    const t = this.add.container(0, 0).setDepth(1);
    const ring = this.add.circle(0, 0, 1, 0x000000, 0).setStrokeStyle(2, LIME);
    const inner = this.add.circle(0, 0, 1, LIME, 0.12);
    const core = this.add.rectangle(0, 0, 1, 1, GOLD).setRotation(Math.PI / 4);
    t.add([inner, ring, core]);
    t.parts = { ring, inner, core };
    t.phase = Math.random() * Math.PI * 2;
    this.targets.push(t);
    this.placeTarget(t);
    t.setScale(0);
    this.tweens.add({ targets: t, scale: 1, duration: reduceMotion ? 0 : 280, ease: 'Back.Out' });
  }

  placeTarget(t, keep = false) {
    const r = Phaser.Math.Clamp(this.unit * 0.055, 18, 40);
    t.r = r;
    t.parts.ring.setRadius(r);
    t.parts.inner.setRadius(r * 0.92);
    t.parts.core.setSize(r * 0.6, r * 0.6);
    // positions are stored as 0..1 inside the play area, so a resize scales them, never stacks them
    const b = this.bounds(), at = (u, v) => ({ x: b.x0 + (b.x1 - b.x0) * u, y: b.y0 + (b.y1 - b.y0) * v });
    if (!keep) {
      for (let i = 0; i < 20; i++) {
        t.u = Math.random(); t.v = Math.random();
        const p = at(t.u, t.v);
        if (this.targets.every((o) => o === t || o.u === undefined || Phaser.Math.Distance.BetweenPoints(at(o.u, o.v), p) > r * 3)) break;
      }
    }
    t.base = at(t.u, t.v);
    t.setPosition(t.base.x, t.base.y);
  }

  destroyTarget(t) {
    if (t.dead) return;
    t.dead = true;
    this.hits++;
    $('hits').textContent = this.hits;
    for (let i = 0; i < 10; i++) {
      const a = (i / 10) * Math.PI * 2 + Math.random() * 0.4;
      const s = this.add.rectangle(t.x, t.y, t.r * 0.28, t.r * 0.12, i % 3 ? LIME : GOLD).setRotation(a).setDepth(4);
      this.tweens.add({ targets: s, x: t.x + Math.cos(a) * t.r * 3, y: t.y + Math.sin(a) * t.r * 3, angle: 180, alpha: 0,
        duration: 420, ease: 'Cubic.Out', onComplete: () => s.destroy() });
    }
    const ring = this.add.circle(t.x, t.y, t.r, 0x000000, 0).setStrokeStyle(2, CREAM).setDepth(4);
    this.tweens.add({ targets: ring, scale: 2.4, alpha: 0, duration: 300, onComplete: () => ring.destroy() });
    if (!reduceMotion) this.cameras.main.shake(90, 0.004);
    this.targets = this.targets.filter((o) => o !== t);
    t.destroy();
    this.time.delayedCall(550, () => this.spawnTarget());
  }

  flash(img) {
    if (reduceMotion || !img.visible) return;
    // Phaser 4: fill tints are setTint + setTintMode (setTintFill was removed)
    img.setTint(CREAM).setTintMode(Phaser.TintModes.FILL);
    this.time.delayedCall(60, () => img.clearTint());
  }

  // ---------- loop ----------
  update(time, dt) {
    const s = Math.min(dt, 50) / 1000, d = this.W8;
    this.cool = Math.max(0, this.cool - s);

    // rifle keeps firing while the pointer is held
    if (d.auto && this.input.activePointer.isDown && this.cool === 0) this.fire();

    // recoil: push the gun back along its barrel, then settle
    if (d.kind === 'gun') {
      this.recoil = Math.max(0, this.recoil - s * 8);
      const back = this.recoil * d.kick * this.unit, r = this.held.rotation;
      this.held.setPosition(this.handAt.x - Math.cos(r) * back, this.handAt.y - Math.sin(r) * back);
    }

    this.targets.forEach((t) => {
      if (!reduceMotion) t.y = t.base.y + Math.sin(time / 600 + t.phase) * t.r * 0.25;
      t.parts.core.rotation += s * 1.5;
    });

    // bolts and pellets: move, fade at the end of their range, test against targets
    this.bolts = this.bolts.filter((b) => {
      b.x += b.vx * s; b.y += b.vy * s; b.life -= s;
      if (b.life < 0.12) b.setAlpha(Math.max(0, b.life / 0.12));
      const hit = this.targets.find((t) => Phaser.Math.Distance.Between(b.x, b.y, t.x, t.y) < t.r);
      if (hit) this.destroyTarget(hit);
      const done = hit || b.life <= 0 || b.x < -50 || b.y < -50 || b.x > this.W + 50 || b.y > this.H + 50;
      if (done) b.destroy();
      return !done;
    });

    // grenades: parabolic flight, then a short blinking fuse
    this.nades = this.nades.filter((n) => {
      if (n.t < 1) {
        n.t = Math.min(1, n.t + s / n.flight);
        n.x = Phaser.Math.Linear(n.from.x, n.to.x, n.t);
        n.y = Phaser.Math.Linear(n.from.y, n.to.y, n.t) - Math.sin(n.t * Math.PI) * n.arc;
        n.rotation += n.spin * s;
        if (n.t >= 1) n.fuse = 0.4;
        return true;
      }
      n.fuse -= s;
      n.setTint(Math.floor(n.fuse * 12) % 2 ? HOT : 0xffffff);
      if (n.fuse <= 0) { this.explode(n.x, n.y); n.destroy(); return false; }
      return true;
    });

    // blade: grip eases toward the pointer, swings on click
    this.trail.clear();
    if (d.kind === 'blade') {
      this.bladePos.lerp(this.bladeGoal, 1 - Math.pow(0.0001, s));
      this.held.setPosition(this.bladePos.x, this.bladePos.y);
      if (this.swing) {
        this.swing.t = Math.min(1, this.swing.t + s / 0.18);
        const k = Phaser.Math.Easing.Cubic.Out(this.swing.t);
        this.held.setRotation(Phaser.Math.Linear(this.swing.from, this.swing.to, k));
        this.drawTrail(k);
        // test points along the edge, grip to tip
        const tip = this.attach(d.point);
        for (let i = 2; i <= 6; i++) {
          const f = i / 6, px = this.held.x + (tip.x - this.held.x) * f, py = this.held.y + (tip.y - this.held.y) * f;
          this.targets.filter((t) => Phaser.Math.Distance.Between(px, py, t.x, t.y) < t.r).forEach((t) => this.destroyTarget(t));
        }
        if (this.swing.t >= 1) {
          this.tweens.add({ targets: this.held, rotation: this.restAngle, duration: 220, ease: 'Sine.InOut' });
          this.swing = null;
        }
      } else if (!this.tweens.isTweening(this.held)) {
        const lean = Phaser.Math.Clamp((this.bladeGoal.x - this.bladePos.x) / this.unit, -0.3, 0.3);
        this.held.setRotation(Phaser.Math.Linear(this.held.rotation, this.restAngle + lean, 0.2));
      }
    }

    if (this.debug) this.drawDebug();
  }

  drawTrail(k) {
    const d = this.W8, len = (d.point[0] - d.pivot[0]) / 1024 * this.framePx;
    const a0 = this.swing.from, a1 = this.held.rotation;
    this.trail.fillStyle(LIME, 0.22 * (1 - k * 0.6));
    this.trail.slice(this.held.x, this.held.y, len, a0 + (a1 - a0) * 0.35, a1, false);
    this.trail.fillPath();
  }

  drawDebug() {
    const fx = this.fx.clear(), d = this.W8;
    const dot = (p, c) => { fx.fillStyle(c, 1).fillCircle(p.x, p.y, 4); fx.lineStyle(1, c, 0.6).strokeCircle(p.x, p.y, 9); };
    if (this.held.visible) {
      const p = this.attach(d.point);
      dot(this.held, GOLD); dot(p, LIME);
      fx.lineStyle(1, LIME, 0.4).lineBetween(this.held.x, this.held.y, p.x, p.y);
    }
    if (d.kind === 'throw' && this.lastAim) fx.lineStyle(1, HOT, 0.35).strokeCircle(this.lastAim.x, this.lastAim.y, this.unit * 0.17);
    this.targets.forEach((t) => fx.lineStyle(1, CREAM, 0.4).strokeCircle(t.x, t.y, t.r));
  }
}

new Phaser.Game({
  type: Phaser.AUTO,
  parent: 'game',
  backgroundColor: '#101311',
  scale: { mode: Phaser.Scale.RESIZE, width: '100%', height: '100%' },
  scene: Demo,
});
