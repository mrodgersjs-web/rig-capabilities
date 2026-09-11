"""Single-transaction production deploy worker for cockpit-v2 (v1).

Grammar per the jarvis_blackwell_activation v13 precedent: one external
subprocess.call per entrypoint invocation, no conditionals, no local-object
method calls, no higher-order builtins. The staged transaction script (bound
by sha256 in the Gate-D ACTION file, NOT here) enforces ordering executably
with set -e:

  1. literal-hash verification of its own staged bytes against the ACTION
     binding,
  2. deploy directory must be at the approved commit (git rev-parse check),
  3. vercel whoami must succeed (login performed out-of-band by the operator;
     no token is stored, printed, or bound here),
  4. exactly one upload deploy to the bound project/org,
  5. post-deploy READY + live-URL health check,
  6. proof JSON written last.

The approved effect is the production upload deploy ONLY. No secret is passed
through this process; Vercel credentials live in the operator's own login
session and never in the ACTION file, worker bytes, or proof.
"""

import subprocess


def run_deploy_transaction(arguments):
    return subprocess.call(arguments)


def deploy(transaction_arguments):
    status = run_deploy_transaction(transaction_arguments)
    return (status,)
