---
name: tool-phoenix
description: Configure local Arize Phoenix OpenTelemetry tracing and OpenInference processing for Design Harness trajectory evidence.
outcome: "data-analytics: Design Harness runs emit queryable local spans through a Phoenix-aware OTel provider without coupling business logic to the UI"
done_when:
  - cmd:/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python -c "import importlib.metadata as m; assert m.version('arize-phoenix-otel') == '0.17.1'; from phoenix.otel import TracerProvider; assert TracerProvider()"
great_example: "A local Phoenix container on UI :6006 and OTLP gRPC :4317 receives spans carrying lane, run_id, day, stage, status, and gate."
quality_floor: 0.7
relates_to: rig-design-harness
provenance: authored-2026-09-16
---

# tool-phoenix

## Role in our stack

Phoenix is the local-first **Evaluation** trajectory ledger candidate. The server image is `arizephoenix/phoenix`; the UI is `http://127.0.0.1:6006`; OTLP gRPC is `http://127.0.0.1:4317`. Python uses `phoenix.otel.register(...)` and OpenInference instrumentation packages. This skill is authored from the Arize Phoenix docs and repository README because Phase 0 specified no registry source.

## Verified snippets

### 1. Construct a Phoenix-aware provider

```python
from phoenix.otel import TracerProvider
provider = TracerProvider()
tracer = provider.get_tracer("rig-design-harness")
assert tracer is not None
```

Verified against harness arize-phoenix-otel 0.17.1: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python /tmp/agentforge-snippets/phoenix/verify.py 1` → exit 0.

### 2. Register the local OTLP endpoint

```python
from phoenix.otel import TracerProvider, register
provider = register(endpoint="http://127.0.0.1:4317", protocol="grpc", batch=True, verbose=False, set_global_tracer_provider=False)
assert isinstance(provider, TracerProvider)
```

Verified without emitting a span: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python /tmp/agentforge-snippets/phoenix/verify.py 2` → exit 0.

### 3. Construct the Pydantic AI OpenInference processor

```python
from openinference.instrumentation.pydantic_ai import OpenInferenceSpanProcessor
processor = OpenInferenceSpanProcessor()
assert processor is not None
```

Verified against harness openinference-instrumentation-pydantic-ai 0.1.27: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python /tmp/agentforge-snippets/phoenix/verify.py 3` → exit 0.

## Pitfalls

- Starting the Docker image or exporting a real span is an integration action, not a unit test.
- Bind local services to loopback unless exposure is explicitly approved.
- `register()` sets a global provider by default; tests should pass `set_global_tracer_provider=False`.
- Phoenix needs framework-specific `openinference-instrumentation-*` packages; installing only the server is insufficient.

## Planted failure

The span contract must reject a missing `run_id`:

```bash
/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python -c "required={'lane','run_id','day','stage','status','gate'}; attrs={'lane':'x','day':'d','stage':'s','status':'ok','gate':'g'}; missing=required-attrs.keys(); assert not missing, f'missing Phoenix attributes: {sorted(missing)}'"
```

Expected: non-zero exit naming `run_id`.
