"""Enterprise Cost Ledger — per-mission LLM spend tracking + budget enforcement.

Every LLM call routes through `record_llm_cost(mission_id, model, tokens, usd)`.
The ledger:
  1. Appends a forensic JSONL row to `audits/cost_ledger.jsonl`
  2. Maintains an in-memory per-mission running total
  3. Enforces per-mission budgets — raises BudgetExceededError if a call
     would push the mission over its cap

This is the canonical "money meter" for the system. Without it, BMS A3
(`cost_cap_usd=0.50`) is just an advisory string.

Usage:
    from rig_lattice.enterprise.cost_ledger import record_llm_cost, mission_spend, set_budget

    set_budget("sys-abc-123", usd=0.50)              # A3 budget
    record_llm_cost("sys-abc-123", "llama3.3:70b", in_tokens=500, out_tokens=200)
    spent = mission_spend("sys-abc-123")             # → e.g. 0.0035

Price table for `record_llm_cost` lookups (USD per 1M tokens) — adjust as
provider pricing changes. Defaults to llama3.3:70b on Ollama which is $0
for the operator.
"""
from __future__ import annotations
import json
import time
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from pathlib import Path
from threading import Lock
from rig_lattice._paths import AUDITS_DIR

ROOT = Path(__file__).parent.parent
LEDGER_PATH = AUDITS_DIR / "cost_ledger.jsonl"


# ── Price table (USD per 1M tokens) ──────────────────────────────────────
# Update these as your provider mix changes. Local llama3.3:70b on Ollama
# is free; OpenAI/Anthropic etc. cost money.
PRICE_PER_1M_TOKENS: dict[str, tuple[float, float]] = {
    # model: (input_cost, output_cost) per 1M tokens
    "llama3.3:70b":          (0.0, 0.0),
    "llama3.1:70b":          (0.0, 0.0),
    "llama3.1:8b":           (0.0, 0.0),
    "gpt-4o":                (2.50, 10.00),
    "gpt-4o-mini":           (0.15, 0.60),
    "gpt-4-turbo":           (10.00, 30.00),
    "claude-3-5-sonnet":     (3.00, 15.00),
    "claude-3-5-haiku":      (0.80, 4.00),
    "claude-3-opus":         (15.00, 75.00),
    "mistral-large":         (3.00, 9.00),
}


class BudgetExceededError(Exception):
    """Raised when an LLM call would push a mission over its per-mission cap."""
    def __init__(self, mission_id: str, spent: float, attempted: float, cap: float):
        self.mission_id = mission_id
        self.spent = spent
        self.attempted = attempted
        self.cap = cap
        super().__init__(
            f"budget exceeded for {mission_id}: "
            f"spent ${spent:.4f} + attempted ${attempted:.4f} > cap ${cap:.4f}"
        )


@dataclass
class LedgerEntry:
    ts_utc: str
    mission_id: str
    model: str
    in_tokens: int
    out_tokens: int
    input_usd: float
    output_usd: float
    total_usd: float
    purpose: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


# ── In-memory state ──────────────────────────────────────────────────────
_lock = Lock()
_mission_spend: dict[str, float] = defaultdict(float)
_mission_budget: dict[str, float] = {}
_mission_call_count: dict[str, int] = defaultdict(int)


def estimate_cost(model: str, in_tokens: int, out_tokens: int) -> tuple[float, float, float]:
    """Look up (input_usd, output_usd, total_usd) for a given model + token counts."""
    in_cost, out_cost = PRICE_PER_1M_TOKENS.get(model, (0.0, 0.0))
    input_usd = (in_tokens / 1_000_000) * in_cost
    output_usd = (out_tokens / 1_000_000) * out_cost
    return input_usd, output_usd, input_usd + output_usd


def set_budget(mission_id: str, usd: float) -> None:
    """Set the per-mission cost cap. Used by orchestrator at A3 entry."""
    with _lock:
        _mission_budget[mission_id] = float(usd)


def get_budget(mission_id: str) -> float | None:
    return _mission_budget.get(mission_id)


def mission_spend(mission_id: str) -> float:
    return _mission_spend.get(mission_id, 0.0)


def mission_call_count(mission_id: str) -> int:
    return _mission_call_count.get(mission_id, 0)


def mission_remaining(mission_id: str) -> float | None:
    cap = _mission_budget.get(mission_id)
    if cap is None:
        return None
    return cap - _mission_spend.get(mission_id, 0.0)


def record_llm_cost(mission_id: str,
                     model: str,
                     in_tokens: int = 0,
                     out_tokens: int = 0,
                     purpose: str = "",
                     usd_override: float | None = None,
                     enforce_budget: bool = True) -> LedgerEntry:
    """Record a single LLM call's cost. Returns the LedgerEntry written.

    Raises BudgetExceededError when enforce_budget=True AND the call would
    push this mission over its set budget.
    """
    if usd_override is not None:
        input_usd, output_usd = 0.0, 0.0
        total_usd = float(usd_override)
    else:
        input_usd, output_usd, total_usd = estimate_cost(model, in_tokens, out_tokens)

    with _lock:
        current = _mission_spend.get(mission_id, 0.0)
        cap = _mission_budget.get(mission_id)
        if enforce_budget and cap is not None and (current + total_usd) > cap:
            raise BudgetExceededError(mission_id, current, total_usd, cap)
        _mission_spend[mission_id] = current + total_usd
        _mission_call_count[mission_id] += 1

    entry = LedgerEntry(
        ts_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        mission_id=mission_id,
        model=model,
        in_tokens=in_tokens,
        out_tokens=out_tokens,
        input_usd=round(input_usd, 6),
        output_usd=round(output_usd, 6),
        total_usd=round(total_usd, 6),
        purpose=purpose,
    )
    _append_ledger(entry)
    return entry


def _append_ledger(entry: LedgerEntry) -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER_PATH.open("a") as f:
        f.write(json.dumps(entry.to_dict(), default=str) + "\n")


def ledger_summary(limit: int = 100) -> dict:
    """Return aggregate stats across recent ledger entries."""
    if not LEDGER_PATH.exists():
        return {"total_entries": 0, "total_usd": 0.0, "by_model": {}, "by_mission": {}}
    by_model: dict[str, dict] = defaultdict(lambda: {"calls": 0, "usd": 0.0})
    by_mission: dict[str, dict] = defaultdict(lambda: {"calls": 0, "usd": 0.0})
    total_usd = 0.0
    total_entries = 0
    with LEDGER_PATH.open() as f:
        for line in f:
            if not line.strip():
                continue
            try:
                e = json.loads(line)
            except Exception:
                continue
            total_entries += 1
            usd = e.get("total_usd", 0.0)
            total_usd += usd
            by_model[e.get("model", "?")]["calls"] += 1
            by_model[e.get("model", "?")]["usd"] += usd
            by_mission[e.get("mission_id", "?")]["calls"] += 1
            by_mission[e.get("mission_id", "?")]["usd"] += usd
    return {
        "total_entries": total_entries,
        "total_usd": round(total_usd, 4),
        "by_model": {k: {"calls": v["calls"], "usd": round(v["usd"], 4)}
                       for k, v in by_model.items()},
        "by_mission": {k: {"calls": v["calls"], "usd": round(v["usd"], 4)}
                        for k, v in list(by_mission.items())[:limit]},
    }


def reset_mission(mission_id: str) -> None:
    """Reset per-mission counters (testing helper). NEVER call from prod."""
    with _lock:
        _mission_spend.pop(mission_id, None)
        _mission_budget.pop(mission_id, None)
        _mission_call_count.pop(mission_id, None)
