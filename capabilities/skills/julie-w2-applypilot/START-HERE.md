# Run Julie in Hermes

Run only the bounded supervised-Flash preflight first. It is not permission to run the full application mission:

```bash
hermes --rig-task "Validate Julie W2 application prerequisites" chat \
  --oneshot -Q \
  --provider rig-blackwell-qwen38-flash \
  --model blackwell-qwen38-flash \
  --skills julie-w2-applypilot,ego-browser \
  --toolsets terminal,file,skills,todo \
  --query-file /Users/rig128gb/.hermes/skills/julie-w2-applypilot/PREFLIGHT-PROMPT.md \
  --run-budget 180 --max-turns 10
```

The supported `chat --oneshot -Q` path returns a compact, machine-readable preflight result and exits within its 180-second, ten-turn bound. It preserves the configured safety rules but keeps Flash output quarantined until independent review. Never use top-level `--oneshot`: it enables a bypass mode. Do not paste `PROMPT.md` into a general session or launch a full mission from this package; a receipt-bearing application requires separate supervised dispatch, current browser ownership, and independent artifact review. Run the dependency/ledger preflight without inference:

```bash
python3 /Users/rig128gb/.hermes/skills/julie-w2-applypilot/scripts/preflight.py
```

Read `references/CAPABILITIES.md` for every dependency and `references/HANDOFF.md` for the starting state. `prompts/WORKERS.md` supplies the worker contracts. `PROMPT.md` is the full reusable instruction, including approved scope, screening defaults, ATS quality, applications, outreach, learning and fallbacks.

Acceptance: dependency/ledger preflight and Hermes's ability to load the skill are tested separately from a real submitted application. Do not claim the latter until Hermes produces and verifies an employer receipt. The existing daily Codex schedule is not automatically replaced by installing this package.
