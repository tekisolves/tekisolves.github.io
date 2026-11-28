#!/usr/bin/env python3
"""Teki Solves social engine.

One YAML brief per post lives in content/social/. This script:
  render   draws each brief's card image into source/assets/social/<id>/card.jpg
  check    enforces the brand rules (fails the PR if a post breaks one)
  publish  queues approved posts in Buffer at their scheduled time
  doctor   checks the Buffer key and channels

Approval = Khaya merging the pull request. Nothing reaches Buffer before that.
Free: GitHub Actions + GitHub Pages + Buffer's free API. No AI APIs.
"""
import argparse, datetime as dt, glob, html, json, os, re, sys, urllib.request, urllib.error
from zoneinfo import ZoneInfo

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = json.load(open(os.path.join(HERE, "brand.json")))
LEDGER_PATH = os.path.join(HERE, "ledger.json")
BRIEFS = os.path.join(ROOT, "content", "social")
OUT = os.path.join(ROOT, "source", "assets", "social")
TZ = ZoneInfo(BRAND["timezone"])
SITE = BRAND["site"]
API = "https://api.buffer.com"
PLATFORMS = list(BRAND["channels"])


# ---------- loading ----------

def load_briefs():
    briefs = []
    for path in sorted(glob.glob(os.path.join(BRIEFS, "*.yml"))):
        b = yaml.safe_load(open(path)) or {}
        b["_file"] = os.path.relpath(path, ROOT)
        b["_stem"] = os.path.splitext(os.path.basename(path))[0]
        briefs.append(b)
    return briefs


def when(b, platform=None):
    """Post time as an aware datetime. A platform can override the brief's date."""
    raw = (b.get("posts", {}).get(platform) or {}).get("date") if platform else None
    raw = raw or b.get("date")
    d = raw if isinstance(raw, dt.datetime) else dt.datetime.fromisoformat(str(raw))
    return d if d.tzinfo else d.replace(tzinfo=TZ)


def public_url(ref):
    """Repo path under source/ -> live site URL. Full URLs pass through."""
    if re.match(r"https?://", ref):
        return ref
    rel = ref.split("source/", 1)[1] if ref.startswith("source/") else ref
    return f"{SITE}/{rel.lstrip('/')}"


def card_path(b):
    return os.path.join(OUT, b["id"], "card.jpg")


def images(b):
    """[(url, alt)] in order: rendered card first, then any listed media."""
    out = []
    if b.get("card"):
        out.append((public_url(os.path.relpath(card_path(b), ROOT)), b["card"].get("alt", "")))
    for m in b.get("media") or []:
        out.append((public_url(m["src"]), m.get("alt", "")))
    return out


def link_for(b, platform):
    if not b.get("link"):
        return ""
    sep = "&" if "?" in b["link"] else "?"
    return f"{b['link']}{sep}utm_source={platform}&utm_medium=social&utm_campaign={b['id']}"


def text_for(b, platform):
    return (b["posts"][platform].get("text") or "").strip().replace("{link}", link_for(b, platform))


# ---------- render ----------

CARD_CSS = """*{margin:0;box-sizing:border-box}
body{width:1080px;height:1350px;background:#101311;position:relative;overflow:hidden;font-family:'Space Grotesk',sans-serif;color:#F4F3ED}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(244,243,237,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(244,243,237,.05) 1px,transparent 1px);background-size:54px 54px}
.glow{position:absolute;inset:0;background:radial-gradient(circle at 50% 58%,rgba(178,221,49,.15),transparent 600px)}
.wrap{position:absolute;left:86px;right:86px;top:96px;bottom:210px;display:flex;flex-direction:column;justify-content:center;align-items:flex-start}
.pts{margin-top:40px;display:grid;gap:22px;width:100%}.pt{display:flex;gap:24px;align-items:baseline;font-size:36px;line-height:1.3;font-weight:500;color:#E4E6E0}.pt b{font:500 28px/1 'DM Mono',monospace;color:#B2DD31;min-width:48px}
.eb{font:500 26px/1 'DM Mono',monospace;letter-spacing:6px;color:#B2DD31;text-transform:uppercase}
h1{margin-top:30px;font-size:96px;font-weight:700;letter-spacing:-3px;line-height:1.02}
h1 span{color:#B2DD31}
.sub{margin-top:30px;font-size:38px;line-height:1.38;color:#C9CFC9;font-weight:500}
pre{margin-top:40px;background:#1A201C;border:1px solid rgba(244,243,237,.1);border-radius:20px;padding:32px 36px;font:500 30px/1.55 'DM Mono',monospace;color:#F4F3ED;white-space:pre-wrap}
.shot{margin-top:44px;width:100%;border-radius:22px;overflow:hidden;box-shadow:0 24px 60px rgba(0,0,0,.45)}.shot img{width:100%;display:block;max-height:560px;object-fit:contain;background:#F4F0E4}
.pill{display:inline-block;margin-top:44px;background:#B2DD31;color:#101311;font:700 30px/1 'Space Grotesk';padding:22px 32px;border-radius:999px}
.foot{position:absolute;left:86px;right:86px;bottom:76px;display:flex;align-items:center;justify-content:space-between;border-top:1px solid rgba(244,243,237,.15);padding-top:32px}
.brand{display:flex;align-items:center;gap:16px;font:700 34px/1 'Space Grotesk';letter-spacing:-1px}
.mark{width:58px;height:58px;border:2px solid rgba(244,243,237,.6);border-radius:8px;display:grid;place-items:center}.mark img{width:44px}
.url{font:500 24px/1 'DM Mono',monospace;letter-spacing:2px;color:#A9B1AA}"""


def card_html(c):
    e = lambda s: html.escape(str(s or ""))
    # *word* in the title is drawn in brand lime.
    title = re.sub(r"\*(.+?)\*", r"<span>\1</span>", e(c.get("title")))
    parts = [f"<div class='eb'>{e(c.get('eyebrow'))}</div>", f"<h1>{title}</h1>"]
    if c.get("sub"):
        parts.append(f"<p class='sub'>{e(c['sub'])}</p>")
    if c.get("points"):
        parts.append("<div class='pts'>" + "".join(
            f"<div class='pt'><b>{i:02d}</b><span>{e(t)}</span></div>" for i, t in enumerate(c["points"], 1)) + "</div>")
    if c.get("code"):
        parts.append(f"<pre>{e(c['code'])}</pre>")
    if c.get("image"):
        parts.append(f"<div class='shot'><img src='file://{os.path.join(ROOT, c['image'])}'></div>")
    if c.get("pill"):
        parts.append(f"<div class='pill'>{e(c['pill'])}</div>")
    logo = os.path.join(ROOT, "source", "assets", "logo-diamond.png")
    fonts = "<link href='https://fonts.googleapis.com/css2?family=DM+Mono:wght@500&family=Space+Grotesk:wght@500;700&display=block' rel='stylesheet'>"
    return (f"<!doctype html><html><head><meta charset='utf-8'>{fonts}<style>{CARD_CSS}</style></head><body>"
            f"<div class='glow'></div><div class='grid'></div><div class='wrap'>{''.join(parts)}</div>"
            f"<div class='foot'><div class='brand'><div class='mark'><img src='file://{logo}'></div>"
            f"TEKI <span style='color:#B2DD31'>/</span> SOLVES</div><div class='url'>tekisolves.github.io</div></div></body></html>")


def cmd_render(args):
    from playwright.sync_api import sync_playwright
    todo = [b for b in load_briefs() if b.get("card")]
    if not todo:
        print("Nothing to render."); return 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1350})
        for b in todo:
            out = card_path(b)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            tmp = out + ".html"
            open(tmp, "w").write(card_html(b["card"]))
            page.goto("file://" + tmp)
            try:
                page.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                pass  # offline: falls back to locally installed fonts
            page.wait_for_timeout(300)
            page.screenshot(path=out, type="jpeg", quality=92)
            os.remove(tmp)
            print("rendered", os.path.relpath(out, ROOT))
        browser.close()
    return 0


# ---------- check ----------

def hashtags(t):
    return re.findall(r"(?<!\w)#\w+", t)


def check_brief(b, ids, fb_links):
    err, warn = [], []
    need = lambda cond, msg: None if cond else err.append(msg)
    need(b.get("id") == b["_stem"], f"id must match the file name ({b['_stem']})")
    need(b.get("id") not in ids, "duplicate id")
    try:
        when(b)
    except Exception:
        err.append("date missing or not like 2026-12-01T18:00"); return err, warn
    posts = b.get("posts") or {}
    need(posts, "no posts: add at least one of " + ", ".join(PLATFORMS))
    need(b.get("honest"), "add an 'honest:' line saying what this post claims and why it is true")
    if b.get("card"):
        c = b["card"]
        need(c.get("title"), "card needs a title")
        need(len(re.sub(r"\*", "", c.get("title", ""))) <= BRAND["limits"]["card_title"], "card title too long")
        need(len(c.get("sub", "")) <= BRAND["limits"]["card_sub"], "card sub too long")
        need(c.get("alt"), "card needs alt text")
        if c.get("image"):
            need(os.path.exists(os.path.join(ROOT, c["image"])), f"card image missing: {c['image']}")
    for m in b.get("media") or []:
        need(m.get("alt"), f"media needs alt text: {m.get('src')}")
        if not re.match(r"https?://", m.get("src", "")):
            need(os.path.exists(os.path.join(ROOT, m.get("src", ""))), f"media file missing: {m.get('src')}")
    if b.get("video") and not re.match(r"https?://", b["video"]):
        need(os.path.exists(os.path.join(ROOT, b["video"])), f"video file missing: {b['video']}")

    for plat, p in posts.items():
        if plat not in PLATFORMS:
            err.append(f"unknown platform '{plat}'"); continue
        p = p or {}
        lim = BRAND["limits"][plat]
        text = text_for(b, plat)
        everything = " ".join([text, p.get("title", ""), json.dumps(b.get("card", {}), ensure_ascii=False)])
        for ch in BRAND["banned_characters"]:
            need(ch not in everything, f"{plat}: no em or en dashes")
        for phrase in BRAND["banned_phrases"]:
            need(phrase.lower() not in everything.lower(), f"{plat}: banned phrase '{phrase}'")
        need(len(text) <= lim["text"], f"{plat}: text is {len(text)} chars, limit {lim['text']}")
        need(len(hashtags(text)) <= lim["hashtags"], f"{plat}: max {lim['hashtags']} hashtags")
        if plat == "instagram":
            need(images(b) or b.get("video"), "instagram: needs an image or video")
            need("http" not in text, "instagram: links aren't clickable in captions, say 'link in bio'")
        if plat == "youtube":
            need(b.get("video"), "youtube: needs a video")
            need(p.get("title"), "youtube: needs a title")
            need(len(p.get("title", "")) <= lim["title"], "youtube: title too long")
        if plat == "facebook" and "http" in text:
            month = when(b, plat).strftime("%Y-%m")
            fb_links[month] = fb_links.get(month, 0) + 1
            if fb_links[month] > lim["links_per_month"]:
                err.append(f"facebook: over {lim['links_per_month']} link posts in {month} (Page link limit)")
        need(SITE not in (p.get("text") or ""), f"{plat}: write {{link}} instead of a raw site URL so clicks are tracked")
        need("{link}" not in (p.get("text") or "") or b.get("link"), f"{plat}: uses {{link}} but the brief has no link")
        if when(b, plat) < dt.datetime.now(TZ) and f"{b['id']}:{plat}" not in ledger():
            warn.append(f"{plat}: date has passed, it will be skipped")
    return err, warn


def cmd_check(args):
    ids, fb_links, failed, rows = set(), {}, 0, []
    briefs = sorted(load_briefs(), key=lambda b: str(b.get("date")))
    for b in briefs:
        err, warn = check_brief(b, ids, fb_links)
        ids.add(b.get("id"))
        failed += bool(err)
        state = "FAIL" if err else ("warn" if warn else "ok")
        print(f"[{state}] {b['_file']}")
        for m in err: print("   x", m)
        for m in warn: print("   !", m)
        rows.append((b, state, err + warn))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as f:
            f.write("## Social posts\n\n| When | Post | Platforms | Check |\n|---|---|---|---|\n")
            for b, state, notes in rows:
                d = when(b).strftime("%a %d %b %H:%M") if b.get("date") else "?"
                f.write(f"| {d} | {b.get('id')} | {', '.join(b.get('posts', {}))} | {state} {'; '.join(notes)} |\n")
    print(f"\n{len(briefs)} briefs, {failed} failing")
    return 1 if failed else 0


# ---------- publish ----------

def ledger():
    try:
        return json.load(open(LEDGER_PATH))
    except FileNotFoundError:
        return {}


def gql(query, variables):
    key = os.environ.get("BUFFER_API_KEY")
    if not key:
        sys.exit("BUFFER_API_KEY is not set (Settings > Secrets and variables > Actions).")
    req = urllib.request.Request(API, method="POST",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    try:
        res = json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        sys.exit(f"Buffer API {e.code}: {e.read().decode()[:500]}")
    if res.get("errors"):
        raise RuntimeError(json.dumps(res["errors"])[:800])
    return res["data"]


CREATE = """mutation($input: CreatePostInput!) {
  createPost(input: $input) {
    ... on PostActionSuccess { post { id dueAt } }
    ... on MutationError { message }
  }
}"""


def live(url):
    try:
        urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=30)
        return True
    except Exception:
        return False


def payload(b, plat):
    p = b["posts"][plat]
    assets = []
    if plat == "youtube":
        assets = [{"video": {"url": public_url(b["video"]), "metadata": {"title": p["title"]}}}]
    else:
        assets = [{"image": {"url": u, "metadata": {"altText": a}}} for u, a in images(b)]
        if not assets and b.get("video"):
            assets = [{"video": {"url": public_url(b["video"])}}]
    reel = bool(b.get("video")) and not images(b)
    if plat == "facebook":
        meta = {"facebook": {"type": "reel" if reel else "post"}}
    elif plat == "instagram":
        meta = {"instagram": {"type": "reel" if reel else "post", "shouldShareToFeed": True}}
    else:
        meta = {"youtube": {"type": "short", "title": p["title"],
                            "categoryId": str(p.get("category", BRAND["youtube_category"])),
                            "privacy": "public", "madeForKids": False}}
    return {"channelId": BRAND["channels"][plat], "text": text_for(b, plat),
            "schedulingType": "automatic", "mode": "customScheduled", "needsApproval": False,
            "dueAt": when(b, plat).isoformat(), "assets": assets, "metadata": meta}


def cmd_publish(args):
    book, now, changed, failed = ledger(), dt.datetime.now(TZ), False, 0
    horizon = now + dt.timedelta(days=BRAND["queue_days"])
    for b in sorted(load_briefs(), key=lambda b: str(b.get("date"))):
        err, _ = check_brief(b, set(), {})
        if err:
            print(f"skip {b['id']}: fails checks"); failed += 1; continue
        for plat in b["posts"]:
            key = f"{b['id']}:{plat}"
            due = when(b, plat)
            if key in book or due > horizon:
                continue
            if due < now + dt.timedelta(minutes=10):
                print(f"skip {key}: due time has passed"); continue
            data = payload(b, plat)
            urls = [list(a.values())[0]["url"] for a in data["assets"]]
            if not all(live(u) for u in urls) and not args.dry_run:
                print(f"wait {key}: media not live yet, will retry"); continue
            if args.dry_run:
                print(f"DRY {key}\n{json.dumps(data, indent=2)}"); continue
            try:
                res = gql(CREATE, {"input": data})["createPost"]
            except RuntimeError as e:
                print(f"FAIL {key}: {e}"); failed += 1; continue
            if "post" not in res:
                print(f"FAIL {key}: {res.get('message')}"); failed += 1; continue
            book[key] = {"buffer_id": res["post"]["id"], "due": data["dueAt"], "queued": now.isoformat(timespec="seconds")}
            changed = True
            print(f"queued {key} for {data['dueAt']}")
    if changed:
        json.dump(book, open(LEDGER_PATH, "w"), indent=2, sort_keys=True)
    return 1 if failed else 0


def cmd_doctor(args):
    q = """query($i: ChannelsInput!) { channels(input: $i) { id service name isDisconnected } }"""
    org = os.environ.get("BUFFER_ORG_ID", "6b0ad2605965a4d22ddae09e")
    chans = gql(q, {"i": {"organizationId": org}})["channels"]
    ok = True
    for plat, cid in BRAND["channels"].items():
        c = next((c for c in chans if c["id"] == cid), None)
        good = bool(c) and not c["isDisconnected"]
        ok &= good
        print(f"{'ok ' if good else 'BAD'} {plat}: {c['name'] if c else 'not found'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("render"); sub.add_parser("check"); sub.add_parser("doctor")
    sp = sub.add_parser("publish"); sp.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    sys.exit({"render": cmd_render, "check": cmd_check, "publish": cmd_publish, "doctor": cmd_doctor}[a.cmd](a))


if __name__ == "__main__":
    main()
