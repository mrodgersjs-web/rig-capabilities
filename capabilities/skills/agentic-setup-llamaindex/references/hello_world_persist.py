"""LlamaIndex durable path (L4): persist an index to disk, reload it, query again.

Run: env -u PYTHONHOME -u PYTHONPATH ~/.rig/agentic-lab/llamaindex/.venv/bin/python hello_world_persist.py
Expected: prints "RESULT: PERSIST_OK nodes=N files=[...]", exit 0.
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from llama_index.core import (  # noqa: E402
    Document,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.llms.mock import MockLLM  # noqa: E402

from hello_world_mock import embed  # noqa: E402  (shared MockEmbedding, embed_dim=4)

docs = [
    Document(text="Checkpointing keeps an index on disk."),
    Document(text="Reloaded indexes answer queries without re-ingesting."),
]
index = VectorStoreIndex.from_documents(docs, embed_model=embed)

with tempfile.TemporaryDirectory(dir=str(Path.home() / ".rig/agentic-lab/llamaindex")) as td:
    persist_dir = Path(td) / "index_store"
    index.storage_context.persist(persist_dir=str(persist_dir))
    assert persist_dir.exists(), "persist dir missing"
    files = sorted(p.name for p in persist_dir.iterdir())
    assert files, "persist dir empty"

    sc = StorageContext.from_defaults(persist_dir=str(persist_dir))
    index2 = load_index_from_storage(sc, embed_model=embed)
    qe = index2.as_query_engine(llm=MockLLM(max_tokens=8))
    response = qe.query("What keeps an index on disk?")
    assert str(response).strip(), "empty response after reload"

print(f"RESULT: PERSIST_OK nodes={len(index2.docstore.docs)} files={files}")
