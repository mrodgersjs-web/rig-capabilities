# Rejected pattern: unsourced numbers

Bare metrics (not 19xx/20xx years) with no source in the same paragraph trip the
fabrication gate (gates.py `_NUMBER` regex, hard block on public lanes).
Fix: attach the source or delete the number. Years are context, not claims.
