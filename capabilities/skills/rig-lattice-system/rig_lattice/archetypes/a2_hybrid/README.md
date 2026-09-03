# A2 — HYBRID (built)

RIG Lattice Mode 2. BMS band ≈ 0.50–0.75. The rung between frozen A1 (no LLM
in the decision path) and approval-gated A3/A4.

## Doctrine
- LLM calls allowed, but **only behind a strict output schema + validator**:
  `LLM output → parser → SchemaValidator → Draft → gate`.
- **No raw LLM output** passes directly into integration.
- **Imports** the frozen contract from `a1_python_only` — never redefines types
  (`test_contract_is_imported_from_a1_not_redefined` asserts identity).
- **Escalates confidence collapse to A3** (`confidence < CONFIDENCE_FLOOR=0.55`).
- **Source-per-claim enforced** (A2 and above).
- **Runs with NO API key**: the default `OfflineMockLLM` returns deterministic,
  schema-valid JSON, so the chain is reproducible with zero network/secrets.

## How A2 differs from A1
| | A1 PYTHON_ONLY | A2 HYBRID |
|---|---|---|
| Model in decision path | none (frozen) | LLM at A2.4, temperature 0, schema-bounded |
| Solution step | templated body | `LLM → parse → validate → Draft` |
| Quality gates | 3 structural | 3 structural **+ `schema_valid`** |
| Proof binding | body + sources + gates | + **exact model bytes + model id** |
| New stop states | quality_failed | **schema_failed**, **escalate-on-low-confidence** |

## Files
- `contract.py` — `LLMRequest`, `LLMResponse`, `A2Schema`, `PipelineInput/Output`
  (+ re-exported frozen A1 models).
- `run.py` — `A2Pipeline` orchestrator, `OfflineMockLLM` (mockable client),
  `parse_llm` / `validate_schema` / `solution` / `quality` stages.
- `proof.py` — SHA-256 `ProofPacket` binding the artifact to the model output.
- `tests/test_a2.py` — 12 tests (pytest **and** standalone).

## Run
```bash
# offline demo, no key
cd platform && python3 -m archetypes.a2_hybrid.run

# tests (standalone, no pytest needed)
python3 platform/archetypes/a2_hybrid/tests/test_a2.py
# or via pytest
cd platform && python3 -m pytest archetypes/a2_hybrid/tests -q
```

## Status
Built to A1's bar: runnable + 12 tests green + SHA-256 ProofPacket. Swap
`OfflineMockLLM` for any object exposing `complete(LLMRequest) -> LLMResponse`
(e.g. a Haiku wrapper at temperature 0 with structured output) without touching
the validator chain.
