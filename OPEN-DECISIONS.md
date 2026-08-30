# Open decisions

Everything on the site that is not yet final. Each item says where to change it.

While `flags.show_open_decisions` is `true` in `content/site.json`, unfinished items
render with a visible yellow marker so nobody can mistake a placeholder for a
decision. **Set that flag to `false` before launch** — it removes every marker in
one edit.

---

## Settled since the last round

- **The powder is named Saede Support.** Applied everywhere.
- **Doses are published.** All twenty, from *Saede Duo Spec v4*.
- **The cost comparison is real.** Figures from *Saede ingredient cost.docx*, and the
  arithmetic checks out (€205.14 + €181.61 = €386.75 ≈ €387).
- **There is a tagline**: *Every ray finds its way*, taken from the header of your own
  spec documents. It appears in the opening, the footer and the social cards.
- **Skin** has been added to Concerns, alongside PCOS, Gut and Metabolic health.

---

## 0. The front page now names androgenetic alopecia

At your direction the site leads with androgenetic alopecia and DHT, and positions
Saede as a complete system formulated around them. This is the biggest regulatory
change in the project and it is flagged at the top of `COPY-REVIEW.md` for your
lawyer. The copy stays on educational ground and carries a visible medical line, but
naming a condition on a supplement's front page is a judgement call that needs a
professional sign-off for Spain before launch.

## 0b. The front-page film is 7.9 MB

There is no video encoder on this machine, so it ships at its original size. It is
handled carefully — the photograph paints instantly and the film only fades in once
it can play, and it is skipped entirely on phones, on data saver, and under reduced
motion — but it is still a large file for anyone on desktop.

Worth compressing before launch. Roughly: `ffmpeg -i hero-water.mp4 -vf scale=1600:-2
-c:v libx264 -crf 26 -preset slow -an -movflags +faststart hero-water.mp4` should take
it under 2 MB with no visible loss on this kind of footage. A WebM alongside it would
help again.

## 1. Product names disagree with the manufacturer spec

The spec v4 calls them **Saede Core** and **Saede Restore**. The packaging renders and
your instruction say **Hero** and **Support**, so the site uses Hero and Support.

Worth reconciling before the next revision goes to the manufacturer, or you will end
up with one name on the technical file and another on the label.

**Change:** `products` in `content/site.json`.

## 2. Two prices are still placeholders

Membership is now **€99/month**. The **3-month starter bundle** and the **single
month** both still show `€00` with a PRICE TBD marker.

**Change:** `content/pages/membership.json`.

## 3. No signup endpoint — read this before you deploy

**The launch-list form stores nothing.** No provider is connected.

It does not pretend otherwise: on a valid address it tells the visitor plainly that
the list is not connected, that their address was not stored, and to email
hello@saede.eu instead. Nothing on the site claims a signup that did not happen.

That is safe, but it is not what you want live. Set `signup.endpoint` in
`content/site.json` to your provider's form URL (Mailchimp, Kit, Klaviyo, Buttondown,
or a serverless function) and the real confirmation message takes over automatically.

The build prints a warning every time it runs until you do.

## 4. No checkout, and no accounts

There is no commerce layer and no login. Every purchase button is currently redirected
to the launch list by `flags.launch_status: "coming_soon"`, and every button on
`/account/` points at `/contact/`.

The account page describes a cancellation flow that does not exist yet. It is written
as a promise about how the membership *will* work — which is the right thing to publish
before launch, but the flow has to actually be built to match before you take money.

**When you launch:** set `flags.launch_status` to `"live"`, and point the account
buttons at your real platform.

## 5. The member library is not gated

`/learn/the-full-briefing/` is labelled *Members* but is **readable by anyone**,
because there is no login. Either gate it or unpublish it before launch.

## 6. Formula sign-off

Doses are target values pending your manufacturer's technical and regulatory sign-off
against EU and AESAN maximum permitted levels. The site says so in the footer
disclaimer. Three have hard EU ceilings to confirm: vitamin D3, selenium, zinc.

Also unresolved from the spec: **capsule fit**. Twelve ingredients including two
oil-solubles is a lot of capsule. If the count per serving changes, `/the-duo/` says
"one capsule daily" and will need updating.

## 7. Horsetail and nettle — flagged for the founder

Two of the twenty ingredients have no human trial in hair.

**Horsetail.** We searched and found none. The study on its card tests a different
silicon source, and the card says so. Your own spec calls it "traditional / structural".

**Nettle root.** The card links a cell-culture study and a human trial in prostate
symptoms. Your spec calls it "mechanistic / adjunct". Both descriptions are accurate,
and both are on the page.

Keeping them with the caveats visible is consistent with the brand. The alternative is
asking whether they earn their place in a formula whose promise is that every
ingredient is there for a researched reason. This is a formulation decision, which is
why it is here rather than quietly softened on the page.

## 8. Company registration country

Leaning Spain; the spec says "Spain first, EU-wide". Not decided, and it determines the
company details block, the lead data-protection authority, and the governing-law clauses.

**Change:** `brand.company_country` in `content/site.json`, and the PLACEHOLDER blocks
in `content/legal/`.

## 9. Trust badges

All five render dashed and faded, marked `pending` — claims about the manufacturer that
have not been confirmed.

**Change:** set a badge's `status` to `confirmed` in `content/site.json` once you hold
the documentation, and add an `href` to the published certificate.

## 10. Photography — now in, with one caveat

All four images are in the build: the sunlit water on the front page, both packaging
renders, and the clouds closing the story page. They were found in your Downloads and
processed into responsive sizes.

**The caveat:** the water and the two renders are screenshots and exports, not master
files. The water in particular came from an Instagram screenshot, so its usable area
is 1276 × 1535 after cropping away the app's own buttons — enough for the front page,
but it is being enlarged on a large desktop display. If you have the original photo,
drop it in and rerun `tools/images.py`; it will look sharper.

**Rights:** the water photograph is credited on Instagram to *bethania*. Please make
sure you have permission to use it commercially before launch. That is a licensing
question, not a technical one, and it is the sort of thing that is much cheaper to
settle now than after the brand is public.

There are also founder photographs in your Downloads. I have deliberately not used
them — publishing someone's face is your call, not mine. Say the word and the story
page gets a portrait.

Note: the detail about waiting for a gynaecology appointment has been removed from the
story and from the two Learn articles that repeated it, at the founder's request. The
ending now says she is still on the journey because androgenetic alopecia is something
you learn to live with and keep under control, rather than something you finish.

## 11. Fonts

No font files arrived, only the reference screenshots, so the wordmark uses
**Bodoni Moda** — the closest open equivalent to the Renessence lettering, and a close
relative of the fine serif on your packaging. Body text is **Jost**.

If you license the actual face used by Renessence (it looks like a commercial Didone
in the Canela / Ogg family), it drops into `assets/fonts/` and one `@font-face` block
in `theme/tokens.css`; nothing else needs to change.
