# Draft options for 2026-11-28-aim-barrel
Written by Gemini from the brief's facts. The first option that passed the brand checks was put in the brief. Edit or swap before merging.

## instagram

### Option 1 (passes checks)
Bullets pass above your target because rotating a gun sprite aims its grip, not its muzzle.

Find the angle to your cursor with Math.atan2. Subtract the arcsine of your vertical offset divided by distance. Flip the sign when the gun points left.

That is three lines of math to fix your aiming. See it running in the browser demo and grab the free laser pistol sprite in the link in bio.

#phaser #indiedev #gamedev #phaserjs #javascript

### Option 2 (passes checks)
Your gun aims high or low because the sprite rotates around its grip instead of the barrel.

Calculate the angle to the cursor, then subtract the offset ratio using Math.asin. Flip the offset sign if the sprite points left.

It takes three lines of code. You can test it live in the browser demo and download the free laser pistol with its muzzle data from the link in bio.

#gamedev #phaserjs #indiedev #javascript #2dart

### Option 3 (passes checks)
Shots miss what you point at because the pivot is the grip, not the tip of the gun.

Get the angle to the cursor, find your vertical offset ratio, and subtract it from your rotation. Remember to flip that offset when the sprite faces left.

This simple math makes your guns hit their marks. Try the live demo and get the free laser pistol sprite from the link in bio.

#phaserjs #gamedev #indiedev #javascript #webgamedev
