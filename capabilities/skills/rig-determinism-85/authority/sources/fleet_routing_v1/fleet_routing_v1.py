"""fleet_routing_v1 — immutable deterministic routing authority for the RIG fleet.

Pure data + pure functions. No I/O, no imports beyond typing, no dynamic
builtins. Grounded in measured artifacts of 2026-09-15 (baselines,
thresholds, plane separation). Any content change requires a NEW process-id.
"""

PLANES = {
    "P1": {"name": "mac-ollama-pair", "quota_governed": False},
    "P2": {"name": "blackwell-gpu", "quota_governed": False},
    "P3": {"name": "omlx-mlx", "quota_governed": False},
    "P4": {"name": "paid-subscription", "quota_governed": True},
}

ENDPOINTS = {
    "flash": {
        "url": "http://192.168.68.90:8011/v1/chat/completions",
        "plane": "P2",
        "model": "blackwell-qwen38-flash",
        "ttft_s_max": 2.0,
        "tps_min": 100.0,
    },
    "uncensored": {
        "url": "http://127.0.0.1:8656/v1/chat/completions",
        "plane": "P2",
        "model": "blackwell-qwen38-uncensored",
        "ttft_s_max": 5.0,
        "tps_min": 40.0,
    },
    "instruct_256": {
        "url": "http://127.0.0.1:8657/v1/chat/completions",
        "plane": "P3",
        "model": "qwen3.8-27b-uncensored:instruct",
        "ttft_s_max": 10.0,
        "tps_min": 80.0,
    },
    "quality_96": {
        "url": "http://127.0.0.1:8771/v1/chat/completions",
        "plane": "P3",
        "model": "qwen3.8-27b-oq6:instruct",
        "ttft_s_max": 10.0,
        "tps_min": 80.0,
    },
    "pair_local": {
        "url": "http://127.0.0.1:11435/v1/chat/completions",
        "plane": "P1",
        "model": "rig-96gb-laguna:latest",
        "ttft_s_max": 3.0,
        "tps_min": 40.0,
    },
    "mimo_cloud": {
        "url": "http://127.0.0.1:8655/v1/chat/completions",
        "plane": "P4",
        "model": "mimo-v2.5-pro",
        "ttft_s_max": 45.0,
        "tps_min": 1.0,
    },
}

DEGRADATION_ORDER = ["P2", "P3", "P1", "P4"]

ROLE_ROUTES = {
    "coding": ["flash", "instruct_256", "pair_local"],
    "architecture": ["instruct_256", "quality_96", "pair_local"],
    "planning": ["uncensored", "instruct_256", "pair_local"],
    "research": ["uncensored", "pair_local", "quality_96"],
    "vision": ["instruct_256", "quality_96"],
    "strategy": ["instruct_256", "quality_96", "pair_local"],
    "triage": ["pair_local", "flash"],
    "paid_fallback": ["mimo_cloud"],
}

KILL_SWITCHES = {
    "KS1": {"detect": "loopback endpoint dead x2", "action": "remove from rotation"},
    "KS2": {"detect": "role has fewer than 2 live planes", "action": "hard stall prevention"},
    "KS3": {"detect": "pair_local api dead", "action": "bypass P1 to node proxies"},
    "KS4": {"detect": "P2 endpoints both dead", "action": "degrade to P3"},
    "KS5": {"detect": "paid quota exhausted", "action": "hard stop paid lane"},
    "KS6": {"detect": "inference process on rig-128gb", "action": "kill and report"},
    "KS7": {"detect": "uncensored ttft over 15s twice", "action": "route to instruct_256"},
}

PAID_QUOTA_STOP_PCT = 98


def endpoint_plane(endpoint):
    return ENDPOINTS[endpoint]["plane"]


def endpoints_in_plane(plane):
    result = []
    for name in ENDPOINTS:
        if ENDPOINTS[name]["plane"] == plane:
            result.append(name)
    return result


def check_endpoint(endpoint, ttft_s, tps):
    spec = ENDPOINTS[endpoint]
    if ttft_s > spec["ttft_s_max"] * 3:
        return "FAIL"
    if ttft_s > spec["ttft_s_max"]:
        return "DEGRADED"
    if tps < spec["tps_min"]:
        return "DEGRADED"
    return "PASS"


def surviving_planes(planes_down):
    result = []
    for plane in DEGRADATION_ORDER:
        if plane not in planes_down:
            result.append(plane)
    return result


def route_for_role(role, planes_down):
    live = surviving_planes(planes_down)
    for endpoint in ROLE_ROUTES[role]:
        if ENDPOINTS[endpoint]["plane"] in live:
            return endpoint
    return ""


def role_has_two_planes(role, planes_down):
    live = surviving_planes(planes_down)
    seen = []
    for endpoint in ROLE_ROUTES[role]:
        plane = ENDPOINTS[endpoint]["plane"]
        if plane in live and plane not in seen:
            seen.append(plane)
    return len(seen) >= 2


def paid_lane_allowed(quota_pct):
    return quota_pct < PAID_QUOTA_STOP_PCT
