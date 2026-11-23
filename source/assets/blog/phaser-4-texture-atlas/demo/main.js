// Retro Arsenal: Phaser 4 weapon demo by Teki Solves
// Pistol: aim, fire from the muzzle, swap tiers without the sprite jumping.
// Blade:  the grip follows your pointer, click/tap to swing, the blade edge destroys targets.
// The canvas fills the window and re-lays itself out on every resize.

const ATLAS = 'arsenal';
const PISTOL = [                                  // atlas frame names include ".png"
  'weapon_laser_pistol_t1_scrap.png',
  'weapon_laser_pistol_t2_military.png',
  'weapon_laser_pistol_t3_prototype.png',
];
const TIER_NAMES = ['Scrap', 'Military', 'Prototype'];

// The blade ships as plain images here, so its attachment points live in code,
// in the same top-left pixel format the atlas uses.
const BLADE = { size: 400, pivot_px: { x: 95, y: 237 }, tip_px: { x: 352, y: 246 }, keys: ['blade1', 'blade2', 'blade3'] };

const LIME = 0xb2dd31, GOLD = 0xe9c55c, CREAM = 0xf4f3ed;
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const $ = (id) => document.getElementById(id);

class Demo extends Phaser.Scene {
  preload() {
    this.load.atlas(ATLAS, 'retro_arsenal_sample.png', 'retro_arsenal_sample.json');
    BLADE.keys.forEach((k, i) => this.load.image(k, `blade-t${i + 1}.webp`));
  }

  create() {
    this.tier = 0;
    this.hits = 0;
    this.weapon = 'pistol';
    this.bolts = [];
    this.targets = [];
    this.debug = false;

    // Pistol: origin from the pixel pivot (top-left, like Phaser).
    this.gun = this.add.image(0, 0, ATLAS, PISTOL[0]);
    const g = this.gun.frame.customData.custom;
    this.gun.setOrigin(g.pivot_px.x / 1024, g.pivot_px.y / 1024);
    this.hand = this.add.circle(0, 0, 5, LIME).setDepth(4);
    this.gun.setDepth(3);

    // Blade: origin on the grip, so it rotates around the hand.
    this.blade = this.add.image(0, 0, BLADE.keys[0])
      .setOrigin(BLADE.pivot_px.x / BLADE.size, BLADE.pivot_px.y / BLADE.size).setDepth(3);
    this.bladePos = new Phaser.Math.Vector2();
    this.bladeGoal = new Phaser.Math.Vector2();
    this.restAngle = -0.6;        // resting angle in radians (blade raised)
    this.swing = null;            // { t, from, to } while a swing is running
    this.trail = this.add.graphics().setBlendMode(Phaser.BlendModes.ADD).setDepth(2);
    this.fx = this.add.graphics().setDepth(5);   // debug overlay

    this.layout(this.scale.gameSize);
    this.scale.on('resize', (size) => this.layout(size));

    this.input.on('pointermove', (p) => this.onMove(p));
    this.input.on('pointerdown', (p) => { this.onMove(p); this.act(); });
    const kb = this.input.keyboard;
    kb?.on('keydown-SPACE', () => this.nextTier());
    kb?.on('keydown-ONE', () => this.setWeapon('pistol'));
    kb?.on('keydown-TWO', () => this.setWeapon('blade'));
    kb?.on('keydown-D', () => this.toggleDebug());

    $('w-pistol').onclick = () => this.setWeapon('pistol');
    $('w-blade').onclick = () => this.setWeapon('blade');
    $('tier').onclick = () => this.nextTier();
    $('debug').onclick = () => this.toggleDebug();

    for (let i = 0; i < 3; i++) this.spawnTarget();
    this.setWeapon('pistol');
  }

  // ---------- layout: everything is sized from the smaller screen side ----------
  layout({ width: w, height: h }) {
    this.cameras.main.setViewport(0, 0, w, h);
    this.W = w; this.H = h;
    const m = Math.min(w, h);
    this.unit = m;
    this.gunScale = Phaser.Math.Clamp(m * 0.5, 140, 360) / 1024;
    const bladeLen = Phaser.Math.Clamp(m * 0.42, 120, 330);
    this.bladeScale = bladeLen / (BLADE.tip_px.x - BLADE.pivot_px.x);
    this.handAt = { x: Math.max(w * 0.2, 90), y: h * 0.58 };
    this.gun.setPosition(this.handAt.x, this.handAt.y);
    this.hand.setPosition(this.handAt.x, this.handAt.y);
    this.blade.setScale(this.bladeScale);
    if (this.bladePos.lengthSq() === 0) { this.bladePos.set(w * 0.3, h * 0.6); this.bladeGoal.copy(this.bladePos); }
    this.bladePos.set(Phaser.Math.Clamp(this.bladePos.x, 0, w), Phaser.Math.Clamp(this.bladePos.y, 0, h));
    this.bladeGoal.copy(this.bladePos);
    this.targets.forEach((t) => this.placeTarget(t, true));
    this.aimAt(this.lastAim ?? { x: w * 0.8, y: h * 0.45 });
    const dpr = window.devicePixelRatio || 1;
    $('size').textContent = `${Math.round(w)} × ${Math.round(h)} @${dpr}x`;
  }

  // keep play space clear of the HUD bars
  bounds() {
    const top = Math.min(90, this.H * 0.16), bot = Math.min(70, this.H * 0.12);
    return { x0: this.W * 0.42, x1: this.W - 40, y0: top + 30, y1: this.H - bot - 30 };
  }

  // ---------- input ----------
  onMove(p) {
    if (this.weapon === 'pistol') this.aimAt({ x: p.worldX, y: p.worldY });
    else this.bladeGoal.set(p.worldX, p.worldY);
  }

  act() { this.weapon === 'pistol' ? this.fire() : this.startSwing(); }

  setWeapon(w) {
    this.weapon = w;
    this.gun.setVisible(w === 'pistol');
    this.hand.setVisible(w === 'pistol');
    this.blade.setVisible(w === 'blade');
    $('w-pistol').setAttribute('aria-pressed', w === 'pistol');
    $('w-blade').setAttribute('aria-pressed', w === 'blade');
  }

  nextTier() {
    this.tier = (this.tier + 1) % 3;
    // updateSize/updateOrigin = false: keep our origin. Every tier shares the same pivot.
    this.gun.setFrame(PISTOL[this.tier], false, false);
    this.blade.setTexture(BLADE.keys[this.tier]);
    $('tier').innerHTML = `Tier <b>${TIER_NAMES[this.tier]}</b>`;
    this.flash(this.weapon === 'pistol' ? this.gun : this.blade);
  }

  toggleDebug() {
    this.debug = !this.debug;
    document.body.classList.toggle('debug', this.debug);
    $('debug').setAttribute('aria-pressed', this.debug);
    if (!this.debug) this.fx.clear();
  }

  // ---------- pistol ----------
  aimAt(p) {
    this.lastAim = p;
    const a = Phaser.Math.Angle.Between(this.gun.x, this.gun.y, p.x, p.y);
    this.gun.setRotation(a);
    // pointing left? flip vertically so the gun isn't upside down
    this.gun.setScale(this.gunScale, Math.abs(a) > Math.PI / 2 ? -this.gunScale : this.gunScale);
  }

  // local attachment point -> world space (offset from pivot, scaled, rotated)
  attach(img, pivot, point) {
    const dx = (point.x - pivot.x) * img.scaleX, dy = (point.y - pivot.y) * img.scaleY;
    const c = Math.cos(img.rotation), s = Math.sin(img.rotation);
    return { x: img.x + dx * c - dy * s, y: img.y + dx * s + dy * c };
  }

  muzzle() {
    const c = this.gun.frame.customData.custom;
    return this.attach(this.gun, c.pivot_px, c.muzzle_px);
  }

  fire() {
    const m = this.muzzle(), r = this.gun.rotation, speed = this.unit * 2.4;
    const bolt = this.add.rectangle(m.x, m.y, this.unit * 0.05, Math.max(3, this.unit * 0.008), LIME).setRotation(r).setDepth(2);
    bolt.vx = Math.cos(r) * speed; bolt.vy = Math.sin(r) * speed;
    this.bolts.push(bolt);
    const flash = this.add.circle(m.x, m.y, this.unit * 0.025, CREAM).setBlendMode(Phaser.BlendModes.ADD);
    this.tweens.add({ targets: flash, scale: 0, alpha: 0, duration: 120, onComplete: () => flash.destroy() });
  }

  // ---------- blade ----------
  startSwing() {
    if (this.swing) return;
    const from = this.restAngle - 0.9, to = this.restAngle + 2.3;   // big overhead arc
    this.swing = { t: 0, from, to };
    this.blade.setRotation(from);
  }

  bladeTip() { return this.attach(this.blade, BLADE.pivot_px, BLADE.tip_px); }

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
    const b = this.bounds();
    if (keep) {
      t.base = { x: Phaser.Math.Clamp(t.base.x, b.x0, b.x1), y: Phaser.Math.Clamp(t.base.y, b.y0, b.y1) };
    } else {
      // pick a spot that doesn't overlap the other targets
      for (let i = 0; i < 20; i++) {
        t.base = { x: Phaser.Math.Between(b.x0, Math.max(b.x0, b.x1)), y: Phaser.Math.Between(b.y0, Math.max(b.y0, b.y1)) };
        if (this.targets.every((o) => o === t || !o.base || Phaser.Math.Distance.BetweenPoints(o.base, t.base) > r * 3)) break;
      }
    }
    t.setPosition(t.base.x, t.base.y);
  }

  destroyTarget(t) {
    if (t.dead) return;
    t.dead = true;
    this.hits++;
    $('hits').textContent = this.hits;
    // shards fly out, then a fresh target appears elsewhere
    for (let i = 0; i < 10; i++) {
      const a = (i / 10) * Math.PI * 2 + Math.random() * 0.4;
      const s = this.add.rectangle(t.x, t.y, t.r * 0.28, t.r * 0.12, i % 3 ? LIME : GOLD).setRotation(a);
      this.tweens.add({ targets: s, x: t.x + Math.cos(a) * t.r * 3, y: t.y + Math.sin(a) * t.r * 3, angle: 180, alpha: 0,
        duration: 420, ease: 'Cubic.Out', onComplete: () => s.destroy() });
    }
    const ring = this.add.circle(t.x, t.y, t.r, 0x000000, 0).setStrokeStyle(2, CREAM);
    this.tweens.add({ targets: ring, scale: 2.4, alpha: 0, duration: 300, onComplete: () => ring.destroy() });
    if (!reduceMotion) this.cameras.main.shake(90, 0.004);
    this.targets = this.targets.filter((o) => o !== t);
    t.destroy();
    this.time.delayedCall(550, () => this.spawnTarget());
  }

  flash(img) {
    if (reduceMotion) return;
    img.setTintFill?.(CREAM);
    this.time.delayedCall(60, () => img.clearTint?.());
  }

  // ---------- loop ----------
  update(time, dt) {
    const s = dt / 1000;

    // targets bob gently
    this.targets.forEach((t) => {
      if (!reduceMotion) t.y = t.base.y + Math.sin(time / 600 + t.phase) * t.r * 0.25;
      t.parts.core.rotation += s * 1.5;
    });

    // bolts: move and test against targets
    this.bolts = this.bolts.filter((b) => {
      b.x += b.vx * s; b.y += b.vy * s;
      const hit = this.targets.find((t) => Phaser.Math.Distance.Between(b.x, b.y, t.x, t.y) < t.r);
      if (hit) this.destroyTarget(hit);
      const out = hit || b.x < -50 || b.y < -50 || b.x > this.W + 50 || b.y > this.H + 50;
      if (out) b.destroy();
      return !out;
    });

    // blade: grip eases toward the pointer, swings on click
    if (this.weapon === 'blade') {
      this.bladePos.lerp(this.bladeGoal, 1 - Math.pow(0.0001, s));
      this.blade.setPosition(this.bladePos.x, this.bladePos.y);
      this.trail.clear();
      if (this.swing) {
        this.swing.t = Math.min(1, this.swing.t + s / 0.2);
        const k = Phaser.Math.Easing.Cubic.Out(this.swing.t);
        this.blade.setRotation(Phaser.Math.Linear(this.swing.from, this.swing.to, k));
        this.drawTrail(k);
        // test points along the edge, grip to tip
        const tip = this.bladeTip();
        for (let i = 2; i <= 6; i++) {
          const f = i / 6, px = this.blade.x + (tip.x - this.blade.x) * f, py = this.blade.y + (tip.y - this.blade.y) * f;
          this.targets.filter((t) => Phaser.Math.Distance.Between(px, py, t.x, t.y) < t.r).forEach((t) => this.destroyTarget(t));
        }
        if (this.swing.t >= 1) {
          this.tweens.add({ targets: this.blade, rotation: this.restAngle, duration: 220, ease: 'Sine.InOut' });
          this.swing = null;
        }
      } else if (!this.tweens.isTweening(this.blade)) {
        // lean slightly with movement for a bit of weight
        const lean = Phaser.Math.Clamp((this.bladeGoal.x - this.bladePos.x) / this.unit, -0.3, 0.3);
        this.blade.setRotation(Phaser.Math.Linear(this.blade.rotation, this.restAngle + lean, 0.2));
      }
    }

    if (this.debug) this.drawDebug();
  }

  drawTrail(k) {
    const len = (BLADE.tip_px.x - BLADE.pivot_px.x) * this.bladeScale;
    const a0 = this.swing.from, a1 = this.blade.rotation;
    this.trail.fillStyle(LIME, 0.22 * (1 - k * 0.6));
    this.trail.slice(this.blade.x, this.blade.y, len, a0 + (a1 - a0) * 0.35, a1, false);
    this.trail.fillPath();
  }

  drawDebug() {
    const fx = this.fx.clear();
    const dot = (p, c) => { fx.fillStyle(c, 1).fillCircle(p.x, p.y, 4); fx.lineStyle(1, c, 0.6).strokeCircle(p.x, p.y, 9); };
    if (this.weapon === 'pistol') { dot(this.gun, GOLD); dot(this.muzzle(), LIME); }
    else { dot(this.blade, GOLD); dot(this.bladeTip(), LIME); fx.lineStyle(1, LIME, 0.5).lineBetween(this.blade.x, this.blade.y, this.bladeTip().x, this.bladeTip().y); }
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
