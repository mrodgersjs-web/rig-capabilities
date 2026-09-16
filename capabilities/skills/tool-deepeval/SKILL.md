---
name: tool-deepeval
description: Build committed DeepEval datasets and LLM test cases for Design Harness golden-set regression evaluation.
outcome: "data-analytics: model and agent changes are compared on explicit reusable cases instead of judged from one favorable run"
done_when:
  - cmd:/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python -c "import importlib.metadata as m; assert m.version('deepeval') == '4.2.3'; from deepeval.test_case import LLMTestCase; assert LLMTestCase(input='x', actual_output='y')"
great_example: "A golden task is an LLMTestCase committed beside the evaluator, with known-good and deliberately wrong outputs proving the metric goes GREEN and RED."
quality_floor: 0.7
relates_to: rig-design-harness
provenance: registry:confident-ai/deepeval
---

# tool-deepeval

## Role in our stack

DeepEval 4.2.3 belongs to the **Evaluation** component. It represents golden examples and observed outputs as committed test cases and datasets. Metrics that call an LLM require credentials and are not used in offline unit verification.

## Verified snippets

### 1. Construct an LLM test case

```python
from deepeval.test_case import LLMTestCase
case = LLMTestCase(input="Capital of France?", actual_output="Paris", expected_output="Paris")
assert case.actual_output == "Paris"
```

Verified first in the required throwaway venv and reverified after HarnessCore installed 4.2.3: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python /tmp/agentforge-snippets/deepeval/verify.py 1` → exit 0.

### 2. Construct a golden example

```python
from deepeval.dataset import Golden
golden = Golden(input="2+2", expected_output="4")
assert golden.expected_output == "4"
```

Verified: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python /tmp/agentforge-snippets/deepeval/verify.py 2` → exit 0.

### 3. Construct an evaluation dataset

```python
from deepeval.dataset import EvaluationDataset, Golden
dataset = EvaluationDataset(goldens=[Golden(input="ping", expected_output="pong")])
assert len(dataset.goldens) == 1
```

Verified: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python /tmp/agentforge-snippets/deepeval/verify.py 3` → exit 0.

## Pitfalls

- Dataset construction is offline; most semantic metrics invoke a judge model.
- Separate metric transport failures from candidate-quality failures.
- Keep known-good and planted-wrong fixtures so a green metric proves it can fail.
- DeepEval was first verified in `/tmp/agentforge-venv`; HarnessCore then installed the same 4.2.3 version in the harness venv and all three snippets were reverified there.

## Planted failure

A wrong actual output must go RED under the deterministic exact-match gate:

```bash
/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python -c "from deepeval.test_case import LLMTestCase; c=LLMTestCase(input='2+2',actual_output='5',expected_output='4'); assert c.actual_output == c.expected_output, 'exact-match regression'"
```

Expected: non-zero exit with `exact-match regression`.
