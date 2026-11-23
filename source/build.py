#!/usr/bin/env python3
"""Teki Solves static site builder.
Run:  python3 build.py        -> writes the finished site to ./dist
Edit products in products.json, copy in the page functions below, set SITE_URL once the domain is final.
"""
import json, os, re, shutil, html

SITE_URL = "https://tekisolves.github.io"   # change if you move to a custom domain
EMAIL = os.environ.get("TEKI_EMAIL", "")   # set before building:  TEKI_EMAIL=you@example.com python3 build.py
if not EMAIL:
    raise SystemExit("Set TEKI_EMAIL first, e.g.  TEKI_EMAIL=you@example.com python3 build.py")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "dist")
LEGACY = os.environ.get("LEGACY_DIR", os.path.join(HERE, "..", "Teki-Solves-Landing-Page-main"))
products = json.load(open(os.path.join(HERE, "products.json")))
esc = html.escape
import hashlib
def asset_ver(name):
    """Short content hash so browsers fetch the new file after every change (no stale CSS)."""
    return hashlib.sha1(open(os.path.join(HERE, name), "rb").read()).hexdigest()[:8]
CSS_V, JS_V = asset_ver("style.css"), asset_ver("script.js")

def has(path):
    return os.path.exists(os.path.join(HERE, path))

# ---------- original artwork (vector, original to Teki Solves) ----------
def arch_svg(p, cls="breathe"):
    leaves = [(28,284,-120,"#5E9E45"),(30,258,-30,"#8CBF2A"),(30,228,-150,"#5E9E45"),(26,198,-20,"#8CBF2A"),
              (26,170,-160,"#5E9E45"),(32,140,-30,"#8CBF2A"),(42,108,-140,"#5E9E45"),(56,80,-50,"#8CBF2A"),
              (80,52,-150,"#5E9E45"),(106,32,-40,"#8CBF2A")]
    lv = "".join(f'<use href="#{p}lf" fill="{c}" transform="translate({x} {y}) rotate({r}) scale(1.2)"/>' for x,y,r,c in leaves)
    return f'''<svg class="{cls}" viewBox="0 0 280 320" aria-hidden="true" focusable="false">
<defs>
<pattern id="{p}d" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="1" fill="#1F3D2F" fill-opacity=".35"/><circle cx="4.5" cy="4.5" r="1" fill="#1F3D2F" fill-opacity=".35"/></pattern>
<path id="{p}lf" d="M0 0 C3 -7 12 -8 17 -3 C13 3 5 5 0 0Z"/>
<clipPath id="{p}c"><path d="M40 296 V120 A100 100 0 0 1 240 120 V296 Z"/></clipPath>
</defs>
<path d="M30 306 V120 A110 110 0 0 1 250 120 V306" fill="none" stroke="#F4F3ED" stroke-opacity=".3"/>
<path d="M40 296 V120 A100 100 0 0 1 240 120 V296 Z" fill="#FBEBBF"/>
<g clip-path="url(#{p}c)">
<circle class="sun-ring" cx="140" cy="130" r="64" fill="none" stroke="#F2B63D" stroke-opacity=".6"/>
<circle class="sun-ring" cx="140" cy="130" r="49" fill="none" stroke="#F2B63D" stroke-opacity=".85"/>
<circle cx="140" cy="130" r="34" fill="#F2B63D"/>
<rect x="180" y="80" width="11" height="11" fill="#F6F1E3" stroke="#1F3D2F" transform="rotate(45 185.5 85.5)"/>
<path d="M40 220 Q92 178 146 205 T240 186 V296 H40Z" fill="#BBD5A4"/>
<path d="M40 250 Q110 212 180 240 T240 232 V296 H40Z" fill="#7FAE74"/>
<path d="M40 250 Q110 212 180 240 T240 232 V296 H40Z" fill="url(#{p}d)"/>
<g stroke="#1F3D2F" stroke-width="2.4" stroke-linecap="round"><line x1="78" y1="240" x2="78" y2="216"/><line x1="140" y1="236" x2="140" y2="206"/><line x1="208" y1="238" x2="208" y2="226"/></g>
<g fill="#2F5E63" stroke="#1F3D2F" stroke-width=".9" stroke-linejoin="round"><polygon points="60,217 96,206 98,215 62,226"/><polygon points="118,206 162,192 165,202 121,215"/><polygon points="192,225 226,214 228,222 194,233"/></g>
<g stroke="#B2DD31" stroke-width="1.1"><line x1="62" y1="221.5" x2="97" y2="210.5"/><line x1="120" y1="210.5" x2="163.5" y2="197"/><line x1="194" y1="229" x2="227" y2="218"/></g>
<path d="M40 290 Q130 262 240 278 V296 H40Z" fill="#2F5B3E"/>
<g fill="#4C8A3A"><circle cx="70" cy="288" r="8"/><circle cx="86" cy="291" r="6"/><circle cx="212" cy="284" r="9"/><circle cx="230" cy="288" r="6"/></g>
</g>
<path d="M40 296 V120 A100 100 0 0 1 240 120 V296 Z" fill="none" stroke="#F4F3ED" stroke-opacity=".85" stroke-width="1.6"/>
<path d="M30 308 C20 262 36 236 26 190 C18 152 30 122 44 96 C60 62 84 38 118 24" fill="none" stroke="#5E9E45" stroke-width="1.6" stroke-linecap="round"/>
{lv}
</svg>'''

def diamond_line():
    return '<svg class="diamond-line" viewBox="0 0 140 20" aria-hidden="true" focusable="false"><path d="M0 10H52L60 10 70 1 80 10 70 19 60 10M80 10H140"/></svg>'


def signature_loader(cls, sub="", extra=""):
    """Teki Solves signature loader: the gold logo diamond turning, the name beneath, a thin gold progress line."""
    layers = "".join(f'<i style="--z:{z}"></i>' for z in range(6))
    sub_html = f'<span class="tk-sub">{sub}</span>' if sub else ""
    return (f'<div class="tk-loader {cls}" aria-hidden="{"true" if cls == "tk-splash" else "false"}"><div class="tk-dia"><div class="tk-dia-body">{layers}</div></div>'
            f'<span class="tk-name">TEKI SOLVES</span>{sub_html}<span class="tk-bar"><i></i></span>{extra}</div>')

# ---------- shared shell ----------
def page_url(path):
    return f'{SITE_URL}/{path[:-len("index.html")] if path.endswith("index.html") else path}'

def canon(path):
    return f'<link rel="canonical" href="{page_url(path)}">' if SITE_URL else ""

DEFAULT_OG_IMAGE = "assets/og-retro-arsenal.png"   # share image for pages that don't set their own
ITCH_PROFILE = "https://tekisolves.itch.io"

def shell(path, title, desc, body, current="", robots="index, follow", og_image=DEFAULT_OG_IMAGE, head_extra="", og_type="website"):
    og = f'<meta property="og:url" content="{page_url(path)}">' if SITE_URL else ""
    if og_image and SITE_URL:
        og += f'<meta property="og:image" content="{SITE_URL}/{og_image}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image">'
    nav = [("products.html","Products"),("blog/","Blog"),("about.html","About"),("contact.html","Contact")]
    cur = ' aria-current="page"'
    desk = "".join(f'<a href="{h}"{cur if h==current else ""}>{t}</a>' for h,t in nav)
    mob = "".join(f'<a href="{h}">{t}</a>' for h,t in nav)
    org_data = {"@context":"https://schema.org","@type":"Organization","name":"Teki Solves",
        "description":"An independent digital product shop and creative workshop making practical digital products that solve real problems.",
        "sameAs":[ITCH_PROFILE]}
    if SITE_URL:
        org_data.update(url=SITE_URL + "/", logo=f"{SITE_URL}/assets/logo-diamond.png")
    org = json.dumps(org_data)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<script>try{{if(!sessionStorage.getItem('tk-splash')&&!matchMedia('(prefers-reduced-motion: reduce)').matches){{document.documentElement.classList.add('splash');sessionStorage.setItem('tk-splash','1')}}}}catch(e){{}}</script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#101311">
{"" if "noindex" in robots else canon(path)}
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="Teki Solves">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">{og}
<link rel="icon" type="image/png" href="assets/favicon.png"><link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css?v={CSS_V}">
<link rel="alternate" type="application/rss+xml" title="Teki Solves blog" href="blog/feed.xml">
<script>document.documentElement.classList.add('js');window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('consent','default',{{analytics_storage:'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'}});</script>
<script type="application/ld+json">{org}</script>
{head_extra}
</head>
<body>
{signature_loader("tk-splash", "KEEP IT SIMPLE, PROBLEM SOLVED.")}
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="index.html" aria-label="Teki Solves home"><span class="brand-mark"><img src="assets/logo-diamond.png" alt="Teki Solves logo" width="26" height="26"></span><span class="brand-text">TEKI / SOLVES</span></a>
    <nav class="nav" aria-label="Main">{desk}<a class="btn btn-primary btn-sm" href="products.html">Explore products</a></nav>
    <button class="menu-btn" id="menuButton" aria-expanded="false" aria-controls="mobileNav" aria-label="Open navigation"><span></span><span></span></button>
  </div>
  <nav class="mobile-nav" id="mobileNav" aria-label="Mobile" hidden>{mob}<a class="btn btn-primary" href="products.html">Explore products</a></nav>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap footer-inner">
    <div><a class="brand" href="index.html" aria-label="Teki Solves home"><span class="brand-mark"><img src="assets/logo-diamond.png" alt="Teki Solves logo" width="26" height="26"></span><span class="brand-text">TEKI / SOLVES</span></a>
    <p class="mono gold-metal" style="margin-top:1rem;font-size:.72rem;letter-spacing:.14em">KEEP IT SIMPLE, PROBLEM SOLVED.</p></div>
    <div class="footer-links"><a href="products.html">Products</a><a href="blog/">Blog</a><a href="about.html">About</a><a href="contact.html">Contact</a><a href="privacy-policy.html">Privacy Policy</a><a href="cookie-policy.html">Cookie Policy</a><a href="{ITCH_PROFILE}" target="_blank" rel="noopener">Teki Solves on itch.io</a><button class="footer-link cookie-settings-trigger" type="button">Cookie Settings</button></div>
    <div class="footer-meta"><a href="mailto:{EMAIL}" style="text-decoration:none">{EMAIL}</a><span>© 2026 Teki Solves</span></div>
  </div>
</footer>
<section class="cookie-banner" id="cookieBanner" aria-label="Cookie consent" hidden>
  <div class="cookie-banner-inner">
    <div><span class="eyebrow">Cookies</span><h2>Optional analytics</h2>
    <p>We would like to use Google Analytics to understand how the site is used. It only loads if you accept. <a href="cookie-policy.html">Cookie Policy</a></p></div>
    <div class="cookie-actions"><button class="btn btn-primary btn-sm" id="cookieAccept" type="button">Accept analytics</button><button class="btn btn-outline btn-sm" id="cookieReject" type="button">Reject</button><button class="btn btn-outline btn-sm" id="cookieManage" type="button">Manage</button></div>
  </div>
</section>
<div class="cookie-settings" id="cookieSettingsPanel" role="dialog" aria-modal="true" aria-labelledby="cookieSettingsTitle" hidden>
  <div class="cookie-settings-card">
    <button class="modal-close" id="cookieSettingsClose" type="button" aria-label="Close cookie settings">×</button>
    <span class="eyebrow">Cookie Settings</span><h2 id="cookieSettingsTitle">Your choice</h2>
    <p>Optional analytics helps us understand how the site is used. You can change or withdraw your choice at any time.</p>
    <div class="cookie-choice"><div><strong>Google Analytics</strong><small>Optional audience measurement</small></div><strong id="analyticsStatus">Off</strong></div>
    <div class="cookie-actions"><button class="btn btn-primary btn-sm" id="cookieSettingsAccept" type="button">Allow analytics</button><button class="btn btn-outline btn-sm" id="cookieSettingsReject" type="button">Reject analytics</button></div>
  </div>
</div>
<div class="reticle" id="reticle" aria-hidden="true"><i></i></div>
<div class="toast" id="achv" role="status" aria-live="polite" hidden><span class="toast-ico" aria-hidden="true">◆</span><div><b>Achievement unlocked: Explorer</b><span>You've seen the whole base. The free sprite sample is on the <a href="blog/">blog</a>.</span></div></div>
<script src="script.js?v={JS_V}" defer></script>
</body>
</html>
'''

# ---------- components ----------
def website_schema():
    if not SITE_URL:
        return ""
    data = {"@context": "https://schema.org", "@type": "WebSite", "name": "Teki Solves", "url": SITE_URL + "/"}
    return f'<script type="application/ld+json">{json.dumps(data)}</script>'

def product_visual(p, cls="product-visual"):
    img = p.get("cardImage") or (p["previewImages"][0] if p.get("previewImages") else "")
    inner = f'<img src="{img}" alt="{esc(p["name"])}: Laser Pistol, prototype tier" width="800" height="600" loading="lazy">' if img and has(img) else arch_svg("pc"+p["id"][:3], cls="")
    return f'<div class="{cls} on-paper">{inner}</div>'

def product_animation(p, cls="focus-visual", eager=False):
    """Tier-swap GIF; shows a still poster to people who prefer reduced motion."""
    a, poster = p.get("animation"), p.get("animationPoster")
    if not (a and has(a)):
        return product_visual(p, cls)
    load = "eager" if eager else "lazy"
    alt = f'{esc(p["name"])}: all five weapons switching between the Scrap, Military and Prototype tiers'
    src = f'<source srcset="{poster}" media="(prefers-reduced-motion: reduce)">' if poster and has(poster) else ""
    return f'<div class="{cls} on-dark"><picture>{src}<img src="{a}" alt="{alt}" width="576" height="918" loading="{load}"></picture></div>'

def product_card(p):
    meta = " • ".join(p["formats"][:3] + [p["store"]]) if p.get("formats") else p["store"]
    return f'''<article class="product-card reveal">
  {product_visual(p)}
  <div class="product-body">
    <span class="eyebrow">{esc(p["category"])}</span>
    <h3><a href="{p["slug"]}">{esc(p["name"])}</a></h3>
    <p>{esc(p["shortDescription"])}</p>
    <div class="product-meta">{esc(meta)}</div>
    <span class="card-cta" aria-hidden="true">See the details →</span>
  </div>
</article>'''

def live_products():
    return [p for p in products if p["status"] == "available"]


# ---------- 3D (pure CSS transforms, no libraries; paused off-screen and for reduced motion) ----------
def diamond3d():
    """The Teki logo as a solid metallic-gold 3D diamond (stacked layers give it thickness), plus small companions."""
    layers = "".join(f'<i style="--z:{z}"></i>' for z in range(12))
    minis = "".join(f'<span class="ldia-mini m{i}"><span class="ldia-mini-in"></span></span>' for i in range(1, 4))
    return f'<div class="ldia-wrap" aria-hidden="true"><div class="ldia"><div class="ldia-body">{layers}</div></div>{minis}</div>'

CAROUSEL = [("pistol", "Laser Pistol"), ("rifle", "Laser Rifle"), ("shotgun", "Laser Shotgun"),
            ("blade", "Energy Blade"), ("grenade", "Plasma Grenade")]

def carousel3d(p):
    """The weapons as a hologram projected from a small emitter. Each weapon cycles Scrap > Military > Prototype.
    Drag to spin it (script.js)."""
    tiers = "".join(f'<b class="c3-tier t{n}">{t}</b>' for n, t in ((1, "SCRAP"), (2, "MILITARY"), (3, "PROTOTYPE")))
    items = "".join(
        f'<figure class="c3-item" style="--i:{i}"><span class="c3-stack">'
        + "".join(f'<img class="t{n}" src="assets/3d/{k}-t{n}.webp" alt="" width="400" height="400" loading="lazy" decoding="async">' for n in (1, 2, 3))
        + f'</span><figcaption>{n}<span class="c3-tiers">{tiers}</span></figcaption></figure>'
        for i, (k, n) in enumerate(CAROUSEL))
    label = f'See {esc(p["name"])}: five weapons, each cycling through its three tiers, shown as a turning hologram'
    return (f'<a class="c3 holo reveal d1" href="{p["slug"]}" aria-label="{label}" draggable="false">'
            f'<span class="holo-beam"></span><div class="c3-drag"><div class="c3-ring" style="--n:{len(CAROUSEL)}">{items}</div></div>'
            f'<span class="holo-scan"></span><span class="holo-emitter"><i></i></span>'
            f'<span class="holo-label">RETRO ARSENAL // 5 WEAPONS · 3 TIERS</span><span class="holo-hint">DRAG TO ROTATE</span></a>')

# ---------- pages ----------
def home():
    p = products[0]
    cards = "".join(product_card(x) for x in live_products())
    return shell("index.html", "Teki Solves — Digital products that solve real problems",
        "Teki Solves is a digital product shop and creative workshop making thoughtful things for people who build, learn and create. Keep it simple, problem solved.", f'''
<section class="hero">
  <div class="wrap hero-grid">
    <div class="hero-copy">
      <span class="eyebrow">Digital products • Creative tools • Practical solutions</span>
      <h1>Useful digital products, <span>starting with game assets.</span></h1>
      <p>Teki Solves is a digital product shop and creative workshop making useful things for people who build, learn and create.</p>
      <p>Right now that means game assets for indie developers, starting with {esc(p["name"])}. Every product starts with a simple question: what problem can we help solve?</p>
      <p class="tagline">Keep it simple, problem solved.</p>
      <div class="hero-actions"><a class="btn btn-primary" href="products.html#catalogue">Browse game assets</a></div>
    </div>
    <div class="hero-art tilt3d">{arch_svg("h")}{diamond3d()}<a class="chip" href="{p["slug"]}"><i></i>Now on itch.io: {esc(p["name"])}</a></div>
  </div>
</section>

<section class="band" aria-labelledby="principles-h">
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">How we think</span><h2 id="principles-h">Three habits behind everything we make.</h2></div>
    <div class="principles">
      <div class="principle reveal"><h3>Clear beats clever.</h3><p>If something can be easier to understand or use, that matters.</p></div>
      <div class="principle reveal d1"><h3>Useful beats impressive.</h3><p>The point isn’t to make something complicated. It’s to make something that helps.</p></div>
      <div class="principle reveal d2"><h3>Curiosity stays.</h3><p>We like to experiment, learn, make things and see what becomes possible.</p></div>
    </div>
    {diamond_line()}
  </div>
</section>

<section class="band band-cream" aria-labelledby="featured-h">
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">Featured</span><h2 id="featured-h">Explore the products</h2>
    <p>Useful digital creations for building, learning and making.</p>
    <p>Every product should have a clear purpose. Browse what’s available, see what’s included and decide what fits your project.</p></div>
    <div class="product-grid">{cards}</div>
    <p style="margin-top:2rem"><a class="btn btn-dark" href="products.html">See the full catalogue</a></p>
  </div>
</section>

<section class="band" aria-labelledby="make-h">
  <div class="wrap cols">
    <div class="reveal stack"><span class="eyebrow">What we make</span><h2 id="make-h">A workshop for useful ideas.</h2></div>
    <div class="prose reveal d1">
      <p style="color:var(--muted)">Teki Solves is a digital product shop and creative workshop. We make things across gaming, software, digital assets, education, digital art and wherever else a good idea can take us.</p>
      <p style="color:var(--muted)">Some products help you build. Some help you learn. Some save you time. Some simply make creating more enjoyable.</p>
      <p style="color:var(--muted)">What connects them is simple: they solve a problem, and they’re made with care.</p>
      <p class="pull">We believe useful things can also be creative. Technical things can have personality. And good work should feel like someone actually cared about making it.</p>
    </div>
  </div>
</section>

<section class="band band-cream" aria-labelledby="problem-h">
  <div class="wrap cols">
    <div class="reveal stack"><span class="eyebrow">Built around real problems</span><h2 id="problem-h">Start with the problem.</h2></div>
    <div class="prose reveal d1">
      <p>A product should have a reason to exist. We look for ways to make a task easier, help someone move forward or give a good idea room to grow.</p>
      <p>That might mean saving time, making a technical concept easier to understand, or giving a creator a useful starting point.</p>
      <p>The format changes. The question stays the same: does it help?</p>
      <p class="pull">Less friction. More making.</p>
    </div>
  </div>
</section>

<section class="band" aria-labelledby="focus-h">
  <div class="wrap focus-card">
    <div class="prose reveal stack">
      <span class="eyebrow" style="color:var(--lime)">Current focus / Game assets</span>
      <h2 id="focus-h">More time making your game.</h2>
      <p style="color:var(--muted)">Our current focus is game assets: practical building blocks for developers who would rather spend their time shaping the game than creating every asset from scratch.</p>
      <p style="color:var(--muted)">Meet {esc(p["name"])}: a stylized retro-futurist 2D weapon asset pack for indie game developers.</p>
      <p style="margin-top:1.4rem"><a class="btn btn-primary" href="{p["slug"]}">Explore {esc(p["name"])}</a></p>
    </div>
    {carousel3d(p)}
  </div>
</section>

<section class="guardian" aria-labelledby="guardian-h">
  <div class="guardian-art"><img src="assets/guardian.webp" srcset="assets/guardian-1200.webp 1200w, assets/guardian.webp 1920w" sizes="100vw" alt="The Teki Solves guardian, an armoured figure standing under a full moon" width="1920" height="1080" loading="lazy" decoding="async"><span class="guardian-scan" aria-hidden="true"></span></div>
  <div class="wrap guardian-copy reveal">
    <span class="eyebrow" style="color:var(--lime)">The Solver</span>
    <h2 id="guardian-h">Every problem has a way through.</h2>
    <p>That’s the whole job: find what’s in your way, build the fix and keep it simple. It’s the same mindset behind every product here.</p>
    <p class="tagline">Keep it simple, problem solved.</p>
  </div>
</section>

<section class="band band-cream" aria-labelledby="why-h">
  <div class="wrap cols">
    <div class="reveal stack"><span class="eyebrow">Why Teki Solves</span><h2 id="why-h">Made with purpose. Built with care.</h2></div>
    <div class="prose reveal d1">
      <p>We care about what a product does and how it’s made. The details matter: clear information, thoughtful design and a useful result.</p>
      <p>We’re here for people who like to make things, learn something new and find a better way to solve a problem.</p>
      <p class="pull">No unnecessary complexity. No pretending a simple thing needs to be complicated. Just useful work, made with care.</p>
    </div>
  </div>
</section>

<section class="band" aria-labelledby="feedback-h">
  <div class="wrap cols">
    <div class="reveal stack"><span class="eyebrow">Feedback</span><h2 id="feedback-h">Looking for something else?</h2></div>
    <div class="prose reveal d1">
      <p style="color:var(--muted)">Not seeing what you need? Tell us what you’re trying to make, what’s getting in the way or what kind of product would help.</p>
      <p class="pull">Your idea might help shape what we make next.</p>
      <p style="margin-top:.6rem"><a class="btn btn-outline" href="contact.html">Tell us what you need</a></p>
    </div>
  </div>
</section>

<section class="band band-cream" aria-labelledby="final-h">
  <div class="wrap">
    <div class="cta-card reveal">
      <h2 id="final-h">Got something to make?</h2>
      <p>Find a useful starting point, discover something new or tell us what problem you’re trying to solve.</p>
      <p class="tagline">Keep it simple, problem solved.</p>
      <div class="cta-actions"><a class="btn btn-primary" href="{p["storeUrl"]}" target="_blank" rel="noopener" data-store-link data-store="{p["store"]}" data-product-id="{p["id"]}" data-product-name="{esc(p["name"])}">Get {esc(p["name"])} on {p["store"]} <span aria-hidden="true">↗</span></a><a class="link-arrow" href="contact.html">Send us an idea</a></div>
    </div>
  </div>
</section>
''', current="", head_extra=website_schema())

def products_page():
    cards = "".join(product_card(x) for x in live_products())
    return shell("products.html", "Game assets and digital products — Teki Solves",
        "Browse game assets and digital products made to help you build, learn and create, starting with Retro Arsenal: 15 retro sci-fi weapon sprites.", f'''
<section class="page-hero">
  <div class="wrap">
    <span class="eyebrow">The Teki Solves catalogue</span>
    <h1 style="margin-top:1rem">Game assets and useful digital products.</h1>
    <p class="lede">Browse game assets and digital products made to help you build, learn and create. Every product has a purpose.</p>
    <p style="margin-top:1.6rem"><a class="btn btn-primary" href="#catalogue">Jump to the catalogue</a></p>
  </div>
</section>
<section class="band band-cream" id="catalogue" aria-labelledby="cat-game">
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">Category</span><h2 id="cat-game">Game assets</h2>
    <p>Ready-to-use visual building blocks for game projects. Check each product page for formats, contents, compatibility and licence details.</p></div>
    <div class="product-grid">{cards}</div>
  </div>
</section>
<section class="band">
  <div class="wrap"><div class="section-head reveal"><h2>Not quite what you had in mind?</h2>
  <p class="lede">Tell us what you’re trying to do. We’re curious about the problems people need solved.</p>
  <p><a class="btn btn-outline" href="contact.html">Get in touch</a></p></div></div>
</section>
''', current="products.html")

def product_page(p):
    ok = [x for x in p.get("previewImages", []) if has(x)]
    if ok:
        labels = ["All 15 sprites on a dark background", "All 15 sprites on a light background"]
        figs = "".join(f'<figure class="preview-slot preview-tall{" light" if i==1 else ""}" style="margin:0"><img src="{x}" alt="{esc(p["name"])}: all 15 sprites, 5 weapons by 3 tiers, {"dark" if i==0 else "light"} background" width="1008" height="1094" loading="lazy"><figcaption>{labels[i] if i<2 else ""}</figcaption></figure>' for i,x in enumerate(ok))
        previews = f'<div class="preview-grid">{figs}</div><p class="note">Rows top to bottom: Laser Pistol, Laser Rifle, Laser Shotgun, Energy Blade, Plasma Grenade. Columns: Scrap, Military, Prototype.</p>'
    else:
        previews = f'<p style="margin-top:1rem">Full previews are on the <a href="{p["storeUrl"]}" target="_blank" rel="noopener">{p["store"]} page</a>.</p>'
    inc = "".join(f"<li>{esc(i)}</li>" for i in p["includedItems"])
    lic = "".join(f"<li>{esc(i)}</li>" for i in p.get("licenceSummary", []))
    price = f'{p["price"]}€' if p.get("price") and p.get("currency") == "EUR" else ""
    store_btn = lambda label: f'<a class="btn btn-primary" href="{p["storeUrl"]}" target="_blank" rel="noopener" data-store-link data-store="{p["store"]}" data-product-id="{p["id"]}" data-product-name="{esc(p["name"])}">{label} <span aria-hidden="true">↗</span></a>'
    buy_label = f'Get it for {price} on {p["store"]}' if price else f'View on {p["store"]}'
    schema = {"@context": "https://schema.org", "@type": "Product", "name": p["name"], "description": p["shortDescription"],
              "category": p["category"], "brand": {"@type": "Brand", "name": "Teki Solves"}}
    if SITE_URL and p.get("ogImage"):
        schema["image"] = f'{SITE_URL}/{p["ogImage"]}'
    if price:
        schema["offers"] = {"@type": "Offer", "price": p["price"], "priceCurrency": p["currency"], "url": p["storeUrl"], "availability": "https://schema.org/InStock"}
    head_extra = f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>'
    desc = f'{p["name"]}: 15 retro sci-fi weapon sprites for indie games. 5 weapons in 3 tiers, PNG, SVG and atlas.' + (f' {price} on {p["store"]}.' if price else '')
    return shell(p["slug"], f'{p["name"]}: 15 retro sci-fi weapon sprites | Teki Solves', desc, f'''
<div data-product-id="{p["id"]}" data-product-name="{esc(p["name"])}" data-product-category="{esc(p["category"])}">
<section class="page-hero">
  <div class="wrap">
    <p class="crumbs"><a href="products.html">Products</a> / {esc(p["name"])}</p>
    <div class="focus-card">
      <div>
        <span class="eyebrow" style="color:var(--lime)">{esc(p["category"])} · {esc(p.get("version",""))}</span>
        <h1 style="margin-top:1rem">{esc(p["name"]).upper()}</h1>
        <p class="lede" style="font-family:var(--display);font-size:1.5rem;color:var(--fg);letter-spacing:-.03em;line-height:1.15">15 retro sci-fi weapons. 5 types, 3 tiers each.</p>
        <p class="lede">A laser pistol, rifle, shotgun, energy blade and plasma grenade, each in Scrap, Military and Prototype versions. Every tier shares the same shape and pivot, so upgrading a weapon in your game is just a texture swap.</p>
        <p class="meta-line">1024 × 1024 transparent PNG • SVG source • Atlas + JSON • Not pixel art</p>
        <p class="price-line">{esc(p.get("priceNote",""))}</p>
        <p style="margin-top:1.2rem">{store_btn(buy_label)}</p>
        <p class="note">Opens {p["store"]} in a new tab, where checkout and downloads are handled.</p>
      </div>
      {product_animation(p, "focus-visual", eager=True)}
    </div>
  </div>
</section>


<section class="band" aria-labelledby="range-h">
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">Try before you buy</span><h2 id="range-h">The weapon range</h2>
    <p>Every weapon and tier, live in your browser, using the pack's real pivot and muzzle data. Aim, fire, then swap tiers and watch the sprite stay exactly in the hand.</p></div>
    <div class="range" id="range" data-data="assets/3d/arsenal-data.json" data-base="assets/3d/">
      <div class="range-hud"><span>WEAPON <b data-hud="weapon">LASER PISTOL</b></span><span>TIER <b data-hud="tier">SCRAP</b></span><span>HITS <b data-hud="hits">000</b></span></div>
      {signature_loader("tk-range-load", "WEAPON RANGE", '<button type="button" class="tk-start" data-start hidden>&#9654; PRESS START</button>')}
      <canvas tabindex="0" aria-label="Weapon range: aim with the mouse or finger, click or tap to fire. Keys 1 to 5 pick a weapon, T swaps tier, Space fires."></canvas>
      <p class="range-note" data-hud="note" aria-live="polite"></p>
      <div class="range-controls">
        <div class="range-group" role="group" aria-label="Weapon"><button type="button" data-w="0" aria-pressed="true"><kbd>1</kbd>Pistol</button><button type="button" data-w="1" aria-pressed="false"><kbd>2</kbd>Rifle</button><button type="button" data-w="2" aria-pressed="false"><kbd>3</kbd>Shotgun</button><button type="button" data-w="3" aria-pressed="false"><kbd>4</kbd>Blade</button><button type="button" data-w="4" aria-pressed="false"><kbd>5</kbd>Grenade</button></div>
        <div class="range-group" role="group" aria-label="Sound"><button type="button" data-sound aria-pressed="true">SOUND ON</button></div>
        <div class="range-group" role="group" aria-label="Tier"><button type="button" data-t="0" aria-pressed="true">Scrap</button><button type="button" data-t="1" aria-pressed="false">Military</button><button type="button" data-t="2" aria-pressed="false">Prototype</button></div>
      </div>
    </div>
  </div>
</section>
<script src="assets/3d/range.js" defer></script>
<section class="band band-cream" aria-labelledby="preview">
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">Preview</span><h2 id="preview">Every sprite in the pack</h2></div>
    {previews}
  </div>
</section>

<section class="band" aria-labelledby="included">
  <div class="wrap cols">
    <div class="reveal stack"><span class="eyebrow">What’s included</span><h2 id="included">Inside the download</h2></div>
    <div class="reveal d1"><ul class="list">{inc}</ul></div>
  </div>
</section>

<section class="band band-cream" aria-labelledby="problem">
  <div class="wrap cols">
    <div class="reveal stack"><span class="eyebrow">Who it’s for</span><h2 id="problem">What this helps with</h2></div>
    <div class="prose reveal d1">
      <p>{esc(p["problemSolved"])}</p>
      <p>{esc(p["audience"])}</p>
      <p>The style is flat and readable, with one thick outline colour across the whole set. Side-on, facing right, no baked shadows, so your engine handles the lighting.</p>
    </div>
  </div>
</section>

<section class="band" aria-labelledby="specs">
  <div class="wrap cols">
    <div class="reveal stack"><span class="eyebrow">Specifications</span><h2 id="specs">Technical details</h2></div>
    <dl class="spec reveal d1" style="margin:0">
      <div><dt>Format</dt><dd>Transparent PNG, SVG source files, atlas and JSON metadata</dd></div>
      <div><dt>Sprites</dt><dd>15 × 1024 × 1024 PNG, straight alpha, facing right</dd></div>
      <div><dt>Atlas</dt><dd>4096 × 4096 PNG with pivot and action-point data per frame</dd></div>
      <div><dt>Engines</dt><dd>{esc(p.get("compatibility",""))}</dd></div>
      <div><dt>Version</dt><dd>{esc(p.get("version",""))}. Updates are free once you’ve bought it.</dd></div>
      <div><dt>Delivery</dt><dd>Download through {p["store"]} after purchase</dd></div>
    </dl>
  </div>
</section>

<section class="band band-cream" aria-labelledby="licence">
  <div class="wrap cols">
    <div class="reveal stack"><span class="eyebrow">Licensing</span><h2 id="licence">How you can use it</h2></div>
    <div class="prose reveal d1">
      <ul class="list">{lic}</ul>
      <p class="note">This is a summary. The full licence is in LICENSE.txt inside the download.</p>
    </div>
  </div>
</section>

<section class="band" aria-labelledby="faq">
  <div class="wrap cols">
    <div class="reveal stack"><span class="eyebrow">Support</span><h2 id="faq">Questions</h2></div>
    <div class="reveal d1">
      <details class="faq"><summary>Is it pixel art?</summary><p>No. It’s flat, vector-style 2D art with a thick outline, and there are SVG sources too, so it scales cleanly.</p></details>
      <details class="faq"><summary>Can I use it in a game I sell?</summary><p>Yes. You can use it in any number of your own commercial projects. You just can’t resell the files themselves.</p></details>
      <details class="faq"><summary>Will it work in my engine?</summary><p>The PNGs work anywhere. The atlas uses TexturePacker’s JSON hash format, which Unity, Godot and Phaser pipelines commonly read, but it hasn’t been tested inside them yet, so check your first import.</p></details>
      <details class="faq"><summary>How do I buy and download it?</summary><p>Use the button on this page. It opens {p["store"]}, where checkout, payment and downloads are handled. If you can’t access your files, <a href="contact.html">contact us</a> with the product name and what happened.</p></details>
    </div>
  </div>
</section>

<section class="band band-cream">
  <div class="wrap"><div class="cta-card reveal"><h2>Ready to arm your game?</h2>
  <p>{esc(p.get("priceNote",""))}</p>
  <div class="cta-actions">{store_btn(buy_label)}<a class="link-arrow" href="products.html">All products</a></div></div></div>
</section>
</div>
''', current="products.html", og_image=p.get("ogImage",""), head_extra=head_extra)

def about():
    return shell("about.html", "About Teki Solves — an independent digital product shop",
        "Teki Solves is an independent digital product shop and creative workshop built around a simple idea: useful things should solve real problems.", '''
<section class="page-hero">
  <div class="wrap">
    <span class="eyebrow">About Teki Solves</span>
    <h1 style="margin-top:1rem">A practical mindset. A creative outlook.</h1>
    <p class="lede">Teki Solves is an independent digital product shop and creative workshop built around a simple idea: useful things should solve real problems, and making them should leave room for creativity.</p>
    <p class="lede" style="margin-top:1rem">We create digital products across gaming, software, assets, learning and digital art. The formats may change, but the aim stays the same: make something thoughtful that helps someone move forward.</p>
  </div>
</section>
<section class="band band-cream"><div class="wrap cols">
  <div class="reveal stack"><span class="eyebrow">Mission and philosophy</span><h2>Solving problems simply. Empowering creativity. Making technology accessible for all.</h2></div>
  <div class="prose reveal d1"><p>We believe clarity is a skill, usefulness matters more than unnecessary complexity, and curiosity is worth protecting.</p><p>A good product doesn’t need to shout. It needs to do its job, communicate clearly and show care in the details.</p></div>
</div></section>
<section class="band"><div class="wrap cols">
  <div class="reveal stack"><span class="eyebrow">Who it’s for</span><h2>For people who make things.</h2></div>
  <div class="prose reveal d1"><p style="color:var(--muted)">Developers, self-learners, hobbyists, creators, artists and curious people arrive with different goals. What connects them is a desire to build, understand, experiment or solve something.</p></div>
</div></section>
<section class="band band-cream"><div class="wrap cols">
  <div class="reveal stack"><span class="eyebrow">What we make</span><h2>A growing collection of useful digital creations.</h2></div>
  <div class="prose reveal d1"><p>Our work can include game assets, software tools, coding products, educational material, digital assets and digital art. Our current product focus is game assets, while the wider scope remains open as the right ideas take shape.</p></div>
</div></section>
<section class="band"><div class="wrap cols">
  <div class="reveal stack"><span class="eyebrow">How we think about products</span><h2>Problem → product → learning.</h2></div>
  <div class="prose reveal d1"><p style="color:var(--muted)">We want each product to have a clear reason to exist. We pay attention to the problem, make something practical, explain it clearly and learn from how people use it. When a product can help someone learn as well as get something done, that’s even better.</p></div>
</div></section>
<section class="band band-cream"><div class="wrap cols">
  <div class="reveal stack"><span class="eyebrow">Where we’re going</span><h2>Technology, design and storytelling belong together.</h2></div>
  <div class="prose reveal d1"><p>Digital products are our current focus. Over time, Teki Solves aims to explore a wider creative space where technology, design and storytelling meet, including games, creative arts and hardware innovation as resources allow.</p></div>
</div></section>
<section class="band"><div class="wrap"><div class="section-head reveal"><h2>See what we’re making.</h2><p><a class="btn btn-primary" href="products.html">See the products</a></p></div></div></section>
''', current="about.html")

def contact():
    return shell("contact.html", "Contact — Teki Solves",
        "Tell us what you’re trying to make, what you need or what’s getting in the way. Teki Solves is interested in problems worth solving.", f'''
<section class="page-hero">
  <div class="wrap">
    <span class="eyebrow">Contact</span>
    <h1 style="margin-top:1rem">Have a problem in mind?</h1>
    <p class="lede">Tell us what you’re trying to make, what you need or what’s getting in the way. It doesn’t have to fit a category. We’re interested in problems worth solving.</p>
  </div>
</section>
<section class="band">
  <div class="wrap form-wrap">
    <ul class="list helper reveal">
      <li>Share as much or as little detail as you’re comfortable with.</li>
      <li>If you’re asking about a product, include its name.</li>
      <li>Please don’t include passwords, payment card details or other sensitive information.</li>
    </ul>
    <div class="reveal d1">
      <form class="contact-form" id="contactForm" novalidate>
        <div class="form-grid">
          <label>Name<input name="name" type="text" autocomplete="name" required></label>
          <label>Email<input name="email" type="email" autocomplete="email" required></label>
        </div>
        <div class="form-grid">
          <label>Business or project name <small>(optional)</small><input name="businessName" type="text" autocomplete="organization"></label>
          <label>What is this about?<select name="trackInterest"><option>Digital Products</option><option>Product idea or request</option><option selected>Not sure</option></select></label>
        </div>
        <label>Message<textarea name="message" rows="6"></textarea></label>
        <label class="honeypot" aria-hidden="true">Website<input name="website" type="text" tabindex="-1" autocomplete="off"></label>
        <label class="privacy-consent"><input name="privacyAcknowledgement" type="checkbox" required><span>I’ve read the <a href="privacy-policy.html" target="_blank" rel="noopener" style="color:var(--lime)">Privacy Policy</a> and understand how my details will be used to reply to me.</span></label>
        <p class="form-error" id="formError" role="alert" hidden></p>
        <div class="form-footer"><button class="btn btn-primary" id="submitButton" type="submit">Send it over <span aria-hidden="true">→</span></button><span>Or email <a href="mailto:{EMAIL}">{EMAIL}</a></span></div>
      </form>
      <div class="success-message" id="successMessage" tabindex="-1" hidden><h2 style="font-size:1.6rem">Thanks, that’s with us.</h2><p style="color:var(--muted)">We’ll read it and get back to you.</p><p><a class="btn btn-outline btn-sm" href="products.html">Explore products</a></p></div>
    </div>
  </div>
</section>
''', current="contact.html")

def legal(src, out, current_title):
    s = open(os.path.join(LEGACY, src), encoding="utf-8").read()
    m = re.search(r'<span class="eyebrow">(.*?)</span>\s*<h1>(.*?)</h1>\s*<p class="legal-updated">(.*?)</p>(.*?)<footer class="legal-footer">', s, re.S)
    eb, h1, upd, secs = m.groups()
    desc = re.search(r'<meta name="description" content="(.*?)">', s).group(1).strip()
    body = f'''<div class="legal"><div class="wrap legal-wrap"><a class="legal-back" href="index.html">← Back to Teki Solves</a>
<span class="eyebrow" style="display:block;margin-top:1.4rem">{eb}</span><h1>{h1}</h1><p class="legal-updated">{upd}</p>{secs}</div></div>'''
    return shell(out, f"{current_title} — Teki Solves", desc, body)

def not_found():
    return shell("404.html", "Page not found — Teki Solves", "That page could not be found.", '''
<section class="page-hero page-hero-lost"><div class="wrap"><span class="eyebrow">404</span><h1 style="margin-top:1rem">That page wandered off.</h1>
<p class="lede">Even the Solver takes a wrong turn sometimes. Let’s get you somewhere useful.</p><p style="margin-top:1.6rem"><a class="btn btn-primary" href="products.html">Explore products</a></p></div></section>''', robots="noindex")

# ---------- blog ----------
# Posts are Markdown files in source/blog/<slug>.md with a small header:
#   ---
#   title: How to ...            (the <h1>)
#   seo_title: Short title       (optional, for Google tabs and results, under 60 characters)
#   description: One or two sentences for Google (50-160 characters)
#   date: 2026-12-06             (first published)
#   updated: 2026-12-06          (change this whenever you improve the post)
#   draft: true                  (drafts are never published; delete the line to publish)
#   image: assets/blog/x.webp    (optional share image, 1200x630)
#   image_alt: What the image shows
#   made: How this post was made (shown at the end, honest note)
#   ---
# Preview drafts locally with:  BLOG_DRAFTS=1 TEKI_EMAIL=... python3 build.py
import datetime, markdown as md_lib

BLOG_DIR = os.path.join(HERE, "blog")
AUTHOR = {"name": "Khaya Khumalo",
          "bio": "Self-taught senior full-stack engineer with 10+ years of experience, including Meta and Accenture. "
                 "I make game assets and small, useful digital products at Teki Solves."}

def read_post(path):
    raw = open(path, encoding="utf-8").read()
    meta, body = {}, raw
    m = re.match(r"---\s*\n(.*?)\n---\s*\n(.*)", raw, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = m.group(2)
    meta["slug"] = os.path.splitext(os.path.basename(path))[0]
    meta["draft"] = meta.get("draft", "").lower() in ("true", "yes", "1")
    meta.setdefault("updated", meta.get("date", ""))
    conv = md_lib.Markdown(extensions=["fenced_code", "tables", "toc", "attr_list"],
                           extension_configs={"toc": {"permalink": False}})
    meta["html"] = conv.convert(body)
    meta["toc"] = conv.toc_tokens
    words = len(re.findall(r"\w+", body))
    meta["minutes"] = max(1, round(words / 220))
    return meta

def blog_posts():
    if not os.path.isdir(BLOG_DIR):
        return []
    show_drafts = os.environ.get("BLOG_DRAFTS") == "1"
    posts = [read_post(os.path.join(BLOG_DIR, f)) for f in sorted(os.listdir(BLOG_DIR)) if f.endswith(".md")]
    return sorted([p for p in posts if show_drafts or not p["draft"]], key=lambda p: p["date"], reverse=True)

def nice_date(d):
    return datetime.date.fromisoformat(d).strftime("%-d %B %Y")

def post_page(p):
    path = f'blog/{p["slug"]}/index.html'
    url = page_url(path)
    image = p.get("image") or DEFAULT_OG_IMAGE
    schema = [{
        "@context": "https://schema.org", "@type": "BlogPosting",
        "headline": p["title"], "description": p["description"],
        "datePublished": p["date"], "dateModified": p["updated"],
        "author": {"@type": "Person", "name": AUTHOR["name"], "url": f"{SITE_URL}/about.html"},
        "publisher": {"@type": "Organization", "name": "Teki Solves", "logo": {"@type": "ImageObject", "url": f"{SITE_URL}/assets/logo-diamond.png"}},
        "image": f"{SITE_URL}/{image}", "mainEntityOfPage": url, "url": url},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Blog", "item": f"{SITE_URL}/blog/"},
            {"@type": "ListItem", "position": 2, "name": p["title"], "item": url}]}]
    head = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in schema)
    head += f'<meta property="article:published_time" content="{p["date"]}"><meta property="article:modified_time" content="{p["updated"]}"><meta name="author" content="{esc(AUTHOR["name"])}">'
    updated = f' · Updated <time datetime="{p["updated"]}">{nice_date(p["updated"])}</time>' if p["updated"] != p["date"] else ""
    toc = "".join(f'<li><a href="#{t["id"]}">{esc(t["name"])}</a></li>' for t in p["toc"] if t["level"] == 2) if p["toc"] else ""
    toc_html = f'<nav class="post-toc" aria-label="On this page"><p class="eyebrow">On this page</p><ol>{toc}</ol></nav>' if toc else ""
    made = f'<p class="note made-note"><strong>How this post was made:</strong> {esc(p["made"])}</p>' if p.get("made") else ""
    draft = '<p class="draft-flag">DRAFT, not published</p>' if p["draft"] else ""
    body = f'''
<article class="post">
<header class="page-hero post-hero">
  <div class="wrap post-wrap">
    {draft}<p class="crumbs"><a href="blog/">Blog</a> / Tutorial</p>
    <h1>{esc(p["title"])}</h1>
    <p class="lede">{esc(p["description"])}</p>
    <p class="post-meta">By <a href="about.html">{esc(AUTHOR["name"])}</a> · <time datetime="{p["date"]}">{nice_date(p["date"])}</time>{updated} · {p["minutes"]} min read</p>
  </div>
</header>
<div class="band"><div class="wrap post-wrap">
  {toc_html}
  <div class="post-body">{p["html"]}</div>
  {made}
  <aside class="author-box" aria-label="About the author"><p class="eyebrow">Written by</p><p><strong>{esc(AUTHOR["name"])}</strong>. {esc(AUTHOR["bio"])}</p></aside>
  <p style="margin-top:2rem"><a class="link-arrow" href="blog/">← All posts</a></p>
</div></div>
</article>'''
    robots = "noindex" if p["draft"] else "index, follow"
    return path, shell(path, p.get("seo_title") or f'{p["title"]} | Teki Solves', p["description"], body, current="blog/",
                       robots=robots, og_image=image, head_extra=head, og_type="article")

def blog_index(posts):
    path = "blog/index.html"
    if posts:
        items = "".join(f'''<article class="post-card reveal">
  <p class="post-meta"><time datetime="{p["date"]}">{nice_date(p["date"])}</time> · {p["minutes"]} min read</p>
  <h2><a href="blog/{p["slug"]}/">{esc(p["title"])}</a></h2>
  <p>{esc(p["description"])}</p>
  <span class="card-cta" aria-hidden="true">Read it →</span>
</article>''' for p in posts)
    else:
        items = '''<div class="post-card"><h2>First post lands in early December</h2>
  <p>A hands-on Phaser 4 tutorial: loading a texture atlas and lining weapons up properly, with a free sample to follow along with.</p></div>'''
    body = f'''
<section class="page-hero">
  <div class="wrap post-wrap">
    <span class="eyebrow">The Teki Solves blog</span>
    <h1 style="margin-top:1rem">Practical game dev notes.</h1>
    <p class="lede">Tutorials and build notes for indie developers, written from real work: what worked, what broke, and the code to skip the trial and error.</p>
  </div>
</section>
<section class="band band-cream"><div class="wrap post-wrap post-list">{items}</div></section>'''
    head = f'<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "Blog", "name": "Teki Solves blog", "url": f"{SITE_URL}/blog/", "publisher": {"@type": "Organization", "name": "Teki Solves"}})}</script>'
    return path, shell(path, "Game dev tutorials and build notes | Teki Solves blog",
        "Practical game dev tutorials for indie developers: Phaser, Godot, sprites and texture atlases, written from real projects.",
        body, current="blog/", head_extra=head)

def blog_feed(posts):
    items = "".join(f'''<item><title>{esc(p["title"])}</title><link>{SITE_URL}/blog/{p["slug"]}/</link><guid>{SITE_URL}/blog/{p["slug"]}/</guid>
<pubDate>{datetime.date.fromisoformat(p["date"]).strftime("%a, %d %b %Y 09:00:00 +0000")}</pubDate><description>{esc(p["description"])}</description></item>''' for p in posts if not p["draft"])
    return f'''<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Teki Solves blog</title><link>{SITE_URL}/blog/</link>
<description>Practical game dev tutorials and build notes.</description><language>en</language>{items}</channel></rss>'''

def relocate(page, path):
    """Pages in sub-folders: make relative links point back to the site root."""
    depth = path.count("/")
    if not depth:
        return page
    up = "../" * depth
    return re.sub(r'(\s(?:href|src|poster|srcset)=")(?!https?:|//|#|mailto:|tel:|data:|/)([^"]*)"',
                  lambda m: f'{m.group(1)}{up}{m.group(2)}"', page)

# ---------- write ----------
if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)
for f in ("style.css", "script.js"):
    shutil.copy(os.path.join(HERE, f), OUT)
shutil.copytree(os.path.join(HERE, "assets"), os.path.join(OUT, "assets"))

pages = {"index.html": home(), "products.html": products_page(), "about.html": about(), "contact.html": contact(), "404.html": not_found()}
for src, title in (("privacy-policy.html", "Privacy Policy"), ("cookie-policy.html", "Cookie Policy")):
    if os.path.exists(os.path.join(LEGACY, src)):
        pages[src] = legal(src, src, title)
    elif os.path.exists(os.path.join(HERE, "..", src)):   # no legacy source: keep the page that's already live
        s = open(os.path.join(HERE, "..", src), encoding="utf-8").read()
        if SITE_URL and 'rel="canonical"' not in s:   # add the SEO tags the old copy lacks
            s = s.replace("</head>", f'{canon(src)}<meta property="og:url" content="{page_url(src)}"><link rel="apple-touch-icon" href="assets/apple-touch-icon.png">\n</head>', 1)
        open(os.path.join(OUT, src), "w", encoding="utf-8").write(s)
for p in products:
    pages[p["slug"]] = product_page(p)
posts = blog_posts()
for p in posts:
    path, content = post_page(p)
    pages[path] = content
path, content = blog_index(posts)
pages[path] = content
for name, content in pages.items():
    os.makedirs(os.path.dirname(os.path.join(OUT, name)), exist_ok=True)
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(relocate(content, name))
open(os.path.join(OUT, "blog", "feed.xml"), "w", encoding="utf-8").write(blog_feed(posts))

for f in os.listdir(HERE):   # IndexNow key file (public by design), used by the SEO bot after each deploy
    if re.fullmatch(r"[0-9a-f]{32}\.txt", f):
        shutil.copy(os.path.join(HERE, f), OUT)

public = sorted(os.path.relpath(os.path.join(r, f), OUT).replace(os.sep, "/")   # includes copied legal pages and the blog
                for r, _, fs in os.walk(OUT) for f in fs if f.endswith(".html") and f != "404.html")
drafts = {f'blog/{p["slug"]}/index.html' for p in posts if p["draft"]}
public = [n for n in public if n not in drafts]
if SITE_URL:
    today = datetime.date.today().isoformat()
    lastmod = {f'blog/{p["slug"]}/index.html': p["updated"] for p in posts}
    urls = "".join(f"<url><loc>{page_url(n)}</loc><lastmod>{lastmod.get(n, today)}</lastmod></url>" for n in public)
    open(os.path.join(OUT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
open(os.path.join(OUT, "robots.txt"), "w").write("User-agent: *\nAllow: /\n" + (f"Sitemap: {SITE_URL}/sitemap.xml\n" if SITE_URL else ""))
print("Built", len(pages), "pages ->", OUT)
