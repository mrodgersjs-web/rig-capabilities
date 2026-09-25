---
name: web-design-business-client
description: Run the client relationship end to end: discovery calls, a phased delivery process, revision control with closed rounds, handoff and training, and retainers after launch.
outcome: A repeatable client process with a written revision policy, a dated revision log, a recorded walkthrough, a training and launch call, and a post-launch retainer decision.
done_when:
  - A project file contains the signed contract, the revision policy the client received before work started, a revision log showing each round with its
great_example: examples/great/design-ux/web-design-business-client.md
quality_floor: Any work that started before the revision policy was sent fails the job. Any revision round without an open date and a close date fails. Any handoff without a recorded walkthrough plus a live call fails the floor.
activation: Load when onboarding a new client, running a discovery or kickoff call, drafting a process document, when revisions are going past the agreed rounds, at handoff and launch, or when a client asks for ongoing support after the site ships.
instruction: Run every client through the same phases: setup, questionnaire, research, kickoff call, structure, design, revision rounds, and launch. Put the revision policy in writing before work starts with a round cap, a feedback deadline, and automatic approval when the deadline passes, and close each round explicitly so reopening it is a paid change. Deliver handoff as a recorded walkthrough plus a live training and launch call, and offer a retainer only after the project has shipped.
applies_when:
  env: Paid client web design engagements from signed contract through launch and optional ongoing support
  runtime: web page or site rendered in a browser
  deps: the project brief and its design system
  params: Paid client web design engagements from signed contract through launch and optional ongoing support. Applies to solo designers and small studios. Does not apply to internal project
  budget: one pass per artifact
  scale: single page up to a full marketing site
permissions:
  - May read client briefs
  - contracts
  - call notes
  - the local corpus at /Users/rig128gb/Developer/rig-design-studio/corpus/youtube
  - may write process documents
  - onboarding packs
  - revision logs
  - walkthrough recordings plans
  - handoff checklists into the project workspace. Outward sends
  - invoices
  - deploys
  - launches
  - purchases need Gate-D approval from Mike
flow:
  - Send the contract, then the welcome pack and questionnaire;
  - Research the client's market and three competitor sites;
  - Run the kickoff call and confirm the brief out loud;
  - Deliver structure (see web-design-discovery-sitemap) and collect written sign-off;
  - Deliver design in agreed stages with a feedback deadline per stage;
  - Close each revision round explicitly and record it;
  - Bill the balance and hand off with a recorded walkthrough and a live training and launch call;
  - Offer a retainer only after launch, with a named monthly scope
out_of_scope:
  - The discovery and structure craft (see web-design-discovery), pricing and quoting (see web-design-business-pricing), legal advice on contract terms,
---
# Web Design Business Client

## Method

One process for every client, written down and sent to them before work starts. Self-Made Web Designer's onboarding runs four phases up front: setup, the questionnaire, research, and the kickoff call. The setup phase is the contract and the templates. The questionnaire is deliberately substantial, and you warm the client that it is: a big intake form gets better answers when they know it is coming.

The kickoff call is where the brief gets confirmed out loud. Paige Brunton's process shows the pattern of a content call at the start of the design phase: discussing the content, asking questions, and settling the expectations before pixels. Will Paterson's question series covers who they are, what they do, what they provide, and why they are different. Take notes verbatim and read the brief back before ending the call.

Revision control is the highest-value habit in client work, and it starts before the work, not after the trouble. Self-Made Web Designer's rule set: by the time you are doing revisions it is too late to fix the problem, so onboarding must include a crystal clear revision policy that tells the client how many rounds they get and when feedback is due. His own cap is two rounds (UNVERIFIED numeric: caption says one round for the homepage and one for the other pages, with a 48-hour feedback window that counts as automatic approval if it passes).

Close rounds explicitly. The corpus version of the rule is the strongest line in this skill: when a client asks to go back and change an earlier stage, "the answer is that round of revisions is currently closed". Offer the paid path at that moment: an additional fee reopens the round. Your revision log records the round, what stage it covered, when it opened, when it closed, and the change order if one was bought.

Feedback deadlines with consequences. Give every round a fixed feedback window and treat silence as approval so the project keeps moving (Self-Made Web Designer gives clients 24 hours on review items: UNVERIFIED numeric). Put the deadline and its consequence in the onboarding document, then enforce it once. Designers who enforce it the first time rarely have to argue about it later.

Explain your reasoning when you present. Self-Made Web Designer attributes revision reduction to being able to say "this is why I put this here", and presents with a recorded walkthrough plus a call when useful. Clients do not fight decisions they understand.

Handoff has two parts and both are mandatory: a recorded walkthrough the client can keep (Loom-style), and a live training and launch call where they learn to perform their own routine tasks. Paige Brunton's process names it directly: she has the client book a training and launch call and trains them during it. Bill the balance before or at go-live, and confirm the site's working state from the client's own browser in the call.

Retainers come after launch, never before. The corpus vocabulary is simple: hourly, daily, weekly, and monthly arrangements, with the recurring ones usually called retainers, and subscription models where a monthly fee buys a set amount of work. Sell maintenance or ongoing design as a named monthly scope with an allowance, to the client who has already seen you ship.

## Corpus evidence

- Self-Made Web Designer / This Web Design Process Cut My Project Times in Half / O96t2rfwmak / [02:29] / I only give my clients two rounds of revisions
- Self-Made Web Designer / This Web Design Process Cut My Project Times in Half / O96t2rfwmak / [02:45] / In that time, it's considered an automatic approval and the project keeps moving
- Self-Made Web Designer / Complete Web Design Process: What Took Me 10 Years to Learn in 12 Minutes [Free Trello Template] / T5JglDcd54A / [07:59] / The answer is that round of revisions is currently closed
- Self-Made Web Designer / Complete Web Design Process: What Took Me 10 Years to Learn in 12 Minutes [Free Trello Template] / T5JglDcd54A / [06:55] / So I'll include a loom video and sometimes I'll even jump on a call
- Paige Brunton / Complete Beginners Guide to Web Design Client Process / yO1U2v9h0S8 / [06:50] / training and launch call.
- Self-Made Web Designer / Scale a 1 to 1 Web Design Business with Productized Services / jVtIzLoQIxM / [33:32] / daily weekly monthly we usually call

## Anti-patterns

- Revision roulette: no written cap, so every round is a new negotiation and the project never ends.
- Round that never closes: taking feedback in five scattered messages so nobody can say when a stage was approved.
- Deadline without teeth: a feedback window that gets ignored and extended twice, teaching the client the schedule is fiction.
- Handoff via zip file: dumping logins and a folder with no walkthrough and no live call, then answering the same six questions for a month.
- Retainer premature: pitching monthly work before the site is live, so the recurring offer has no proof behind it.

## Links

parent: web-design-business
children: none

## Contract detail (full text)

- A project file contains the signed contract, the revision policy the client received before work started, a revision log showing each round with its open and close date, a walkthrough recording or script, a completed training and launch call note, and a dated retainer offer or an explicit decision not to make one
- The discovery and structure craft (see web-design-discovery), pricing and quoting (see web-design-business-pricing), legal advice on contract terms, ad buying, SEO campaigns, and anything that binds money or launches publicly without Mike's Gate-D approval
