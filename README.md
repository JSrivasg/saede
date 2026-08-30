# Saede — website

A launch site for Saede: a root-cause, full-dose women's health brand whose first
system is hair. Built so that new concern areas (PCOS, gut, metabolic health) slot
in without a rebuild, and so that a non-developer can change any word on the site.

**Read [`OPEN-DECISIONS.md`](OPEN-DECISIONS.md) and [`COPY-REVIEW.md`](COPY-REVIEW.md)
before publishing.** They list every placeholder and every line that needs a
regulatory reviewer.

---

## Deploying

The site is a folder of static files. Any static host works.

**Cloudflare Pages** (current setup). Connect the GitHub repo and use:

| Setting | Value |
|---|---|
| Framework preset | None |
| Build command | `python3 build.py` |
| Build output directory | `dist` |
| Root directory | *(leave blank)* |

Do not commit `dist/` or a zip of it — `.gitignore` excludes both. Cloudflare runs
the build itself and needs the source files.

`functions/api/subscribe.js` is picked up automatically and handles the launch-list
signups; it needs one KV binding, documented at the top of that file.
`dist/_headers` sets the cache policy and is understood by Cloudflare Pages as-is.

**Netlify** also works: `netlify.toml` is already configured, and switching
`signup.provider` to `"netlify"` in `content/site.json` moves the form to Netlify Forms.

## Running it

There is no install step, no `npm`, and no dependencies. Python 3 is all you need,
and it is already on every Mac.

```bash
python3 build.py --serve
```

Then open <http://localhost:8000>. To build without serving:

```bash
python3 build.py
```

The site is written to `dist/`, which is what you upload to a host. Any static host
works — Netlify, Cloudflare Pages, Vercel, or plain S3. There is no server to run.

> **Why not Astro or Next.js?** Node is not installed on this machine, and a
> dependency-free builder will still work in five years with no `npm audit` and no
> broken lockfile. The content is plain JSON and Markdown, so moving to a framework
> later is a porting job on the templates only — the words come across untouched.

---

## Where everything lives

```
content/          the words — this is the only folder most edits touch
  site.json         brand-wide settings: nav, product names, footer, flags
  products.json     the two product descriptions
  ingredients.json  ingredient cards + verified research links
  comparison.json   the cost-comparison table (all figures are placeholders)
  faq.json          questions and answers
  pages/            one file per page, section by section
  legal/            contact, privacy, terms, shipping, subscription terms
  learn/            Learn hub articles, as Markdown

theme/            the design system
  tokens.css        colour, type, space — change a value here, it changes everywhere
  base.css          reset, typography, layout primitives
  components.css    every component

assets/           JavaScript and images
_build/           the generator (md.py, render.py)
build.py          run this to build
dist/             the output — never edit by hand, it is overwritten every build
```

---

## Common edits

### Turn the opening sequence off
`flags.show_opening` in `content/site.json` → `false`. It plays once per browsing
session, is always skippable, is skipped automatically for anyone who has asked for
reduced motion, and never appears at all with JavaScript disabled. The film itself
is `assets/video/opening.mp4` — replace that file to change it.

### Connect the launch-list form
`signup.endpoint` in `content/site.json`. While it is `null` the form validates the
address but stores nothing, and **says so plainly to the visitor** rather than
claiming they are on a list. The build prints a warning every time it runs until you
set it. Point it at a Mailchimp / Kit / Klaviyo / Buttondown form URL.

### Switch from "coming soon" to selling
`flags.launch_status` in `content/site.json` → `"live"`. That single change swaps the
navigation button from *Join the list* to *Start your Saede*, restores every purchase
button that is currently redirected to the launch list, and removes the COMING SOON
markers.

### Change the front-page photograph
Replace the files in `assets/img/` and rebuild:

| File | Used for |
|---|---|
| `hero-water-wide-1600/2200.jpg` | the front page on desktop |
| `hero-water-800/1280.jpg` | the front page on phones (a taller crop) |
| `duo-cream-900/1400/2000.jpg` | the wide product plate |
| `duo-silk-900/1400.jpg` | the product photograph beside copy |
| `clouds-1200.jpg` | the closing image on the story page |

`tools/images.py` regenerates every size from the originals — edit the paths at the
top of that file and run `python3 tools/images.py`. It also strips app chrome from
screenshots, which is what the crop boxes in it are for.

### Change any wording
Find it in `content/` and edit it. Everything is plain text. Three bits of markup
work inside any string:

| You write | You get |
|---|---|
| `**important**` | **important** |
| `[the link text](/some-page/)` | a link |
| `{{hero}}` / `{{hero_short}}` | Saede Hero / Hero |
| `{{partner}}` / `{{partner_short}}` | Saede Support / Support |

### Rename a product
Change the `name` and `short` fields under `products` in `content/site.json`.
Every page, title and meta description updates on the next build — that is what the
`{{hero}}` / `{{partner}}` tokens are for.

> Note: your manufacturer spec v4 calls these **Core** and **Restore**. The site uses
> **Hero** and **Support**, matching the packaging renders. Keep the two in step when
> you send the next revision to the manufacturer.

### Change a price
Membership prices live in `content/pages/membership.json`.
Cost-comparison figures live in `content/comparison.json`.

### Hide the exact ingredient doses
They are currently **shown** — all twenty, from the Duo Spec v4.

1. `flags.show_doses_globally` in `content/site.json` → `false` hides them all
2. `show_dose` on a single ingredient in `content/ingredients.json` → `false` hides one

Hiding a dose never breaks the card layout.

### Hide the yellow TBD markers before launch
Set `flags.show_open_decisions` to `false` in `content/site.json`. Every marker
across the site disappears in one edit. The build prints a reminder while it is on.

### Add a Learn article
Drop a `.md` file into `content/learn/`. It appears on `/learn/` automatically.

```markdown
---
title: "Your title"
description: "One sentence for the card and the search result."
access: public      # or: members
order: 7            # controls position in the list
reading_time: "5 min"
---

Your article. Use ## for headings, - for lists, **bold**, and [links](/faq/).

:::medical
Text in here renders as the "please also see a doctor" call-out.
:::
```

### Add a new concern area (PCOS, gut, metabolic)
1. Copy `content/pages/concerns-hair.json` to e.g. `concerns-pcos.json`.
2. Change `meta.path` to `/concerns/pcos/` and rewrite the copy.
3. In `content/site.json`, give the PCOS entry in `nav` a `href` instead of `null`,
   and do the same in `footer.columns`.

Until an entry has an `href` it renders as a greyed-out "In development" line —
present, but never announced with a date we cannot keep.

---

## Page sections

Each page in `content/pages/` is a list of `sections`. Reorder the list to reorder
the page; delete an entry to remove that section. Add `"tint": true` to any section
to give it the alternating background.

| `type` | What it renders |
|---|---|
| `hero` | Homepage hero with the belief passage and plain subline |
| `page_hero` | The smaller interior-page header |
| `prose` | Heading, paragraphs, optional statement line and button |
| `pillars` | Three cards in a row |
| `cycle` | The interconnected-cycle diagram |
| `duo` | The two product cards (`"detailed": true` adds ingredient lists) |
| `ingredients` | Every ingredient card, from `ingredients.json` |
| `comparison` | The cost-comparison table |
| `timeline` | The three-stage results timeline |
| `timeline_full` | The same timeline, reusing the homepage copy so they cannot drift |
| `plans` | Membership options plus the EU disclosure block |
| `learn_index` | Every Learn article as a card |
| `faq` | Questions (`"featured_only": true` shows only the homepage set) |
| `badges` | Trust badges from `site.json` |
| `teaser` | The founder-story teaser |
| `story` | The long-form founder story |
| `legal` | Long-form legal text |
| `cta` | The full-width call-to-action band |
| `signup` | The launch-list email capture |
| `account` | The account cards, including the cancel flow |
| `member_gate` | What sits inside membership |
| `disclaimer` | The food-supplement disclaimer |

Any section can also carry a **`mood`**, which paints one of the mood-board textures
behind it: `veil`, `silk`, `nacre`, `caustic`, `shore` or `glow`. They are sequenced
down each page so scrolling moves through the board rather than repeating one effect.
The textures are in `theme/textures.css` — pure gradients, no image files.

If you use a `type` that does not exist, the build stops and tells you the valid
options rather than producing a broken page.

---

## The design system

Everything visual is driven by `theme/tokens.css`. Change a token and the whole
site follows.

The palette is powdery and pearlescent, and leans on the pinks from your cloud
reference — `--cloud-rose`, `--cloud-pink`, `--cloud-veil`, `--cloud-amber` — over
ivory and pearl-white bases, with nacre gradients through blush, peach, lilac, mint
and pale gold. A grain overlay gives the matte, non-digital finish. The glowing pearl
(`.pearl`) is the brand signature and appears as the logo mark, list bullets and
section accents.

`theme/textures.css` is the mood board translated into layered CSS — shell nacre,
silk folds, water caustics, the shore, sheer veils and rays of light. No image files,
nothing to download.

**There are no section backgrounds.** A single tall gradient runs behind the whole
document on `<main>`, and every section is transparent over it, so the colour drifts
from warm to cool and back with no visible edge anywhere. Sections used to paint their
own blocks, which drew a line across the page at every boundary. If you add a section
that needs its own colour, fade it with a mask rather than painting a block — see how
`.cta-band` and `.page-hero` do it.

**Type.** Headlines and the wordmark are **Playfair Display** — the same editorial,
high-contrast feeling as the reference wordmark, but with strokes sturdy enough to
hold up at heading sizes and on a phone. (Bodoni was tried first; its hairlines are
beautiful at poster size and vanish everywhere else.) Body text is **Mulish**, a soft
humanist sans with open shapes, easy to read over long stretches. Both have full
system fallbacks if the webfonts fail to load.

**The wordmark is set in capitals with wide tracking everywhere it appears** — header,
opening sequence and front page — so it reads as one consistent mark, matching the
lettering on the packaging. Tracking is one token: `--track-wordmark` in
`theme/tokens.css`.

**Colour contrast:** every text colour has been checked to at least 4.5:1 against
every background it sits on. If you change `--plum-mute` or `--cta`, re-check them —
they were the two that needed adjusting, and they have the least headroom.

---

## Accessibility

- Semantic HTML: real headings, `<nav>`, `<main>`, `<footer>`, `<details>` for the FAQ.
- Skip link, visible focus rings, `aria-current` on the active nav item.
- The cycle diagram is real DOM text, not SVG labels, so it is selectable,
  translatable and readable by a screen reader.
- `prefers-reduced-motion` disables every animation.
- The site is fully readable with JavaScript disabled. JS only adds the mobile
  menu, the dropdown and the fade-in.

## Caching and deployment

Upload `dist/`. The CSS and JS URLs carry a content hash, so a change reaches
visitors immediately instead of sitting behind a cached copy. `dist/_headers` sets the
matching policy for Netlify and Cloudflare Pages: HTML always revalidates, fingerprinted
assets cache for a year. On another host, apply the same two rules by hand.

`python3 build.py --serve` uses the same policy locally, so what you see matches
production. It also keeps serving correctly while you rebuild in another terminal.

## Performance

No frameworks, no trackers, no dependencies. The only external request is Google
Fonts. Total CSS is around 45 KB and JS around 6 KB, both uncompressed, plus the
1.4 MB opening film, which only loads on the homepage.
