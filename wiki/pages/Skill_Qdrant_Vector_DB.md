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
- Skill_Chroma_Vector_DB
tags:
- qdrant
- vector-database
- vector-search
- embeddings
- semantic-search
- rag
- hnsw
- production
- distributed
- rust
sources:
- Hermes official skill: official/mlops/qdrant
- Qdrant docs: https://qdrant.tech/documentation
- GitHub: https://github.com/qdrant/qdrant
last_sync: '2026-05-18'
confidence: 0.95
---

# Skill: Qdrant — Vector Similarity Search Engine

**Qdrant** is the high-performance vector similarity search engine for production RAG and semantic search. Written in Rust, it powers the federation's L3 semantic memory layer with HNSW indexing, rich metadata filtering, quantization, and distributed scaling.

## Purpose

To give federation agents production-grade vector storage:
- Low-latency nearest neighbor search for RAG pipelines
- Hybrid search (dense vectors + sparse vectors + metadata filtering)
- Horizontal scaling with sharding and replication
- Multi-vector storage per record (dense + sparse + multi-dense)
- Memory-efficient quantization for large collections

## Specifications

- **Stage**: 555 (Memory)
- **Layer**: MACHINE
- **Trinity**: Ω (Heart — memory, retrieval, grounding)
- **Floors touched most directly**: F2 (Truth — retrieved vectors must be verifiable), F4 (Guardrails — collection boundaries), F8 (Audit — all vector ops logged)

## Installation

```bash
# Python client
pip install qdrant-client

# Docker (development / local)
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant

# Docker with persistent storage
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```

**Installed on**: `/root` (VPS host, Hermes venv)  
**Client version**: 1.18.0  
**Server version**: 1.17.1 (Docker container `qdrant/qdrant:latest`)  
**Ports**: 6333 (REST), 6334 (gRPC)  
**License**: Apache 2.0

## Core Concepts

### Points
```python
from qdrant_client.models import PointStruct

point = PointStruct(
    id=123,                              # Integer or UUID
    vector=[0.1, 0.2, 0.3, ...],        # Dense vector
    payload={                            # Arbitrary JSON metadata
        "title": "Document title",
        "category": "tech",
        "timestamp": 1699900000,
        "tags": ["python", "ml"]
    }
)
```

### Collections
```python
from qdrant_client.models import VectorParams, Distance, HnswConfigDiff

client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    hnsw_config=HnswConfigDiff(
        m=16,                # Connections per node
        ef_construct=100,    # Build-time accuracy
        full_scan_threshold=10000
    ),
    on_disk_payload=True     # Store payload on disk
)
```

### Distance Metrics

| Metric | Use Case | Range |
| :--- | :--- | :--- |
| **COSINE** | Text embeddings, normalized vectors | 0 to 2 |
| **EUCLID** | Spatial data, image features | 0 to ∞ |
| **DOT** | Recommendations, unnormalized | -∞ to ∞ |
| **MANHATTAN** | Sparse features, discrete data | 0 to ∞ |

## Search Operations

### Basic query
```python
results = client.query_points(
    collection_name="documents",
    query=[0.1, 0.2, ...],
    limit=10,
    with_payload=True,
    with_vectors=False   # Don't return vectors (faster)
)
```

### Filtered query
```python
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range

results = client.query_points(
    collection_name="documents",
    query=query_embedding,
    query_filter=Filter(
        must=[
            FieldCondition(key="category", match=MatchValue(value="tech")),
            FieldCondition(key="timestamp", range=Range(gte=1699000000))
        ],
        must_not=[
            FieldCondition(key="status", match=MatchValue(value="archived"))
        ]
    ),
    limit=10
)
```

### Batch query
```python
from qdrant_client.models import QueryRequest

results = client.query_batch_points(
    collection_name="documents",
    requests=[
        QueryRequest(query=[0.1, ...], limit=5),
        QueryRequest(query=[0.2, ...], limit=5, filter={"must": [...]}),
        QueryRequest(query=[0.3, ...], limit=10)
    ]
)
```

## RAG Integration

### With sentence-transformers
```python
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

encoder = SentenceTransformer("all-MiniLM-L6-v2")
client = QdrantClient(host="localhost", port=6333)

client.create_collection(
    collection_name="knowledge_base",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

documents = [
    {"id": 1, "text": "Python is a programming language", "source": "wiki"},
    {"id": 2, "text": "Machine learning uses algorithms", "source": "textbook"},
]

points = [
    PointStruct(
        id=doc["id"],
        vector=encoder.encode(doc["text"]).tolist(),
        payload={"text": doc["text"], "source": doc["source"]}
    )
    for doc in documents
]
client.upsert(collection_name="knowledge_base", points=points)

# RAG retrieval
def retrieve(query: str, top_k: int = 5) -> list[dict]:
    query_vector = encoder.encode(query).tolist()
    results = client.query_points(
        collection_name="knowledge_base",
        query=query_vector,
        limit=top_k
    )
    return [{"text": p.payload["text"], "score": p.score} for p in results.points]
```

### With LangChain
```python
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Qdrant.from_documents(
    documents, embeddings,
    url="http://localhost:6333",
    collection_name="docs"
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
```

### With LlamaIndex
```python
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import VectorStoreIndex, StorageContext

vector_store = QdrantVectorStore(client=client, collection_name="llama_docs")
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
query_engine = index.as_query_engine()
```

## Advanced Features

### Multi-vector (named vectors)
```python
client.create_collection(
    collection_name="hybrid_search",
    vectors_config={
        "dense": VectorParams(size=384, distance=Distance.COSINE),
        "sparse": VectorParams(size=30000, distance=Distance.DOT)
    }
)

client.upsert(
    collection_name="hybrid_search",
    points=[PointStruct(
        id=1,
        vector={"dense": dense_embedding, "sparse": sparse_embedding},
        payload={"text": "document text"}
    )]
)

results = client.query_points(
    collection_name="hybrid_search",
    query=("dense", query_dense),
    limit=10
)
```

### Quantization (memory optimization)
```python
from qdrant_client.models import ScalarQuantization, ScalarQuantizationConfig, ScalarType

client.create_collection(
    collection_name="quantized",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    quantization_config=ScalarQuantization(
        scalar=ScalarQuantizationConfig(
            type=ScalarType.INT8,
            quantile=0.99,
            always_ram=True
        )
    )
)

# Search with rescoring
results = client.query_points(
    collection_name="quantized",
    query=query,
    search_params={"quantization": {"rescore": True}},
    limit=10
)
```

### Payload indexing
```python
from qdrant_client.models import PayloadSchemaType

client.create_payload_index(
    collection_name="documents",
    field_name="category",
    field_schema=PayloadSchemaType.KEYWORD
)

client.create_payload_index(
    collection_name="documents",
    field_name="timestamp",
    field_schema=PayloadSchemaType.INTEGER
)
```

## Production Deployment

### Qdrant Cloud
```python
client = QdrantClient(
    url="https://your-cluster.cloud.qdrant.io",
    api_key="your-api-key"
)
```

### Performance tuning
```python
# Optimize for search speed
client.update_collection(
    collection_name="documents",
    hnsw_config=HnswConfigDiff(ef_construct=200, m=32)
)

# Optimize for indexing speed (bulk loads)
client.update_collection(
    collection_name="documents",
    optimizer_config={"indexing_threshold": 20000}
)
```

## Federation Context

**Qdrant is the canonical production vector store of the arifOS Federation:**
- **Service**: `qdrant` Docker container (port 6333/6334)
- **Network**: `arifos_core_network`
- **Used by**: arifOS L3 memory, agent semantic recall, embedding storage
- **Docker Compose**: Defined in `/root/arifOS/deploy/docker-compose.yml`

**Contrast with Chroma:**
| Feature | Qdrant | Chroma |
| :--- | :--- | :--- |
| Language | Rust | Python |
| Performance | High | Moderate |
| Scaling | Horizontal (sharding) | Single-node |
| Quantization | Scalar, product, binary | None |
| Multi-vector | Dense + sparse + named | Single per doc |
| Best for | Production RAG | Prototyping |
| Federation role | L3 production memory | L3 dev/prototype memory |

## Pitfalls

| Problem | Fix |
| :--- | :--- |
| Slow query with filters | Create payload index: `create_payload_index(...)` |
| Out of memory | Enable quantization + `on_disk_payload=True` |
| Connection timeout | Set `timeout=30`, use `prefer_grpc=True` |
| Collection already exists | Check with `get_collections()` before create |
| Large bulk loads slow | Increase `indexing_threshold` temporarily |

## Related

- [[Skill_Chroma_Vector_DB]] (Development vector DB alternative)
- [[Skill_MCP_Mcporter]] (MCP mesh CLI — can query Qdrant via MCP if exposed)
- [[Skill_Docker_Management]] (Container ops for Qdrant server deployment)
- [[Concept_Vault999_Architecture]] (Immutable ledger — contrast with mutable vector memory)
- [[MCP_Tools]] (Tool surface architecture)
