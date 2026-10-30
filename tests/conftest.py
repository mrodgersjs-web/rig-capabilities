# pytest collection policy for the fixtures tree.
#
# fixtures/<branch>/dispatch-captured/ holds the anti-fabrication canary exactly as
# it failed during its dispatch run (canary.py doctrine: the planted failure is kept
# as a regression fixture, reported BY NAME with its real output in canary-run.log).
# It is evidence — a frozen record of "the suite can go red and the dispatcher says
# so" — not a live test. Collecting it makes every future suite permanently red and
# destroys the canary's signal (a always-failing failure can't detect fabrication).
# The LIVE canary instance lives outside every worktree under the state root and is
# rotated per dispatch; only its captured log stays here, uncollected.
collect_ignore_glob = ["fixtures/*/dispatch-captured/*.py"]
