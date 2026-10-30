---
name: web-design-critique
description: The final gate. Judge a web surface against its brief and buyer, and return named findings, not adjectives. Use at the end of every design job and whenever something "feels off".
outcome: A critique record that a different person could act on without asking what was meant.
done_when:
  - 'grep:capabilities/skills/web-design-critique/SKILL.md:[F]indings are triples'
  - 'grep:capabilities/skills/web-design-critique/SKILL.md:[S]everity, then verdict'
  - every finding is a triple of issue, location and failed check
  - every finding carries a severity from the fixed ladder
  - the verdict is stated explicitly as PASS or FAIL
  - zero findings are adjectives without a location
great_example: examples/great/design-ux/web-design-critique.md
quality_floor: A verdict with no named finding fails the gate. A finding with no location fails the gate. "It looks premium" is not a finding.
activation: Load last in any web design job, or when the user says "critique this", "why does this look wrong", "this feels off", "is this any good".
instruction: >
  Judge against the brief and the named buyer, not against taste in the abstract. Return findings as
  triples: what is wrong, where it is, and the check that failed. A verdict of "looks good" is not a
  verdict. The critique is allowed to fail the job and send it back upstream.
applies_when:
  env: any context holding a web artifact and its brief
  runtime: static mock, live page, or mid-flight build rendered in a browser
  deps: the brief, the named buyer, and the artifact under review
  params: one artifact per critique; severity ladder is blocker, major, minor, preference
  budget: one full craft walk plus one job walk per artifact
  scale: single page up to a full marketing site
permissions:
  - fs.read
  - fs.write
  - browser.read
  - gate-d-required:deploy
  - gate-d-required:publish
flow:
  - Restate the brief and the named buyer in one line; if there is none, that is the first finding.
  - Run the first-5-seconds test: what does a stranger think this is and who is it for.
  - Walk the craft axes in order: type, color, layout, motion, imagery, copy.
  - Walk the job axes: CTA hierarchy, clarity of the ask, placement of the proof.
  - Run the anti-slop pass (web-design-critique-antislop) and the taste pass (web-design-critique-taste).
  - Emit findings as triples with severity; verdict is FAIL if any blocker remains.
out_of_scope:
  - rewriting the design (that is the craft skills)
  - scoring for an award
  - judgments about people rather than artifacts
---
# Design Critique

The gate that can say no. Named findings only.

## Method

**Judge against the brief.** There is no design that is good in the abstract. A brutalist page can be
perfect for one buyer and wrong for another. Restate the buyer first so the findings have a referent.

**The first-5-seconds test.** Show the page for five seconds, hide it, ask: what is this, who is it
for, what do they want me to do. Any mismatch between those three answers and the brief is a blocker,
because nothing below the fold rescues it.

**Findings are triples.** (what is wrong, where it is, which check failed). The third element is the
one agents skip and it is the one that makes a finding falsifiable. If you cannot name the check,
the finding is a preference and is labelled [preference], never [blocker].

**Severity, then verdict.** [blocker] stops the job. [major] must be fixed before ship. [minor] is
recorded. [preference] cannot block. Verdict is FAIL while any blocker stands.

**The craft walk is ordered on purpose:** type (most visible), color, layout, motion, imagery, copy.
Fixing copy before type hides the hierarchy problem that made the copy feel weak.

## Corpus evidence

- charlimarieTV / Dropbox rebrand - LOVE it or HATE it? (Design News) / 48Sd42c1YPA / [07:37] / "rather than a proper design critique."
- charlimarieTV / Dropbox rebrand - LOVE it or HATE it? (Design News) / 48Sd42c1YPA / [07:38] / "So let's try to have a proper design critique"
- charlimarieTV / Design projects & life updates - Work-with-me vlog! / iDXjxu2tJ80 / [04:26] / "marketing site stand out from others"

The corpus explicitly distinguishes "a proper design critique" from a reaction, which is the whole
premise of this skill. The triple format and the severity ladder are RIG method, UNVERIFIED against
this corpus.

## Anti-patterns

- Verdicts made of adjectives: "clean", "premium", "nice".
- Findings with no location (as in "the type is off", with no section named).
- Critiquing the person or the tool instead of the artifact.
- Judging a page against the critic's own taste while the brief named a different buyer.
- Softening a blocker so the job passes.

## Links

parent: when-designing-websites
children: web-design-critique-taste, web-design-critique-antislop
