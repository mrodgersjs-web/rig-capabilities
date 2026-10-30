# Exemplar: Octopus Energy's service innovation (reconstructed; Jev verdict ESCALATE)

This is the family's form exemplar: a real business, the new value named before the
innovation, the only-statement tested against a fiercest competitor, explicit trade-offs,
and execution visible to an outsider. It is written in the five-section form from
strategy-document. **Its recorded Jev verdict is ESCALATE, and that is the most useful thing
about it** - see the gate record at the end. Every doctrine claim resolves to a corpus videoId.

## 1. Context

Octopus Energy sells electricity and gas to UK households and small businesses, competing
against the big-six energy suppliers. The category the customer shops in is not "energy
provider" in the abstract: it is the monthly bill, the meter reading, the complaint line and
the annual statement, with switching costs measured in tenancy length and a comparison habit
that runs through price-comparison sites. The status quo of that category is a supplier whose
operational design is built to keep phone lines busy and to make contact deliberately hard
(CLAIM(qxdY2kdKz9g), CLAIM(FF46sruCVpY)).

## 2. The strategy argument

- **Status quo.** Big-six suppliers model the customer as a passive meter. Contact is a cost
  centre to be deflected: phone menus, hold queues, automated meters that rarely need reading.
- **Why that sucks.** The whole industry spent decades building operations to stop people
  getting through, and in doing so it made its most painful moment, the moment a customer has
  a real problem, the moment it is worst at helping. Every pound of efficiency saved on
  handling a complaint is a pound of value deliberately destroyed (CLAIM(qxdY2kdKz9g)).
- **Unique belief.** The category treats human contact as a cost to minimise. It is the
  opposite: a supplier that answers the phone in seconds with a person empowered to fix the
  problem has made the thing the industry treats as a weakness into the reason to choose it,
  and no amount of price competition reaches that (CLAIM(FF46sruCVpY), CLAIM(y1-5nxulR68)).
- **What the business does.** A real person answers every call, with no menu and no bot, and
  is empowered to resolve the issue on the spot. Hiring, incentives, technology and training
  are all oriented around picking up the phone, and the advertisement simply says what is
  true: outstanding customer service at fair prices (CLAIM(FF46sruCVpY), CLAIM(ElaWyEeHS1w),
  CLAIM(qxdY2kdKz9g)).
- **Value the customer gains.** A customer with a problem is not routed, not held, not
  told to ring back. They speak to someone who can end the problem in that call, which is
  value no price-comparison site can rank, because it is not a price.

## 3. How we must change

- Stop measuring success by call-centre efficiency, deflection rate and average handle time;
  these optimise the disease.
- Stop designing the phone journey to route people away from a human.
- Stop letting price-per-kWh be the headline of the offer, because the only-statement
  requires that customers not be able to get this from anyone else, and price is the thing
  everyone else is competing on.
- Accept that the innovation is a service-model cost, not a software feature, and that it
  will look, in a cost table, like a permanent overhead: the only-statement's Z has to be
  bought with supply you control (CLAIM(y1-5nxulR68), CLAIM(ElaWyEeHS1w)).

## 4. Strategy statement

We are the only UK energy supplier who answers the phone with a human being who is
empowered to fix your problem in that call, so customers get an energy problem solved in
minutes instead of a week, at a fair price.

Fiercest-competitor test: the big-six cannot say this. Their call centres are built to
deflect, their staff are not empowered to credit or resolve, and copying the claim would
mean dismantling the operational model that makes their business work. They would concede
the claim is true and dispute that it is worth their economics, which is the sign of a
defensible strategy rather than an empty one (CLAIM(kIw__JxmbUo), CLAIM(y1-5nxulR68)).

## 5. Execution

**Delivery** (what the business physically does, so the claim is true):
- Staffing and shift design: answer-rate targets, not deflection targets.
- Empowerment policy: what a person on the phone may decide, credit or change without
  approval, written down.
- Onboarding and training: the phone call is the product, so it is rehearsed.
- Technology: a routing layer that gets a human in seconds, never a menu tree.

**Communication** (how the customer hears it):
- The advertisement states the operational fact, with no adjective it cannot pay for:
  "outstanding customer service at fair prices".
- Copy on the site and in the switcher flow leads with the problem the customer is calling
  about, not with the company's story (CLAIM(qxdY2kdKz9g), CLAIM(ElaWyEeHS1w)).
- Story shape: you know the feeling of a supplier who makes you ring back, we are the one
  who answers, so you are done in minutes (CLAIM(uAP9fPmv35U)).

## What this document deliberately does not do

- It does not claim the innovation was profitable. The corpus presents Octopus as the
  example of a concrete innovation behind a claimed virtue; profitability is not in the
  corpus and is not asserted here.
- It does not claim any market share or customer number. Creator figures elsewhere in the
  corpus are unverified creator claims and stay labelled as such.
- It does not turn "outstanding customer service" into a virtue claim: the sentence is
  admissible only because the innovation behind it is concrete and observable.

## Gate record (recorded, not edited to look good)

- `strategy_lint.py examples/great/business-ops/great-strategy-document.md`: **0 high
  findings**, exit 0. The linter's own self-test still trips 11 high findings on the
  boilerplate red fixture, so the clean result is not a blind gate.
- `rig-s1gate check strategy.output --subject strategy.output:octopus-exemplar`: **ESCALATE**
  (`genuine_disagreement` 0.90, `only_claim_holds` 0.79, `externally_visible` 0.88,
  `specificity` 4.83 at confidence 0.89; `tradeoffs_named` 0.98, `concrete_innovation` 0.94,
  `category_customer_frame` 0.93, `strategy_not_goal` 0.91).
- **Why Jev escalated, and why it is right.** The claim "the only UK energy supplier who
  answers the phone with a human" was a *historical* only. Jev, reading what the category
  looks like now, judges that other suppliers have since adopted human-answer models, so the
  only-claim no longer survives the fiercest-competitor test. A linter cannot see that; only
  a judgment can. This is the gate working, not failing.
- **What a stronger statement would need**: a Z that competitors structurally cannot
  reproduce - for example an empowerment depth (what a person may decide on the call, up to
  what credit) that no rival's operating model allows, stated as a specific number or limit
  rather than a virtue. That is a rewrite for a live business to make, not for an exemplar to
  fake.
- **Verdict under the ladder**: *Park*. Sound argument, right era, only-claim no longer
  current; the trigger to revive it is a re-test of the competitive set, not more writing.
- Every CLAIM(videoId) above resolves in `data/corpora/strategy/manifest.jsonl`
  (`claims_check.py`).
