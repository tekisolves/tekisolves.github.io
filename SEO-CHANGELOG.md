# Teki Solves: SEO change log

Newest first. Updated automatically after every deploy.

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
