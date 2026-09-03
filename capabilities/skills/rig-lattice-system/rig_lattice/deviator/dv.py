#!/usr/bin/env python3
"""dv — RIG DV (Deviation) Engines orchestrator.

ONE COMMAND. WHOLE PIPELINE. Call this on any text or file and it runs the full
process end-to-end:

  1. Capture     — read input (file or stdin), save as seed
  2. Score seed  — strict 40-engine audit
  3. Deviate     — dispatch agents at +20σ on the weakest engines via llama3.3:70b
  4. Mesh        — Coral Reef synthesis of all +20σ variants
  5. Patch       — apply deterministic structural overlays if mesh fails
  6. Re-audit    — score every artifact
  7. Select best — pick highest-RIG-L artifact (seed | mesh | patched)
  8. Render      — self-contained HTML report
  9. Report      — terminal summary + output paths

Usage:
    dv <file>                       # full pipeline, default settings
    dv <file> --bar +10              # require RIG-L ≥ +10 before shipping
    dv <file> --quick                # audit + patch only (no LLM call, ~5 s)
    dv <file> --full                 # audit + deviate + mesh + patch (~10 min)
    dv - < strategy.md               # read from stdin
    dv <file> --workflow proposal    # use preset for proposal docs
    dv <file> --no-render            # skip HTML, terminal output only

The pipeline is idempotent: re-running on the same input produces the same artifacts.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from urllib import request as ur

from rig_lattice._paths import RUNS_DIR

from rig_lattice.deviator.auditor import audit_all  # noqa: E402
from rig_lattice.deviator.patch_overlays import build_overlay  # noqa: E402
from rig_lattice.deviator.des_squared import amplify  # noqa: E402
from rig_lattice.deviator.result_packet import emit as emit_packet  # noqa: E402

# ── Defaults ────────────────────────────────────────────────────────────────
DEFAULT_LLM_URL = (
    os.environ.get("RIG_DV_LLM_URL")
    or os.environ.get("RIG_LATTICE_LLM_URL")
    or "http://127.0.0.1:11434/v1/chat/completions"
)
DEFAULT_MODEL = os.environ.get("RIG_LATTICE_LLM_MODEL", "llama3.3:70b")
DEFAULT_BAR = 5.0          # ship at RIG-L ≥ +5 (publishable)
DEFAULT_MAX_DEVIATE = 7    # most agents to dispatch at +20σ
DEFAULT_LLM_TIMEOUT = 600  # 10 min per agent call
DEFAULT_OUTPUT_BASE = RUNS_DIR / "dv-runs"

ANSI = {"red": "\033[31m", "green": "\033[32m", "yellow": "\033[33m",
        "blue": "\033[34m", "cyan": "\033[36m", "magenta": "\033[35m",
        "bold": "\033[1m", "dim": "\033[2m", "reset": "\033[0m"}


def _c(text: str, color: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"{ANSI.get(color,'')}{text}{ANSI['reset']}"


def _banner(title: str, color: str = "cyan"):
    print()
    print(_c("━" * 76, "dim"))
    print(_c(f"  {title}", color))
    print(_c("━" * 76, "dim"))


def _read_input(target: str) -> str:
    if target == "-":
        return sys.stdin.read()
    p = Path(target).expanduser().resolve()
    if not p.exists():
        sys.exit(f"input not found: {p}")
    return p.read_text()


# ── Step prompts per engine ────────────────────────────────────────────────
# Each engine has a +20σ prompt template. The orchestrator dispatches one agent
# per weak engine with this template + the seed text.
ENGINE_PROMPTS = {
    "reality_anchor": (
        "FORGE +20σ axis: sourced evidence with sample sizes and falsifications. "
        "For every numeric claim in the input, add: (a) primary source name and date, "
        "(b) sample size or N, (c) confidence interval or range, (d) explicit falsification "
        "with a calendar date ('wrong if X by DATE'). Add a 'Falsification Calendar' "
        "section listing ≥3 dated kill claims."
    ),
    "mechanism_furnace": (
        "FORGE +20σ axis: causal mechanism chains. For every claim, expose the full "
        "chain Input → Activity → Behavior → System → Economic → Loop. Burn off every "
        "adjective that lacks a mechanism. Replace each unsupported phrase with the "
        "specific causal step that produces it."
    ),
    "temporal_horizon_integrity": (
        "HORIZON +20σ axis: 10-year compounding arc. Replace each phase milestone with "
        "(a) leading indicator (weekly observable), (b) lagging indicator (quarterly), "
        "(c) kill criterion with date and threshold, (d) compounding loop that strengthens "
        "without new input. Architect 2026 → 2028 → 2031 → 2033 progression."
    ),
    "rupture": (
        "BREAKER +20σ axis: orthodoxy demolition. Identify the industry-default move the "
        "input still accepts. Demolish it explicitly. Rebuild from first principles. "
        "Commit to ONE radical reframe — e.g., from 'product with software attach' to "
        "'operating system for the category'."
    ),
    "bayesian_calibration": (
        "BAYES +20σ axis: decomposed probabilities + base rates + Brier scoring. "
        "Decompose every probability into 2-3 conditional factors (P(A | B) form). "
        "Anchor headline ROI claims to a base rate. Name the next update event for each "
        "competitor probability. Add a Brier-score tracking commitment."
    ),
    "frame_collision": (
        "COLLIDER +20σ axis: orthogonal frame imports. Collide the input with 2 "
        "non-adjacent frames (defense procurement / developer-platform economics / "
        "electrification / etc.). Weave both into the strategy. Output should feel like "
        "a different KIND of company than the input did."
    ),
    "cognitive_sovereignty": (
        "SHIELD +20σ axis: steelmanned attacks pre-empted. Pre-empt 5 plausible attacks "
        "with explicit rebuttal sections (owner/buyer/customer/engineering/competitor). "
        "Add an 'Attacks Survived' index at the bottom listing each attack and its defense."
    ),
    "gravity_escape": (
        "GRAVITON +20σ axis: maximum distance from generic-AI median. Remove every "
        "consultant token ('leverage', 'synergy', 'holistic', 'furthermore', 'world-class', "
        "'cutting-edge'). Replace each generic noun with a domain-specific concrete object."
    ),
    "kolmogorov_originality": (
        "GLYPH +20σ axis: cannot be compressed to a known phrase. Add ≥3 unique compound "
        "phrases specific to this domain. Add ≥1 extended cross-domain metaphor "
        "(Bloomberg of X, iOS of X, etc.) developed over ≥80 chars."
    ),
    "feynman_xray": (
        "XRAY +20σ axis: mechanism transparency. For each technical claim, name the "
        "model type, the specific input signals, the inference latency, the false-positive "
        "rate, and the failure mode. No buzzword without a mechanism."
    ),
    "voltage": (
        "VOLT +20σ axis: emotional voltage without manipulation. Name specific humans "
        "(by role + ideally by name). Name the explicit cost of NOT moving. Name the "
        "operational drain (hours/week, days/cycle). Name the named competitor closing the gap."
    ),
    "predictive_surprise": (
        "SURPRISE +20σ axis: at least one claim updates the reader's model. Add a "
        "counter-intuitive finding ('most assume X, but Y'). Add a niche insight few "
        "buyers would know. Add one explicit anti-consensus call."
    ),
    "bell_entanglement": (
        "BELL gate: claim + evidence + falsification must be co-located. For every "
        "headline numeric claim, place the source citation AND the kill criterion within "
        "the same paragraph. Add an explicit 'Bell triangle' line: claim, evidence, "
        "falsification together."
    ),
    "critical_phase": (
        "CRITICAL gate: commitment statements. Add ≥2 'we commit / past this point, no "
        "retreat' phrases. Add explicit skin-in-game (production-or-nothing guarantee, "
        "refund pro-rata, extend at no additional fee)."
    ),
    "hawking_horizon": (
        "HORIZON-GATE: proof of access. Add ≥6 'we have / we own / we built / we deliver / "
        "we ship' statements with specific named assets (certifications, contracts, SKUs, "
        "silicon, customers)."
    ),
}


def _build_engine_prompt(engine_slug: str, seed: str, length_hint: int = 1100) -> str:
    """Build the +20σ rewrite prompt for one engine."""
    axis = ENGINE_PROMPTS.get(engine_slug,
        f"+20σ axis for {engine_slug}: doctrine-grade rewrite. Make this engine's "
        "criteria pass with civilization-grade rigor."
    )
    return (
        f"You are a RIG DV Engine agent operating at σ=+20 on the {engine_slug} axis.\n\n"
        "UNIVERSAL +20σ RUNG: civilization-grade. New formal system. Defensible at the highest bar.\n\n"
        f"AXIS INSTRUCTION:\n{axis}\n\n"
        "ORIGINAL ARTIFACT:\n---\n"
        f"{seed}\n"
        "---\n\n"
        f"Rewrite the artifact at +20σ along ONLY this axis. Preserve all evidence, numbers, "
        f"and named entities from the original — do not compress them away. Length: {length_hint-200}-{length_hint+200} words. "
        "Output ONLY the rewritten artifact. No preamble. No commentary."
    )


def _llm_call(prompt: str, url: str, model: str, timeout: int,
               temperature: float = 0.5, max_tokens: int = 2400) -> tuple[bool, str, float]:
    """Returns (success, content, elapsed_seconds)."""
    t0 = time.time()
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}],
               "temperature": temperature, "max_tokens": max_tokens}
    try:
        req = ur.Request(url, data=json.dumps(payload).encode("utf-8"),
                         headers={"Content-Type": "application/json"}, method="POST")
        with ur.urlopen(req, timeout=timeout) as r:
            body = json.loads(r.read().decode("utf-8"))
        msg = body["choices"][0]["message"]
        content = (msg.get("content") or msg.get("reasoning") or "").strip()
        return True, content, time.time() - t0
    except Exception as e:
        return False, f"[failed: {e}]", time.time() - t0


def _select_weak_engines(audit: dict, max_n: int) -> list[str]:
    """Pick the N engines with worst σ + any HARD_BLOCK, capped at max_n."""
    items = list(audit["engines"].items())
    # Always include HARD_BLOCKs
    blocks = [slug for slug, r in items if r["status"] == "HARD_BLOCK"]
    # Then lowest σ
    by_sigma = sorted(items, key=lambda x: x[1]["sigma"])
    weak = list(blocks)
    for slug, r in by_sigma:
        if slug not in weak and r["sigma"] < 10:
            weak.append(slug)
        if len(weak) >= max_n:
            break
    return weak[:max_n]


def _coral_reef_mesh(seed: str, variants: dict, url: str, model: str,
                       timeout: int) -> tuple[bool, str, float]:
    """Single LLM call: synthesize variants into a unified strict v2."""
    parts = []
    for slug, v in variants.items():
        if not v.get("ok"):
            continue
        parts.append(
            f"### Variant from RIG-{slug.upper()} (axis: {v.get('axis','?')})\n\n"
            f"{v['content']}\n"
        )
    if not parts:
        return False, "", 0.0
    variants_block = "\n---\n".join(parts)

    prompt = (
        "You are the RIG Coral Reef Mesher. You receive multiple +20σ variants of the "
        "same artifact — each produced by a different RIG DV Engine agent operating on "
        "ONE specific axis. Your job is to synthesize them into a single unified artifact "
        "that takes the strongest element of each variant.\n\n"
        f"ORIGINAL SEED:\n---\n{seed[:6000]}\n---\n\n"
        f"VARIANTS:\n\n{variants_block}\n\n"
        "Synthesis rules:\n"
        "1. Preserve every claim, number, named entity, and citation from the seed.\n"
        "2. Pick the strongest causal chains from FORGE/mechanism_furnace.\n"
        "3. Pick the strongest sourced-evidence/falsification language from ANCHOR.\n"
        "4. Pick the strongest compounding loops + kill criteria from HORIZON.\n"
        "5. Pick the radical reframe from BREAKER (if it's coherent).\n"
        "6. Pick the decomposed probabilities + Brier commitment from BAYES.\n"
        "7. Pick the frame collisions from COLLIDER.\n"
        "8. Pick the steelmanned-attacks index from SHIELD.\n"
        "9. Pick the proof-of-access statements from HORIZON-GATE.\n"
        "10. Remove every consultant token GRAVITON flagged.\n"
        "11. Output a unified artifact, 1500-2200 words. Output ONLY the synthesized artifact. No preamble."
    )
    return _llm_call(prompt, url, model, timeout, temperature=0.4, max_tokens=3200)


# ── Main pipeline ──────────────────────────────────────────────────────────
def run_pipeline(text: str, opts: argparse.Namespace) -> dict:
    """Run the full DV pipeline. Returns dict with paths and final audit."""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = Path(opts.output or DEFAULT_OUTPUT_BASE / ts).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "agents").mkdir(exist_ok=True)
    (out_dir / "scoring").mkdir(exist_ok=True)

    _banner("DV ENGINES — full pipeline starting", "magenta")
    print(f"  output: {_c(str(out_dir), 'cyan')}")
    print(f"  input:  {len(text.split())} words / {len(text):,} chars")
    print(f"  bar:    RIG-L ≥ {_c(f'{opts.bar:+.1f}', 'yellow')}")
    print(f"  mode:   {_c(opts.mode, 'yellow')}")

    # ── 1. Capture ─────────────────────────────────────────────────────────
    (out_dir / "seed.md").write_text(text)
    artifacts: dict[str, dict] = {}

    # ── 2. Audit seed ──────────────────────────────────────────────────────
    _banner("[1/7] Audit seed", "cyan")
    seed_audit = audit_all(text, llm_enabled=False)
    (out_dir / "scoring" / "seed.json").write_text(json.dumps(seed_audit, indent=2, default=str))
    print(f"  RIG-L: {_c(f'{seed_audit["rig_l"]:+.2f}', _rig_color(seed_audit['rig_l'], opts.bar))}  "
          f"BDF: {seed_audit['bdf']:+.2f}  "
          f"HARD_BLOCKs: {_c(f'{seed_audit["hard_blocks"]}/40', 'red' if seed_audit['hard_blocks'] else 'green')}  "
          f"status: {seed_audit['status']}")
    artifacts["seed"] = {"path": out_dir/"seed.md", "audit": seed_audit, "rig_l": seed_audit["rig_l"]}

    # If already at the bar and no hard blocks → ship as-is
    if seed_audit["rig_l"] >= opts.bar and seed_audit["hard_blocks"] == 0:
        print(_c("  ✓ Seed already at bar. Skipping deviate + mesh.", "green"))
        return _finalize(out_dir, artifacts, seed_audit, opts, ts)

    if opts.mode == "quick":
        # Skip LLM steps — go straight to patch
        return _patch_and_finalize(out_dir, text, seed_audit, artifacts, opts, ts)

    # ── 3. Select weak engines ─────────────────────────────────────────────
    _banner("[2/7] Select weak engines for +20σ dispatch", "cyan")
    weak = _select_weak_engines(seed_audit, opts.max_deviate)
    for slug in weak:
        r = seed_audit["engines"][slug]
        print(f"  → {_c(r['codename'], 'yellow'):14} {slug:32} {r['sigma']:+7.1f}σ  {r['status']}")
    if not weak:
        print(_c("  no weak engines selected, skipping deviate", "dim"))

    # ── 4. Dispatch +20σ agents ────────────────────────────────────────────
    variants: dict[str, dict] = {}
    if weak and opts.mode != "patch-only":
        _banner(f"[3/7] Dispatch {len(weak)} +20σ agents via {opts.model}", "cyan")
        dispatch = _dispatch_serial if opts.serial else _dispatch_parallel
        variants = dispatch(text, weak, opts)
        (out_dir / "agents" / "all_variants.json").write_text(
            json.dumps(variants, indent=2, default=str))
        for slug, v in variants.items():
            (out_dir / "agents" / f"{slug}_plus20.md").write_text(v.get("content", ""))
        n_ok = sum(1 for v in variants.values() if v.get("ok"))
        print(f"  → {n_ok}/{len(weak)} agents succeeded")

    # ── 5. Coral Reef mesh ─────────────────────────────────────────────────
    if variants and any(v.get("ok") for v in variants.values()):
        _banner("[4/7] Coral Reef mesh", "cyan")
        ok, meshed_content, elapsed = _coral_reef_mesh(text, variants, opts.url, opts.model, DEFAULT_LLM_TIMEOUT)
        if ok and meshed_content:
            mesh_path = out_dir / "mesh.md"
            mesh_path.write_text(meshed_content)
            print(f"  mesh complete · {elapsed:.0f}s · {len(meshed_content)} chars / {len(meshed_content.split())} words")

            mesh_audit = audit_all(meshed_content, llm_enabled=False)
            (out_dir / "scoring" / "mesh.json").write_text(json.dumps(mesh_audit, indent=2, default=str))
            print(f"  RIG-L: {_c(f'{mesh_audit["rig_l"]:+.2f}', _rig_color(mesh_audit['rig_l'], opts.bar))}  "
                  f"BDF: {mesh_audit['bdf']:+.2f}  HARD_BLOCKs: {mesh_audit['hard_blocks']}/40  "
                  f"Δ {_c(f'{mesh_audit["rig_l"]-seed_audit["rig_l"]:+.2f}', 'green' if mesh_audit['rig_l']>seed_audit['rig_l'] else 'red')}")
            artifacts["mesh"] = {"path": mesh_path, "audit": mesh_audit, "rig_l": mesh_audit["rig_l"]}
        else:
            print(_c(f"  ✗ mesh failed: {meshed_content[:200]}", "red"))

    # ── 6. Patch overlay (if best so far is still under bar) ───────────────
    best_key = max(artifacts, key=lambda k: artifacts[k]["rig_l"])
    best = artifacts[best_key]
    if best["rig_l"] < opts.bar or best["audit"]["hard_blocks"] > 0:
        return _patch_and_finalize(out_dir, best["path"].read_text(),
                                     best["audit"], artifacts, opts, ts, best_key)
    return _finalize(out_dir, artifacts, best["audit"], opts, ts)


def _dispatch_parallel(seed: str, weak: list[str], opts: argparse.Namespace) -> dict:
    """Parallel dispatch — faster but may hit model contention."""
    results: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=min(len(weak), opts.parallel_max)) as ex:
        futs = {}
        for slug in weak:
            prompt = _build_engine_prompt(slug, seed)
            futs[ex.submit(_llm_call, prompt, opts.url, opts.model, DEFAULT_LLM_TIMEOUT)] = slug
        for f in as_completed(futs):
            slug = futs[f]
            ok, content, elapsed = f.result()
            results[slug] = {
                "ok": ok, "content": content if ok else None,
                "elapsed_s": round(elapsed, 1),
                "axis": ENGINE_PROMPTS.get(slug, "")[:120],
            }
            mark = _c("✓", "green") if ok else _c("✗", "red")
            print(f"  {mark} {slug:32} {elapsed:5.0f}s · {len(content) if ok else 0} chars")
    return results


def _dispatch_serial(seed: str, weak: list[str], opts: argparse.Namespace) -> dict:
    """Serial dispatch — slower but no contention. Use if parallel times out."""
    results: dict[str, dict] = {}
    for slug in weak:
        prompt = _build_engine_prompt(slug, seed)
        ok, content, elapsed = _llm_call(prompt, opts.url, opts.model, DEFAULT_LLM_TIMEOUT)
        results[slug] = {
            "ok": ok, "content": content if ok else None,
            "elapsed_s": round(elapsed, 1),
            "axis": ENGINE_PROMPTS.get(slug, "")[:120],
        }
        mark = _c("✓", "green") if ok else _c("✗", "red")
        print(f"  {mark} {slug:32} {elapsed:5.0f}s · {len(content) if ok else 0} chars")
    return results


def _patch_and_finalize(out_dir: Path, text: str, audit: dict,
                         artifacts: dict, opts: argparse.Namespace, ts: str,
                         source_key: str = "seed") -> dict:
    _banner(f"[5/7] Patch overlay on {source_key}", "cyan")
    patched = build_overlay(text, audit)
    patched_path = out_dir / "patched.md"
    patched_path.write_text(patched)
    p_audit = audit_all(patched, llm_enabled=False)
    (out_dir / "scoring" / "patched.json").write_text(
        json.dumps(p_audit, indent=2, default=str))
    print(f"  patched: RIG-L {_c(f'{p_audit["rig_l"]:+.2f}', _rig_color(p_audit['rig_l'], opts.bar))}  "
          f"BDF: {p_audit['bdf']:+.2f}  HARD_BLOCKs: {p_audit['hard_blocks']}/40  "
          f"Δ {_c(f'{p_audit["rig_l"]-audit["rig_l"]:+.2f}', 'green')}")
    artifacts["patched"] = {"path": patched_path, "audit": p_audit, "rig_l": p_audit["rig_l"]}
    return _finalize(out_dir, artifacts, p_audit, opts, ts)


def _finalize(out_dir: Path, artifacts: dict, final_audit: dict,
               opts: argparse.Namespace, ts: str) -> dict:
    _banner("[6/7] Select best artifact", "cyan")
    best_key = max(artifacts, key=lambda k: artifacts[k]["rig_l"])
    best = artifacts[best_key]
    final_path = out_dir / "FINAL.md"
    final_path.write_text(best["path"].read_text())
    print(f"  best: {_c(best_key, 'green')} · RIG-L {best['rig_l']:+.2f} · status {best['audit']['status']}")
    print(f"  wrote: {_c(str(final_path), 'cyan')}")

    # Render HTML
    if not opts.no_render:
        _banner("[7/7] Render HTML report", "cyan")
        html_path = _render_html(out_dir, artifacts, final_audit, ts)
        print(f"  wrote: {_c(str(html_path), 'cyan')}")

    # ── DES² 5-amplifier overlay (DOCTRINE.md §3) ─────────────────────────
    final_text = final_path.read_text()
    enriched = amplify(best["audit"], final_text)
    d = enriched.get("des2", {})
    if d:
        _banner("[7b/7] DES² amplification overlay", "cyan")
        print(f"  composite uplift: {_c(f'{d["composite_uplift"]:.2f}×', 'green')} / max {d['max_uplift']:.2f}×  "
              f"efficiency {d['efficiency']*100:.0f}%  "
              f"amplifiers passed: {d['amplifiers_passed']}/{d['amplifiers_total']}")
        for name, r in d["amplifiers"].items():
            mark = _c("✓", "green") if r["passed"] else _c("✗", "red")
            print(f"    {mark} {name:18}  {r['multiplier']:.2f}×  {r['detail']}")

    # ── Result packet emit (DOCTRINE.md §6.1) ─────────────────────────────
    packet = emit_packet(enriched, final_path,
                          tier="client",
                          mission_id=f"dv-{ts}",
                          des2=enriched.get("des2"))
    packet_path = Path("audits/packets") / f"dv-{ts}.json"
    print(f"  result packet:     {_c(str(packet_path), 'cyan')}")

    _banner("DV PIPELINE COMPLETE", "magenta")
    print(f"\n  Final artifact:    {_c(str(final_path), 'green')}")
    print(f"  Final RIG-L:       {_c(f'{best["rig_l"]:+.2f}', _rig_color(best['rig_l'], opts.bar))}")
    des2_score_text = f"{d.get('des2_score', 0):+.2f}" if d else "n/a"
    print(f"  DES² score:        {_c(des2_score_text, 'green')}")
    print(f"  Status:            {packet.get('status', best['audit']['status'])}")
    print(f"  HARD_BLOCKs:       {best['audit']['hard_blocks']}/40")
    print(f"  Output directory:  {out_dir}")
    if not opts.no_render:
        print(f"  HTML report:       {out_dir/'report.html'}")
    print()
    return {"final": final_path, "best_key": best_key, "audit": final_audit,
            "des2": d, "packet": packet,
            "out_dir": out_dir, "artifacts": artifacts}


def _render_html(out_dir: Path, artifacts: dict, final_audit: dict, ts: str) -> Path:
    """Self-contained HTML showing seed → variants → mesh → patched → final progression."""
    import html as _html
    safe = lambda s: _html.escape(s or "")
    rig_color = lambda v: "var(--good)" if v >= 5 else "var(--warn)" if v >= 0 else "var(--bad)"

    tiles = []
    for key in ["seed", "mesh", "patched"]:
        if key not in artifacts:
            continue
        a = artifacts[key]
        rl = a["rig_l"]
        hb = a["audit"]["hard_blocks"]
        tiles.append(
            f'<div class="tile"><div class="label">{safe(key.upper())} RIG-L</div>'
            f'<div class="value" style="color:{rig_color(rl)}">{rl:+.2f}</div>'
            f'<div class="sub">HB {hb}/40 · {a["audit"]["status"]}</div></div>'
        )

    engine_rows = []
    final_engines = final_audit["engines"]
    seed_engines = artifacts["seed"]["audit"]["engines"]
    for slug, fr in sorted(final_engines.items(), key=lambda x: -x[1]["sigma"]):
        sr = seed_engines[slug]
        delta = fr["sigma"] - sr["sigma"]
        dc = "var(--good)" if delta > 0 else "var(--bad)" if delta < 0 else "var(--dim)"
        engine_rows.append(
            f'<tr><td><strong>{safe(fr["codename"])}</strong></td>'
            f'<td><code>{safe(slug)}</code></td>'
            f'<td>{sr["sigma"]:+.1f}σ</td>'
            f'<td>{fr["sigma"]:+.1f}σ</td>'
            f'<td style="color:{dc};font-weight:600">{delta:+.1f}σ</td>'
            f'<td>{fr["status"]}</td></tr>'
        )

    html_doc = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>DV Pipeline — {ts}</title>
<style>
:root{{--bg:#0d1117;--panel:#161b22;--text:#c9d1d9;--dim:#8b949e;--good:#3fb950;--bad:#f85149;--warn:#d29922;--cyan:#58a6ff}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:14px/1.55 -apple-system,sans-serif}}
.container{{max-width:1200px;margin:0 auto;padding:32px 24px}}
h1{{margin:0;font-size:28px;letter-spacing:-0.02em}}
h2{{margin-top:36px;font-size:18px;border-bottom:1px solid #30363d;padding-bottom:8px}}
.subtitle{{color:var(--dim);font-size:13px;margin-bottom:24px}}
.tile-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:18px 0}}
.tile{{background:var(--panel);border:1px solid #30363d;border-radius:8px;padding:16px}}
.label{{color:var(--dim);font-size:11px;text-transform:uppercase;letter-spacing:0.04em}}
.value{{font-size:26px;font-weight:600;margin-top:4px}}
.sub{{color:var(--dim);font-size:11px;margin-top:4px}}
table{{width:100%;border-collapse:collapse;background:var(--panel);border-radius:8px;overflow:hidden;margin:8px 0}}
th,td{{padding:6px 12px;text-align:left;border-bottom:1px solid #21262d;font-size:13px}}
th{{background:#1c2128;color:var(--dim);text-transform:uppercase;font-size:11px;letter-spacing:0.04em}}
code{{background:#21262d;padding:2px 6px;border-radius:4px;font:11px/1 'SF Mono',monospace;color:#79c0ff}}
section{{margin:32px 0}}
</style></head>
<body><div class="container">
<h1>DV Pipeline Run — {ts}</h1>
<p class="subtitle">RIG DV (Deviation) Engines — full pipeline · seed → +20σ agents → Coral Reef mesh → patch → final</p>

<section><h2>Pipeline progression</h2>
<div class="tile-grid">{''.join(tiles)}</div>
</section>

<section><h2>Engine-by-engine delta (seed → final)</h2>
<table>
<tr><th>Codename</th><th>Engine</th><th>Seed σ</th><th>Final σ</th><th>Δ</th><th>Status</th></tr>
{''.join(engine_rows)}
</table>
</section>

</div></body></html>
"""
    html_path = out_dir / "report.html"
    html_path.write_text(html_doc)
    return html_path


def _rig_color(rig_l: float, bar: float) -> str:
    if rig_l >= bar: return "green"
    if rig_l >= 0: return "yellow"
    return "red"


# ── CLI ────────────────────────────────────────────────────────────────────
def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="dv",
        description="RIG DV (Deviation) Engines — full pipeline in one command")
    p.add_argument("input", help="file path, or '-' for stdin")
    p.add_argument("--bar", type=float, default=DEFAULT_BAR,
                   help=f"RIG-L threshold to ship (default {DEFAULT_BAR:+.1f})")
    p.add_argument("--mode", choices=["full", "quick", "patch-only"], default="full",
                   help="full = audit+deviate+mesh+patch (default), quick = audit+patch only, "
                        "patch-only = audit+patch (no LLM)")
    p.add_argument("--quick", dest="mode", action="store_const", const="quick",
                   help="alias for --mode quick (no LLM call)")
    p.add_argument("--full", dest="mode", action="store_const", const="full",
                   help="alias for --mode full (default)")
    p.add_argument("--model", default=DEFAULT_MODEL, help=f"LLM model (default {DEFAULT_MODEL})")
    p.add_argument("--url", default=DEFAULT_LLM_URL, help="OpenAI-compatible chat completions URL")
    p.add_argument("--max-deviate", type=int, default=DEFAULT_MAX_DEVIATE,
                   help=f"max agents to dispatch at +20σ (default {DEFAULT_MAX_DEVIATE})")
    p.add_argument("--serial", action="store_true",
                   help="dispatch agents serially (slower, no model contention)")
    p.add_argument("--parallel-max", type=int, default=4,
                   help="max parallel agents when not --serial (default 4)")
    p.add_argument("--output", help="output directory (default runs/dv-runs/<ts>)")
    p.add_argument("--no-render", action="store_true", help="skip HTML report")
    p.add_argument("--workflow", choices=["strategy", "proposal", "landing", "outreach"],
                   help="apply a workflow preset (adjusts bar + engine selection)")

    opts = p.parse_args(argv)

    # Workflow presets
    if opts.workflow:
        presets = {
            "strategy": {"bar": 10.0, "max_deviate": 7},
            "proposal": {"bar": 14.0, "max_deviate": 9},
            "landing": {"bar": 5.0, "max_deviate": 5},
            "outreach": {"bar": 8.0, "max_deviate": 6},
        }
        for k, v in presets[opts.workflow].items():
            setattr(opts, k, v)

    text = _read_input(opts.input)
    if not text.strip():
        sys.exit("input is empty")

    run_pipeline(text, opts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
