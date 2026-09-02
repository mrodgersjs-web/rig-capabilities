## 3. REQUIRED OUTPUT SECTIONS — in this exact order, with these exact headings

Output the sections S0 → S8, then the terminal marker. Do not reorder, merge, rename, or add
top-level sections.

**S0 — MissionPacket.** Six fields, each explicitly labelled:
`jobs_to_be_done`, `mechanism`, `unit_economics`, `falsifier`, `kill_criteria`, `transformation`.
Unit economics must be declared targets or cited card text (never a measured result). Falsifier and
kill criteria must be things that could actually go RED in a named check.

**S1 — Inputs read + declared gaps.** The cards/files you actually opened in this session, with
what each contributed, plus the declared gaps: the three truncations (with their anchors), the
absent Phase 12, the absent Gates 11/12, the missing `E_stage` baseline (all six Studios DORMANT,
`baseline_recorded: false`), and zero bookings by evidence. A file listed here must be a file you
opened.

**S2 — Register rows in the criteria-card schema, each mapped to the expert-OS phase it serves.**
Use the 22 columns of §1.4 in order, one block per proposed row (proposed rows only — you do not
write the CSV). Every row: non-empty `evidence_paths` of real paths, non-empty
`enables_product_classes`, a named `owner`, ISO `last_touched`, and its phase mapping drawn from
Phases 1–10 only; anything belonging to Phase 11 is `type: offer`, `maturity_M0_5: 0`, flagged
`objective_only_truncated`; nothing maps to Phase 12. Do not re-propose `booked_qualified_conversations`
as a new row — it exists. Rows must survive `register.validate_row` as you read it.

**S3 — Gated routing and fallback safety.** The dormant-by-default route (`model_route.py`), the
three registries and the single Gate-D transaction, the `DORMANT_PER_STUDIO_UNTIL_E_STAGE_LOWER_THAN_OPUS5`
gate, the fallback-ladder audit matching the deployment alias and not the raw model id, the
pinned-no-earlier-family-fallback rule, forced-`tool_choice` blocking, and what stays explicitly
untouched. Say plainly that no baseline exists, so dormancy is today's correct state.

**S4 — Weekly Realign spec.** The five weekly artifacts, the weekly gate's five PASS conditions,
`BASELINE_ONLY` semantics, three-consecutive-FAIL and C_t-rise-with-zero-bookings kill criteria,
and the honest first-week verdict under zero bookings.

**S5 — Migration safeguards.** What must not break while this lands: existing gates/tests,
harness-compiler anchor preservation, the dormant cron staying dormant, the untouched config list,
Gate-D scoping per action class, lease/worktree laws (no agent-created checkouts), and rollback
paths.

**S6 — 2031 phase-gate falsifiers.** Per year/phase of the card's 2031 arc (card 4, `## The 2031
roadmap — two nested arcs`, lines 99–115), the falsifier that would kill that phase — phrased as an
observable that could go RED, cited to the card's own line, plus "No phase advances on calendar.
Only on gate." (card 4 line 115). Do not invent falsifiers for regions that are truncated.

**S7 — Per-claim `path:line` citations.** A numbered list mapping every material claim in S0–S6 to
the `path:line` you read, with the exact quoted text from that line. One entry per claim. Anything
you cannot cite goes in S8 as an open question — never asserted.

**S8 — Open questions.** Unanswered, explicitly unresolved items, including every truncated region
you could not resolve and every proposal that would need a write or an approval to settle.

**Terminal marker (last line, alone): `FABLE2031-END`**

---

