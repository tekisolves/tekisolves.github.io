#!/usr/bin/env python3
"""Teki Solves static site builder.
Run:  python3 build.py        -> writes the finished site to ./dist
Edit products in products.json, copy in the page functions below, set SITE_URL once the domain is final.
"""
import json, os, re, shutil, html

SITE_URL = ""          # e.g. "https://tekisolves.com" -- leave empty until final; canonical/OG url/sitemap are skipped while empty
EMAIL = "tekisolutions2@gmail.com"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "dist")
LEGACY = os.environ.get("LEGACY_DIR", os.path.join(HERE, "..", "Teki-Solves-Landing-Page-main"))
products = json.load(open(os.path.join(HERE, "products.json")))
esc = html.escape

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

# ---------- shared shell ----------
def canon(path):
    return f'<link rel="canonical" href="{SITE_URL}/{path}">' if SITE_URL else ""

def shell(path, title, desc, body, current="", robots="index, follow"):
    og = f'<meta property="og:url" content="{SITE_URL}/{path}">' if SITE_URL else ""
    nav = [("products.html","Products"),("about.html","About"),("contact.html","Contact")]
    cur = ' aria-current="page"'
    desk = "".join(f'<a href="{h}"{cur if h==current else ""}>{t}</a>' for h,t in nav)
    mob = "".join(f'<a href="{h}">{t}</a>' for h,t in nav)
    org = json.dumps({"@context":"https://schema.org","@type":"Organization","name":"Teki Solves",
        "description":"An independent digital product shop and creative workshop making practical digital products that solve real problems."})
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#101311">
{canon(path)}
<meta property="og:type" content="website"><meta property="og:site_name" content="Teki Solves">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">{og}
<link rel="icon" type="image/png" href="assets/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
<script>document.documentElement.classList.add('js');window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('consent','default',{{analytics_storage:'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'}});</script>
<script type="application/ld+json">{org}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="index.html" aria-label="Teki Solves home"><span class="brand-mark"><img src="assets/logo-diamond.png" alt="" width="26" height="26"></span><span class="brand-text">TEKI / SOLVES</span></a>
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
    <div><a class="brand" href="index.html"><span class="brand-mark"><img src="assets/logo-diamond.png" alt="" width="26" height="26"></span><span class="brand-text">TEKI / SOLVES</span></a>
    <p class="mono" style="margin-top:1rem;font-size:.72rem;letter-spacing:.14em;color:var(--gold)">KEEP IT SIMPLE, PROBLEM SOLVED.</p></div>
    <div class="footer-links"><a href="products.html">Products</a><a href="about.html">About</a><a href="contact.html">Contact</a><a href="privacy-policy.html">Privacy Policy</a><a href="cookie-policy.html">Cookie Policy</a><button class="footer-link cookie-settings-trigger" type="button">Cookie Settings</button></div>
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
<script src="script.js" defer></script>
</body>
</html>
'''

# ---------- components ----------
def product_visual(p, cls="product-visual"):
    img = p["previewImages"][0] if p.get("previewImages") else ""
    inner = f'<img src="{img}" alt="{esc(p["name"])} preview" loading="lazy">' if img and has(img) else arch_svg("pc"+p["id"][:3], cls="")
    return f'<div class="{cls}">{inner}</div>'

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
      <h1>Good ideas deserve <span>useful solutions.</span></h1>
      <p>Teki Solves is a digital product shop and creative workshop making thoughtful things for people who build, learn and create.</p>
      <p>From game assets to software tools and learning resources, every product starts with a simple question: what problem can we help solve?</p>
      <p class="tagline">Keep it simple, problem solved.</p>
      <div class="hero-actions"><a class="btn btn-primary" href="products.html">Explore products</a></div>
    </div>
    <div class="hero-art">{arch_svg("h")}<a class="chip" href="{p["slug"]}"><i></i>Now on itch.io: {esc(p["name"])}</a></div>
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
    <p style="margin-top:2rem"><a class="btn btn-dark" href="products.html">Explore all products</a></p>
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
    {product_visual(p, "focus-visual reveal d1")}
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
      <div class="cta-actions"><a class="btn btn-primary" href="products.html">Explore products</a><a class="link-arrow" href="contact.html">Tell us what you need</a></div>
    </div>
  </div>
</section>
''', current="")

def products_page():
    cards = "".join(product_card(x) for x in live_products())
    return shell("products.html", "Products — Teki Solves",
        "Browse digital products made to help you build, learn and create. Every Teki Solves product has a purpose.", f'''
<section class="page-hero">
  <div class="wrap">
    <span class="eyebrow">The Teki Solves catalogue</span>
    <h1 style="margin-top:1rem">Find your next useful thing.</h1>
    <p class="lede">Browse digital products made to help you build, learn and create. From game assets to practical technical resources, every product has a purpose.</p>
    <p style="margin-top:1.6rem"><a class="btn btn-primary" href="#catalogue">Explore products</a></p>
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
    previews = ""
    if ok:
        labels = ["On a dark background", "On a light background"]
        figs = "".join(f'<figure class="preview-slot{" light" if i==1 else ""}" style="margin:0"><img src="{x}" alt="{esc(p["name"])} preview {i+1}" loading="lazy"><figcaption>{labels[i] if i<2 else ""}</figcaption></figure>' for i,x in enumerate(ok))
        previews = f'<div class="preview-grid">{figs}</div>'
    else:
        previews = f'<p style="margin-top:1rem">Full previews, including close-ups, are on the <a href="{p["storeUrl"]}" target="_blank" rel="noopener" data-store-link data-store="{p["store"]}" data-product-id="{p["id"]}" data-product-name="{esc(p["name"])}">{p["store"]} page</a>.</p>'
    inc = "".join(f"<li>{esc(i)}</li>" for i in p["includedItems"])
    store_btn = lambda label: f'<a class="btn btn-primary" href="{p["storeUrl"]}" target="_blank" rel="noopener" data-store-link data-store="{p["store"]}" data-product-id="{p["id"]}" data-product-name="{esc(p["name"])}">{label} <span aria-hidden="true">↗</span></a>'
    return shell(p["slug"], f'{p["name"]} — Stylized 2D weapon assets | Teki Solves',
        f'{p["name"]}: a stylized retro-futurist 2D weapon asset pack for indie game developers. See what is included, the formats and how to get it.', f'''
<!-- BEFORE LAUNCH: verify package details against the live download: sprite count, 1024x1024 PNGs, SVG sources, atlas + JSON, pivots. Confirm price, licence terms and store URL. -->
<div data-product-id="{p["id"]}" data-product-name="{esc(p["name"])}" data-product-category="{esc(p["category"])}">
<section class="page-hero">
  <div class="wrap">
    <p class="crumbs"><a href="products.html">Products</a> / {esc(p["name"])}</p>
    <div class="focus-card">
      <div>
        <span class="eyebrow" style="color:var(--lime)">{esc(p["category"])}</span>
        <h1 style="margin-top:1rem">{esc(p["name"]).upper()}</h1>
        <p class="lede" style="font-family:var(--display);font-size:1.5rem;color:var(--fg);letter-spacing:-.03em;line-height:1.15">Stylized 2D weapon assets for your next game.</p>
        <p class="lede">Spend less time building every weapon from scratch and more time building your game. Retro Arsenal is a stylized retro-futurist weapon asset pack for indie developers who want a coherent visual set they can work with.</p>
        <p class="tagline" style="margin-top:1rem">A consistent look. Multiple weapon styles. A practical starting point for your game’s visual world.</p>
        <p class="meta-line">1024 × 1024 transparent PNG • SVG source • Atlas + JSON • Sold on {p["store"]}</p>
        <p style="margin-top:1.4rem">{store_btn("View on " + p["store"])}</p>
        <p class="note">Opens {p["store"]} in a new tab. Price and checkout are shown there.</p>
      </div>
      {product_visual(p, "focus-visual")}
    </div>
  </div>
</section>

<section class="band band-cream" aria-labelledby="problem">
  <div class="wrap cols">
    <div class="reveal stack"><span class="eyebrow">The problem</span><h2 id="problem">What this helps with</h2></div>
    <div class="prose reveal d1">
      <p>{esc(p["problemSolved"])}</p>
      <h3 style="margin-top:1rem">Who it’s for</h3>
      <p>{esc(p["audience"])}</p>
      <h3 style="margin-top:1rem">The style</h3>
      <p>Stylized retro-futurist 2D game art with clean outlines and flat, vector-inspired shapes. It has a retro sci-fi, industrial character and simplified, readable forms. It is not pixel art.</p>
    </div>
  </div>
</section>

<section class="band" aria-labelledby="included">
  <div class="wrap cols">
    <div class="reveal stack"><span class="eyebrow">What’s included</span><h2 id="included">Inside the download</h2></div>
    <div class="reveal d1"><ul class="list">{inc}</ul><p class="note">Check the {p["store"]} page for the current package contents.</p></div>
  </div>
</section>

<section class="band band-cream" aria-labelledby="preview">
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">Preview</span><h2 id="preview">See what you’re getting</h2></div>
    {previews}
  </div>
</section>

<section class="band" aria-labelledby="specs">
  <div class="wrap cols">
    <div class="reveal stack"><span class="eyebrow">Specifications</span><h2 id="specs">Technical details</h2></div>
    <dl class="spec reveal d1" style="margin:0">
      <div><dt>Format</dt><dd>Transparent PNG, SVG source files, atlas and JSON metadata</dd></div>
      <div><dt>Dimensions</dt><dd>1024 × 1024 PNG sprites</dd></div>
      <div><dt>Compatibility</dt><dd>See the {p["store"]} page for engine and software notes</dd></div>
      <div><dt>Requirements</dt><dd>See the {p["store"]} page</dd></div>
      <div><dt>Delivery</dt><dd>Download through {p["store"]} after purchase</dd></div>
    </dl>
  </div>
</section>

<section class="band band-cream" aria-labelledby="licence">
  <div class="wrap cols">
    <div class="reveal stack"><span class="eyebrow">Licensing</span><h2 id="licence">How you can use it</h2></div>
    <div class="prose reveal d1">
      <p>The licence is listed on the <a href="{p["storeUrl"]}" target="_blank" rel="noopener">{p["store"]} page</a>. Read it before using {esc(p["name"])} in commercial work.</p>
      <p>Do not redistribute or resell the files unless the licence explicitly allows it.</p>
    </div>
  </div>
</section>

<section class="band" aria-labelledby="faq">
  <div class="wrap cols">
    <div class="reveal stack"><span class="eyebrow">Support</span><h2 id="faq">Questions about this product?</h2></div>
    <div class="reveal d1">
      <details class="faq"><summary>What is included?</summary><p>The list above shows the files in the pack. Check it, and the {p["store"]} page, before you buy.</p></details>
      <details class="faq"><summary>Is it pixel art?</summary><p>No. It is stylized retro-futurist 2D art with clean outlines and flat, vector-inspired shapes.</p></details>
      <details class="faq"><summary>Can I use it commercially?</summary><p>That depends on the licence on the {p["store"]} page. Read it before using the pack in commercial work.</p></details>
      <details class="faq"><summary>Where do I buy it, and how do I download it?</summary><p>Use the button on this page. It opens {p["store"]}, where checkout, payment and downloads are handled. If you can’t access your files, <a href="contact.html">contact us</a> with the product name and what happened.</p></details>
      <p style="margin-top:1.4rem;color:var(--muted)">Still unsure? <a href="contact.html" style="color:var(--lime)">Contact us before buying.</a></p>
    </div>
  </div>
</section>

<section class="band band-cream">
  <div class="wrap"><div class="cta-card reveal"><h2>Keep exploring</h2>
  <div class="cta-actions">{store_btn("Get the product")}<a class="link-arrow" href="products.html">All products</a></div></div></div>
</section>
</div>
''', current="products.html")

def about():
    return shell("about.html", "About — Teki Solves",
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
<section class="band"><div class="wrap"><div class="section-head reveal"><h2>See what we’re making.</h2><p><a class="btn btn-primary" href="products.html">Explore products</a></p></div></div></section>
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
<section class="page-hero"><div class="wrap"><span class="eyebrow">404</span><h1 style="margin-top:1rem">That page wandered off.</h1>
<p class="lede">Let’s get you somewhere useful.</p><p style="margin-top:1.6rem"><a class="btn btn-primary" href="products.html">Explore products</a></p></div></section>''', robots="noindex")

# ---------- write ----------
if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)
for f in ("style.css", "script.js"):
    shutil.copy(os.path.join(HERE, f), OUT)
shutil.copytree(os.path.join(HERE, "assets"), os.path.join(OUT, "assets"))

pages = {"index.html": home(), "products.html": products_page(), "about.html": about(), "contact.html": contact(), "404.html": not_found(),
         "privacy-policy.html": legal("privacy-policy.html", "privacy-policy.html", "Privacy Policy"),
         "cookie-policy.html": legal("cookie-policy.html", "cookie-policy.html", "Cookie Policy")}
for p in products:
    pages[p["slug"]] = product_page(p)
for name, content in pages.items():
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(content)

public = [n for n in pages if n != "404.html"]
if SITE_URL:
    urls = "".join(f"<url><loc>{SITE_URL}/{n}</loc></url>" for n in public)
    open(os.path.join(OUT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
open(os.path.join(OUT, "robots.txt"), "w").write("User-agent: *\nAllow: /\n" + (f"Sitemap: {SITE_URL}/sitemap.xml\n" if SITE_URL else ""))
print("Built", len(pages), "pages ->", OUT)
