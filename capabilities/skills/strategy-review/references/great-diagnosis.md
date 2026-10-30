# Great diagnosis: the six diseases in action

A worked example of `strategy-diagnose` output, so an agent can see the shape of a
diagnosis rather than infer it. It is reconstructed from a public case; the doctrine rules
it applies carry CLAIM(videoIds) that resolve in `data/corpora/strategy/manifest.jsonl`.

> **This file trips `strategy_lint.py` on purpose.** It quotes a founder's bad strategy
> ("leading, high-quality", "best-in-class", "ambitious clients") in order to diagnose it, so
> the virtue-claim and goal-as-strategy rules fire on the quoted text. That is the gate
> working. Do not edit the quoted strategy to make the linter quiet; the findings are the
> first step of the diagnosis.

## Case: a well-run B2B agency that keeps losing deals on price

**Stated strategy, in the founder's words**: "We are a leading, high-quality agency
delivering best-in-class digital solutions to ambitious clients, and we plan to grow
revenue 20% next year."

### Step 1 - the how-not-how test

| question | answer | verdict |
|---|---|---|
| Ask "how?" until you cannot | "hire, market harder, improve delivery" | goal, not a strategy: CLAIM(Ikx1ECodt1M, rWcJOpdrbCY) |
| Would the fiercest competitor agree? | yes - "quality", "best-in-class" and "tailored" are what every agency says | the only-claim is empty |
| What are we stopping? | nothing | nothing is refused, so nothing changes: CLAIM(y1-5nxulR68) |
| Rumelt's crux test | three goals, no single crux | not a strategy: CLAIM(Ggl_O1vhk_c) |

**Diagnosis: goal-not-strategy.** The document describes a status quo, not a move.

### Step 2 - the market era and the K-shape

The agency answers requests it finds (supply-driven). Requests of that kind are the
"served" era: everyone can get them, so the era-2 answer is positioning, then niching
CLAIM(r-B79h2GUPk). But its actual supply is rising faster than buyers' willingness to pay
for generic delivery, which is the overserved condition. **The era-2 playbook is cooked for
this business**, and the win is changing the conditions of the category rather than playing
better inside it CLAIM(r-B79h2GUPk, XipA7Kl-t-g).

### Step 3 - the true competitive set

The founder says the category is "digital agency". Buyers do not shop that way. They shop
a **named outcome** (pipeline, compliance, retention, launch), and compare the agency
against three other options: an in-house hire, a freelancer or a platform, and the
incumbent they already have. Leverage is set by that set CLAIM(XPhxUrUPO-A, LInrWGuTn68).
The agency is comparing itself to other agencies while buyers compare it to "do nothing
this quarter", which is why it keeps meeting price.

### Step 4 - leverage

| test | result |
|---|---|
| high demand for what it sells | weak: the demand is for outcomes, not deliverables |
| low supply of it | none: every agency and every platform can deliver |
| desert-water test | far from it: hundreds of sellers, no one badly wants this particular delivery |

**Diagnosis: wrong competitive set, then no leverage.** CLAIM(u-jQ74wAqvo, udkwqWaBjnw).

### Step 5 - the disease, named

> **Primary disease: wrong competitive set.** The agency's own language puts it in a
> comparison it loses by construction, which is also why price keeps rising to the decision
> rather than falling away. The goal-not-strategy framing is real but secondary: no
> only-statement could hold in "digital agency" because every agency is the only one doing
> exactly what it does.

**Next pillar: `strategy-new-value`.** Not marketing (the offer is not marketable yet),
not pricing (pricing cannot fix a set you are losing in), not tactics.

### What this diagnosis deliberately does not do

- It does not name the fix. Fixing is `strategy-new-value`'s job; a diagnosis that also
  prescribes is how a symptom treatment gets sold as a cure CLAIM(c_AwFCghnBU).
- It does not blame execution. Execution is good here, which is the point: good execution
  inside the wrong set is what "better" is a synonym for CLAIM(PpcQFN9euao).
- It does not assume the agency should niche. Niching is an era-2 answer and it is
  overserved here CLAIM(3h178lirdcw).

### Output contract this example fills

```json
{
  "stated_strategy": "We are a leading, high-quality agency delivering best-in-class digital solutions; grow revenue 20% next year",
  "is_a_strategy": false,
  "disease": "wrong-competitive-set",
  "evidence": "CLAIM(XPhxUrUPO-A) the category is what the customer is shopping for; CLAIM(u-jQ74wAqvo) leverage is high demand plus low supply",
  "era": "overserved",
  "leverage_note": "low: buyers compare the agency against in-house, a freelancer and doing nothing, not against other agencies",
  "next_pillar": "strategy-new-value",
  "not_a_strategy_because": "three goals and no crux, no only-claim a competitor would not concede, and nothing stopped"
}
```
