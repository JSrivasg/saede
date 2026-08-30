#!/usr/bin/env python3
"""
Saede site builder.

    python3 build.py          build the site into dist/
    python3 build.py --serve  build, then serve it at http://localhost:8000

No dependencies, no install step, no node_modules. Everything it needs is in
the Python standard library, so it will still build in five years.

How it works
------------
  content/   the words (JSON pages + Markdown articles) — edit these
  theme/     the CSS design system
  _build/    the generator (md.py renders Markdown, render.py renders sections)
  dist/      the output — never edit this by hand, it is overwritten

Every page is a list of 'sections' in a JSON file. Reordering the page means
reordering that list. The section types are documented in README.md.
"""
import hashlib
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_build"))

import md          # noqa: E402
import render      # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------

def asset_version(*parts):
    """Short content hash for a static asset.

    Appended to the CSS and JS URLs as ?v=... so that when you change a
    stylesheet, visitors get the new one immediately instead of a cached
    copy. Without this a returning visitor can sit on last week's CSS for
    days, which is the single most common cause of "it looks broken for me
    but fine for you".
    """
    path = os.path.join(ROOT, *parts)
    try:
        with open(path, "rb") as f:
            return hashlib.sha1(f.read()).hexdigest()[:8]
    except OSError:
        return "0"


def load_json(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return json.load(f)


def strip_readme(obj):
    """Drop the _readme / _*_note keys so editor comments never reach the HTML."""
    if isinstance(obj, dict):
        return {k: strip_readme(v) for k, v in obj.items() if not k.startswith("_")}
    if isinstance(obj, list):
        return [strip_readme(v) for v in obj]
    return obj


def load_articles(site):
    """Read every Markdown file in content/learn/ into a list, sorted by 'order'."""
    out = []
    d = os.path.join(ROOT, "content", "learn")
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".md"):
            continue
        with open(os.path.join(d, fn), encoding="utf-8") as f:
            meta, body = md.frontmatter(f.read())
        slug = fn[:-3]
        out.append({
            "slug": slug,
            "path": "/learn/%s/" % slug,
            "meta": meta,
            "body": body,
        })
    out.sort(key=lambda a: a["meta"].get("order", 999))
    return out


# --------------------------------------------------------------------------
# {{partner}} substitution — rename the powder in one place
# --------------------------------------------------------------------------

def substitute(obj, tokens):
    """Replace {{token}} placeholders throughout the content tree.

    Keys are applied longest-first so that {{partner_short}} is matched
    before {{partner}} and does not get eaten by it.
    """
    if isinstance(obj, str):
        for k in sorted(tokens, key=len, reverse=True):
            obj = obj.replace("{{%s}}" % k, tokens[k])
        return obj
    if isinstance(obj, dict):
        return {k: substitute(v, tokens) for k, v in obj.items()}
    if isinstance(obj, list):
        return [substitute(v, tokens) for v in obj]
    return obj


# --------------------------------------------------------------------------
# chrome: head, header, footer
# --------------------------------------------------------------------------

def head(site, meta):
    url = site["brand"]["url"].rstrip("/") + meta.get("path", "/")
    tagline = site["brand"].get("tagline")
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<link rel="canonical" href="%(url)s">
<meta property="og:type" content="website">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:url" content="%(url)s">
<meta property="og:site_name" content="Saede">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#FBF7F3">
%(tagline)s
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..600;1,400..500&family=Mulish:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/theme/tokens.css?v=%(v_tokens)s">
<link rel="stylesheet" href="/theme/base.css?v=%(v_base)s">
<link rel="stylesheet" href="/theme/components.css?v=%(v_components)s">
<link rel="stylesheet" href="/theme/textures.css?v=%(v_textures)s">
<link rel="icon" href="/assets/img/pearl.svg" type="image/svg+xml">
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
""" % {
        "title": render.esc(meta["title"]),
        "desc": render.esc(meta["description"]),
        "url": render.esc(url),
        "tagline": '<meta name="subject" content="%s">' % render.esc(tagline) if tagline else "",
        "v_tokens": asset_version("theme", "tokens.css"),
        "v_base": asset_version("theme", "base.css"),
        "v_components": asset_version("theme", "components.css"),
        "v_textures": asset_version("theme", "textures.css"),
    }


def opening(site):
    """The film, the fade to white, then the name.

    Rendered with the `hidden` attribute already set, so with JavaScript off
    or blocked it never appears at all and the visitor simply lands on the
    page. main.js decides whether to run it: once per browsing session, never
    for anyone who has asked for reduced motion, and never if the video
    cannot autoplay.
    """
    if not site["flags"].get("show_opening"):
        return ""
    letters = "".join("<span>%s</span>" % c for c in site["brand"]["name"].upper())
    return """<div class="opening" data-opening data-phase="film" hidden>
  <video class="opening-video" data-opening-video
         muted autoplay playsinline preload="auto"
         disablepictureinpicture aria-hidden="true">
    <source src="/assets/video/opening.mp4" type="video/mp4">
  </video>
  <div class="opening-name">
    <p class="opening-wordmark" role="img" aria-label="Saede">%s</p>
    <div class="opening-rule"><span class="pearl pearl--glow" aria-hidden="true"></span></div>
    <p class="opening-line">%s</p>
    <p class="opening-sub">%s</p>
  </div>
  <button class="opening-skip" type="button" data-opening-skip>Skip</button>
</div>
""" % (letters, render.esc(site["brand"]["meaning"]), render.esc(site["brand"]["tagline"] or ""))


def header(site, current):
    links, mobile = "", ""
    for item in site["nav"]:
        if item.get("type") == "dropdown":
            sub, msub = "", ""
            for s in item["items"]:
                if s.get("href"):
                    sub += '<li><a href="%s">%s</a></li>' % (render.esc(s["href"]), render.esc(s["label"]))
                    msub += '<li><a href="%s">%s</a></li>' % (render.esc(s["href"]), render.esc(s["label"]))
                else:
                    # future concern areas: present, but not announced as dated
                    sub += '<li><span class="soon">%s <em>%s</em></span></li>' % (
                        render.esc(s["label"]), render.esc(s.get("note", ""))
                    )
                    msub += '<li><span>%s — %s</span></li>' % (
                        render.esc(s["label"]), render.esc(s.get("note", ""))
                    )
            links += """<li class="nav-drop" data-drop>
                <button type="button" aria-expanded="false">%s
                  <svg width="9" height="6" viewBox="0 0 9 6" fill="none" aria-hidden="true">
                    <path d="M1 1L4.5 4.5L8 1" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                  </svg>
                </button>
                <ul class="nav-drop-panel">%s</ul></li>""" % (render.esc(item["label"]), sub)
            mobile += '<li><a href="%s">%s</a></li><li class="sub"><ul>%s</ul></li>' % (
                render.esc(item["items"][0]["href"]), render.esc(item["label"]), msub
            )
        else:
            cur = ' aria-current="page"' if item["href"] == current else ""
            links += '<li><a href="%s"%s>%s</a></li>' % (render.esc(item["href"]), cur, render.esc(item["label"]))
            mobile += '<li><a href="%s"%s>%s</a></li>' % (render.esc(item["href"]), cur, render.esc(item["label"]))

    cta = site["nav_cta"]
    if site["flags"].get("launch_status") == "live" and site.get("nav_cta_live"):
        cta = site["nav_cta_live"]
    return """<header class="site-header" data-header>
  <div class="wrap">
    <nav class="nav" aria-label="Main">
      <a class="brand" href="/"><span class="pearl pearl--glow" aria-hidden="true"></span>Saede</a>
      <ul class="nav-links">%s</ul>
      <div class="nav-cta"><a class="btn btn--primary" href="%s">%s</a></div>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="mobile-nav" data-nav-toggle>
        <span class="visually-hidden">Menu</span>
        <span aria-hidden="true"></span><span aria-hidden="true"></span><span aria-hidden="true"></span>
      </button>
    </nav>
  </div>
  <div class="mobile-nav" id="mobile-nav">
    <ul>%s</ul>
    <a class="btn btn--primary" href="%s">%s</a>
  </div>
</header>
<main id="main">""" % (
        links, render.esc(cta["href"]), render.esc(cta["label"]),
        mobile, render.esc(cta["href"]), render.esc(cta["label"]),
    )


def footer(site):
    cols = ""
    for col in site["footer"]["columns"]:
        items = ""
        for l in col["links"]:
            if l.get("href"):
                items += '<li><a href="%s">%s</a></li>' % (render.esc(l["href"]), render.esc(l["label"]))
            else:
                items += '<li><span class="soon">%s</span></li>' % render.esc(l["label"])
        cols += '<div class="footer-col"><h4>%s</h4><ul>%s</ul></div>' % (render.esc(col["title"]), items)

    legal = " · ".join(
        '<a href="%s">%s</a>' % (render.esc(l["href"]), render.esc(l["label"]))
        for l in site["footer"]["legal_links"]
    )

    return """</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-top">
      <div class="footer-brand">
        <span class="brand"><span class="pearl" aria-hidden="true"></span>Saede</span>
        <p>%s</p>
        <p class="footer-tagline">%s</p>
        <p style="margin-top:var(--s-3);font-size:var(--t-micro);opacity:.75">%s · %s</p>
      </div>
      %s
    </div>
    <p class="footer-disclaimer">%s</p>
    <div class="footer-legal">
      <span>&copy; %s Saede. %s</span>
      <span>%s</span>
    </div>
  </div>
</footer>
<script src="/assets/js/main.js?v=%s" defer></script>
</body>
</html>""" % (
        render.esc(site["footer"]["blurb"]),
        render.esc(site["brand"]["tagline"] or ""),
        render.esc(site["brand"]["meaning"]),
        render.esc(site["brand"]["made_in"]),
        cols,
        render.esc(site["disclaimer"]["footer"]),
        "2026",
        render.esc(site["brand"]["made_in"]),
        legal,
        asset_version("assets", "js", "main.js"),
    )


# --------------------------------------------------------------------------
# building
# --------------------------------------------------------------------------

def render_page(page, ctx):
    site = ctx["site"]
    html_out = head(site, page["meta"])
    if page["meta"].get("path") == "/":
        html_out += opening(site)
    html_out += header(site, page["meta"].get("path"))
    for sec in page["sections"]:
        fn = render.SECTIONS.get(sec["type"])
        if not fn:
            raise SystemExit(
                "Unknown section type %r in %s.\nAvailable types: %s"
                % (sec["type"], page["meta"]["path"], ", ".join(sorted(render.SECTIONS)))
            )
        html_out += fn(sec, ctx)
    return html_out + footer(site)


def render_article(article, ctx):
    site = ctx["site"]
    m = article["meta"]
    members = m.get("access") == "members"
    meta = {
        "title": "%s — Saede" % m["title"],
        "description": m["description"],
        "path": article["path"],
    }
    out = head(site, meta) + header(site, "/learn/")
    out += """<section class="page-hero"><div class="wrap">
        <p class="eyebrow"><a href="/learn/" style="color:inherit;text-decoration:none">Learn</a></p>
        <h1>%s</h1>
        <p class="lead">%s</p>
        <p style="margin-top:var(--s-5)"><span class="tag %s">%s</span>
           <span class="small muted" style="margin-left:.6rem">%s</span></p>
      </div></section>""" % (
        md.inline(m["title"]), md.inline(m["description"]),
        "tag--members" if members else "tag--open",
        "Members" if members else "Open to all",
        render.esc(m.get("reading_time", "")),
    )
    out += '<section class="section"><div class="wrap"><article class="prose reveal">%s</article></div></section>' % (
        md.render(article["body"])
    )
    out += render.render_disclaimer({}, ctx)
    return out + footer(site)


def write(path, html_out):
    """Write a page to dist/<path>/index.html.

    A path ending in .html is written as that exact file instead, which is how
    404.html gets to sit at the root where the host expects it.
    """
    rel = path.strip("/")
    if rel.endswith(".html"):
        target = os.path.join(DIST, rel)
    elif rel:
        target = os.path.join(DIST, rel, "index.html")
    else:
        target = os.path.join(DIST, "index.html")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(html_out)
    return target


def main():
    site = strip_readme(load_json("content", "site.json"))
    tokens = {
        "partner":       site["products"]["partner"]["name"],
        "partner_short": site["products"]["partner"]["short"],
        "hero":          site["products"]["hero"]["name"],
        "hero_short":    site["products"]["hero"]["short"],
    }

    ctx = {
        "site": site,
        "ingredients": strip_readme(substitute(load_json("content", "ingredients.json"), tokens)),
        "comparison": strip_readme(substitute(load_json("content", "comparison.json"), tokens)),
        "faq": strip_readme(substitute(load_json("content", "faq.json"), tokens)),
        "products_copy": strip_readme(substitute(load_json("content", "products.json"), tokens)),
        "articles": [],
        "pages": {},
    }

    # pages
    page_files = []
    for d in ("pages", "legal"):
        folder = os.path.join(ROOT, "content", d)
        for fn in sorted(os.listdir(folder)):
            if fn.endswith(".json"):
                page_files.append((fn[:-5], os.path.join(d, fn)))

    for name, relpath in page_files:
        ctx["pages"][name] = strip_readme(substitute(load_json("content", *relpath.split("/")), tokens))

    ctx["articles"] = substitute(load_articles(site), tokens)

    # clean output
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)

    written = []
    for name, page in ctx["pages"].items():
        written.append(write(page["meta"]["path"], render_page(page, ctx)))

    for a in ctx["articles"]:
        written.append(write(a["path"], render_article(a, ctx)))

    # static assets
    for folder in ("theme", "assets"):
        shutil.copytree(os.path.join(ROOT, folder), os.path.join(DIST, folder))

    # sitemap + robots
    base = site["brand"]["url"].rstrip("/")
    urls = [p["meta"]["path"] for p in ctx["pages"].values()
            if not p["meta"]["path"].endswith(".html")] + [a["path"] for a in ctx["articles"]]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join("  <url><loc>%s%s</loc></url>\n" % (base, u) for u in sorted(urls))
    sm += "</urlset>\n"
    with open(os.path.join(DIST, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sm)
    with open(os.path.join(DIST, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % base)

    # Cache headers for Netlify / Cloudflare Pages. The CSS and JS URLs carry a
    # content hash, so they can be cached forever; the HTML must always be
    # revalidated or visitors sit on an old page after you publish a change.
    with open(os.path.join(DIST, "_headers"), "w", encoding="utf-8") as f:
        f.write(
            "/*\n"
            "  Cache-Control: no-cache, must-revalidate\n"
            "  X-Content-Type-Options: nosniff\n"
            "  Referrer-Policy: strict-origin-when-cross-origin\n"
            "\n"
            "/theme/*\n"
            "  Cache-Control: public, max-age=31536000, immutable\n"
            "\n"
            "/assets/*\n"
            "  Cache-Control: public, max-age=31536000, immutable\n"
        )

    print("Built %d pages into dist/" % len(written))
    for w in sorted(written):
        print("  /" + os.path.relpath(w, DIST))

    signup = site.get("signup", {})
    if signup.get("provider") == "cloudflare":
        print("\nSignup: posting to the Cloudflare Pages Function at %s."
              % signup.get("endpoint", "/api/subscribe"))
        print("It needs a KV namespace bound as SIGNUPS in the Pages project settings.")
        print("Until that binding exists the form tells visitors to email instead.")
        print("Setup steps are at the top of functions/api/subscribe.js.")
    elif signup.get("provider") == "netlify":
        print("\nSignup: using Netlify Forms (form name %r)." % signup.get("form_name", "launch-list"))
        print("Addresses appear under Forms in the Netlify dashboard after the first deploy.")
    elif not signup.get("endpoint"):
        print("\nWarning: nothing is connected to the launch-list form.")
        print("Set signup.provider to \"netlify\", or signup.endpoint to your provider's URL,")
        print("in content/site.json. Until then the form stores nothing — and says so to the")
        print("visitor rather than claiming they are on a list.")

    if site["flags"].get("show_open_decisions"):
        print("\nNote: show_open_decisions is TRUE — TBD markers are visible on the site.")
        print("Set flags.show_open_decisions to false in content/site.json before launch.")


if __name__ == "__main__":
    main()
    if "--serve" in sys.argv:
        import functools
        import http.server
        import socketserver

        class H(http.server.SimpleHTTPRequestHandler):
            """Serves dist/ with the same cache policy as production:
            HTML always revalidates, fingerprinted assets cache hard.
            Without this you spend an afternoon looking at a stale page."""

            def end_headers(self):
                path = self.path.split("?")[0]
                if path.endswith("/") or path.endswith(".html"):
                    self.send_header("Cache-Control", "no-cache, must-revalidate")
                elif path.startswith(("/theme/", "/assets/")):
                    self.send_header("Cache-Control", "public, max-age=31536000, immutable")
                super().end_headers()

            def log_message(self, *a):
                pass

        # Bind the handler to dist/ by absolute path rather than chdir-ing
        # into it. A rebuild deletes and recreates dist/, which would leave a
        # chdir-ed server with a working directory that no longer exists and
        # every request failing until you restarted it.
        handler = functools.partial(H, directory=DIST)

        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("", 8000), handler) as httpd:
            print("\nServing http://localhost:8000  (ctrl-c to stop)")
            httpd.serve_forever()
