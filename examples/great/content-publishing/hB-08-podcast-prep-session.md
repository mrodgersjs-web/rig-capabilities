---
name: great-hB-08-podcast-prep-session-yaml
lane: content-publishing
exemplar_of: hB-08-podcast-prep-session.yaml
description: Reference exemplar for a researched podcast run sheet with novel questions, timed ladders, follow-up forks, logistics, and provenance.
---

# hB-08-podcast-prep-session.yaml — great example

## Input

Prepare a 45-minute interview around one through-line and one listener takeaway. Research the guest's biography, three prior appearances, five known positions, and two contradictions. Prior transcripts are available for checking whether each proposed question has already been answered.

## Output

The dossier links its sources; the run sheet sequences warmup, core, stretch, and close with a balanced time budget. Each core question has two conditional follow-ups. `logistics.yaml` records the primary link, backup plan, one-sheet path, and promotion obligations; sensitive-topic handling and voice-matched intro/outro are present.

```console
$ python3 scripts/question_novelty.py "$SESS/questions.md" "$SESS/prior_transcripts/" --min 0.7
# expected: every question clears the novelty threshold

$ python3 scripts/run_sheet_math.py "$SESS/runsheet.yaml"
# expected: exit 0 and proof/run_math.json lands within ±10% of target runtime

$ sha256sum -c "$SESS/proof/packet.sha256"
# expected: dossier, run sheet, novelty report, and logistics hashes verify
```

## Acceptance

- `throughline.yaml` contains one through-line and one actionable takeaway.
- The dossier includes all required appearances, positions, and contradictions with at least three URLs.
- Every core question has two forks and cites its research origin; generic biography prompts do not survive.
- The one-sheet exists, backup recording is explicit, sensitive topics are mapped or cleared, and the packet is sealed.
