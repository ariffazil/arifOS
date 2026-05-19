---
type: Tool
tier: 20_RUNTIME
strand:
- tools
- mlops
- memory
audience:
- engineers
- researchers
- operators
difficulty: intermediate
prerequisites:
- MCP_Tools
- Concept_LLM_Wiki_Pattern
tags:
- chroma
- vector-database
- embeddings
- semantic-search
- rag
- document-retrieval
- metadata-filtering
- open-source
sources:
- Hermes official skill: official/mlops/chroma
- Chroma docs: https://docs.trychroma.com
- GitHub: https://github.com/chroma-core/chroma
last_sync: '2026-05-18'
confidence: 0.95
---

# Skill: Chroma — Vector Database

**Chroma** is the open-source embedding database for building LLM applications with memory. Store embeddings and metadata, perform vector and full-text search, filter by metadata — simple 4-function API that scales from notebooks to production clusters.

## Purpose

To give federation agents local, self-hosted vector storage for:
- RAG (retrieval-augmented generation) applications
- Semantic search over documents
- Storing embeddings with rich metadata
- Prototyping memory systems without cloud dependencies

## Specifications

- **Stage**: 555 (Memory)
- **Layer**: MACHINE
- **Trinity**: Ω (Heart — memory, retrieval, grounding)
- **Floors touched most directly**: F2 (Truth — retrieved memory must be verifiable), F4 (Guardrails — data boundaries), F11 (Audit — memory changes logged)

## Installation

```bash
# Python
pip install chromadb sentence-transformers

# JavaScript/TypeScript
npm install chromadb @chroma-core/default-embed
```

**Installed on**: `/root` (VPS host, Hermes venv)  
**Default embedder**: `all-MiniLM-L6-v2` (Sentence Transformers)  
**Version**: 1.5.9+  
**License**: Apache 2.0

## Core Operations

### 1. Create collection
```python
import chromadb

# In-memory (ephemeral)
client = chromadb.Client()

# Persistent (disk)
client = chromadb.PersistentClient(path="./chroma_db")

# Server mode (production)
client = chromadb.HttpClient(host="localhost", port=8000)

# Create collection
collection = client.create_collection("my_docs")

# With custom embedding function
from chromadb.utils import embedding_functions
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="your-key", model_name="text-embedding-3-small"
)
collection = client.create_collection(
    name="my_docs", embedding_function=openai_ef
)
```

### 2. Add documents
```python
collection.add(
    documents=["Doc 1", "Doc 2", "Doc 3"],
    metadatas=[
        {"source": "web", "category": "tutorial"},
        {"source": "pdf", "page": 5},
        {"source": "api", "timestamp": "2025-01-01"}
    ],
    ids=["id1", "id2", "id3"]
)
```

### 3. Query (similarity search)
```python
# Basic query
results = collection.query(
    query_texts=["machine learning tutorial"],
    n_results=5
)

# Query with filters
results = collection.query(
    query_texts=["Python programming"],
    n_results=3,
    where={"source": "web"}
)

# Complex metadata filters
results = collection.query(
    query_texts=["advanced topics"],
    where={
        "$and": [
            {"category": "tutorial"},
            {"difficulty": {"$gte": 3}}
        ]
    }
)
```

### 4. Get / Update / Delete
```python
# Get by IDs
docs = collection.get(ids=["id1", "id2"])

# Get with filters
docs = collection.get(where={"category": "tutorial"}, limit=10)

# Update
collection.update(
    ids=["id1"],
    documents=["Updated content"],
    metadatas=[{"source": "updated"}]
)

# Delete
collection.delete(ids=["id1", "id2"])
collection.delete(where={"source": "outdated"})
```

## Metadata Filtering

| Operator | Meaning |
| :--- | :--- |
| `$eq`, `$ne` | Equal / not equal |
| `$gt`, `$gte` | Greater than / greater than or equal |
| `$lt`, `$lte` | Less than / less than or equal |
| `$in` | Contains in array |
| `$and`, `$or` | Logical operators |

## Embedding Functions

| Provider | Function | Use Case |
| :--- | :--- | :--- |
| **Default** | `sentence-transformers/all-MiniLM-L6-v2` | Local, fast, no API key |
| **OpenAI** | `text-embedding-3-small` | High quality, cloud |
| **HuggingFace** | `sentence-transformers/all-mpnet-base-v2` | Custom models |
| **Custom** | Subclass `EmbeddingFunction` | Proprietary embeddings |

## Framework Integrations

### LangChain
```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(),
    persist_directory="./chroma_db"
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
```

### LlamaIndex
```python
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, StorageContext

db = chromadb.PersistentClient(path="./chroma_db")
collection = db.get_or_create_collection("my_collection")
vector_store = ChromaVectorStore(chroma_collection=collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
```

## Server Mode

```bash
# Run Chroma server
chroma run --path ./chroma_db --port 8000

# Connect from any client
client = chromadb.HttpClient(host="localhost", port=8000)
```

## Federation Context

- **Hermes**: Skill installed at `~/.hermes/skills/mlops/chroma/`
- **arifOS**: Qdrant is the primary production vector store (port 6333). Chroma is the local development / prototyping alternative.
- **Use Chroma when**: Quick RAG experiments, notebook prototyping, self-hosted small-scale memory
- **Use Qdrant when**: Production federation memory, high throughput, multi-tenant collections

## Performance

| Operation | Latency | Notes |
| :--- | :--- | :--- |
| Add 100 docs | ~1-3s | With embedding generation |
| Query (top 10) | ~50-200ms | Depends on collection size |
| Metadata filter | ~10-50ms | Fast with proper indexing |

## Pitfalls

| Problem | Fix |
| :--- | :--- |
| Data lost on restart | Use `PersistentClient(path=...)` instead of `Client()` |
| Slow embedding | Batch operations; choose faster model |
| ID collisions | Use unique IDs; check before add |
| Large collection slowdown | Monitor size; use server mode for production |
| Missing metadata filter fields | Ensure fields exist in all documents or use `$exists` |

## Related

- [[Skill_MCP_Mcporter]] (MCP mesh CLI — can query Chroma via MCP if exposed)
- [[Skill_Docker_Management]] (Container ops for Chroma server deployment)
- [[Concept_Vault999_Architecture]] (Immutable ledger — contrast with mutable vector memory)
- [[MCP_Tools]] (Tool surface architecture)
