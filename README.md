# Teki Solves site

The live site is built from `source/` and published automatically by GitHub Actions
(`.github/workflows/deploy.yml`) on every push to `main`.

```
source/   build.py + products.json + style.css + script.js + assets  (edit these)
```

The HTML files at the repo root are the old hand-published build. Once Pages is set to
"GitHub Actions" they are no longer served, but `build.py` still copies the privacy and
cookie policy pages from them, so keep those two.

## One-time setup

1. Settings > Secrets and variables > Actions > **New repository secret**:
   `TEKI_EMAIL` = the contact email shown on the site.
2. Settings > Pages > Build and deployment > **Source: GitHub Actions**.

## Local preview (Termux)

```
cd source && TEKI_EMAIL=you@example.com python3 build.py   # writes source/dist
```

## Editing products

Everything about a product lives in `source/products.json`: price, included items,
licence summary, engine notes and image paths. Images go in `source/assets/`.

## Still to do

- Privacy and cookie policy text still mentions services; review it.
- Terms, Refund Policy and Licensing pages are not built (no invented legal wording).
