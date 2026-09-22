"""fleet_routing_v2 — immutable deterministic routing authority for the RIG fleet.

v2 supersedes fleet_routing_v1: v1 was terminally BLOCKed at score time
(SOURCE_UNSUPPORTED_GRAMMAR, exit 2) — module-level Assign of the PLANES table
is outside the D85 closed module grammar. Under the exit-2 rule v1 is never
retried; it is preserved as failed evidence.

v2 redesign under the closed grammar (no module-level data, no conditionals,
no comparisons, no subscripts, no keyword arguments):

- Tables are returned by plain functions; every function is TOTAL (unknown
  role/endpoint/plane yields "" / {} / () / False instead of v1's KeyError).
- Conditional routing is precomputed dispatch: ROUTE_TABLE and
  TWO_PLANES_TABLE were GENERATED from v1's route_for_role /
  role_has_two_planes over all 16 live-plane sets x 8 roles and verified
  cell-for-cell against v1 before this file was written.
- All threshold COMPARISONS move to the executor/monitor. The authority
  exposes limits, never verdicts. Executor contract (v1 check_endpoint
  semantics): FAIL when ttft_s > ttft_s_fail; else DEGRADED when
  ttft_s > ttft_s_max or tps < tps_min; else PASS. Paid lane: executor stops
  the lane when quota_pct >= paid_quota_stop_pct().
- planes_down arguments name DOWN planes (v1 semantics); route keys are the
  derived LIVE-plane tuples, sorted-canonical.

# ponytail: tables rebuild per call because the grammar forbids module-level
# constants; O(tiny) literals — revisit only if a profiler names this hot.
# Any content change requires a NEW process-id (fleet_routing_v3, ...).
"""


def planes():
    return {'P1': {'name': 'mac-ollama-pair', 'quota_governed': False},
 'P2': {'name': 'blackwell-gpu', 'quota_governed': False},
 'P3': {'name': 'omlx-mlx', 'quota_governed': False},
 'P4': {'name': 'paid-subscription', 'quota_governed': True}}


def endpoints():
    return {'flash': {'model': 'blackwell-qwen38-flash',
           'plane': 'P2',
           'tps_min': 100.0,
           'ttft_s_max': 2.0,
           'url': 'http://192.168.68.90:8011/v1/chat/completions'},
 'instruct_256': {'model': 'qwen3.8-27b-uncensored:instruct',
                  'plane': 'P3',
                  'tps_min': 80.0,
                  'ttft_s_max': 10.0,
                  'url': 'http://127.0.0.1:8657/v1/chat/completions'},
 'mimo_cloud': {'model': 'mimo-v2.5-pro',
                'plane': 'P4',
                'tps_min': 1.0,
                'ttft_s_max': 45.0,
                'url': 'http://127.0.0.1:8655/v1/chat/completions'},
 'pair_local': {'model': 'rig-96gb-laguna:latest',
                'plane': 'P1',
                'tps_min': 40.0,
                'ttft_s_max': 3.0,
                'url': 'http://127.0.0.1:11435/v1/chat/completions'},
 'quality_96': {'model': 'qwen3.8-27b-oq6:instruct',
                'plane': 'P3',
                'tps_min': 80.0,
                'ttft_s_max': 10.0,
                'url': 'http://127.0.0.1:8771/v1/chat/completions'},
 'uncensored': {'model': 'blackwell-qwen38-uncensored',
                'plane': 'P2',
                'tps_min': 40.0,
                'ttft_s_max': 5.0,
                'url': 'http://127.0.0.1:8656/v1/chat/completions'}}


def degradation_order():
    return ("P2", "P3", "P1", "P4")


def role_routes():
    return {'architecture': ('instruct_256', 'quality_96', 'pair_local'),
 'coding': ('flash', 'instruct_256', 'pair_local'),
 'paid_fallback': ('mimo_cloud',),
 'planning': ('uncensored', 'instruct_256', 'pair_local'),
 'research': ('uncensored', 'pair_local', 'quality_96'),
 'strategy': ('instruct_256', 'quality_96', 'pair_local'),
 'triage': ('pair_local', 'flash'),
 'vision': ('instruct_256', 'quality_96')}


def kill_switches():
    return {'KS1': {'action': 'remove from rotation', 'detect': 'loopback endpoint dead x2'},
 'KS2': {'action': 'hard stall prevention', 'detect': 'role has fewer than 2 live planes'},
 'KS3': {'action': 'bypass P1 to node proxies', 'detect': 'pair_local api dead'},
 'KS4': {'action': 'degrade to P3', 'detect': 'P2 endpoints both dead'},
 'KS5': {'action': 'hard stop paid lane', 'detect': 'paid quota exhausted'},
 'KS6': {'action': 'kill and report', 'detect': 'inference process on rig-128gb'},
 'KS7': {'action': 'route to instruct_256', 'detect': 'uncensored ttft over 15s twice'}}


def paid_quota_stop_pct():
    return 98


def route_table():
    return {'architecture': {(): '',
                  ('P1',): 'pair_local',
                  ('P1', 'P2'): 'pair_local',
                  ('P1', 'P2', 'P3'): 'instruct_256',
                  ('P1', 'P2', 'P3', 'P4'): 'instruct_256',
                  ('P1', 'P2', 'P4'): 'pair_local',
                  ('P1', 'P3'): 'instruct_256',
                  ('P1', 'P3', 'P4'): 'instruct_256',
                  ('P1', 'P4'): 'pair_local',
                  ('P2',): '',
                  ('P2', 'P3'): 'instruct_256',
                  ('P2', 'P3', 'P4'): 'instruct_256',
                  ('P2', 'P4'): '',
                  ('P3',): 'instruct_256',
                  ('P3', 'P4'): 'instruct_256',
                  ('P4',): ''},
 'coding': {(): '',
            ('P1',): 'pair_local',
            ('P1', 'P2'): 'flash',
            ('P1', 'P2', 'P3'): 'flash',
            ('P1', 'P2', 'P3', 'P4'): 'flash',
            ('P1', 'P2', 'P4'): 'flash',
            ('P1', 'P3'): 'instruct_256',
            ('P1', 'P3', 'P4'): 'instruct_256',
            ('P1', 'P4'): 'pair_local',
            ('P2',): 'flash',
            ('P2', 'P3'): 'flash',
            ('P2', 'P3', 'P4'): 'flash',
            ('P2', 'P4'): 'flash',
            ('P3',): 'instruct_256',
            ('P3', 'P4'): 'instruct_256',
            ('P4',): ''},
 'paid_fallback': {(): '',
                   ('P1',): '',
                   ('P1', 'P2'): '',
                   ('P1', 'P2', 'P3'): '',
                   ('P1', 'P2', 'P3', 'P4'): 'mimo_cloud',
                   ('P1', 'P2', 'P4'): 'mimo_cloud',
                   ('P1', 'P3'): '',
                   ('P1', 'P3', 'P4'): 'mimo_cloud',
                   ('P1', 'P4'): 'mimo_cloud',
                   ('P2',): '',
                   ('P2', 'P3'): '',
                   ('P2', 'P3', 'P4'): 'mimo_cloud',
                   ('P2', 'P4'): 'mimo_cloud',
                   ('P3',): '',
                   ('P3', 'P4'): 'mimo_cloud',
                   ('P4',): 'mimo_cloud'},
 'planning': {(): '',
              ('P1',): 'pair_local',
              ('P1', 'P2'): 'uncensored',
              ('P1', 'P2', 'P3'): 'uncensored',
              ('P1', 'P2', 'P3', 'P4'): 'uncensored',
              ('P1', 'P2', 'P4'): 'uncensored',
              ('P1', 'P3'): 'instruct_256',
              ('P1', 'P3', 'P4'): 'instruct_256',
              ('P1', 'P4'): 'pair_local',
              ('P2',): 'uncensored',
              ('P2', 'P3'): 'uncensored',
              ('P2', 'P3', 'P4'): 'uncensored',
              ('P2', 'P4'): 'uncensored',
              ('P3',): 'instruct_256',
              ('P3', 'P4'): 'instruct_256',
              ('P4',): ''},
 'research': {(): '',
              ('P1',): 'pair_local',
              ('P1', 'P2'): 'uncensored',
              ('P1', 'P2', 'P3'): 'uncensored',
              ('P1', 'P2', 'P3', 'P4'): 'uncensored',
              ('P1', 'P2', 'P4'): 'uncensored',
              ('P1', 'P3'): 'pair_local',
              ('P1', 'P3', 'P4'): 'pair_local',
              ('P1', 'P4'): 'pair_local',
              ('P2',): 'uncensored',
              ('P2', 'P3'): 'uncensored',
              ('P2', 'P3', 'P4'): 'uncensored',
              ('P2', 'P4'): 'uncensored',
              ('P3',): 'quality_96',
              ('P3', 'P4'): 'quality_96',
              ('P4',): ''},
 'strategy': {(): '',
              ('P1',): 'pair_local',
              ('P1', 'P2'): 'pair_local',
              ('P1', 'P2', 'P3'): 'instruct_256',
              ('P1', 'P2', 'P3', 'P4'): 'instruct_256',
              ('P1', 'P2', 'P4'): 'pair_local',
              ('P1', 'P3'): 'instruct_256',
              ('P1', 'P3', 'P4'): 'instruct_256',
              ('P1', 'P4'): 'pair_local',
              ('P2',): '',
              ('P2', 'P3'): 'instruct_256',
              ('P2', 'P3', 'P4'): 'instruct_256',
              ('P2', 'P4'): '',
              ('P3',): 'instruct_256',
              ('P3', 'P4'): 'instruct_256',
              ('P4',): ''},
 'triage': {(): '',
            ('P1',): 'pair_local',
            ('P1', 'P2'): 'pair_local',
            ('P1', 'P2', 'P3'): 'pair_local',
            ('P1', 'P2', 'P3', 'P4'): 'pair_local',
            ('P1', 'P2', 'P4'): 'pair_local',
            ('P1', 'P3'): 'pair_local',
            ('P1', 'P3', 'P4'): 'pair_local',
            ('P1', 'P4'): 'pair_local',
            ('P2',): 'flash',
            ('P2', 'P3'): 'flash',
            ('P2', 'P3', 'P4'): 'flash',
            ('P2', 'P4'): 'flash',
            ('P3',): '',
            ('P3', 'P4'): '',
            ('P4',): ''},
 'vision': {(): '',
            ('P1',): '',
            ('P1', 'P2'): '',
            ('P1', 'P2', 'P3'): 'instruct_256',
            ('P1', 'P2', 'P3', 'P4'): 'instruct_256',
            ('P1', 'P2', 'P4'): '',
            ('P1', 'P3'): 'instruct_256',
            ('P1', 'P3', 'P4'): 'instruct_256',
            ('P1', 'P4'): '',
            ('P2',): '',
            ('P2', 'P3'): 'instruct_256',
            ('P2', 'P3', 'P4'): 'instruct_256',
            ('P2', 'P4'): '',
            ('P3',): 'instruct_256',
            ('P3', 'P4'): 'instruct_256',
            ('P4',): ''}}


def two_planes_table():
    return {'architecture': {(): False,
                  ('P1',): False,
                  ('P1', 'P2'): False,
                  ('P1', 'P2', 'P3'): True,
                  ('P1', 'P2', 'P3', 'P4'): True,
                  ('P1', 'P2', 'P4'): False,
                  ('P1', 'P3'): True,
                  ('P1', 'P3', 'P4'): True,
                  ('P1', 'P4'): False,
                  ('P2',): False,
                  ('P2', 'P3'): False,
                  ('P2', 'P3', 'P4'): False,
                  ('P2', 'P4'): False,
                  ('P3',): False,
                  ('P3', 'P4'): False,
                  ('P4',): False},
 'coding': {(): False,
            ('P1',): False,
            ('P1', 'P2'): True,
            ('P1', 'P2', 'P3'): True,
            ('P1', 'P2', 'P3', 'P4'): True,
            ('P1', 'P2', 'P4'): True,
            ('P1', 'P3'): True,
            ('P1', 'P3', 'P4'): True,
            ('P1', 'P4'): False,
            ('P2',): False,
            ('P2', 'P3'): True,
            ('P2', 'P3', 'P4'): True,
            ('P2', 'P4'): False,
            ('P3',): False,
            ('P3', 'P4'): False,
            ('P4',): False},
 'paid_fallback': {(): False,
                   ('P1',): False,
                   ('P1', 'P2'): False,
                   ('P1', 'P2', 'P3'): False,
                   ('P1', 'P2', 'P3', 'P4'): False,
                   ('P1', 'P2', 'P4'): False,
                   ('P1', 'P3'): False,
                   ('P1', 'P3', 'P4'): False,
                   ('P1', 'P4'): False,
                   ('P2',): False,
                   ('P2', 'P3'): False,
                   ('P2', 'P3', 'P4'): False,
                   ('P2', 'P4'): False,
                   ('P3',): False,
                   ('P3', 'P4'): False,
                   ('P4',): False},
 'planning': {(): False,
              ('P1',): False,
              ('P1', 'P2'): True,
              ('P1', 'P2', 'P3'): True,
              ('P1', 'P2', 'P3', 'P4'): True,
              ('P1', 'P2', 'P4'): True,
              ('P1', 'P3'): True,
              ('P1', 'P3', 'P4'): True,
              ('P1', 'P4'): False,
              ('P2',): False,
              ('P2', 'P3'): True,
              ('P2', 'P3', 'P4'): True,
              ('P2', 'P4'): False,
              ('P3',): False,
              ('P3', 'P4'): False,
              ('P4',): False},
 'research': {(): False,
              ('P1',): False,
              ('P1', 'P2'): True,
              ('P1', 'P2', 'P3'): True,
              ('P1', 'P2', 'P3', 'P4'): True,
              ('P1', 'P2', 'P4'): True,
              ('P1', 'P3'): True,
              ('P1', 'P3', 'P4'): True,
              ('P1', 'P4'): False,
              ('P2',): False,
              ('P2', 'P3'): True,
              ('P2', 'P3', 'P4'): True,
              ('P2', 'P4'): False,
              ('P3',): False,
              ('P3', 'P4'): False,
              ('P4',): False},
 'strategy': {(): False,
              ('P1',): False,
              ('P1', 'P2'): False,
              ('P1', 'P2', 'P3'): True,
              ('P1', 'P2', 'P3', 'P4'): True,
              ('P1', 'P2', 'P4'): False,
              ('P1', 'P3'): True,
              ('P1', 'P3', 'P4'): True,
              ('P1', 'P4'): False,
              ('P2',): False,
              ('P2', 'P3'): False,
              ('P2', 'P3', 'P4'): False,
              ('P2', 'P4'): False,
              ('P3',): False,
              ('P3', 'P4'): False,
              ('P4',): False},
 'triage': {(): False,
            ('P1',): False,
            ('P1', 'P2'): True,
            ('P1', 'P2', 'P3'): True,
            ('P1', 'P2', 'P3', 'P4'): True,
            ('P1', 'P2', 'P4'): True,
            ('P1', 'P3'): False,
            ('P1', 'P3', 'P4'): False,
            ('P1', 'P4'): False,
            ('P2',): False,
            ('P2', 'P3'): False,
            ('P2', 'P3', 'P4'): False,
            ('P2', 'P4'): False,
            ('P3',): False,
            ('P3', 'P4'): False,
            ('P4',): False},
 'vision': {(): False,
            ('P1',): False,
            ('P1', 'P2'): False,
            ('P1', 'P2', 'P3'): False,
            ('P1', 'P2', 'P3', 'P4'): False,
            ('P1', 'P2', 'P4'): False,
            ('P1', 'P3'): False,
            ('P1', 'P3', 'P4'): False,
            ('P1', 'P4'): False,
            ('P2',): False,
            ('P2', 'P3'): False,
            ('P2', 'P3', 'P4'): False,
            ('P2', 'P4'): False,
            ('P3',): False,
            ('P3', 'P4'): False,
            ('P4',): False}}


def surviving_table():
    return {(): ('P2', 'P3', 'P1', 'P4'),
 ('P1',): ('P2', 'P3', 'P4'),
 ('P1', 'P2'): ('P3', 'P4'),
 ('P1', 'P2', 'P3'): ('P4',),
 ('P1', 'P2', 'P3', 'P4'): (),
 ('P1', 'P2', 'P4'): ('P3',),
 ('P1', 'P3'): ('P2', 'P4'),
 ('P1', 'P3', 'P4'): ('P2',),
 ('P1', 'P4'): ('P2', 'P3'),
 ('P2',): ('P3', 'P1', 'P4'),
 ('P2', 'P3'): ('P1', 'P4'),
 ('P2', 'P3', 'P4'): ('P1',),
 ('P2', 'P4'): ('P3', 'P1'),
 ('P3',): ('P2', 'P1', 'P4'),
 ('P3', 'P4'): ('P2', 'P1'),
 ('P4',): ('P2', 'P3', 'P1')}


def plane_endpoints_table():
    return {'P1': ('pair_local',),
 'P2': ('flash', 'uncensored'),
 'P3': ('instruct_256', 'quality_96'),
 'P4': ('mimo_cloud',)}


def endpoint_limits_table():
    return {'flash': {'tps_min': 100.0, 'ttft_s_fail': 6.0, 'ttft_s_max': 2.0},
 'instruct_256': {'tps_min': 80.0, 'ttft_s_fail': 30.0, 'ttft_s_max': 10.0},
 'mimo_cloud': {'tps_min': 1.0, 'ttft_s_fail': 135.0, 'ttft_s_max': 45.0},
 'pair_local': {'tps_min': 40.0, 'ttft_s_fail': 9.0, 'ttft_s_max': 3.0},
 'quality_96': {'tps_min': 80.0, 'ttft_s_fail': 30.0, 'ttft_s_max': 10.0},
 'uncensored': {'tps_min': 40.0, 'ttft_s_fail': 15.0, 'ttft_s_max': 5.0}}


def endpoint_plane(endpoint):
    return endpoints().get(endpoint, {}).get("plane")


def endpoints_in_plane(plane):
    return plane_endpoints_table().get(plane, ())


def endpoint_limits(endpoint):
    return endpoint_limits_table().get(endpoint, {})


def surviving_planes(planes_down):
    down_key = tuple(sorted(set(("P1", "P2", "P3", "P4")).intersection(planes_down)))
    return surviving_table().get(down_key, ("P2", "P3", "P1", "P4"))


def route_for_role(role, planes_down):
    live_key = tuple(sorted(set(("P1", "P2", "P3", "P4")).difference(planes_down)))
    role_table = route_table().get(role, {})
    return role_table.get(live_key, "")


def role_has_two_planes(role, planes_down):
    live_key = tuple(sorted(set(("P1", "P2", "P3", "P4")).difference(planes_down)))
    role_table = two_planes_table().get(role, {})
    return role_table.get(live_key, False)
