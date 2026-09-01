---
name: capabilities-certify
description: Run the deterministic certification gates over the capability estate — suite, index freshness, done-tests, token integrity, ACL — with --plant proving each gate actually fires.
argument-hint: "[plant]"
allowed-tools: Read, Bash
category: meta
outcome: "meta: a green certification is earned, never assumed — every gate must be able to go RED"
done_when:
  - file:capabilities/commands/capabilities-certify.md
  - file:examples/great/meta/capabilities-certify.md
  - grep:capabilities/commands/capabilities-certify.md:No LLM participates in certification
great_example: examples/great/meta/capabilities-certify.md
acl: public
quality_floor: 0.7
---

# capabilities-certify

1. Call `capabilities_certify` with `{}` for the live gate matrix (suite / index_fresh / done_tests / idp_integrity / acl_jake).
2. With the word `plant` in args, call it with `{plant: true}`: copies the repo, breaks exactly what each gate guards, and demands RED — restore — GREEN for all five gates.
3. A gate that stays green while planted is a bug in the gate: file it before anything built on that gate is trusted.
4. Quote the artifact path written under `.context/certify/` — the seal references it, not this conversation.

No LLM participates in certification. If a gate needs judgment, it is the wrong gate.
