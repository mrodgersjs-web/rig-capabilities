import type { Board, Card, Link } from './types';

// Seed board rebuilt from LIVE content sources (2026-09-30):
// - /Users/rig128gb/Developer/loehr-hr-group/site/index.html — the deployed Loehr Impact Ventures
//   landing page ("The Denver HR Leadership Group Run by an Operator"), sections: #hero, #group,
//   #sequence, #members, #operator, #pricing, #offers, #denver, #book.
// - /Users/rig128gb/Developer/loehr-hr-group/research/JEV-AUDIT.md — the Jev user-test audit
//   (web.market 0.747 final, no BLOCK; named_pain_lead 0.46→0.73; diagnostic_wedge 0.17→0.69;
//   boring_reliable_job 0.96; ui.design clarity 0.98 / mobile 0.93 / accessible 0.75).
// Demo brief: "iterate the HR-group landing page" through all 4 diamond phases — the full loop
// research → diamond → mockup → dev handoff.

const cards: Card[] = [
  // ── DISCOVER ────────────────────────────────────────────────────────────
  {
    id: 'c1',
    title: 'Where did the JEV audit leave the page, honestly?',
    body:
      'JEV-AUDIT.md: web.market FINAL 0.747 (baseline 0.649), no BLOCK at any point, but the 0.9 ' +
      'mean was never reached. Strongest fit items: boring_reliable_job 0.96, rulebook_accountability 0.88. ' +
      'Weakest: diagnostic_wedge (0.17→0.69 after the r4 rewrite), named_pain_lead (0.46→0.73). ' +
      'The iteration target is those two, not a redesign.',
    phase: 'discover',
    kind: 'research-question',
    status: 'approved',
    deviation: 0,
    x: 80,
    y: 120,
  },
  {
    id: 'c2',
    title: 'Which sections already carry evidence the buyer trusts?',
    body:
      'Live page audit: #hero leads with the named pain ("Your renewal just jumped 27% and nobody can ' +
      'show you what the service fee actually buys"); #operator gives James Loehr — 18 years running ' +
      'operations, largest 37 locations / ~550 employees; #pricing shows the fee in writing plus market ' +
      'context (SHRM Executive Network $3,995/yr, Hacking HR $2,000, Mile High SHRM cap 12 — same cap). ' +
      'These are the credibility spine; the iteration must not dilute them.',
    phase: 'discover',
    kind: 'research-question',
    status: 'approved',
    deviation: 0,
    x: 80,
    y: 320,
  },
  {
    id: 'c3',
    title: 'Who is the reader the audit could not score well — and why?',
    body:
      'JEV-AUDIT.md website.buyer: mean 0.634 on best-fit section packets, ~0.40 full page. Structural ' +
      'ceiling documented: ~11 rubric questions (vert_healthcare_regulated, typ_free_kit, typ_paid_review, ' +
      'design_visual_evidence…) score the RIG AI-intake product shape — a membership group can score ≤0.1 ' +
      'on them regardless of copy. Doctrine applied: split the bimodal distribution, never average it away. ' +
      'The page should serve the real buyer (Denver HR leader), not chase the mismatched questions.',
    phase: 'discover',
    kind: 'persona',
    status: 'in-review',
    deviation: 1,
    x: 380,
    y: 160,
  },
  {
    id: 'c4',
    title: 'What do the demand-thread pain numbers say?',
    body:
      '#group / #members carry pain numbers that are JEV scores from a September 2026 sweep of HR-leader ' +
      'demand threads on Reddit (quotes and sources in the research file): pain 6.0 — the solo HR lead ' +
      'paying $1,300/month for tools and getting no human; pain 6.90 — the price jack gets read out loud ' +
      'in the room before the vendor writes it into your renewal. Language rule from the audit: named pain ' +
      'first, product language never.',
    phase: 'discover',
    kind: 'research-question',
    status: 'approved',
    deviation: 0,
    x: 380,
    y: 380,
  },

  // ── DEFINE ──────────────────────────────────────────────────────────────
  {
    id: 'c5',
    title: 'HMW lift named_pain_lead (0.73) to top-of-page strength?',
    body:
      'From c1 + c4. The hero already opens on the renewal shock; the fix is named-pain precision: ' +
      'one sentence a Denver HR leader says verbatim ("nobody can show you what the service fee actually ' +
      'buys"), kept above the fold in #hero, with the CTA "Apply for the Denver room — 12 seats" directly ' +
      'under it. Target: named_pain_lead ≥ 0.9 on re-run.',
    phase: 'define',
    kind: 'hmw',
    status: 'approved',
    deviation: 0,
    x: 820,
    y: 120,
  },
  {
    id: 'c6',
    title: 'HMW hold diagnostic_wedge (0.69) without sales pressure?',
    body:
      'From c2. The wedge is the Guest offer in #pricing/#offers: $0, one diagnostic session a year, ' +
      'bring one document, leave with the room\'s written read on it — yours to keep whether or not you ' +
      'apply. It must read as the room already working for you, not a lead magnet. No "book a demo" energy.',
    phase: 'define',
    kind: 'hmw',
    status: 'approved',
    deviation: 1,
    x: 820,
    y: 320,
  },
  {
    id: 'c7',
    title: 'HMW let the pricing page carry the qualifying burden?',
    body:
      'From c2 + c3. Targeting carries the data burden: #pricing already prices under national networks ' +
      'and inside the local band, caps at 12, bans vendors (including as guests), and prints the fee sheet ' +
      'before the first conversation. The iteration should make "who this is NOT for" a visible line so ' +
      'the wrong applicants self-select out — the structural ceiling stays disclosed, not papered over.',
    phase: 'define',
    kind: 'hmw',
    status: 'in-review',
    deviation: 2,
    x: 820,
    y: 520,
  },
  {
    id: 'c8',
    title: 'HMW close the accessible-apply-form gap on #book?',
    body:
      'JEV-AUDIT.md ui.design: clarity 0.98, mobile_considered 0.93, primary_action_obvious 0.83, ' +
      'accessible 0.75 — the audit\'s weakest ui item. The #book form (Name, Work email, Company, What would ' +
      'you put on the table?) needs real labels, error states, contrast that survives the no-pure-#000/#FFF ' +
      'rule, and 44px tap targets. Target: accessible ≥ 0.9 on re-run.',
    phase: 'define',
    kind: 'hmw',
    status: 'in-review',
    deviation: 0,
    x: 820,
    y: 720,
  },

  // ── DEVELOP ─────────────────────────────────────────────────────────────
  {
    id: 'c9',
    title: 'Variant A — #hero named-pain spine rewrite',
    body:
      'Keep the hero photo plate and the "run by an operator, not an association" line; rewrite the lede ' +
      'so the named pain is the first full sentence and the fee-sheet promise is the second. CTA unchanged: ' +
      '"Apply for the Denver room — 12 seats · 30-minute conversation first. No employee data needed." ' +
      'Risk: over-tilting to pain reads alarmist — the no-BLOCK calm from the audit must survive.',
    phase: 'develop',
    kind: 'variant-sketch',
    status: 'in-review',
    deviation: 1,
    x: 1260,
    y: 120,
  },
  {
    id: 'c10',
    title: 'Variant B — #sequence year-in-the-room timeline',
    body:
      '"Monthly. Quarterly. Renewal season. Year two." rendered as a four-stop timeline card set — ' +
      'this is the boring_reliable_job 0.96 evidence made visible: the room keeps a rhythm that outlasts ' +
      'the renewal cycle. Mono data labels overline each stop; one concrete meeting cadence per stop.',
    phase: 'develop',
    kind: 'variant-sketch',
    status: 'approved',
    deviation: 0,
    x: 1260,
    y: 320,
  },
  {
    id: 'c11',
    title: 'Variant C — #members bring/take ledger with pain numbers',
    body:
      '"What Members Bring. What Members Take." as a two-column CARD ledger, each row footnoted with the ' +
      'JEV pain score and its source note (September 2026 Reddit sweep, quotes in the research file): ' +
      'pain 6.0 tools-with-no-human, pain 6.90 renewal price jack. Real numbers with provenance, never ' +
      'unattributed stats.',
    phase: 'develop',
    kind: 'variant-sketch',
    status: 'in-review',
    deviation: 2,
    x: 1260,
    y: 520,
  },
  {
    id: 'c12',
    title: 'Variant D — #pricing fee-sheet decode table',
    body:
      'Solo seat, Company pack (3 seats, one org, different functions, $6,600/year), Guest diagnostic ' +
      '($0 · one session) as a three-row comparison, with the verified 2026-09-30 market context as a ' +
      'TRUST STRIP (max 5 stats): SHRM $3,995 · Hacking HR $2,000 · Mile High SHRM cap 12 · this room ' +
      'under the national band · monthly seat = leave any month. Deviation +5 from the system table ' +
      'component — outside the |d| ≤ 3 budget, flagged for human review before shipping.',
    phase: 'develop',
    kind: 'variant-sketch',
    status: 'draft',
    deviation: 5,
    x: 1260,
    y: 720,
  },

  // ── DELIVER ─────────────────────────────────────────────────────────────
  {
    id: 'c13',
    title: 'Dev handoff — #hero + #sequence spine (Variants A, B)',
    body:
      'Ship the named-pain hero and the year-in-the-room timeline. Tokens: light theme (--void #FAF7F2, ' +
      '--cream #F5F0E8, --gold #B8860B, --ink #14110D). Components: OVERLINE, DISPLAY H1 (Cormorant 300, ' +
      'max 2 gold ems), LEDE max 55ch, BUTTON PRIMARY. Acceptance: named_pain_lead ≥ 0.9 and ' +
      'boring_reliable_job held ≥ 0.9 on JEV re-run; mobile_considered ≥ 0.9 at 390px.',
    phase: 'deliver',
    kind: 'dev-handoff',
    status: 'approved',
    deviation: 0,
    x: 1700,
    y: 120,
  },
  {
    id: 'c14',
    title: 'Dev handoff — accessible #book apply form (c8)',
    body:
      'Form fields Name, Work email, Company, "What would you put on the table?" — explicit <label>s, ' +
      'inline error states, focus rings in --gold, contrast ≥ 4.5:1 within the token palette, tap targets ' +
      '≥ 44px, submit "Apply for a seat" with the honest note ("This form opens the 30-minute conversation…"). ' +
      'Acceptance: ui accessible ≥ 0.9 on JEV re-run; no pure #000/#FFF anywhere.',
    phase: 'deliver',
    kind: 'dev-handoff',
    status: 'in-review',
    deviation: 0,
    x: 1700,
    y: 320,
  },
  {
    id: 'c15',
    title: 'Dev handoff — #pricing clarity block (Variant D, flagged)',
    body:
      'Fee-sheet decode table + TRUST STRIP of verified market context (dates on every number — ' +
      '"Market context, verified 2026-09-30"). Deviation +5 is outside the |d| ≤ 3 budget: human review ' +
      'required before this block ships. If review rejects the custom table, fall back to standard CARD ' +
      'rows with identical copy.',
    phase: 'deliver',
    kind: 'dev-handoff',
    status: 'draft',
    deviation: 5,
    x: 1700,
    y: 520,
  },
  {
    id: 'c16',
    title: 'Dev handoff — this board exported as a coding bundle',
    body:
      'The loop closes here: Export dev handoff renders rig-dev-handoff.json (cards, phase, links, ' +
      'deviation scores, token set) + rig-ai-coding-prompts.md (board-level prompt then per-card prompts) ' +
      'into the side panel. A coding agent consumes the bundle directly; the Stitch mockups in the Mockups ' +
      'tab (export handoff modal, mobile canvas 390px) are the visual contract for the same surfaces.',
    phase: 'deliver',
    kind: 'dev-handoff',
    status: 'in-review',
    deviation: 1,
    x: 1700,
    y: 720,
  },
];

const links: Link[] = [
  { id: 'l1', from: 'c1', to: 'c5' },
  { id: 'l2', from: 'c1', to: 'c6' },
  { id: 'l3', from: 'c2', to: 'c6' },
  { id: 'l4', from: 'c2', to: 'c7' },
  { id: 'l5', from: 'c3', to: 'c7' },
  { id: 'l6', from: 'c4', to: 'c5' },
  { id: 'l7', from: 'c4', to: 'c11' },
  { id: 'l8', from: 'c2', to: 'c8' },
  { id: 'l9', from: 'c5', to: 'c9' },
  { id: 'l10', from: 'c5', to: 'c10' },
  { id: 'l11', from: 'c6', to: 'c11' },
  { id: 'l12', from: 'c7', to: 'c12' },
  { id: 'l13', from: 'c8', to: 'c14' },
  { id: 'l14', from: 'c9', to: 'c13' },
  { id: 'l15', from: 'c10', to: 'c13' },
  { id: 'l16', from: 'c11', to: 'c15' },
  { id: 'l17', from: 'c12', to: 'c15' },
  { id: 'l18', from: 'c13', to: 'c16' },
  { id: 'l19', from: 'c14', to: 'c16' },
  { id: 'l20', from: 'c15', to: 'c16' },
];

export function seedBoard(): Board {
  return {
    title: 'Iterate the Loehr HR-group landing page (JEV-audit-driven)',
    cards: cards.map((c) => ({ ...c })),
    links: links.map((l) => ({ ...l })),
  };
}
