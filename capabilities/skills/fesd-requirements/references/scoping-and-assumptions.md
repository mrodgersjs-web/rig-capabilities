# Scoping and assumptions: what is out, what is bonus, what is assumed

Purpose: write the explicit scope statement and environment assumptions so the design has a
defensible boundary and no promised item is silently dropped.

When to load: at the end of requirements collection, when an optional feature appears, and when
an environment assumption (browser generation, user population, deployment channel) is being
made in someone's head instead of on the page.

## Step checklist

1. List the environment assumptions first: who the users are, what browsers and devices they
   carry. For professional trading desks, assume modern browsers and do not design around legacy
   clients. CLAIM(HR2jXy_wPg4@07:33)
2. Mark each non-core feature as bonus, not core (chart synchronization by asset and time frame
   is bonus in the dashboard problem). CLAIM(HR2jXy_wPg4@04:31)
3. State distribution as a requirement, not an afterthought: the component ships as an npm
   package. CLAIM(lO6GyCvbDm8@05:08)
4. State embeddability as a requirement: iframe or provider service.
   CLAIM(lO6GyCvbDm8@05:34)
5. Put offline support and delta-based network updates in the advanced requirements list for an
   offline-first editor, so the core stays small. CLAIM(tsGarhpWOws@06:56)
6. Declare anything that belongs to backend or distributed systems design out of scope, mention
   it once, and move on. CLAIM(tsGarhpWOws@04:20)
7. Raise optional features as questions to the interviewer instead of assuming them in.
   CLAIM(u6jhTo13_No@05:01)
8. Re-check the requirements list at the end against what got designed, including the scope
   calls. CLAIM(lO6GyCvbDm8@31:56)

## Decision table

| Item | Treat as | Why | Cite |
|---|---|---|---|
| Cross-component sync parameters | Bonus | Not the core of the problem | CLAIM(HR2jXy_wPg4@04:31) |
| Legacy browser support for professional desks | Assumed out | Users carry modern browsers | CLAIM(HR2jXy_wPg4@07:33) |
| npm distribution of a widget | Requirement | Changes the API and bundling design | CLAIM(lO6GyCvbDm8@05:08) |
| Embedding in third-party pages | Requirement | iframe/provider constraints shape the state design | CLAIM(lO6GyCvbDm8@05:34) |
| Offline-first behavior | Advanced requirement | Core must stay shippable without it | CLAIM(tsGarhpWOws@06:56) |
| Conflict resolution / CRDTs | Out of scope | Backend-distributed problem | CLAIM(tsGarhpWOws@04:20) |
| CSV export and similar | Ask the interviewer | Never assume optional features in | CLAIM(u6jhTo13_No@05:01) |

## Laws for this sub-topic

- Scope chart synchronization (asset ID, time frame) as a bonus feature, not the core of the
  problem. CLAIM(HR2jXy_wPg4@04:31) single-source.
- Assume modern browsers when the user population is professional desks, and do not design
  around legacy clients. CLAIM(HR2jXy_wPg4@07:33) single-source.
- Treat distribution as a requirement: state that the component ships as an npm package.
  CLAIM(lO6GyCvbDm8@05:08) single-source.
- Treat embeddability as a requirement (iframe or provider service), not an afterthought.
  CLAIM(lO6GyCvbDm8@05:34) single-source.
- List offline support and delta-based network updates as advanced requirements for an
  offline-first editor. CLAIM(tsGarhpWOws@06:56) single-source.
- Declare conflict resolution out of scope for a frontend system design, mention it, and move on
  rather than designing CRDTs. CLAIM(tsGarhpWOws@04:20) single-source.
- Raise optional features (for example CSV export) as a question to the interviewer instead of
  assuming them. CLAIM(u6jhTo13_No@05:01) single-source.
- After the design, re-check the original requirements list so nothing promised is left
  undesigned. CLAIM(lO6GyCvbDm8@31:56) single-source.

## Worked cases

- lO6GyCvbDm8 "[Front-End System Design] - Design a Poll Widget": distribution and embeddability
  as scope-shaping requirements, plus the closing re-check.
- HR2jXy_wPg4 "Frontend System Design - Financial Dashboard / TradingView": bonus scoping and
  the modern-browser assumption.
- tsGarhpWOws "Frontend System Design - Notion": advanced-requirement parking and the CRDT
  out-of-scope call.
- u6jhTo13_No "[Front-End System Design] - Data Table Component": optional features raised as
  questions.

## Dated / contestable

- The modern-browser assumption for professional desks is from a 2025 episode and holds, but the
  specific browser floor drifts. Distiller note (not the author): name the floor (for example the
  last two evergreen versions) rather than the word "modern". CLAIM(HR2jXy_wPg4@07:33)
