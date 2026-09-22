# LinkedIn Comment — RIG Communication Protocol V10

## Formula

```
CommentValue = 0.30*AddedInsight + 0.25*SpecificEvidence + 0.20*DisagreementQuality
             + 0.15*QuestionAsked + 0.10*AuthoritySignal
```

## Gate

`if Comment == generic agreement → DON'T POST`

## Deviation Ladder

| Lv | Example |
|----|---------|
| **0** | "🔥 Great post!" / "Totally agree" / "Thanks for sharing" |
| **+3** | Adds a specific data point or personal experience that extends the post's thesis |
| **+5** | Respectfully disagrees with evidence, creating a mini-debate that attracts attention |
| **+7** | Provides a framework or insight that's more valuable than the original post |
| **+10** | The comment becomes more shared/saved than the post itself |

## Targets
- L4 (Comment Magnetism): +3 to +5
- **Min to ship:** L4 ≥ +3

## Comment Types That Ship

**Type 1: Build (+3σ)**
Add a new data point the original author didn't include. Name a specific company, statistic, or personal experience.

**Type 2: Extend (+5σ)**
Take the author's thesis one step further. "The pattern you described also explains X in Y industry." Adds new territory.

**Type 3: Challenge (+7σ)**
Respectfully disagree with evidence. "The data shows the opposite for companies under $10M ARR." Creates a mini-debate that attracts attention from both sides.
