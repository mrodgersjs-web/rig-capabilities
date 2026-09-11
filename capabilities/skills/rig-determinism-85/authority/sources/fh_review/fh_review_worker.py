import subprocess

def run_job(job):
    return seal(witness(failure(remediate(validate(review(attest(job)))))))

def attest(job):
    return subprocess.call(["/bin/sh", "-c", "PATH=/usr/bin:/bin; export PATH; w=/tmp/fh-review-run; if mkdir \"$w\" 2> /dev/null; then cp /tmp/fh-prompt.md \"$w/prompt.md\" && cp /tmp/fh-evidence.md \"$w/evidence.md\" && shasum -a 256 \"$w/prompt.md\" \"$w/evidence.md\" > \"$w/attest.sha256\" && { cat \"$w/prompt.md\"; awk '{print \"EVIDENCE: \" $1}' \"$w/attest.sha256\"; } > \"$w/review-input.md\" || { rm -rf \"$w\"; exit 1; }; exit 0; else echo NO_LOCK; exit 17; fi"])

def review(status):
    return subprocess.call(["/bin/sh", "-c", "PATH=/usr/bin:/bin; export PATH; w=/tmp/fh-review-run; if test \"$1\" -ne 0; then echo NO_LOCK; exit 17; fi; cd \"$w\" && /Users/rig128gb/.rig/bin/fusion-harness omp --stack rig5 -p @review-input.md --max-time 15m --no-session > verdict.md 2> verdict.err; echo rc=$? > launch.rc", "sh", str(status)])

def validate(receipt):
    return subprocess.call(["/bin/sh", "-c", "PATH=/usr/bin:/bin; export PATH; w=/tmp/fh-review-run; if test \"$1\" -ne 0; then echo UNVERIFIED; exit 17; fi; ok=1; test -f \"$w/verdict.md\" || ok=0; test -f \"$w/launch.rc\" || ok=0; grep -q ^rc=0$ \"$w/launch.rc\" || ok=0; p=$(grep -c ^PARTICIPANT: \"$w/verdict.md\" 2> /dev/null) || p=0; t=$(grep -c ^VERDICT: \"$w/verdict.md\" 2> /dev/null) || t=0; v=$(grep -cE '^VERDICT: (PASS|REVISE|BLOCK)$' \"$w/verdict.md\" 2> /dev/null) || v=0; c=$(grep -cE '^CONSENSUS: (PASS|REVISE|BLOCK)$' \"$w/verdict.md\" 2> /dev/null) || c=0; m=$(grep -cE '^MARKER: EVIDENCE-MARKER-[a-z]+$' \"$w/verdict.md\" 2> /dev/null) || m=0; e=$(grep -cE '^EVIDENCE: [0-9a-f]{64}$' \"$w/verdict.md\" 2> /dev/null) || e=0; hp=$(sed -n 1p \"$w/attest.sha256\" | awk '{print $1}'); he=$(sed -n 2p \"$w/attest.sha256\" | awk '{print $1}'); u=$(grep '^PARTICIPANT: ' \"$w/verdict.md\" 2> /dev/null | sed 's/^PARTICIPANT:[[:space:]]*//' | tr 'A-Z' 'a-z' | sed 's/[[:space:]]*$//' | sed '/^$/d' | sort -u | wc -l | tr -d ' ') || u=0; test \"$p\" -eq 4 || ok=0; test \"$u\" -eq 4 || ok=0; test \"$t\" -eq \"$p\" || ok=0; test \"$v\" -eq \"$t\" || ok=0; test \"$c\" -eq 1 || ok=0; test \"$m\" -eq \"$t\" || ok=0; test \"$e\" -ge 2 || ok=0; test -n \"$hp\" || ok=0; test -n \"$he\" || ok=0; grep -q \"^EVIDENCE: $hp$\" \"$w/verdict.md\" || ok=0; grep -q \"^EVIDENCE: $he$\" \"$w/verdict.md\" || ok=0; if test \"$ok\" -eq 1; then grep ^CONSENSUS: \"$w/verdict.md\" > \"$w/status.txt\"; exit 0; fi; echo UNVERIFIED > \"$w/status.txt\"; exit 1", "sh", str(receipt)])

def remediate(status):
    return subprocess.call(["/bin/sh", "-c", "PATH=/usr/bin:/bin; export PATH; w=/tmp/fh-review-run; if test \"$1\" -eq 17; then echo NO_LOCK; exit 17; fi; if test \"$1\" -ne 0; then printf FH_NO_VERDICT > \"$w/fallback.md\"; exit 1; fi; cp \"$w/verdict.md\" \"$w/fallback.md\"", "sh", str(status)])

def failure(status_ok):
    return subprocess.call(["/bin/sh", "-c", "PATH=/usr/bin:/bin; export PATH; w=/tmp/fh-review-run; if test \"$1\" -eq 17; then echo NO_LOCK; exit 17; fi; if test \"$1\" -ne 0; then echo FH_REVIEW_FAILED >> \"$w/failure.md\"; exit 1; fi; exit 0", "sh", str(status_ok)])

def witness(marker):
    return subprocess.call(["/bin/sh", "-c", "PATH=/usr/bin:/bin; export PATH; w=/tmp/fh-review-run; if test \"$1\" -ne 0; then exit \"$1\"; fi; shasum -a 256 \"$w/attest.sha256\" \"$w/review-input.md\" \"$w/fallback.md\"; shasum -a 256 \"$w/verdict.md\"; exit 0", "sh", str(marker)])

def seal(receipts):
    return subprocess.call(["/bin/sh", "-c", "PATH=/usr/bin:/bin; export PATH; w=/tmp/fh-review-run; if test \"$1\" -eq 17; then echo NO_LOCK_NO_MANIFEST; exit 17; fi; if test \"$1\" -ne 0; then cat \"$w/failure.md\" \"$w/fallback.md\" > \"$w/manifest.md\" || exit 1; else cat \"$w/attest.sha256\" \"$w/status.txt\" \"$w/verdict.md\" \"$w/fallback.md\" > \"$w/manifest.md\" || exit 1; fi; test -s \"$w/manifest.md\" || exit 1; rm -rf /tmp/fh-review-last || exit 1; mv \"$w\" /tmp/fh-review-last || exit 1; exit \"$1\"", "sh", str(receipts)])
