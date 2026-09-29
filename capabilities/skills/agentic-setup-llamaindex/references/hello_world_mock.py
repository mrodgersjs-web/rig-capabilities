"""LlamaIndex hello-world (L2): MockLLM over a real local document index, no network.

Run: env -u PYTHONHOME -u PYTHONPATH ~/.rig/agentic-lab/llamaindex/.venv/bin/python hello_world_mock.py
Expected: prints "RESULT: MOCK_OK docs=2 nodes=N", exit 0.
"""
import importlib.metadata as m

from llama_index.core import Document, VectorStoreIndex
from llama_index.core.embeddings import MockEmbedding
from llama_index.core.llms.mock import MockLLM

print("VERSION: llama-index-core", m.version("llama-index-core"))

# MockEmbedding is exported from llama_index.core.embeddings in 0.14.25
# (there is no llama_index.core.embeddings.mock_embedder module).
embed = MockEmbedding(embed_dim=4)


docs = [
    Document(text="The RIG lab machine runs local models on port 8771."),
    Document(text="MockLLM answers deterministically for tests."),
]
index = VectorStoreIndex.from_documents(docs, embed_model=embed)
n_nodes = len(index.docstore.docs)
assert n_nodes >= 2, f"expected >=2 nodes, got {n_nodes}"

query_engine = index.as_query_engine(llm=MockLLM(max_tokens=8))
response = query_engine.query("What port do local models run on?")
assert str(response).strip(), "empty response from MockLLM query engine"
print(f"RESULT: MOCK_OK docs={len(docs)} nodes={n_nodes}")
