---
title: How to Load a Texture Atlas in Phaser 4 (and Line Up Weapons Properly)
seo_title: Phaser 4 Texture Atlas Tutorial: Pivots and Muzzle Points
description: Load a texture atlas in Phaser 4, fix the pivot bug that misaligns weapons, spawn bullets from the muzzle and swap tiers. Free sample included.
date: 2026-11-22
updated: 2026-11-23
image: assets/blog/phaser-4-texture-atlas/og.png
image_alt: Three tiers of a retro sci-fi laser pistol next to the title of the tutorial
devto: 2026-11-24T14:00:00Z
devto_tags: phaser, gamedev, javascript, tutorial
made: Written by Khaya, drafted with help from Claude (AI). The demo was tested in Phaser 4.2.1 on a low-end Android phone before publishing.
---

Loading a texture atlas in Phaser takes one line. Getting a weapon to sit in a character's hand, fire from the right spot and upgrade without jumping around takes a bit more, and that's the part most tutorials skip.

This guide covers both. It's written for **Phaser 4**, which came out in April 2026. Most atlas tutorials out there are still for Phaser 2 or 3.

You can follow along with a **free sample**: the Laser Pistol from my pack Retro Arsenal, in all 3 tiers, as an atlas + JSON with a working demo.

**[Download the free sample (ZIP, 210 KB)](assets/blog/phaser-4-texture-atlas/retro-arsenal-free-sample.zip)** · **[Try the live demo](assets/blog/phaser-4-texture-atlas/demo/)**

The live demo goes further than the ZIP: all five weapons from the pack, each behaving like what it is. Hold to fire the rifle, get close with the shotgun, swing the blade onto a target or lob a grenade. Press **D** to see every pivot and muzzle point while you play.

## What a texture atlas is (and why bother)

A texture atlas is one big image with lots of sprites packed into it, plus a data file that says where each sprite is. Instead of loading 15 separate PNGs, the game loads one image and one JSON file.

Why it's worth it:

- **Fewer downloads.** One request instead of dozens, which matters on mobile.
- **Faster rendering.** Sprites that share a texture can be drawn together.
- **Extra data travels with the art.** This is the underrated part. The JSON can carry pivot points, muzzle points, tier names, anything you want. We'll use that below.

## Loading the atlas in Phaser 4

In your scene's `preload`, point Phaser at the image and the JSON:

```js
preload() {
  this.load.atlas('arsenal', 'retro_arsenal_sample.png', 'retro_arsenal_sample.json');
}
```

Phaser reads the two common TexturePacker formats, JSON Hash and JSON Array, so most packers work out of the box.

Then in `create`, add a sprite using the atlas key and a frame name:

```js
create() {
  this.gun = this.add.image(260, 260, 'arsenal', 'weapon_laser_pistol_t1_scrap.png');
}
```

### Gotcha 1: frame names often include ".png"

Look at your JSON before you guess frame names. Many packers keep the original file name as the key, extension and all:

```json
"frames": {
  "weapon_laser_pistol_t1_scrap.png": { "frame": { "x": 0, "y": 0, "w": 1024, "h": 1024 }, ... }
}
```

If you write `'weapon_laser_pistol_t2_military'` without `.png`, Phaser doesn't crash. It logs a warning (`Texture "arsenal" has no frame ...`) and quietly shows the **first frame in the atlas** instead. So you get a real sprite, just the wrong one, which is easy to miss. Keep the console open and it's a four-character fix.

## Putting the weapon in the hand: pivots

A pivot (or origin) is the point of a sprite that sits on its x and y position, and the point it rotates around. For a gun, you want that to be the grip, not the middle of the image. Otherwise the gun swings around its own centre like a propeller.

Good asset packs store the pivot for you. Retro Arsenal stores two versions per frame:

- `pivot`: normalised 0 to 1, measured from the **bottom-left** (Unity's convention)
- `custom.pivot_px`: in pixels, measured from the **top-left**

### Gotcha 2: Phaser applies the pivot for you, upside down

This one is sneaky. When Phaser loads a JSON atlas, it looks for a `pivot` on each frame, and if it finds one, every sprite using that frame gets that origin automatically.

The catch: Phaser measures origin from the **top-left**. If your atlas was exported with a bottom-left pivot, like many Unity-friendly packs, Phaser applies it without complaint and your weapon ends up noticeably above or below the hand. No error, just a gun floating in the wrong place.

The fix is to set the origin yourself from the top-left pixel values:

```js
const data = this.gun.frame.customData.custom;   // everything from the JSON frame
this.gun.setOrigin(data.pivot_px.x / 1024, data.pivot_px.y / 1024);
```

`frame.customData` is Phaser's copy of the whole JSON entry for that frame, so any extra data your atlas carries is right there.

If your atlas only has a bottom-left `pivot`, flip the y yourself:

```js
this.gun.setOrigin(frame.pivotX, 1 - frame.pivotY);
```

## Aiming and firing from the muzzle

Rotating towards the pointer is one line:

```js
this.input.on('pointermove', (p) => {
  const angle = Phaser.Math.Angle.Between(this.gun.x, this.gun.y, p.worldX, p.worldY);
  this.gun.setRotation(angle);
  // Pointing left? Flip vertically so the gun isn't upside down.
  this.gun.setScale(0.25, Math.abs(angle) > Math.PI / 2 ? -0.25 : 0.25);
});
```

Now the interesting bit. Bullets should come out of the barrel, not the hand. Retro Arsenal stores a `muzzle_px` point per frame, so we can work out where it is in the world, whatever the rotation and scale:

```js
muzzle() {
  const c = this.gun.frame.customData.custom;
  const dx = (c.muzzle_px.x - c.pivot_px.x) * this.gun.scaleX;
  const dy = (c.muzzle_px.y - c.pivot_px.y) * this.gun.scaleY;
  const cos = Math.cos(this.gun.rotation);
  const sin = Math.sin(this.gun.rotation);
  return { x: this.gun.x + dx * cos - dy * sin, y: this.gun.y + dx * sin + dy * cos };
}
```

That's the offset from the grip to the muzzle, scaled, then rotated. Spawn your projectile there:

```js
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
```

The same idea works for any attachment point: a blade tip for hit effects, a grenade pin, a muzzle flash.

## Swapping weapon tiers at runtime

Every weapon in Retro Arsenal comes in three tiers (Scrap, Military, Prototype) drawn on the same shape, with the **same pivot and muzzle point**. So an upgrade is just a frame swap:

```js
this.gun.setFrame('weapon_laser_pistol_t2_military.png', false, false);
```

### Gotcha 3: setFrame resets your origin

Look at that last `false`. By default, `setFrame` re-applies the frame's pivot from the JSON, which brings Gotcha 2 straight back and undoes your `setOrigin`. Passing `false` as the third argument (`updateOrigin`) keeps the origin you set.

## Will a 4096px atlas work on a cheap phone?

The full Retro Arsenal atlas is 4096 × 4096. Most phones from the last several years handle that, but older or budget GPUs can top out lower. You can check the device limit with plain WebGL:

```js
const gl = document.createElement('canvas').getContext('webgl');
console.log(gl.getParameter(gl.MAX_TEXTURE_SIZE)); // e.g. 4096, 8192 or 16384
```

If you need to support very old devices, repack into smaller atlases (2048 is a safe size) and load them with `this.load.multiatlas()`. The free sample is 3072 × 1024, so it runs anywhere.

## Phaser 3 vs Phaser 4: what changed for atlases?

Very little for this workflow. `this.load.atlas`, `frame.customData`, the automatic pivot and `setFrame(frame, updateSize, updateOrigin)` all work the same way in both, so this guide applies to Phaser 3 too.

The new thing in Phaser 4 is the **Phaser Compact Texture Atlas** (`.pct`), a text format that's typically 90 to 95% smaller than the JSON, loaded with `this.load.atlasPCT()`. Worth a look once you're shipping lots of atlases.

## Grab the code

The free sample includes everything in this post as one working file (`main.js`), plus the pistol in all 3 tiers:

**[Download the free sample (ZIP)](assets/blog/phaser-4-texture-atlas/retro-arsenal-free-sample.zip)** · **[Try the live demo](assets/blog/phaser-4-texture-atlas/demo/)**

Use the sprites in your own games, commercial ones included. Just don't resell the files.

If you want the other four weapons (laser rifle, shotgun, energy blade and plasma grenade), each in the same three tiers with pivot and muzzle data, that's **[Retro Arsenal](retro-arsenal.html)**. I made it, so I'm biased, but it's built for exactly this setup.
