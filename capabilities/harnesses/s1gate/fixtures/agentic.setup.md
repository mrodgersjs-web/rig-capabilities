# Setup receipt: plain-code baseline (agentic-proof-ladder), 2026-09-28

Framework: none (framework-free hello, the baseline every framework must beat). Route: Aside sandbox.
Probe: capabilities/skills/agentic-env-probe/references/probe-2026-09-28.json (09:25 MDT).

| Level | Command | Exit | Observed |
|---|---|---|---|
| L0 docs | fetched https://www.anthropic.com/engineering/building-effective-agents on 2026-09-28 | 200 | text sha256 89870adf27e0; quote "we recommend finding the simplest solution possible"; pinned: CPython 3.13.12 stdlib, no packages |
| L1 install | `env -u PYTHONHOME -u PYTHONPATH python3 --version` | 0 | Python 3.13.12 |
| L2 fake model | `python3 scripts/hello_baseline.py --model fake` | 0 | model fake:scripted-add requested add(2,3); result 5; assertion add(2,3)==5 PASS |
| L3 local model | `python3 scripts/hello_baseline.py --model local` | 0 | endpoint http://127.0.0.1:8771/v1, model qwen3.8-uncensored:27b, content "5", finish_reason stop, 2.02 s, thinking disabled |

Not attempted: L4 (a framework-free baseline has no durable runtime; L4 belongs to the framework skills),
L5 (nothing to deploy). Blocked on this machine today and recorded, not hidden: Docker route
(`docker info`: cannot connect to ~/.colima/default/docker.sock; Colima 0.10.3 is installed but not running). JVM: the
macOS `java` stub fails; JDK 26 is installed keg-only at ~/.homebrew/opt/openjdk@26 and this baseline did not need it.

Secrets: none used; local route is keyless. Fallback named, not used: OpenRouter via keychain item
com.rig.env.OPENROUTER_API_KEY. No deploy, signup, push, or paid call happened.
Validator: `proof_ladder.py fixtures/receipt_baseline_real.json` -> 0 violations, highest proven level L3.
