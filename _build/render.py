"""
Section renderers.

Each function here renders one 'type' from a page's content JSON.
To add a new kind of section: write a render_x(sec, ctx) function and
register it in SECTIONS at the bottom.
"""
import html
import md

# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------

def esc(s):
    return html.escape(str(s), quote=True) if s is not None else ""


def paras(items, cls=""):
    if not items:
        return ""
    c = ' class="%s"' % cls if cls else ""
    return "".join("<p%s>%s</p>" % (c, md.inline(p)) for p in items)


def eyebrow(text):
    return '<p class="eyebrow">%s</p>' % md.inline(text) if text else ""


def pearl(extra=""):
    return '<span class="pearl %s" aria-hidden="true"></span>' % extra


def btn(cta, ctx=None):
    """Render a button.

    A CTA marked "buy": true is a purchase action. While the product is not on
    sale yet it is swapped for the join-the-launch-list button, so no button
    on the site can ever promise something you cannot actually do.
    """
    if not cta:
        return ""
    label, href = cta["label"], cta["href"]
    if cta.get("buy") and ctx and ctx["site"]["flags"].get("launch_status") == "coming_soon":
        label, href = "Join the launch list", "/#join"
    style = cta.get("style", "primary")
    return '<a class="btn btn--%s" href="%s">%s</a>' % (esc(style), esc(href), md.inline(label))


def btn_row(ctas, ctx=None):
    if not ctas:
        return ""
    return '<div class="btn-row">%s</div>' % "".join(btn(c, ctx) for c in ctas)


def soon_pill(ctx, text="Coming soon"):
    """The marker that says the product is not on sale yet."""
    if ctx["site"]["flags"].get("launch_status") != "coming_soon":
        return ""
    return '<p class="soon-pill">%s%s</p>' % (pearl(), esc(text))


def attr_html(text):
    """Rendered markup, safe to sit inside a double-quoted HTML attribute.

    Used where JavaScript reads the attribute and writes it with innerHTML,
    so the tags must survive. Only the quote character needs escaping —
    md.inline has already escaped the source text.
    """
    return md.inline(text).replace('"', "&quot;")


def tbd(ctx, text):
    """A visible marker for an open decision. Hidden once the flag is off."""
    if not ctx["site"]["flags"].get("show_open_decisions"):
        return ""
    return '<span class="tbd" title="This is an open decision, not final content">%s</span>' % esc(text)


def section_open(sec, extra_class=""):
    """Open a section, carrying its mood-board texture if one is set.

    'mood' picks a texture from theme/textures.css: veil, silk, nacre,
    caustic, shore or glow. Moods are sequenced down each page so the site
    reads as one continuous surface catching light.
    """
    cls = "section"
    if sec.get("tint"):
        cls += " section--tint"
    if extra_class:
        cls += " " + extra_class
    mood = ' data-mood="%s"' % esc(sec["mood"]) if sec.get("mood") else ""
    return '<section class="%s"%s>' % (cls, mood)


def heading_block(sec, level="h2"):
    """The shared eyebrow + heading + intro paragraphs opening of a section."""
    out = eyebrow(sec.get("eyebrow"))
    if sec.get("heading"):
        out += "<%s>%s</%s>" % (level, md.inline(sec["heading"]), level)
    if sec.get("paragraphs"):
        out += '<div class="stack measure" style="margin-top:var(--s-5)">%s</div>' % paras(
            sec["paragraphs"], "lead"
        )
    return out


# --------------------------------------------------------------------------
# section types
# --------------------------------------------------------------------------

def render_hero(sec, ctx):
    belief = ""
    b = sec.get("belief")
    if b:
        belief = '<div class="hero-belief reveal">%s%s</div>' % (
            paras(b.get("paragraphs")),
            '<p class="statement">%s</p>' % md.inline(b["statement"]) if b.get("statement") else "",
        )
    plain = ('<p class="hero-plain">%s</p>' % md.inline(sec["plain"])) if sec.get("plain") else ""
    pill = soon_pill(ctx) if sec.get("coming_soon") else ""
    mood = ' data-mood="%s"' % esc(sec["mood"]) if sec.get("mood") else ""
    return """<section class="hero"%s>
  <div class="wrap">
    %s
    <h1 class="reveal">%s</h1>
    <div class="hero-sub stack reveal">%s</div>
    %s
    %s
    <div class="reveal">%s</div>
  </div>
</section>""" % (
        mood,
        pill,
        md.inline(sec["heading"]),
        paras(sec.get("paragraphs"), "lead"),
        belief,
        plain,
        btn_row(sec.get("ctas"), ctx),
    )


def render_page_hero(sec, ctx):
    mood = ' data-mood="%s"' % esc(sec["mood"]) if sec.get("mood") else ""
    return """<section class="page-hero"%s>
  <div class="wrap">
    %s<h1>%s</h1>%s
  </div>
</section>""" % (
        mood,
        eyebrow(sec.get("eyebrow")),
        md.inline(sec["heading"]),
        '<p class="lead">%s</p>' % md.inline(sec["lead"]) if sec.get("lead") else "",
    )


def render_prose(sec, ctx):
    open_tag = section_open(sec)
    if sec.get("anchor"):
        open_tag = open_tag[:-1] + ' id="%s">' % esc(sec["anchor"])
    out = open_tag + '<div class="wrap"><div class="measure reveal">'
    out += heading_block(sec)
    if sec.get("statement"):
        out += '<p class="statement" style="margin-top:var(--s-6)">%s</p>' % md.inline(sec["statement"])
    if sec.get("plain"):
        out += '<p class="hero-plain">%s</p>' % md.inline(sec["plain"])
    if sec.get("cta"):
        out += '<div class="btn-row" style="margin-top:var(--s-6)">%s</div>' % btn(sec["cta"], ctx)
    return out + "</div></div></section>"


def render_pillars(sec, ctx):
    cards = "".join(
        """<article class="card card--lift reveal">
             %s<h3>%s</h3><p>%s</p>
           </article>"""
        % (
            '<span class="card-num">%s</span>' % esc(c["num"]) if c.get("num") else "",
            md.inline(c["title"]),
            md.inline(c["body"]),
        )
        for c in sec.get("cards", [])
    )
    return """%s<div class="wrap">
      <div class="measure reveal">%s</div>
      <div class="grid grid--3" style="margin-top:var(--s-8)">%s</div>
    </div></section>""" % (section_open(sec), heading_block(sec), cards)


def render_cycle(sec, ctx):
    """The signature hub-and-spoke diagram.

    The nodes are real DOM text so they stay selectable and readable to a
    screen reader. On desktop CSS rotates them onto a ring using --angle;
    on mobile the same markup reflows to a plain grid.
    """
    hub = sec["hub"]
    nodes = sec.get("nodes", [])
    n = len(nodes) or 1
    node_html = ""
    for idx, node in enumerate(nodes):
        angle = (360 / n) * idx
        cls = "cycle-node" + (" cycle-node--seen" if node.get("seen") else "")
        node_html += (
            '<li class="%s" style="--angle:%.1fdeg"><span class="dot" aria-hidden="true"></span>%s</li>'
            % (cls, angle, md.inline(node["label"]))
        )

    hub_items = "".join("<li>%s</li>" % md.inline(i) for i in hub["items"])

    diagram = """<div class="cycle reveal">
      <div class="cycle-hub">
        %s
        <p class="cycle-hub-label">%s</p>
        <ul>%s</ul>
      </div>
      <ul class="cycle-nodes">%s</ul>
    </div>
    <p class="cycle-caption">%s</p>""" % (
        pearl(),
        md.inline(hub["label"]),
        hub_items,
        node_html,
        md.inline(sec.get("caption", "")),
    )

    statements = ""
    if sec.get("statements"):
        statements = (
            '<div class="measure reveal" style="margin:var(--s-9) auto 0;text-align:center">'
            + "".join('<p class="statement">%s</p>' % md.inline(s) for s in sec["statements"])
            + "</div>"
        )

    return """%s<div class="wrap">
      <div class="measure reveal">%s</div>
      %s
      %s
    </div></section>""" % (section_open(sec), heading_block(sec), diagram, statements)


def _product_card(kind, ctx, detailed=False):
    """One product card. 'kind' is 'hero' or 'partner'."""
    p = ctx["site"]["products"][kind]
    copy = ctx["products_copy"][kind]
    cls = "product product--" + ("hero" if kind == "hero" else "partner")

    name_tbd = tbd(ctx, "name TBD") if kind == "partner" else ""

    items = ""
    if detailed and copy.get("contains"):
        items = '<ul class="product-list">%s</ul>' % "".join(
            "<li>%s<span>%s</span></li>" % (pearl(), md.inline(i)) for i in copy["contains"]
        )

    return """<article class="%s reveal">
      <p class="product-role">%s%s</p>
      <h3 class="product-name">%s %s</h3>
      <p class="product-form">%s</p>
      <div class="product-desc stack">%s</div>
      %s
      <div class="product-foot">%s</div>
    </article>""" % (
        cls,
        pearl(),
        esc(p["role"]),
        md.inline(p["name"]),
        name_tbd,
        esc(p["form"]),
        paras(copy["desc"]),
        items,
        btn(copy.get("cta"), ctx) if detailed else "",
    )


def render_duo(sec, ctx):
    detailed = sec.get("detailed", False)
    together = ""
    t = sec.get("together")
    if t:
        together = """<div class="duo-together reveal">
          <p class="statement">%s</p>%s</div>""" % (
            md.inline(t["statement"]),
            '<div class="btn-row" style="margin-top:var(--s-5);justify-content:center">%s</div>' % btn(t["cta"], ctx)
            if t.get("cta") else "",
        )
    head = '<div class="measure reveal">%s</div>' % heading_block(sec) if sec.get("heading") else ""
    return """%s<div class="wrap">
      %s
      <div class="duo">%s%s</div>
      %s
    </div></section>""" % (
        section_open(sec),
        head,
        _product_card("hero", ctx, detailed),
        _product_card("partner", ctx, detailed),
        together,
    )


def render_ingredients(sec, ctx):
    data = ctx["ingredients"]
    show_globally = ctx["site"]["flags"].get("show_doses_globally", False)
    out = section_open(sec) + '<div class="wrap">'

    for group in data["groups"]:
        out += """<div class="measure reveal" style="margin-top:var(--s-8)">
            <h2>%s</h2><p class="lead" style="margin-top:var(--s-4)">%s</p></div>""" % (
            md.inline(group["title"]), md.inline(group["intro"])
        )
        cards = ""
        for ing in group["ingredients"]:
            dose = ""
            if show_globally and ing.get("show_dose"):
                dose = '<p class="ingredient-dose">%s%s</p>' % (
                    pearl(), md.inline(ing["dose"])
                )

            research = ""
            for r in ing.get("research", []):
                link = "https://pubmed.ncbi.nlm.nih.gov/%s/" % esc(r["pmid"])
                research += """<dd style="margin-top:var(--s-4)">
                    <a href="%s" target="_blank" rel="noopener noreferrer">Read the study on PubMed &rarr;</a>
                    <span class="cite">%s%s</span></dd>""" % (
                    link,
                    md.inline(r["citation"]),
                    " " + md.inline(r["note"]) if r.get("note") else "",
                )

            note = ""
            if ing.get("honest_note"):
                note = '<p class="ingredient-note">%s</p>' % md.inline(ing["honest_note"])

            which = ctx["site"]["products"][ing["in"]]["name"]
            cards += """<article class="ingredient reveal">
                <div class="ingredient-head">
                  <h3>%s</h3>
                  <span class="ingredient-latin">%s</span>
                </div>
                <p class="tag" style="margin-top:var(--s-3);width:max-content">In %s</p>
                %s
                <dl class="ingredient-why"><dt>Why it is here</dt><dd>%s</dd></dl>
                <dl class="ingredient-research"><dt>The research</dt>%s</dl>
                %s
              </article>""" % (
                md.inline(ing["name"]),
                md.inline(ing.get("latin") or ""),
                md.inline(which),
                dose,
                md.inline(ing["why"]),
                research,
                note,
            )
        out += '<div class="grid grid--2" style="margin-top:var(--s-6)">%s</div>' % cards

    if not show_globally:
        out += """<p class="small muted center" style="margin-top:var(--s-7)">
          Exact per-ingredient amounts are not published yet. %s</p>""" % tbd(ctx, "doses TBD")
    return out + "</div></section>"


def render_ingredients_preview(sec, ctx):
    return render_prose(sec, ctx)


def render_comparison(sec, ctx):
    """The cost of doing this yourself, as a statement rather than a basket.

    The itemised list is gone: seeing every ingredient priced as its own
    product made it look like you could buy them from us one at a time.
    The underlying research still lives in content/comparison.json.

    The headline figure is the monthly equivalent, not the shelf total.
    Several of those bottles last two or three months, so quoting the bigger
    number as "per month" would not be true.
    """
    c = ctx["comparison"]
    hero = ctx["site"]["products"]["hero"]["name"]
    partner = ctx["site"]["products"]["partner"]["name"]

    return """%s<div class="wrap">
      <div class="measure reveal">%s</div>
      <div class="ledger reveal">
        <div class="ledger-side">
          <p class="ledger-label">%s</p>
          <p class="ledger-figure">%s%s – %s%s%s</p>
          <p class="ledger-note">%s</p>
        </div>
        <div class="ledger-divider" aria-hidden="true"><span class="pearl pearl--glow"></span></div>
        <div class="ledger-side ledger-side--ours">
          <p class="ledger-label">%s + %s</p>
          <p class="ledger-figure">%s%s</p>
          <p class="ledger-note">%s</p>
        </div>
      </div>
      <p class="ledger-line reveal">%s</p>
      <p class="ledger-foot reveal">%s</p>
    </div></section>""" % (
        section_open(sec),
        heading_block(sec),
        md.inline(c["theirs_label"]),
        esc(c["currency"]), esc(c["normalised_low"]),
        esc(c["currency"]), esc(c["normalised_high"]), esc(c.get("theirs_suffix", "")),
        md.inline(c["theirs_note"]),
        md.inline(hero), md.inline(partner),
        esc(c["currency"]), esc(c["saede_price"]),
        md.inline(c["saede_note"]),
        md.inline(c["line"]),
        md.inline(c["footnote"]),
    )


def _timeline(steps):
    out = ""
    for s in steps:
        out += """<article class="tl-step reveal">
            <div class="tl-marker">%s<span class="tl-when">%s</span></div>
            <h3>%s</h3><p>%s</p>
          </article>""" % (
            pearl("pearl--glow"), md.inline(s["when"]), md.inline(s["title"]), md.inline(s["body"])
        )
    return '<div class="timeline">%s</div>' % out


def render_timeline(sec, ctx):
    honesty = ""
    h = sec.get("honesty")
    if h:
        honesty = """<div class="honesty-note measure reveal" style="margin-inline:auto">
            <p class="statement">%s</p><p style="margin-top:var(--s-4)">%s</p></div>""" % (
            md.inline(h["statement"]), md.inline(h["body"])
        )
    return """%s<div class="wrap">
      <div class="measure reveal">%s</div>%s%s
    </div></section>""" % (
        section_open(sec), heading_block(sec), _timeline(sec["steps"]), honesty
    )


def render_timeline_full(sec, ctx):
    """The timeline on /how-it-works/, reusing the homepage's copy verbatim
    so the two pages can never drift apart."""
    home = ctx["pages"]["home"]
    tl = next(s for s in home["sections"] if s["type"] == "timeline")
    merged = dict(tl)
    merged["tint"] = sec.get("tint", False)
    merged["eyebrow"] = "The timeline"
    return render_timeline(merged, ctx)


def render_plans(sec, ctx):
    plans = ""
    for p in sec["plans"]:
        cls = "plan"
        if p.get("featured"):
            cls += " plan--featured"
        if p.get("quiet"):
            cls += " plan--quiet"
        feats = "".join("<li>%s<span>%s</span></li>" % (pearl(), md.inline(f)) for f in p.get("features", []))
        plans += """<article class="%s reveal">
            %s
            <h3>%s</h3>
            <p class="plan-price">%s%s %s <small>%s</small></p>
            <p class="plan-sub">%s</p>
            <ul>%s</ul>
            <div class="plan-foot">%s</div>
          </article>""" % (
            cls,
            '<span class="plan-badge">%s</span>' % md.inline(p["badge"]) if p.get("badge") else "",
            md.inline(p["name"]),
            esc(p["price_unit"]), esc(p["price"]), tbd(ctx, "price TBD"), md.inline(p["price_sub"]),
            md.inline(p["sub"]),
            feats,
            btn(p["cta"], ctx),
        )

    terms = ""
    t = sec.get("eu_terms")
    if t:
        terms = """<div class="eu-terms reveal">
            <h4>%s</h4><ul>%s</ul></div>""" % (
            md.inline(t["title"]),
            "".join("<li>%s</li>" % md.inline(i) for i in t["items"]),
        )

    return """%s<div class="wrap">
      %s<div class="plans">%s</div>%s
    </div></section>""" % (
        section_open(sec),
        '<div class="measure reveal">%s</div>' % heading_block(sec) if sec.get("heading") else "",
        plans, terms,
    )


def render_membership_preview(sec, ctx):
    return render_prose(sec, ctx)


def render_learn_preview(sec, ctx):
    return render_prose(sec, ctx)


def render_learn_index(sec, ctx):
    cards = ""
    for a in ctx["articles"]:
        members = a["meta"].get("access") == "members"
        cards += """<a class="article-card reveal" href="%s">
            <div class="article-meta" style="margin:0 0 var(--s-3);padding:0">
              <span class="tag %s">%s</span>
            </div>
            <h3>%s</h3>
            <p>%s</p>
            <div class="article-meta">
              <span class="small muted">%s</span>
              <span class="btn--quiet small">Read &rarr;</span>
            </div>
          </a>""" % (
            esc(a["path"]),
            "tag--members" if members else "tag--open",
            "Members" if members else "Open to all",
            md.inline(a["meta"]["title"]),
            md.inline(a["meta"]["description"]),
            esc(a["meta"].get("reading_time", "")),
        )
    return """%s<div class="wrap">
      <div class="grid grid--3">%s</div>
    </div></section>""" % (section_open(sec), cards)


def render_faq(sec, ctx):
    items = ctx["faq"]["items"]
    if sec.get("featured_only"):
        items = [i for i in items if i.get("featured")]
    body = ""
    for i in items:
        body += """<details>
            <summary>%s</summary>
            <div class="faq-answer">%s</div>
          </details>""" % (md.inline(i["q"]), paras(i["a"]))
    cta = '<div class="btn-row" style="margin-top:var(--s-6)">%s</div>' % btn(sec["cta"], ctx) if sec.get("cta") else ""
    return """%s<div class="wrap">
      <div class="measure reveal">%s</div>
      <div class="faq measure reveal">%s</div>%s
    </div></section>""" % (section_open(sec), heading_block(sec), body, cta)


def render_badges(sec, ctx):
    out = ""
    for b in ctx["site"]["badges"]:
        inner = """%s<p class="t">%s</p><span class="s">%s</span>""" % (
            pearl(), md.inline(b["title"]), md.inline(b["sub"])
        )
        if b.get("href"):
            out += '<a class="badge" data-status="%s" href="%s">%s</a>' % (esc(b["status"]), esc(b["href"]), inner)
        else:
            out += '<div class="badge" data-status="%s">%s</div>' % (esc(b["status"]), inner)

    pending = any(b["status"] == "pending" for b in ctx["site"]["badges"])
    note = ""
    if pending:
        note = """<p class="small muted center" style="margin-top:var(--s-5)">
          Shown dashed because they are not confirmed yet. We will publish the
          certificates themselves here, not just the claim. %s</p>""" % tbd(ctx, "awaiting manufacturer")

    return """%s<div class="wrap">
      <div class="measure reveal">%s</div>
      <div class="badges reveal">%s</div>%s
    </div></section>""" % (section_open(sec), heading_block(sec), out, note)


def render_teaser(sec, ctx):
    return """%s<div class="wrap">
      <div class="teaser reveal">
        <blockquote><p>%s</p><cite>%s</cite></blockquote>
        <div>%s%s<div class="stack">%s</div><div class="btn-row" style="margin-top:var(--s-6)">%s</div></div>
      </div>
    </div></section>""" % (
        section_open(sec),
        md.inline(sec["quote"]),
        md.inline(sec["cite"]),
        eyebrow(sec.get("eyebrow")),
        "",
        paras(sec.get("paragraphs")),
        btn(sec.get("cta"), ctx),
    )


def render_story(sec, ctx):
    out = section_open(sec) + '<div class="wrap"><div class="story-body reveal">'
    out += paras(sec.get("paragraphs"))
    if sec.get("statement"):
        out += '<p class="statement">%s</p>' % md.inline(sec["statement"])
    out += paras(sec.get("paragraphs_2"))
    if sec.get("statement_2"):
        out += '<p class="statement">%s</p>' % md.inline(sec["statement_2"])
    out += paras(sec.get("paragraphs_3"))
    if sec.get("sign"):
        out += """<div class="story-sign">%s<div>
            <p class="name">%s</p><p class="role">%s</p></div></div>""" % (
            pearl("pearl--lg pearl--glow"),
            md.inline(sec["sign"]["name"]),
            md.inline(sec["sign"]["role"]),
        )
    return out + "</div></div></section>"


def render_legal(sec, ctx):
    note = ""
    if sec.get("note") and ctx["site"]["flags"].get("show_open_decisions"):
        note = """<div class="disclaimer" style="margin-bottom:var(--s-7)">%s
            <p><strong>Draft.</strong> %s</p></div>""" % (pearl(), md.inline(sec["note"]))
    return """%s<div class="wrap">
      <div class="prose reveal">%s%s</div>
    </div></section>""" % (
        section_open(sec), note, md.render("\n\n".join(sec["body"]))
    )


def render_cta(sec, ctx):
    mood = ' data-mood="%s"' % esc(sec["mood"]) if sec.get("mood") else ""
    cloud = ""
    cls = "cta-band"
    if sec.get("cloud"):
        cls += " cta-band--cloud"
        cloud = ('<div class="cloudscape" aria-hidden="true">'
                 '<img src="/assets/img/cloudscape-1200.jpg" '
                 'srcset="/assets/img/cloudscape-1200.jpg 1200w, '
                 '/assets/img/cloudscape-1900.jpg 1900w" sizes="100vw" '
                 'alt="" loading="lazy" decoding="async" width="1900" height="1178"></div>')
    return """<section class="%s"%s>
      %s
      <span class="glints" aria-hidden="true"></span>
      <div class="wrap reveal halo">
        <h2>%s</h2>
        <div class="stack">%s</div>
        <div style="margin-top:var(--s-7)">%s</div>
      </div>
    </section>""" % (
        cls,
        mood,
        cloud,
        md.inline(sec["heading"]),
        paras(sec.get("paragraphs"), "lead"),
        btn_row(sec.get("ctas"), ctx),
    )


def render_disclaimer(sec, ctx):
    return """<section class="section" style="padding-top:0">
      <div class="wrap"><div class="disclaimer measure" style="margin-inline:auto">%s
        <p>%s</p></div></div>
    </section>""" % (pearl(), md.inline(ctx["site"]["disclaimer"]["short"]))


HONEYPOT = ('<p class="visually-hidden" aria-hidden="true">'
            '<label>Leave this field empty <input name="bot-field" tabindex="-1" '
            'autocomplete="off"></label></p>')


def render_signup(sec, ctx):
    """The launch-list email capture.

    No endpoint is connected yet, so the form validates the address, tells the
    visitor plainly that it has been noted, and stores nothing. The note under
    the form never claims more than that.
    """
    c = ctx["site"]["signup"]
    provider = c.get("provider")
    endpoint = c.get("endpoint")
    form_name = c.get("form_name", "launch-list")

    # Three ways the form can be wired, chosen by signup.provider:
    #   "netlify"    Netlify Forms. Needs its attributes in the deployed HTML,
    #                because Netlify parses them at deploy time.
    #   "cloudflare" Posts to the Pages Function in functions/api/subscribe.js.
    #   anything else with signup.endpoint set: posts there.
    # With none of them set the form stores nothing and says so.
    action, hidden, extra = "", "", ""
    live = "false"

    if provider == "netlify":
        action = (' name="%s" method="post" data-netlify="true" netlify-honeypot="bot-field"'
                  % esc(form_name))
        hidden = ('<input type="hidden" name="form-name" value="%s">' % esc(form_name)) + HONEYPOT
        extra = ' data-ajax="/"'
        live = "true"
    elif provider == "cloudflare":
        target = endpoint or "/api/subscribe"
        action = ' action="%s" method="post"' % esc(target)
        hidden = HONEYPOT
        extra = ' data-ajax="%s"' % esc(target)
        live = "true"
    elif endpoint:
        action = ' action="%s" method="post"' % esc(endpoint)
        hidden = HONEYPOT
        extra = ' data-ajax="%s"' % esc(endpoint)
        live = "true"

    connected = live == "true"

    # With nothing connected the form must not claim to have stored anything.
    success = c["success"] if connected else c.get("success_no_endpoint", c["success"])

    return """%s<div class="wrap">
      <div class="signup center reveal" id="join">
        <span class="glints" aria-hidden="true"></span>
        <div class="signup-inner halo">
          %s
          <h2>%s</h2>
          <div class="stack" style="margin-top:var(--s-5)">%s</div>
          <form class="signup-form" data-signup data-live="%s"%s
                data-success="%s" data-error="%s"%s novalidate>
            %s<label class="signup-field">
              <span class="visually-hidden">Your email address</span>
              <input type="email" name="email" autocomplete="email" required
                     placeholder="%s" data-signup-input>
            </label>
            <button class="btn btn--primary" type="submit">%s</button>
          </form>
          <p class="signup-status" role="status" aria-live="polite" data-signup-status></p>
          <p class="signup-note">%s</p>
        </div>
      </div>
    </div></section>""" % (
        section_open(sec),
        soon_pill(ctx, md.inline(c["eyebrow"])),
        md.inline(c["heading"]),
        paras(c["paragraphs"], "lead"),
        live, action,
        attr_html(success), esc(c["error"]), extra,
        hidden,
        esc(c["placeholder"]),
        md.inline(c["button"]),
        md.inline(c["note"]),
    )


def render_account(sec, ctx):
    """The account area. Built around leaving quickly, not around staying."""
    cards = ""
    for card in sec["cards"]:
        cls = "account-card account-card--cancel" if card.get("cancel") else "account-card"
        steps = ""
        if card.get("steps"):
            steps = '<ol class="account-steps">%s</ol>' % "".join(
                "<li>%s</li>" % md.inline(x) for x in card["steps"]
            )
        cards += """<article class="%s reveal">
            <h3>%s%s</h3>
            <div class="stack">%s</div>
            %s
            %s
          </article>""" % (
            cls, pearl(), md.inline(card["title"]),
            paras(card.get("paragraphs")),
            steps,
            btn(card["cta"], ctx) if card.get("cta") else "",
        )

    promise = ""
    if sec.get("promise"):
        pr = sec["promise"]
        promise = """<div class="promise measure reveal" style="margin-inline:auto">
            <p class="statement">%s</p>
            <ul>%s</ul>
          </div>""" % (
            md.inline(pr["statement"]),
            "".join("<li>%s<span>%s</span></li>" % (pearl(), md.inline(i)) for i in pr["items"]),
        )

    return """%s<div class="wrap">
      <div class="measure reveal">%s</div>
      <div class="account-grid">%s</div>
      %s
    </div></section>""" % (section_open(sec), heading_block(sec), cards, promise)


def render_member_gate(sec, ctx):
    """What sits behind membership. Depth and detail, not personalisation."""
    return """%s<div class="wrap">
      <div class="measure reveal">%s</div>
      <div class="member-gate measure reveal" style="margin-inline:auto">
        %s
        <h3>%s</h3>
        <div class="stack">%s</div>
        %s
      </div>
    </div></section>""" % (
        section_open(sec), heading_block(sec),
        pearl("pearl--glow"),
        md.inline(sec["gate"]["title"]),
        paras(sec["gate"]["paragraphs"]),
        btn_row(sec["gate"].get("ctas"), ctx),
    )


def render_hero_image(sec, ctx):
    """The front page: sunlit water as the ray of light, the name over it.

    The <h1> carries both the wordmark and the line beneath it, so the page
    has one heading that actually says what it is — search engines and screen
    readers get "Saede — for you who has tried everything" rather than five
    loose letters.
    """
    img = sec["image"]

    # The still is the real hero: it paints immediately and is what everyone
    # sees first. The film is layered over it and only fades in once it can
    # actually play, so a slow connection, a phone, reduced motion or data
    # saver all simply keep the photograph. main.js decides.
    video = ""
    if sec.get("video"):
        video = ('<video class="hero-img-video" data-hero-video muted loop playsinline '
                 'preload="none" disablepictureinpicture aria-hidden="true" '
                 'data-src="%s"></video>' % esc(sec["video"]))

    cue = ""
    if sec.get("scroll_cue"):
        cue = ('<a class="scroll-cue" href="%s">%s<span class="line" aria-hidden="true"></span></a>'
               % (esc(sec["scroll_cue"]["href"]), md.inline(sec["scroll_cue"]["label"])))

    return """<section class="hero-img"%s>
  <div class="hero-img-media">
    <picture>
      <source media="(max-width: 700px)" srcset="%s 800w, %s 1280w" sizes="100vw">
      <img src="%s" srcset="%s 1600w, %s 2200w" sizes="100vw"
           alt="%s" fetchpriority="high" decoding="async" width="2200" height="1238">
    </picture>%s
  </div>
  <div class="hero-img-inner wrap halo">
    <h1>
      <span class="wordmark">%s</span>
      <span class="wordmark-line">%s</span>
    </h1>
    %s
  </div>
  %s
</section>""" % (
        ' data-mood="%s"' % esc(sec["mood"]) if sec.get("mood") else "",
        esc(img["mobile_800"]), esc(img["mobile_1280"]),
        esc(img["wide_1600"]), esc(img["wide_1600"]), esc(img["wide_2200"]),
        esc(img["alt"]),
        video,
        md.inline(sec["wordmark"]).upper(),
        md.inline(sec["line"]),
        btn_row(sec.get("ctas"), ctx),
        cue,
    )


def render_plate(sec, ctx):
    """A product photograph beside its copy. The editorial layout."""
    img = sec["image"]
    items = ""
    if sec.get("items"):
        items = '<ul class="plate-list">%s</ul>' % "".join(
            "<li>%s<span>%s</span></li>" % (pearl(), md.inline(i)) for i in sec["items"]
        )
    cls = "plate plate--flip" if sec.get("flip") else "plate"
    return """%s<div class="wrap">
      <div class="%s reveal">
        <figure class="plate-media">
          <img src="%s" srcset="%s 900w, %s 1400w" sizes="(min-width: 900px) 50vw, 92vw"
               alt="%s" loading="lazy" decoding="async" width="%s" height="%s">
        </figure>
        <div class="plate-body">
          %s
          %s
          %s
        </div>
      </div>
    </div></section>""" % (
        section_open(sec), cls,
        esc(img["src_900"]), esc(img["src_900"]), esc(img["src_1400"]),
        esc(img["alt"]), esc(img["w"]), esc(img["h"]),
        heading_block(sec),
        items,
        btn_row(sec.get("ctas"), ctx),
    )


def render_showcase(sec, ctx):
    """One wide product photograph, floating on its own light."""
    img = sec["image"]
    head = ""
    if sec.get("heading"):
        head = '<div class="measure center reveal" style="margin:0 auto var(--s-8)">%s</div>' % heading_block(sec)
    return """%s<div class="wrap showcase">
      %s
      <figure class="showcase-figure reveal">
        <img src="%s" srcset="%s 900w, %s 1400w, %s 2000w"
             sizes="(min-width: 1200px) 1140px, 94vw"
             alt="%s" loading="lazy" decoding="async" width="2000" height="1116">
        %s
      </figure>
    </div></section>""" % (
        section_open(sec),
        head,
        esc(img["src_1400"]), esc(img["src_900"]), esc(img["src_1400"]), esc(img["src_2000"]),
        esc(img["alt"]),
        "<figcaption>%s</figcaption>" % md.inline(sec["caption"]) if sec.get("caption") else "",
    )


def render_pullquote(sec, ctx):
    """One line, made impossible to miss.

    Deliberately plain markup: a kicker, a large line, an optional sentence
    under it, and optionally three short columns. Kept for the two moments on
    the front page where a reader scanning the page has to land on something.
    """
    fronts = ""
    if sec.get("fronts"):
        fronts = '<div class="pullquote-fronts">%s</div>' % "".join(
            '<div class="pullquote-front"><h3>%s</h3><p>%s</p></div>'
            % (md.inline(f["title"]), md.inline(f["body"]))
            for f in sec["fronts"]
        )
    cls = "pullquote pullquote--billboard" if sec.get("billboard") else "pullquote"
    return """<section class="%s"%s>
      <div class="wrap reveal">
        %s
        <p class="pullquote-line">%s</p>
        %s
        %s
      </div>
    </section>""" % (
        cls,
        ' data-mood="%s"' % esc(sec["mood"]) if sec.get("mood") else "",
        '<span class="pullquote-kicker">%s%s</span>' % (pearl(), md.inline(sec["kicker"]))
        if sec.get("kicker") else "",
        md.inline(sec["line"]),
        '<p class="pullquote-sub">%s</p>' % md.inline(sec["sub"]) if sec.get("sub") else "",
        fronts,
    )


SECTIONS = {
    "hero": render_hero,
    "page_hero": render_page_hero,
    "prose": render_prose,
    "pillars": render_pillars,
    "cycle": render_cycle,
    "duo": render_duo,
    "ingredients": render_ingredients,
    "ingredients_preview": render_ingredients_preview,
    "comparison": render_comparison,
    "timeline": render_timeline,
    "timeline_full": render_timeline_full,
    "plans": render_plans,
    "membership_preview": render_membership_preview,
    "learn_preview": render_learn_preview,
    "learn_index": render_learn_index,
    "faq": render_faq,
    "badges": render_badges,
    "teaser": render_teaser,
    "story": render_story,
    "legal": render_legal,
    "cta": render_cta,
    "disclaimer": render_disclaimer,
    "signup": render_signup,
    "account": render_account,
    "member_gate": render_member_gate,
    "hero_image": render_hero_image,
    "plate": render_plate,
    "showcase": render_showcase,
    "pullquote": render_pullquote,
}
