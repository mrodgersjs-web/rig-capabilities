# Frontend security

Purpose: the two frontend security moves this corpus actually teaches (DOM encapsulation and untrusted-content filtering), plus an honest map of where the real depth lives in the estate.

When to load: when server data the client does not control reaches the DOM, when a component must resist surrounding page scripts, or when a security question exceeds these two laws.

## Coverage, stated plainly

This corpus is thin on security. Stage S10 contains exactly 2 laws, both from one video
(9mjsRrJYOWE, Typeahead component, 2023). They cover the widget boundary (isolate the component's
DOM) and the data boundary (filter what an untrusted server sends back before it renders). They do
not cover authentication, authorization, CSRF, CSP, dependency supply chain, secret handling,
transport security, or threat modeling. Do not let a design answer imply this stage covers those.

## Laws

- Encapsulate the component DOM (web component / shadow DOM) so external scripts cannot rewrite it
  or steal data through it. Single-source. (CLAIM(9mjsRrJYOWE@52:57))
- Offer a content-filter function when results come from a server you do not trust, so unwanted
  markup or scripts are stripped without building a proxy. Single-source.
  (CLAIM(9mjsRrJYOWE@55:05))

## Step checklist

1. Name the trust boundary in the design: which data crosses from a server you do not control into
   a DOM you do.
2. Decide encapsulation: does the component need a shadow-DOM boundary so the surrounding page's
   scripts cannot read or rewrite its internals (CLAIM(9mjsRrJYOWE@52:57))?
3. Decide filtering: if results arrive from an untrusted server, expose a filter hook that strips
   unwanted markup and scripts before render, instead of standing up a proxy
   (CLAIM(9mjsRrJYOWE@55:05)).
4. Say in the answer which risks these two moves do not address, and where those are handled.
5. For anything beyond these two moves, route to estate depth: security-threat-model for the threat
   model, threat-mitigation-mapping for mitigation coverage, when-securing-the-estate for triage
   skills, and fixing-accessibility's sibling fix-* skills for surface-level audits.

## Decision table

| Situation | Move | Why | Cites |
|---|---|---|---|
| Embedded widget on a page with other scripts | shadow DOM / web component encapsulation | surrounding scripts cannot rewrite or read the component's DOM | CLAIM(9mjsRrJYOWE@52:57) |
| Search or render results from an untrusted server | content-filter function on the render path | strips unwanted markup and scripts without a proxy | CLAIM(9mjsRrJYOWE@55:05) |
| Data from your own trusted API, escaped by the framework | no extra filter hook needed | the framework's escaping covers the case | CLAIM(9mjsRrJYOWE@55:05) |
| Auth, CSRF, CSP, secrets, supply chain | out of this stage's scope | not covered by these 2 laws; use the estate skills named above | no corpus law |

## Anti-patterns

- Rendering untrusted server markup into the component DOM with no filter step
  (CLAIM(9mjsRrJYOWE@55:05)).
- Assuming a framework component is encapsulated from the rest of the page when no boundary exists
  (CLAIM(9mjsRrJYOWE@52:57)).
- Citing these two laws as if they constitute a security design. Coverage is 2 laws, 1 video.

## Worked cases

- 9mjsRrJYOWE, Typeahead component: the only case in the corpus with a security pass. Steal the
  shape: encapsulate first, then filter what crosses the trust boundary
  (CLAIM(9mjsRrJYOWE@52:57, 9mjsRrJYOWE@55:05)).

## Dated / contestable

- His prediction that web components still needed about five years to be widely adopted is a 2023
  guess. Distiller note (not the author): browser support is broad now and framework-first teams
  still debate shadow DOM styling workflows, but the security motivation for encapsulation stands
  regardless. (CLAIM(9mjsRrJYOWE@53:26))
- A filter hook on the render path is a pragmatic middle ground. Distiller note (not the author):
  prefer a well-maintained sanitizer library over a hand-written filter, and treat sanitization as
  one layer, not the whole XSS story.
