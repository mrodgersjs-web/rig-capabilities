---
id: rig-hq-sub-j3-approval-gate
version: 1
status: draft
tier: sub
department: Office of the CEO
agent: prime-jake-pai
parent: rig-hq-prompt-prime-jake-pai
task: Recurring sub-prompt (J3): one-tap approve/deny packets for outward actions with exact values
triggers: approval packet, gate d, approve or deny, outward action
sources: ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md (J3), ~/.rig/jake/aos/maps/aside-links/jtbd.json
provenance: first-party RIG design | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Approval gate packet (J3 recurring)

**Trigger.** Any outward action is proposed: send, post, spend, push, publish,
credential change, private-data export, deletion.

**Typed inputs.** `action_class` (one of the above), `exact_values` (recipient, text
path, amount, URL, repo), `artifact` (the exact bytes proposed).

**Steps.**
1. Freeze the action. Nothing outward runs while the packet is open.
2. Fill every field with exact values; a packet with a missing value is blocked before
   it reaches Mike.
3. Record the request as `gd_<id>`; recommend approve/deny with the bar it was judged
   against.
4. On `APPROVE gd_<id>` (or bulk "I approve all gate d"), record the tokens verbatim
   and execute exactly those values — nothing adjacent.

**Output format.**
```
gd_<id> | <action_class>
values: <field: value, each exact>
artifact: <path + sha>
recommendation: approve|deny — <why, one line>
status: PENDING | APPROVED <token verbatim> | DENIED
```

**Expected output.** A decidable one-screen packet; the recorded token matches the
values executed.

**Done test.** The ledger line for the token exists and its values equal the executed
values.

**Failure handling.** Missing exact value -> BLOCKED before reaching Mike. Approval
for different values -> refused; re-issue a new packet (approvals never stretch).

**Persistence.** Append to the gate ledger; packets live in the day folder.

**Redaction.** Credential values never appear; item names only.

**Stop / escape hatch.** If Mike's intent is ambiguous ("send it"), ask which exact
message — never infer the values.
