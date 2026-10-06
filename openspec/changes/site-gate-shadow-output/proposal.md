# Preserve input workspaces during shadow verification

## Why

The current gate invalidates and overwrites the input site's result before trust admission. A shadow evaluation must not replace an existing production result, including when evidence is rejected.

## What Changes

- Add an explicit stdout-only `--dry-run` mode for single-site and portfolio invocations.
- Forbid Airtable writes and output-path arguments in this mode; propagate it to each portfolio child.
- Preserve legacy non-shadow verdict, invalidation and provider behavior.
- Prove input file bytes and directory/file metadata remain unchanged in disposable synthetic success, failure and refusal cases.

## Impact

Only the canonical site-gate implementation, regression suite and contract documentation change. No production invocation, website edit, trust enrollment, install, publication or acceptance claim is included.
