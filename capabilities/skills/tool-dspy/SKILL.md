---
name: tool-dspy
description: Define typed DSPy signatures, modules, examples, and optimizer metrics for evidence-driven Design Harness improvement.
outcome: "research-intel: prompt behavior is expressed as optimizable programs tied to explicit examples and metrics rather than hand-tuned prose"
done_when:
  - cmd:/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python -c "import dspy; assert dspy.__version__ == '3.3.1'; assert dspy.Predict"
great_example: "An outer-loop candidate compiles a DSPy module against train examples and is accepted only when the independent dev metric does not regress."
quality_floor: 0.7
relates_to: rig-design-harness
provenance: local:/Users/rig128gb/.claude/skills/zazen-dspy-structured
---

# tool-dspy

## Role in our stack

DSPy 3.3.1 supports the **Evaluation** and outer-loop optimization components. Use signatures for typed behavior, modules for executable prompt programs, examples for train/dev sets, and optimizers only when a real metric and sufficient examples exist.

## Verified snippets

### 1. Define a signature

```python
import dspy

class Classify(dspy.Signature):
    text: str = dspy.InputField()
    label: str = dspy.OutputField()

assert set(Classify.input_fields) == {"text"}
```

Verified: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python /tmp/agentforge-snippets/dspy/verify.py 1` → exit 0.

### 2. Construct a module

```python
import dspy

class Summarize(dspy.Signature):
    text: str = dspy.InputField()
    summary: str = dspy.OutputField()

module = dspy.Predict(Summarize)
assert isinstance(module, dspy.Predict)
```

Verified: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python /tmp/agentforge-snippets/dspy/verify.py 2` → exit 0.

### 3. Build an example with inputs and labels

```python
import dspy
example = dspy.Example(question="2+2", answer="4").with_inputs("question")
assert example.inputs().question == "2+2"
assert example.labels().answer == "4"
```

Verified: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python /tmp/agentforge-snippets/dspy/verify.py 3` → exit 0.

## Pitfalls

- Do not optimize without a metric and a separate dev set.
- Module construction is offline; calling a module requires a configured LM.
- Keep train and dev examples separate from the proposer to avoid leakage.
- Inspect compiled behavior and traces; generated prompts are otherwise hidden.

## Planted failure

The acceptance metric must reject a known-wrong candidate:

```bash
/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python -c "metric=lambda expected,actual: float(expected==actual); score=metric('4','5'); assert score >= 1.0, f'metric rejected candidate: {score}'"
```

Expected: non-zero exit with score `0.0`.
