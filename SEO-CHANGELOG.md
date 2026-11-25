# Teki Solves: SEO change log

Newest first. Updated automatically after every deploy.

## 2026-11-25 14:57 UTC: Polish the guardian banner: clean diamonds and shoulder

- (no details in the commit message)
- Areas changed: Images
- SEO check after deploy: 11 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-25 11:47 UTC: No horizontal overflow: wrap instead of scrolling sideways

- 'Keep it simple' line slides inside its own strip; the strip never moves past the screen edge
- Weapon range buttons wrap onto rows on phones instead of a sideways scroller
- Blog code blocks and inline code wrap
- Long words and links wrap in headings, text, lists and tables
- html/body clip sideways overflow; older Safari hides it on the root so the sticky header still works
- Checked: 10 pages at 360, 390, 768 and 1280px through the full scroll; SEO bot 0 critical
- Areas changed: Design and layout
- SEO check after deploy: 11 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-25 10:48 UTC: Flow layer: sections blend and scrolling becomes an experience

- Soft eased seams where dark and cream sections meet; hard band lines hidden
- Cream sections open from a rounded inset panel to full width as they arrive
- Section content rises in, hero sinks back as you leave it, guardian camera pulls back
- Interlude line and product grid move with your scroll; gentle heading parallax
- Section tracker rail on wide screens (1280px+), built from each page's own sections
- Scroll effects only where the browser supports scroll timelines, all off for reduced motion
- Checked: every page desktop and phone with no errors, contact form, weapon range, SEO bot 0 critical
- Areas changed: Design and layout
- SEO check after deploy: 11 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-23 21:18 UTC: Demo: grenade can reach every target on wide screens

- (no details in the commit message)
- Areas changed: Images
- SEO check after deploy: 11 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-23 20:47 UTC: Add DEV cover image for the Phaser 4 atlas post

- (no details in the commit message)
- Areas changed: Images
- SEO check after deploy: 11 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-23 20:20 UTC: DEV workflow: accept common secret names

- (no details in the commit message)
- Areas changed: Automation (build, deploy, checks)
- SEO check after deploy: 11 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-23 20:15 UTC: Cross-post blog posts to DEV as drafts, publish on schedule

- .github/devto/devto.py: creates a DEV draft for any post with a devto:
- Runs on blog changes and hourly; needs the DEVTO_API_KEY secret
- First post scheduled for Tue 24 Nov 14:00 UTC
- Areas changed: Automation (build, deploy, checks), Documentation
- SEO check after deploy: 11 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-23 19:39 UTC: Footer: Facebook link uses the new @tekisolves username

- (no details in the commit message)
- Areas changed: Page templates and SEO tags
- SEO check after deploy: 11 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-23 18:07 UTC: Footer: add Facebook to social links (and schema sameAs)

- (no details in the commit message)
- Areas changed: Design and layout, Page templates and SEO tags
- SEO check after deploy: 11 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-23 17:47 UTC: Titles: replace em-dashes with the site's | separator

- (no details in the commit message)
- Areas changed: Page templates and SEO tags
- SEO check after deploy: 11 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-23 17:45 UTC: Demo: all five weapons; contact form rebuilt

- Rifle (hold to fire), shotgun (5-pellet spread, short range, big kick),
- Guns aim through the muzzle, not the grip, so shots land where you point
- Game-style hotbar (1-5) with sprite icons; HUD adapts to narrow windows
- Fix: success panel no longer shows before sending ([hidden] was overridden)
- Field-level validation with clear messages, ticks on valid fields,
- Honest copy: real person reads it, reply aims, what to do if no reply
- Sending state, animated confirmation naming the reply email, send another
- Areas changed: Design and layout, Documentation, Images, Page templates and SEO tags
- SEO check after deploy: 11 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-23 17:33 UTC: Demo: return focus to the game after HUD clicks

- (no details in the commit message)
- Areas changed: Images
- SEO check after deploy: 11 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-23 17:31 UTC: Demo: Phaser 4 tint API, cache-bust main.js

- (no details in the commit message)
- Areas changed: Images
- SEO check after deploy: 11 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-23 17:28 UTC: Demo: movable energy blade, destructible targets, fully responsive

- Blade grip follows the pointer, click/tap swings it; points along the edge
- Pistol bolts now hit targets too; tier swap applies to both weapons
- Phaser Scale.RESIZE: canvas fills the window, everything sized from the
- Brand HUD (weapon toggle, tier, hit counter, pivots debug with live size
- Post mentions the blade in the live demo
- Areas changed: Documentation, Images
- SEO check after deploy: 11 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-23 17:13 UTC: Add social links to footer and upgrade the hologram

- Footer: chamfered HUD tiles for Instagram, TikTok, YouTube, X, Pinterest,
- Organization schema sameAs now lists every profile
- Hologram: soft volumetric beam with travelling light pulses, RGB fringe and
- All new motion is off for reduced-motion users
- Areas changed: Design and layout, Page templates and SEO tags
- SEO check after deploy: 11 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-23 16:39 UTC: Add Pinterest domain verification tag

- (no details in the commit message)
- Areas changed: Page templates and SEO tags
- SEO check after deploy: 11 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-23 02:44 UTC: Mobile polish + installable app + range upgrades (PR #20)

- (no details in the commit message)
- Areas changed: Design and layout, Images, Page templates and SEO tags
- SEO check after deploy: 11 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-23 02:38 UTC: Signature loader + sound for the weapon range (PR #19)

- (no details in the commit message)
- Areas changed: Design and layout, Images, Page templates and SEO tags
- SEO check after deploy: 11 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-23 02:29 UTC: Retro Arsenal: playable weapon range (try before you buy) (PR #18)

- (no details in the commit message)
- Areas changed: Design and layout, Images, Page templates and SEO tags
- SEO check after deploy: 11 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-23 02:24 UTC: Game UI level 2: interactive hologram, reticle, decode text, achievement (PR #17)

- (no details in the commit message)
- Areas changed: Design and layout, Images, Page templates and SEO tags
- SEO check after deploy: 11 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-23 02:18 UTC: Game UI layer + fix stale stylesheet caching (PR #16)

- (no details in the commit message)
- Areas changed: Design and layout, Page templates and SEO tags
- SEO check after deploy: 11 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-23 02:11 UTC: Logo diamond in gold 3D + hologram projector carousel (PR #15)

- (no details in the commit message)
- Areas changed: Design and layout, Page templates and SEO tags
- SEO check after deploy: 11 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-23 01:57 UTC: Homepage 3D: hero diamond + weapon carousel (PR #14)

- (no details in the commit message)
- Areas changed: Design and layout, Images, Page templates and SEO tags
- SEO check after deploy: 11 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-22 21:15 UTC: Fix changelog and IndexNow jobs: install Markdown before building

- (no details in the commit message)
- Areas changed: Automation (build, deploy, checks)
- SEO check after deploy: 11 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-22 19:48 UTC: Content coach: email reminders for blog posts (PR #8)

- (no details in the commit message)
- Areas changed: Automation (build, deploy, checks)
- SEO check after deploy: 8 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-22 18:43 UTC: SEO fixes from the Seobility audit (PR #7)

- (no details in the commit message)
- Areas changed: Images, Page templates and SEO tags
- SEO check after deploy: 8 pages checked, 0 critical problems, 1 minor warnings

## 2026-11-22 18:28 UTC: SEO change log + share images on every page (PR #6)

- (no details in the commit message)
- Areas changed: Automation (build, deploy, checks), Documentation, Page templates and SEO tags, SEO bot rules
- SEO check after deploy: 8 pages checked, 0 critical problems, 3 minor warnings

## 2026-11-22 18:17 UTC: SEO bot: remove Search Engine Land feed (PR #4)

- Removed Search Engine Land from the news feeds because it blocks automated readers. Search Engine Roundtable and Search Engine Journal cover the same news.
- Areas changed: SEO bot news sources
- SEO check after deploy: 8 pages checked, 0 critical problems, 3 minor warnings

## 2026-11-22 18:17 UTC: SEO bot: stop false alarms from Google's docs page (PR #5)

- The bot compares the update headings on Google's search documentation page instead of the whole page, which changes slightly on every load.
- New ranking-related entries send an urgent email. Everything else goes in the Monday digest.
- Areas changed: SEO bot rules
- SEO check after deploy: 8 pages checked, 0 critical problems, 3 minor warnings

## 2026-11-22 15:47 UTC: SEO bot: backup feed addresses, clearer feed errors (PR #3)

- Feeds can list backup addresses, and failed feeds show the HTTP code.
- Areas changed: SEO bot rules, SEO bot news sources

## 2026-11-22 15:42 UTC: SEO bot: daily checks, Monday email digest, deploy guard, IndexNow (PR #2)

- SEO guard: a deploy is blocked if a page breaks a critical rule (missing title or description, noindex, wrong number of h1 tags, missing alt text, invalid structured data, broken internal link).
- IndexNow: search engines are told which pages changed after every deploy.
- Daily news check from official and trusted SEO sources, with emails only for urgent official news or site problems, plus a Monday digest.
- Homepage canonical and og:url now point to the clean address (/).
- Sitemap now includes the privacy and cookie pages, with last-modified dates.
- Areas changed: Automation (build, deploy, checks), Page templates and SEO tags, SEO bot rules, IndexNow key
- SEO check after deploy: 8 pages checked, 0 critical problems, 3 minor warnings

## 2026-11-22 14:40 UTC: Retro Arsenal: real previews, price, licence, share image + auto deploy (PR #1)

- Retro Arsenal page shows the real sprites: tier-swap animation and full 15-sprite previews.
- Price (4.99€), licence summary and engine notes added to the product page.
- Share image (og:image) and Product structured data with the offer price added.
- Product card uses a real sprite; duplicate HTML ids removed; card title contrast fixed.
- Site address set to https://tekisolves.github.io (canonical links, og:url, sitemap).
- Areas changed: Images, Page templates and SEO tags, Product details, Design and layout, Automation (build, deploy, checks)
