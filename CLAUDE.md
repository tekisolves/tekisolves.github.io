# Teki Solves website: notes for Claude

Owner: Khaya (Teki Solves). Keep answers short. Correct grammar, no em-dashes, his voice: casual, warm, professional.

## How the site works
- Static site built by `source/build.py` (Python). Output goes to `source/dist/`, which is never committed.
- Build locally: `cd source && TEKI_EMAIL=test@example.com python3 build.py`. The real email comes from a repo secret, never hard-code it.
- Products live in `source/products.json`. Images live in `source/assets/`.
- Blog posts are Markdown in `source/blog/<slug>.md` with a front-matter header (see the top of the blog section in build.py). Posts marked `draft: true` are never published. Preview drafts with `BLOG_DRAFTS=1`.
- Pages in sub-folders get their links rewritten by `relocate()`, so always write links relative to the site root (e.g. `retro-arsenal.html`, `assets/...`).

## Checks before any PR
- `python3 .github/seo-bot/seo_bot.py check --dist source/dist` must show 0 critical problems. The deploy is blocked otherwise.
- Titles 10-65 characters, meta descriptions 50-160, exactly one `<h1>`, alt text on every image.

## Workflow rules
- Work on a branch, open a PR with `gh api repos/tekisolves/tekisolves.github.io/pulls`. Khaya merges PRs himself.
- Pushing to `main` deploys automatically (GitHub Actions to GitHub Pages).
- Bots in `.github/`: `seo-bot` (daily SEO news, Monday digest, IndexNow), `content-coach` (blog reminder emails, plan in `.github/content-coach/plan.json`). Both email via the `TEKI_EMAIL` and `GMAIL_APP_PASSWORD` secrets. `.github/social` is the social engine (briefs in `content/social/`, queued to Buffer after merge). No paid services. AI (Gemini free tier) may draft, but every post passes the brand checks and Khaya's approval before it publishes.
- `SEO-CHANGELOG.md` is appended automatically on each deploy.

## Content rules (to stay on the right side of Google)
- One genuinely useful post at a time. Real, tested code. No mass-produced or auto-published AI posts.
- Every post names Khaya as author and has an honest "How this post was made" note.
- Only claim what Khaya has actually done or tested.
- Link to Retro Arsenal at the end of posts, and say plainly that he made it.
