# Teki Solves site (lean build)

site/    ready to deploy static files (open index.html to preview)
source/  build.py + products.json + style.css + script.js + assets

Rebuild after edits (Termux):  cd source && LEGACY_DIR=/path/to/old-site python3 build.py   -> writes source/dist

Before launch
- Set SITE_URL in build.py (enables canonical, og:url, sitemap.xml)
- Add real previews: assets/retro-arsenal-preview-dark.png and -light.png (the arch art stands in until then)
- Verify Retro Arsenal package details, price, licence, store URL against the live itch.io page
- Verify GA4 ID in script.js (G-8V28F53XS9)
- Contact form: same endpoint, field names and payload as the old site. "Services" removed from the dropdown.
- Privacy and cookie policy text is carried over unchanged; it still mentions services, so review it
- Terms, Refund Policy and Licensing pages are not built (no invented legal wording)
