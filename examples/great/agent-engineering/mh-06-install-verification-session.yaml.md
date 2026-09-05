---
name: great-mh-06-install-verification-session
lane: agent-engineering
source: canonical-curated
exemplar_of: mh-06-install-verification-session
description: "Reference exemplar for certifying an installed asset through source hashing, destination identity, discoverability, and demonstrated RED-to-GREEN recovery."
---

# Install verification: copied capability

## Input

Pin one source asset, declare `copy` as the install method, and enumerate every destination before writing. Capture the source hash and pre-install done-test result; archive any non-identical destination rather than clobbering it.

```console
$ ./bin/rig-capabilities goal-spec --stem mh-06-install-verification-session
$ python3 ~/Developer/needle-haystack/artifacts/meta/mathexec_substrate.py self-test
$ sha256sum <source-file>
```

## Output

The installed copies hash-match the source and are visible through their intended discovery surfaces. The asset done-test passes from each installed location. A temporary copy is then sabotaged so the same done-test exits non-zero with an informative message; after restoration, it exits 0 again. `install-record.json` contains `name`, `path`, `sha256`, `green_exit`, `red_exit`, and `red_message`, followed by a recomputable chained seal and a round-tripped `install_certified` event.

## Acceptance

- The goal-spec and MathExec commands exit 0; MathExec prints `SELF-TEST PASS`.
- `red-proof.txt` records sabotage, non-zero exit, revert, and final zero exit in that order.
- Every manifest destination has independent mechanics and RED-path evidence.
- Certification is blocked if the done-test stays green under sabotage, and the installed asset is left restored.
