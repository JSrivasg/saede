# Copy review — for the regulatory reviewer

Saede is EU-facing, so supplement wording is tightly regulated. This lists the
rules the copy was written to, the lines a professional should look at before
launch, and the wording that was deliberately avoided.

**Nothing here is legal advice.** It is a map of where the risk sits, written so
that a lawyer's time goes to the passages that need it.

---

## Rules the copy follows

**Avoided everywhere.** No disease or drug-style claims. The site never says
"blocks DHT", "cures", "treats", "the solution", "last resort", or anything framing
androgenetic alopecia or PCOS as a condition the product fixes. There is no
before/after language and no promise of regrowth.

**Used instead.** Ingredients "support", "contribute to" or "help maintain".
Where an EU authorised health claim exists, the copy stays close to its wording:

- *Biotin contributes to the maintenance of normal hair.*
- *Zinc contributes to the maintenance of normal hair, nails and skin.*
- *Iron contributes to normal oxygen transport and to the reduction of tiredness
  and fatigue.*

Each of the twenty ingredients in `content/ingredients.json` carries a `claim_status`
field for your review:

- `efsa_authorised` — biotin, iron, zinc, selenium, vitamin D3, vitamin C, the
  B-complex, tocotrienols (as vitamin E). An approved EU claim exists.
- `no_authorised_claim` — saw palmetto, pumpkin seed oil, ashwagandha, nettle root,
  marine collagen, myo-inositol, D-chiro-inositol, hyaluronic acid, horsetail, and
  the three amino acids. **These are the ones to scrutinise.** Botanical claims are
  still on hold in the EU, so the copy for these describes only *our reasoning for
  choosing the ingredient* and *what researchers have studied* — never an effect on
  the reader.

**Doses are now published on the site**, which raises the stakes on this page: an
amount next to an ingredient invites a reading that the amount does something. Please
review the ingredient cards with that in mind. The site states in the footer
disclaimer that doses are target values pending your manufacturer's technical and
regulatory sign-off against EU and AESAN maximum permitted levels.

**Disclaimer.** The food-supplement disclaimer appears at the foot of every page and
again as a call-out block on most. Text is in `content/site.json` under `disclaimer`.
It now also states that doses are target values pending manufacturer and regulatory
sign-off.

**Member content.** Described throughout as a fuller, more detailed briefing — never as
personalised or individually assessed. `/learn/the-full-briefing/` says in its opening
that it is not an assessment of the reader, that we have not seen their results, and
that nobody is writing them a plan. That wording is deliberate: a personalisation claim
made from a checkout form would be a claim we could not stand behind.

**Minoxidil.** Kept strictly educational at `/learn/minoxidil-honestly/`. That page
states explicitly that minoxidil is a medicine, that Saede is a food supplement,
that Saede does not replace it, and that nothing there is a reason to stop a
prescribed treatment.

---

## Please review these specifically

### 1. Ingredient "why it is here" lines — highest priority
`content/ingredients.json`. The botanicals are the exposure. Two to look at closely:

- **Saw palmetto**: *"studied for its role in androgen activity — the hormonal
  pathway most often involved when a woman's hair thins at the temples and the
  parting."* This describes a mechanism and names a pattern of hair loss. It stops
  short of a claim, but it is the closest line on the site to one.
- **Myo-inositol**: *"the most-researched nutritional ingredient in women with
  PCOS."* A factual statement about research volume, on a page for a product a woman
  with PCOS might buy. Check whether the proximity implies a claim.

### 1. "Is Saede a food supplement?" — the answer, and why it matters

The founder asked whether the site should say Saede is *"a supplement dedicated to
minimising the symptoms of a medical condition — female pattern hair loss."*

**It must not say that, and the site does not.** Two separate points of EU law:

1. **Food supplement is a legal category, not a marketing choice.** Under Directive
   2002/46/EC that is what Saede is, and the label and the site have to say so.
2. **A product presented as treating or relieving a disease is legally a medicinal
   product** (Directive 2001/83/EC, the "by presentation" limb). "Minimises the
   symptoms of a medical condition" is exactly that phrasing. Putting it on a food
   supplement does not merely risk a fine — it can reclassify the product, which
   means no lawful sale without a marketing authorisation.

**What the site says instead**, which is as close as the wording can safely go:

> Not a general hair vitamin. A supplement made specifically for women living with
> female pattern hair loss.

That describes *who it is for*, which is permitted, rather than *what it does to a
disease*, which is not. Please confirm you are comfortable even with this framing for
Spain — naming the condition at all is the judgement call in item 1a below.

### 1a. THE FRONT PAGE NOW NAMES ANDROGENETIC ALOPECIA — read this first

`content/pages/home.json`, the section headed *"Not another biotin supplement."*,
and `/concerns/hair/`.

At the founder's direction the site now leads with androgenetic alopecia and DHT,
explains the mechanism, and positions Saede as a complete system formulated around
it. **This is the single largest regulatory change since the last review and it needs
your sign-off before launch.**

How it has been written to stay on the right side of the line:

- The medical content is **educational** — what androgenetic alopecia is, what DHT
  does, where it shows first. Explaining a condition is permitted; claiming to treat
  it is not.
- The product is described as **"formulated around those mechanisms"**, never as
  treating, reversing or curing anything.
- A visible line directly under that section states that androgenetic alopecia is a
  medical condition, that the reader should see a doctor, and that Saede is a food
  supplement — support alongside care, not instead of it. **Do not let anyone remove
  that line.**
- No before/after language, no regrowth promise, no percentages.

What still needs your judgement: naming a medical condition on a supplement's front
page invites the reader to connect the two, even where the copy never does. Some
member states read that context more strictly than others. Please rule on it for
Spain specifically.

### 2. Ashwagandha — new, and the one to look at first

`content/ingredients.json`. The evidence cited is about **cortisol and stress**, not
hair. The card says this explicitly. But it sits on a hair-loss product's ingredient
page at a 600 mg dose, and the surrounding copy explains that stress is one of the
three roots we built the formula around.

That chain of reasoning is honest and it is stated openly — but it is an inference the
page invites the reader to make, and it is the closest thing on the site to a claim
assembled out of two true statements. Worth your judgement.

Note also: ashwagandha is subject to specific national restrictions in some EU member
states, and it carries pregnancy and thyroid-medication cautions. The FAQ raises the
thyroid interaction. Confirm the position in Spain and in your other launch markets.

### 3. The PCOS article
`content/learn/pcos-what-it-is.md` discusses a medical condition at length and cites
inositol research. It states that a supplement is not a treatment for PCOS and
carries a prominent call-out, but it is the longest piece of medical content on the
site.

### 4. The results timeline
`/how-it-works/` says most women see first changes around three months and fuller
results by six. This is an efficacy expectation. It is framed as honesty about how
slowly hair grows rather than as a promise, and the page arguably lowers
expectations rather than raising them — but it is a numeric outcome statement and
should be checked.

### 5. The founder story — now much longer, and it names two prescription medicines

`content/pages/my-story.json` (the page moved from `/our-story/` to `/my-story/`).

The story is now a full first-person account, dictated by the founder. Three things
in it need your eye:

- **It names minoxidil and spironolactone**, as medicines she was prescribed, and
  says minoxidil increased her shedding at first and that her hair loss continued.
  That is her own medical history, not a comparison — but it sits on a page selling a
  supplement, so the page carries a closing section stating plainly that these are
  medicines, that this is her experience rather than advice, and that nothing there is
  a reason to stop a treatment her reader's doctor has recommended.
- **It contains efficacy testimony**: *"the shedding decreased"*, *"my hair loss
  stopped"*. This is about the routine she assembled for herself before Saede existed,
  not about the finished product — but the reader will not necessarily make that
  distinction. Testimonials implying efficacy are treated seriously in several member
  states.
- **It explains mechanisms** — DHT, and inositol's role in insulin signalling — inside
  a personal narrative. The explanations are accurate and educational, and phrased as
  what the research has studied.

**New, and please note it:** the founder now discloses that she *still* takes minoxidil
and spironolactone, and says plainly that on their own they never stopped her hair loss
but do help her keep it under control. She has chosen to publish this so readers know
their full range of options rather than only the product being sold.

Two things follow for you. First, the site now shows its founder combining Saede with
prescription medicines — which is honest and is exactly the sort of disclosure that
makes a testimonial defensible, but it is a fact about the brand's own use that you
should be aware of. Second, the mechanisms named are accurate and deliberately
distinguished: spironolactone acting on the androgen receptors DHT acts on, minoxidil
acting on the follicle and the growth phase. Minoxidil is *not* an anti-androgen and the
copy does not say it is. Please keep that distinction if the section is ever edited.

The section closes with **"Saede is a supplement, not a medication"** in her own voice.
The full legal designation ("Saede is a food supplement…") still appears in the standing
disclaimer block on that same page and in the footer of every page, so the statutory
wording is not displaced — only phrased personally at that one moment.

### 5b. The founder story (previous note)
`content/pages/our-story.json` is first-person testimonial: *"my hair loss decreased.
A lot"*, and *"the hair loss stopped again."* Personal testimony about a
pre-Saede routine of separate supplements, not about the finished product — but
testimonials implying efficacy are treated seriously in some member states.

### 6. Subscription terms — a second, separate review
`content/legal/subscription-terms.json` and the disclosure block on `/membership/`.
Minimum-term subscriptions are closely regulated and the rules vary by member state.
The three-delivery minimum, the renewal notice, and the interaction with the
statutory 14-day withdrawal right all need checking against the country of
registration — which is not yet decided (see `OPEN-DECISIONS.md`).

### 7. Comparative pricing
The cost-comparison section makes claims about competitors' prices. Once real
figures replace the placeholders, comparative advertising rules apply: the
comparison must be verifiable and not misleading. Publishing the source for every
line, as the page promises, is the safeguard — make sure that actually happens.

### 9. All five legal pages
`content/legal/` are plain-language drafts written so the pages exist and read in
the brand's voice. They are marked as drafts on the page itself while
`show_open_decisions` is on. Each contains an explicit PLACEHOLDER block listing
what a lawyer still needs to add. The company details block on `/contact/` and
`/terms/` is a legal requirement for an EU trading website and is currently empty.

---

## On the research citations

All 29 studies linked on the site were verified against the PubMed database
(**2026-08-29 and 2026-08-30**) — titles, authors, journals and PMIDs all checked.
Several plausible-looking citations turned out to be the wrong paper and were corrected
or dropped rather than published. The citations named in your spec v4 were checked the
same way and all resolved correctly.

Thirteen of the twenty cards carry a note about the limits of their own evidence. The
ones that matter most:

- **Saw palmetto** — most of the older research was in men.
- **Pumpkin seed oil** — the trial was in men. Our 400 mg is that trial's exact dose.
- **Ashwagandha** — the evidence is about cortisol, not hair.
- **Tocotrienols** — one small study; the authorised claim we rely on is about
  oxidative stress, not hair.
- **Marine collagen** — the strongest evidence is for skin, not hair. Fish allergen.
- **Nettle root** — a cell-culture study and a trial in an unrelated condition.
- **Horsetail** — no human trial in hair was found at all.
- **Hyaluronic acid** — a skin ingredient, and the card volunteers that it is
  inexpensive relative to how good it looks on a label.
- **Biotin** — the card explains that we deliberately did *not* use a headline-grabbing
  dose, because very high biotin distorts thyroid and cardiac blood tests.
- **Iron** — the card asks the reader not to add more without a ferritin test.

Those notes are a legal asset as much as an editorial one: they make the page harder to
characterise as misleading. Please do not let anyone remove them to tidy up the copy.

---

## If you change wording

Keep to `support` / `contributes to` / `helps maintain`. If a proposed line
describes what the product will do *for the reader* rather than what an ingredient
contributes or what researchers studied, it has probably crossed the line.

Flag anything you are unsure about rather than guessing — that is the instruction
this copy was written under.
