---
name: "web-imagery-provenance"
description: "Sourcing, licensing and asset records for web imagery so nothing unlicensed ever ships. Covers licence classes and what each permits, model and property releases, AI-generated asset
outcome: "An assets/SOURCES.md bible covering every shipped image with a filled licence cell, release references where a person or mark appears, and a written hold list of everything rejected and
done_when:
  - cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/web-imagery-provenance/SKILL.md
  - observable: assets/SOURCES.md exists and has one row per shipped asset with no empty licence cell
  - observable: no editorial-only asset appears on a commercial page, and every rejected row keeps its reason
  - observable: every recognisable person or third-party mark on the page has a release row with a reference
  - observable: every generated asset carries tool, model version, prompt and date, and is labelled as generated in the record
great_example: examples/great/design-ux/web-imagery-provenance.md
quality_floor: "Every shipped asset has a row with a non-empty licence class and version, a source URL and a retrieval date; nothing editorial-only sits on a commercial page; every generated asset is
activation: "An asset is about to be sourced, downloaded, generated or accepted from a client, or a page is heading to launch and nobody can say where its images came from or what they may be used for."
instruction: "Keep one asset bible per project and treat it as the gate, not the paperwork. Never let an asset reach the page with an empty licence cell. Record for every file the source URL, the author
applies_when:
  env: "macOS or Linux workstation with the project and its asset folder checked out locally"
  runtime: "any web build that renders third-party or generated imagery on a public page"
  deps: "the asset bible at assets/SOURCES.md and access to each asset's source or licence page"
  params: "one row per shipped asset; licence class recorded as a class name plus version, never as free or paid"
  budget: "under 30 minutes per asset for rights research, then escalate rather than guess"
  scale: "up to 30 assets per project, commercial use assumed unless the record says otherwise"
permissions:
  - Read the project asset folder and any client-supplied files
  - Write and maintain assets/SOURCES.md in the project
  - Read public licence, terms and stock pages to establish permitted use
  - Bash for hashing, listing and comparing local asset files
  - Outward, deploy, paid or public actions (buying a licence, contacting a rights holder, publishing the page) need Gate-D approval from Mike before they run
flow:
  - Inventory every image that will reach the page, including logos, icons and background textures
  - Classify each by permitted use (commercial, editorial-only, attribution-required, non-commercial, public domain) rather than by where it was found
  - Fill one bible row per asset with source URL, author, licence class and version, retrieval date, release status and edits applied
  - Flag every row with an unknown licence, an editorial-only class on a commercial page, or a recognisable person or mark with no release, and hold it out of the build
  - Record generated assets with tool, model version, verbatim prompt and date, and confirm the tool's terms permit commercial use
  - Get written confirmation for client-supplied material that the client holds rights and releases, and store the reference in the row
  - Run the gate before handoff and report the pass, the holds and the replacements
out_of_scope:
  - Legal advice or a legal opinion on any licence (escalate to a lawyer through Mike)
  - Buying, renewing or extending a licence (Gate-D, Mike approves)
  - Shooting, editing or grading the imagery itself (see web-imagery)
  - 3D and generative scene rights beyond recording their provenance (see web-imagery-3d)
  - Trademark registration, brand clearance and logo design
---
# Web Imagery Provenance

"Found it on Google" is not a licence and "the client sent it" is not a release. This skill
is the difference between a page you can defend and a page that becomes a liability the
moment it works.

## Method

### 1. The asset bible is the gate

One file, `assets/SOURCES.md`, one row per shipped asset. This is not documentation for its
own sake: it is the only artefact that lets you answer "may we use this" after the person
who chose the image has left the project.

Required columns:

| column | what goes in it |
|---|---|
| filename | exact shipped filename, including the resized variants |
| role | which role it plays on the page |
| source URL | the page it came from, not a search result |
| author / rights holder | a named person or company |
| licence class and version | e.g. CC BY 4.0, Unsplash Licence, client-owned |
| date retrieved | ISO date, because terms change under you |
| release status | model release yes/no/n-a, with a reference |
| edits applied | crop, grade, composite, retouch |
| decided by | who signed off on shipping it |

The gate is one line: **no asset ships with an empty licence cell.** If the cell is empty,
the asset is not in the build.

### 2. Classify by permitted use, not by price

The class decides what you may do. Learn the five that matter.

- **Public domain / CC0.** No permission needed. Keep the source record anyway, because you
  still have to prove where it came from and that it really was CC0 on the day you took it.
- **CC BY (any version).** Commercial use allowed with attribution. The attribution needs
  the author name, the title if given, the source link and the licence link. "Photo from
  Unsplash" is not attribution.
- **CC BY-NC.** Commercial use forbidden. A marketing landing page is commercial. Do not
  talk yourself into this one.
- **Royalty-free (marketplace licence).** Pay once, use widely, but read the tier. Extended
  or enhanced tiers govern resale items, templates for resale, and large print runs. The
  standard tier is usually fine for a website hero and usually wrong for a product you sell.
- **Rights-managed.** Scoped by use, territory, medium and term. Every one of those four has
  to match your deployment or it does not cover you.

### 3. Editorial-only is the trap

Marketplaces and photo agencies mark a large slice of their catalogue editorial-only, which
means newsworthy or illustrative use with attribution and **no promotional or marketing
use**. A landing page selling something is promotional use. The visible markers are a person
at a real event, a recognisable brand, a sports or entertainment figure, and anything from a
news photographer.

UNVERIFIED - the precise boundary between editorial and promotional use is a legal question
and the corpus does not cover it. This skill states the safe operating rule (do not put
editorial-only material on a commercial page) and not a legal test.

### 4. People and marks need releases

A recognisable person, and often a recognisable building or a trademarked mark in shot,
needs a release for commercial use. Stock catalogues expose this as "model release" and
"property release" fields. Absent release means do not use it as the hero of anything paid.

Watch for the marks nobody notices: a competitor's logo on a laptop lid, a real bank's
wordmark on a card prop, a car badge in a car park. Either crop it out, retouch it out, or
replace the shot. Each is a claim you did not mean to make.

### 5. Client material is not automatically licensed

Written confirmation, from someone with authority, that the client holds the rights and that
the people in the photograph have agreed to commercial use. Store the reference in the row.
An email attachment and a Slack paste are not that confirmation.

### 6. Generated assets get the fullest record of all

Record the tool, the model and version, the verbatim prompt, and the generation date. Then
check two things: that the tool's terms grant commercial use for your account tier, and that
you are not presenting the output as a real person, a real product screen or a real result.

UNVERIFIED - whether any specific generator's current terms grant commercial rights or
indemnity. Those terms change and the corpus does not cover them. Read them at the time.

### 7. Run the gate and report three lists

Before handoff produce exactly three lists: **ship** (rows complete), **hold** (rows
incomplete or class mismatched), **rejected** (with the reason kept in the bible so the same
photo is not re-proposed next quarter). A page with a non-empty hold list does not launch.

## Corpus evidence

will-paterson / Create Professional Mockups in Photoshop in MINUTES / 0sjUYG0dTM0 / [00:53] / "do that through Invato, Unsplash, Adobe"
paige-brunton / 51 Squarespace Lessons I Wish I Knew Sooner / 9wrLKLzpuP4 / [02:19] / "beautiful royalty-free photos built into"
self-made-web-designer / How to Be Confident in Your Choice of Career Field / LUVqVfA2W5w / [10:40] / "there's a website called Unsplash that has royalty"
designcourse / Modern LOGO / BRAND Design with David Airey | Q&A / 5fKijXrToWM / [17:18] / "you can find some um stock photography"
designcourse / Modern LOGO / BRAND Design with David Airey | Q&A / 5fKijXrToWM / [17:21] / "so they prefer stock photography to AI"
will-paterson / Watch Me Design a Typographic Poster (Step-by-Step) / RvykWGAUTiw / [13:36] / "unsplash to find these"

**Corpus coverage thin at authoring time.** The corpus names where designers get images and
that "royalty-free" is a category they think in, and that is the whole of its support here.
It does not teach licensing, releases, attribution or rights. Consequently almost every rule
above is UNVERIFIED against this corpus: the five licence classes and their permitted uses,
the editorial-only boundary, the model and property release rule, the client-confirmation
rule, and the generated-asset record. They are written as studio doctrine at authoring time
and carry the standing caveat that licence terms are legal instruments read at the time of
use, not remembered. All caption tracks in the corpus are automatic.

## Anti-patterns

- Empty licence cell: an asset shipped with a search page or "found on Google" as its source record.
- Editorial trap: an editorial-only photograph used on a page that sells something.
- Client said it was fine: rights assumed from an attachment nobody had authority to send.
- Ghost author: a CC BY asset shipped without the four-part attribution line.
- Synthetic customer: a generated face presented as a real testimonial or a real user.

## Links

- parent: when-designing-websites
- parent: web-imagery
- children: none (leaf skill)

## description (full text)

"Sourcing, licensing and asset records for web imagery so nothing unlicensed ever ships. Covers licence classes and what each permits, model and property releases, AI-generated asset attribution, and the asset bible that makes a page auditable. Use when sourcing stock, accepting client photos, recording rights, or auditing an existing asset set before launch."

## outcome (full text)

"An assets/SOURCES.md bible covering every shipped image with a filled licence cell, release references where a person or mark appears, and a written hold list of everything rejected and why, so the page is auditable in under a minute per asset."

## quality_floor (full text)

"Every shipped asset has a row with a non-empty licence class and version, a source URL and a retrieval date; nothing editorial-only sits on a commercial page; every generated asset is labelled and attributed. A single blank licence cell fails the job and blocks handoff."

## instruction (full text)

"Keep one asset bible per project and treat it as the gate, not the paperwork. Never let an asset reach the page with an empty licence cell. Record for every file the source URL, the author or rights holder, the licence class and its version, the retrieval date, and whether a model or property release exists, and refuse to ship anything you cannot fill in. Classify by permitted use rather than by price, because editorial-only material is the trap that looks free and is not. Generate nothing without recording the tool, model, prompt and date, and never present a generated face or screen as a real one."
