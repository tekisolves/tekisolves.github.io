// Retro Arsenal free sample: Phaser 4 demo
// Aim with the mouse or your finger, tap/click to fire, press "Next tier" (or Space) to upgrade.

const KEY = 'arsenal';
const SCALE = 0.25;                 // sprites are 1024x1024, so 0.25 = 256px on screen
const TIERS = [
  'weapon_laser_pistol_t1_scrap.png',       // frame names include ".png"
  'weapon_laser_pistol_t2_military.png',
  'weapon_laser_pistol_t3_prototype.png',
];

class Demo extends Phaser.Scene {
  preload() {
    this.load.atlas(KEY, 'retro_arsenal_sample.png', 'retro_arsenal_sample.json');
  }

  create() {
    this.tier = 0;

    // The "hand". Put the gun's pivot exactly here.
    const hand = { x: 260, y: 260 };
    this.add.circle(hand.x, hand.y, 5, 0xb2dd31);

    this.gun = this.add.image(hand.x, hand.y, KEY, TIERS[0]).setScale(SCALE);

    // Phaser applies the atlas "pivot" automatically, but reads y from the TOP.
    // Retro Arsenal stores pivot y from the BOTTOM (Unity style), so use the
    // pixel version instead, which is top-left like Phaser.
    const data = this.gun.frame.customData.custom;
    this.gun.setOrigin(data.pivot_px.x / 1024, data.pivot_px.y / 1024);

    this.input.on('pointermove', (p) => this.aim(p));
    this.input.on('pointerdown', (p) => { this.aim(p); this.fire(); });
    this.input.keyboard?.on('keydown-SPACE', () => this.nextTier());

    const btn = this.add.text(20, 20, 'Next tier', {
      fontFamily: 'monospace', fontSize: '22px', color: '#101311',
      backgroundColor: '#b2dd31', padding: { x: 12, y: 8 },
    }).setInteractive({ useHandCursor: true });
    btn.on('pointerdown', (p, x, y, e) => { e.stopPropagation(); this.nextTier(); });

    this.label = this.add.text(20, 70, '', { fontFamily: 'monospace', fontSize: '18px', color: '#f4f3ed' });
    this.showTier();
  }

  aim(p) {
    const angle = Phaser.Math.Angle.Between(this.gun.x, this.gun.y, p.worldX, p.worldY);
    this.gun.setRotation(angle);
    // Pointing left? Flip vertically so the gun isn't upside down.
    this.gun.setScale(SCALE, Math.abs(angle) > Math.PI / 2 ? -SCALE : SCALE);
  }

  // Where the bullet should come from, in world space.
  muzzle() {
    const c = this.gun.frame.customData.custom;
    const dx = (c.muzzle_px.x - c.pivot_px.x) * this.gun.scaleX;
    const dy = (c.muzzle_px.y - c.pivot_px.y) * this.gun.scaleY;
    const cos = Math.cos(this.gun.rotation), sin = Math.sin(this.gun.rotation);
    return { x: this.gun.x + dx * cos - dy * sin, y: this.gun.y + dx * sin + dy * cos };
  }

  fire() {
    const m = this.muzzle();
    const r = this.gun.rotation;
    const bolt = this.add.rectangle(m.x, m.y, 26, 5, 0xb2dd31).setRotation(r);
    this.tweens.add({
      targets: bolt,
      x: m.x + Math.cos(r) * 900,
      y: m.y + Math.sin(r) * 900,
      duration: 600,
      onComplete: () => bolt.destroy(),
    });
  }

  nextTier() {
    this.tier = (this.tier + 1) % TIERS.length;
    // updateOrigin = false: keep our origin. All tiers share the same pivot.
    this.gun.setFrame(TIERS[this.tier], false, false);
    this.showTier();
  }

  showTier() {
    this.label.setText('Tier: ' + this.gun.frame.customData.custom.tier_name);
  }
}

new Phaser.Game({
  type: Phaser.AUTO,
  width: 800,
  height: 450,
  backgroundColor: '#101311',
  scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
  scene: Demo,
});
