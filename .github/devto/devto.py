"""Cross-post blog posts to DEV (dev.to) and publish them on schedule.

A post opts in with front matter:
    devto: 2026-11-24T14:00:00Z      # when it should go live on DEV (UTC)
    devto_tags: phaser, gamedev, javascript, tutorial   # up to 4

Each run (on deploy and hourly):
  - no DEV copy yet      -> create it as a draft (canonical_url = the post on our site)
  - draft and time is up -> publish it
  - already published    -> leave it alone (edits are made on DEV by hand)
Drafts posts (draft: true) are never sent. Needs the DEVTO_API_KEY secret.
"""
import datetime, json, os, re, sys, urllib.request, urllib.error

SITE = "https://tekisolves.github.io"
API = "https://dev.to/api"
BLOG = os.path.join(os.path.dirname(__file__), "..", "..", "source", "blog")
KEY = os.environ.get("DEVTO_API_KEY", "")
DRY = os.environ.get("DRY_RUN") == "1"


def call(method, path, body=None):
    req = urllib.request.Request(API + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"api-key": KEY, "accept": "application/vnd.forem.api-v1+json",
                 "content-type": "application/json", "user-agent": "tekisolves-devto/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        sys.exit(f"DEV API {method} {path} failed: {e.code} {e.read()[:300]!r}")


def read(path):
    raw = open(path, encoding="utf-8").read()
    m = re.match(r"---\s*\n(.*?)\n---\s*\n(.*)", raw, re.S)
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    meta["slug"] = os.path.splitext(os.path.basename(path))[0]
    return meta, m.group(2)


def absolute(body):
    """Site-root-relative links and images become full URLs, so they work on DEV."""
    def fix(m):
        url = m.group(2)
        if re.match(r"(https?:|mailto:|#|/)", url):
            return m.group(0)
        return f"{m.group(1)}({SITE}/{url})"
    return re.sub(r"(!?\[[^\]]*\])\(([^)\s]+)\)", fix, body)


def main():
    if not KEY:
        print("DEVTO_API_KEY not set; skipping."); return
    now = datetime.datetime.now(datetime.timezone.utc)
    mine = []
    page = 1
    while True:
        batch = call("GET", f"/articles/me/all?per_page=1000&page={page}") or []
        mine += batch
        if len(batch) < 1000: break
        page += 1
    by_canon = {a.get("canonical_url"): a for a in mine if a.get("canonical_url")}

    for f in sorted(os.listdir(BLOG)):
        if not f.endswith(".md"): continue
        meta, body = read(os.path.join(BLOG, f))
        if not meta.get("devto") or meta.get("draft", "").lower() in ("true", "yes", "1"):
            continue
        canon = f"{SITE}/blog/{meta['slug']}/"
        when = datetime.datetime.fromisoformat(meta["devto"].replace("Z", "+00:00"))
        existing = by_canon.get(canon)
        if not existing:
            made = meta.get("made")
            text = absolute(body).rstrip()
            if made:
                text += f"\n\n---\n\n*How this post was made: {made}*"
            article = {"title": meta["title"], "body_markdown": text, "published": False,
                       "canonical_url": canon, "description": meta.get("description", ""),
                       "tags": [t.strip() for t in meta.get("devto_tags", "").split(",") if t.strip()][:4]}
            if meta.get("image"):
                article["main_image"] = f"{SITE}/{meta['image']}"
            print(f"create draft: {meta['title']}  (goes live {when.isoformat()})")
            if not DRY:
                existing = call("POST", "/articles", {"article": article})
                print("  ->", existing.get("url"))
        if existing and not existing.get("published") and now >= when:
            print(f"publish: {meta['title']}")
            if not DRY:
                out = call("PUT", f"/articles/{existing['id']}", {"article": {"published": True}})
                print("  ->", out.get("url"))
        elif existing and not existing.get("published"):
            print(f"waiting: {meta['title']} goes live {when.isoformat()}")


if __name__ == "__main__":
    main()
