#!/usr/bin/env python3
"""Teki Solves SEO bot. Standard library only: no AI, no paid APIs, no third-party scoring.

  check     --dist DIR              rule checks on the built site; exit 1 if a critical rule fails (blocks the deploy)
  indexnow  --dist DIR --site URL   tell Bing/Yandex/Seznam (IndexNow) which pages exist after a deploy
  run       --site URL [--digest]   read the news feeds, check the live site, email you if anything matters

Email goes from and to TEKI_EMAIL using GMAIL_APP_PASSWORD (both repo secrets).
Rules live in this file in plain Python, so you can read and change every one of them.
"""
import argparse, datetime as dt, email.utils, hashlib, html, json, os, re, smtplib, sys
import urllib.request, urllib.error, urllib.parse
import xml.etree.ElementTree as ET
from email.message import EmailMessage
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(HERE, "state.json")
FEEDS_FILE = os.path.join(HERE, "feeds.json")
UA = "TekiSolvesSEOBot/1.0 (+https://tekisolves.github.io)"
NOW = dt.datetime.now(dt.timezone.utc)

# ---------- urgent topics (official sources only) ----------
URGENT = re.compile(r"core update|spam update|helpful content|ranking (update|issue|incident)|algorithm|"
                    r"indexing (issue|incident|problem)|crawling (issue|incident)|deprecat|"
                    r"structured data|product (snippet|rich result|markup)|core web vitals|\bINP\b|"
                    r"page experience|merchant listing", re.I)
STOP = set("""a an and are as at be by for from has have how in into is it its new of on or our that the this to
up was we what when where which who why will with you your can now more about after than not do does get
google googles seo search 2025 2026 guide tips best way ways using use new vs""".split())

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()

# ---------- site rules ----------
class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self.in_title, self.meta, self.links = "", False, {}, []
        self.h1, self.imgs_no_alt, self.canonical, self.jsonld, self._ld = 0, 0, "", [], None
        self.lang = ""
    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == "html": self.lang = a.get("lang", "")
        if tag == "title": self.in_title = True
        if tag == "meta":
            k = a.get("name") or a.get("property")
            if k: self.meta[k.lower()] = a.get("content", "")
        if tag == "link" and a.get("rel") == "canonical": self.canonical = a.get("href", "")
        if tag == "a" and a.get("href"): self.links.append(a["href"])
        if tag == "h1": self.h1 += 1
        if tag == "img" and "alt" not in a: self.imgs_no_alt += 1
        if tag == "script" and a.get("type") == "application/ld+json": self._ld = ""
    def handle_endtag(self, tag):
        if tag == "title": self.in_title = False
        if tag == "script" and self._ld is not None: self.jsonld.append(self._ld); self._ld = None
    def handle_data(self, d):
        if self.in_title: self.title += d
        if self._ld is not None: self._ld += d

def check_page(name, text, files=None):
    """Returns (critical, warnings). Critical problems can hurt rankings or block indexing."""
    p = Page(); p.feed(text)
    crit, warn = [], []
    t, d = p.title.strip(), p.meta.get("description", "").strip()
    public = name != "404.html"
    if not t: crit.append("no <title>")
    elif not 10 <= len(t) <= 65: warn.append(f"title is {len(t)} characters (aim for 10-65)")
    if not d: crit.append("no meta description")
    elif not 50 <= len(d) <= 160: warn.append(f"meta description is {len(d)} characters (aim for 50-160)")
    if public and "noindex" in p.meta.get("robots", ""): crit.append("page is set to noindex")
    if p.h1 != 1: crit.append(f"{p.h1} <h1> tags (should be exactly 1)")
    if not p.lang: warn.append("no lang attribute on <html>")
    if "viewport" not in p.meta: crit.append("no mobile viewport tag")
    if public and not p.canonical: warn.append("no canonical link")
    if p.imgs_no_alt: crit.append(f"{p.imgs_no_alt} image(s) without alt text")
    for raw in p.jsonld:
        try: json.loads(raw)
        except Exception: crit.append("structured data (JSON-LD) is not valid JSON")
    if files is not None:
        for href in p.links:
            u = urllib.parse.urlparse(href)
            if u.scheme or href.startswith(("#", "mailto:", "tel:")): continue
            target = u.path.lstrip("/") or "index.html"
            if target not in files: crit.append(f"broken internal link: {href}")
    return crit, warn

def cmd_check(args):
    files = set()
    for root, _, fs in os.walk(args.dist):
        for f in fs: files.add(os.path.relpath(os.path.join(root, f), args.dist).replace(os.sep, "/"))
    pages = sorted(f for f in files if f.endswith(".html"))
    total_crit = 0
    for name in pages:
        crit, warn = check_page(name, open(os.path.join(args.dist, name), encoding="utf-8").read(), files)
        for c in crit: print(f"CRITICAL  {name}: {c}")
        for w in warn: print(f"warning   {name}: {w}")
        total_crit += len(crit)
    sm = os.path.join(args.dist, "sitemap.xml")
    if os.path.exists(sm):
        listed = {x or "index.html" for x in re.findall(r"<loc>[^<]*/([^/<]*)</loc>", open(sm).read())}
        missing = [n for n in pages if n != "404.html" and n not in listed]
        if missing: print("warning   sitemap.xml is missing: " + ", ".join(missing))
    print(f"{len(pages)} pages checked, {total_crit} critical problem(s).")
    sys.exit(1 if total_crit else 0)

# ---------- IndexNow ----------
def cmd_indexnow(args):
    keys = [f[:-4] for f in os.listdir(args.dist) if re.fullmatch(r"[0-9a-f]{32}\.txt", f)]
    if not keys: print("No IndexNow key file in the build; skipping."); return
    urls = [f"{args.site}/{f}" for f in sorted(os.listdir(args.dist)) if f.endswith(".html") and f != "404.html"]
    body = json.dumps({"host": urllib.parse.urlparse(args.site).netloc, "key": keys[0],
                       "keyLocation": f"{args.site}/{keys[0]}.txt", "urlList": urls}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=25) as r: print(f"IndexNow: HTTP {r.status} for {len(urls)} URLs")
    except urllib.error.HTTPError as e: print(f"IndexNow: HTTP {e.code} (not fatal)")
    except Exception as e: print(f"IndexNow: {e} (not fatal)")

# ---------- feeds ----------
def parse_date(s):
    if not s: return None
    s = s.strip()
    try:
        d = email.utils.parsedate_to_datetime(s)
    except Exception:
        try: d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception: return None
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)

def parse_feed(data):
    root = ET.fromstring(data)
    items = []
    for el in root.iter():
        tag = el.tag.split("}")[-1]
        if tag not in ("item", "entry"): continue
        f = {c.tag.split("}")[-1]: c for c in el}
        title = (f["title"].text or "").strip() if "title" in f else ""
        link = ""
        if "link" in f: link = (f["link"].text or f["link"].get("href") or "").strip()
        date = None
        for k in ("pubDate", "published", "updated", "date"):
            if k in f: date = parse_date(f[k].text); break
        if title: items.append({"title": html.unescape(title), "link": link, "date": date})
    return items

def keywords(title):
    words = [w for w in re.findall(r"[a-z0-9]+", title.lower()) if w not in STOP and len(w) > 2]
    return set(words) | {f"{a} {b}" for a, b in zip(words, words[1:])}

def agreed_topics(items, days=7):
    """Topics (word pairs) that at least 2 different sources mentioned in the last `days` days."""
    since = NOW - dt.timedelta(days=days)
    by_topic = {}
    for it in items:
        if it["date"] and it["date"] < since: continue
        for k in keywords(it["title"]):
            if " " in k: by_topic.setdefault(k, {}).setdefault(it["source"], it)
    out = [(k, v) for k, v in by_topic.items() if len(v) >= 2]
    return sorted(out, key=lambda kv: -len(kv[1]))[:8]

# ---------- email ----------
def send(subject, text):
    to, pw = os.environ.get("TEKI_EMAIL"), os.environ.get("GMAIL_APP_PASSWORD")
    if not (to and pw):
        print(f"[no email secrets set] would send: {subject}\n{text}"); return
    m = EmailMessage(); m["Subject"], m["From"], m["To"] = subject, to, to
    m.set_content(text)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as s:
        s.login(to, pw.replace(" ", "")); s.send_message(m)
    print(f"Emailed: {subject}")

# ---------- main run ----------
def cmd_run(args):
    cfg = json.load(open(FEEDS_FILE))
    state = json.load(open(STATE_FILE)) if os.path.exists(STATE_FILE) else {}
    first_run = not state.get("seen")
    seen = set(state.get("seen", []))

    items, broken, new_urgent, new_official = [], [], [], []
    for fd in cfg["feeds"]:
        try:
            data = None
            for u in [fd["url"]] + fd.get("fallbacks", []):   # try the feed's other official addresses
                try: _, data = fetch(u); break
                except Exception as e: err = e
            if data is None: raise err
            for it in parse_feed(data):
                it.update(source=fd["name"], tier=fd["tier"])
                it["id"] = hashlib.sha1((fd["url"] + it["title"] + it["link"]).encode()).hexdigest()[:16]
                items.append(it)
        except Exception as e:
            reason = f"HTTP {e.code}" if getattr(e, "code", None) else type(e).__name__
            hint = " (the site blocks automated readers; consider removing it)" if getattr(e, "code", None) in (401, 403) else ""
            broken.append(f'{fd["name"]} ({fd["url"]}): {reason}{hint}')
    for it in items:
        if it["id"] in seen: continue
        seen.add(it["id"])
        if it["tier"] == 1 and not first_run:
            new_official.append(it)
            if URGENT.search(it["title"]): new_urgent.append(it)

    # Watch pages: compare the list of headings (each update entry), not the whole page,
    # because the page's markup changes slightly on every load.
    known = state.get("doc_headings", {})
    doc_news = state.get("doc_news", [])     # new entries waiting for the Monday digest
    changed_docs = []                        # new entries that look ranking-related (urgent)
    for wp in cfg.get("watch_pages", []):
        try:
            _, data = fetch(wp["url"])
            heads = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", h))).strip()
                     for h in re.findall(r"<h[23][^>]*>(.*?)</h[23]>", data.decode("utf-8", "ignore"), re.S)]
            heads = [h for h in heads if h]
            if wp["url"] in known:
                for h in heads:
                    if h not in known[wp["url"]]:
                        entry = f'{h} ({wp["name"]}: {wp["url"]})'
                        (changed_docs if URGENT.search(h) else doc_news).append(entry)
            known[wp["url"]] = heads[:300]
        except Exception as e:
            broken.append(f'{wp["name"]} ({wp["url"]}): {type(e).__name__}')

    site_crit, site_warn = [], []
    for path in ["", "retro-arsenal.html", "products.html", "sitemap.xml", "robots.txt"]:
        url = f"{args.site}/{path}"
        try:
            status, data = fetch(url)
            if path.endswith(".xml") or path.endswith(".txt"): continue
            c, w = check_page(path or "index.html", data.decode("utf-8", "ignore"))
            site_crit += [f"{path or 'home'}: {x}" for x in c]; site_warn += [f"{path or 'home'}: {x}" for x in w]
        except urllib.error.HTTPError as e: site_crit.append(f"{url} returned HTTP {e.code}")
        except Exception as e: site_crit.append(f"{url} could not be reached ({type(e).__name__})")
    try:
        _, data = fetch(f"{args.site}/retro-arsenal.html")
        for href in set(re.findall(r'href="(https?://[^"]+)"', data.decode("utf-8", "ignore"))):
            if "fonts.g" in href: continue
            try: fetch(href)
            except urllib.error.HTTPError as e:
                if e.code not in (403, 405, 429): site_crit.append(f"external link broken ({e.code}): {href}")
            except Exception: site_warn.append(f"external link unreachable: {href}")
    except Exception: pass

    is_monday = NOW.weekday() == 0
    send_digest = args.digest or first_run or (is_monday and state.get("last_digest") != NOW.date().isoformat())

    # urgent email: only for new official ranking news or a broken live site, and only once per problem
    problem_key = hashlib.sha1("|".join(sorted(site_crit)).encode()).hexdigest()[:12] if site_crit else ""
    site_alert = bool(site_crit) and problem_key != state.get("last_site_problem")
    if (new_urgent or changed_docs or site_alert) and not first_run:
        lines = []
        if site_alert:
            lines += ["YOUR SITE NEEDS A LOOK", *[f"- {x}" for x in site_crit], ""]
        if new_urgent:
            lines += ["OFFICIAL SEARCH NEWS THAT CAN AFFECT RANKINGS", *[f'- {i["title"]} ({i["source"]})\n  {i["link"]}' for i in new_urgent], ""]
        if changed_docs:
            lines += ["NEW GOOGLE SEARCH DOCUMENTATION UPDATE ABOUT RANKINGS", *[f"- {d}" for d in changed_docs], ""]
        lines.append("Nothing has been changed on the site. Read, then decide.")
        send("🔴 Teki SEO: " + ("site problem" if site_alert else "official search update"), "\n".join(lines))
    state["last_site_problem"] = problem_key

    if send_digest:
        topics = agreed_topics(items)
        week = [i for i in items if i["date"] and i["date"] >= NOW - dt.timedelta(days=7)]
        lines = ["TEKI SOLVES WEEKLY SEO DIGEST", ""]
        if first_run: lines += ["The SEO bot is live. From now on you only hear from it on Mondays, or when something urgent happens.", ""]
        lines += ["YOUR SITE",
                  "- All rule checks pass." if not site_crit else f"- {len(site_crit)} critical problem(s):",
                  *[f"  - {x}" for x in site_crit], *[f"  - (minor) {x}" for x in site_warn[:6]],
                  "- Every deploy refreshes the sitemap, blocks pages that break a critical rule, and pings IndexNow.", ""]
        lines += ["WHAT 2+ SOURCES AGREE ON THIS WEEK"]
        lines += [f'- "{k}" ({len(v)} sources): ' + "; ".join(f'{x["title"]} ({s})' for s, x in list(v.items())[:2]) for k, v in topics] or ["- Nothing that more than one source covered."]
        lines += ["", "OFFICIAL (tier 1), LAST 7 DAYS"]
        lines += [f'- {i["title"]} ({i["source"]})\n  {i["link"]}' for i in week if i["tier"] == 1][:10] or ["- No new official posts."]
        if doc_news:
            lines += ["", "GOOGLE SEARCH DOCUMENTATION CHANGES", *[f"- {d}" for d in doc_news[:10]]]
            doc_news = []
        lines += ["", f"Read {len(items)} items from {len(cfg['feeds']) - len(broken)} feeds; {len(week)} were from this week."]
        if broken: lines += ["", "FEEDS THAT FAILED (swap the URL in .github/seo-bot/feeds.json)", *[f"- {b}" for b in broken]]
        send("📬 Teki SEO weekly digest", "\n".join(lines))
        state["last_digest"] = NOW.date().isoformat()

    state["seen"] = sorted(seen)[-3000:]
    state.pop("pages", None)   # old whole-page hashes (replaced by doc_headings)
    state["doc_headings"] = known
    state["doc_news"] = doc_news[-50:]
    state["last_run"] = NOW.isoformat(timespec="minutes")
    json.dump(state, open(STATE_FILE, "w"), indent=1)
    print(f"items={len(items)} broken_feeds={len(broken)} urgent={len(new_urgent)} site_critical={len(site_crit)} digest={send_digest}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("check"); a.add_argument("--dist", required=True)
    b = sub.add_parser("indexnow"); b.add_argument("--dist", required=True); b.add_argument("--site", required=True)
    c = sub.add_parser("run"); c.add_argument("--site", required=True); c.add_argument("--digest", action="store_true")
    args = ap.parse_args()
    {"check": cmd_check, "indexnow": cmd_indexnow, "run": cmd_run}[args.cmd](args)
