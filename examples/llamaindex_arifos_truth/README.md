# arifOS + LlamaIndex: RAG Truth Governor

**Constitutional governance for Retrieval-Augmented Generation.** Verify LLM responses are grounded in retrieved documents using F1 Truth Floor verification.

```
+=============================================================================+
|  RAG Truth Governor - Document-Grounded AI                                  |
|  F1 Truth >= 0.99: Responses must cite sources accurately                   |
|  Hallucination Detection: Flag fabricated data not in documents             |
+=============================================================================+
```

## Quick Start

```bash
cd examples/llamaindex_arifos_truth/
pip install -r requirements.txt
python rag_truth_governor.py "What are the oil reserves in Malay Basin?"
```

**Expected Output:**
```
============================================================
RAG TRUTH GOVERNOR: Constitutional RAG Pipeline
============================================================
Query: What are the oil reserves in Malay Basin?

--- Step 1: Document Retrieval ---
  [1] Petronas Annual Report 2023 (score: 0.85)
  [2] Malaysian Geological Survey (score: 0.72)
  [3] Petronas Economic Analysis 2023 (score: 0.65)

--- Step 3: F1 Truth Verification ---
  Grounding Score: 0.95
  Citations Found: ['Petronas Annual Report 2023']
  Hallucination Flags: 0
  F1 Truth Score: 0.99

--- Step 6: APEX PRIME Verdict ---
  Verdict: SEAL

============================================================
RAG VERDICT SUMMARY
============================================================
Verdict: SEAL
F1 Truth: 0.99 (threshold: >= 0.99)
Grounding: 95%
============================================================
```

## Architecture

```
+---------------------------------------------------------------------+
|                    RAG Truth Governor Architecture                   |
+---------------------------------------------------------------------+
|                                                                     |
|   User Query                                                        |
|       |                                                             |
|       v                                                             |
|   +-------------------------------------------------------+         |
|   |  DOCUMENT RETRIEVAL (LlamaIndex/Vector Store)         |         |
|   |  - Semantic similarity search                         |         |
|   |  - Top-K relevant documents                           |         |
|   |  - Relevance scoring                                  |         |
|   +-------------------------------------------------------+         |
|       |                                                             |
|       v                                                             |
|   +-------------------------------------------------------+         |
|   |  LLM RESPONSE GENERATION                               |         |
|   |  - Context: Retrieved documents                       |         |
|   |  - Generate response with citations                   |         |
|   +-------------------------------------------------------+         |
|       |                                                             |
|       v                                                             |
|   +-------------------------------------------------------+         |
|   |  F1 TRUTH VERIFICATION                                 |         |
|   |  - Extract factual claims from response               |         |
|   |  - Verify claims against source documents             |         |
|   |  - Compute grounding score                            |         |
|   |  - Detect hallucinations (ungrounded facts)           |         |
|   +-------------------------------------------------------+         |
|       |                                                             |
|       v                                                             |
|   +-------------------------------------------------------+         |
|   |  APEX PRIME VERDICT                                    |         |
|   |  SEAL: F1 >= 0.99, response grounded in sources       |         |
|   |  VOID: F1 < 0.99, hallucination detected              |         |
|   |  PARTIAL: Soft floor warning, proceed with caution    |         |
|   +-------------------------------------------------------+         |
|       |                                                             |
|       v                                                             |
|   GOVERNED RESPONSE (with Cooling Ledger audit trail)               |
|                                                                     |
+---------------------------------------------------------------------+
```

## F1 Truth Floor Verification

The Truth Governor verifies responses using multiple checks:

### 1. Fact Extraction
```python
# Extract verifiable facts from response
facts = verifier.extract_facts(response)
# Examples: "3.6 billion barrels", "2023", "80,000 km2"
```

### 2. Grounding Check
```python
# Verify facts appear in retrieved documents
grounding_score, citations, hallucinations = verifier.verify_grounding(
    response, retrieved_nodes
)
```

### 3. Truth Score Computation
```python
# Combine grounding and retrieval relevance
truth_score = 0.7 * grounding_score + 0.3 * retrieval_relevance
# Must be >= 0.99 for SEAL verdict
```

### 4. Hallucination Detection
```python
# Flag facts not found in source documents
hallucination_flags = ["Ungrounded fact: 999 billion barrels"]
# Hallucinations reduce truth score and may trigger VOID
```

## Usage Examples

### Basic RAG Query

```python
from rag_truth_governor import RAGTruthGovernor, create_petronas_documents

governor = RAGTruthGovernor()
governor.add_documents(create_petronas_documents())

result = governor.query("What are the oil reserves?")
print(f"Verdict: {result.verdict}")
print(f"Truth: {result.metrics.truth}")
print(f"Grounding: {result.grounding_score}")
```

### With Custom LLM

```python
import openai

def openai_generate(query: str, context: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Context:\n{context}"},
            {"role": "user", "content": query},
        ],
    )
    return response.choices[0].message.content

governor = RAGTruthGovernor(llm_generate=openai_generate)
```

### With LlamaIndex Vector Store

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# Load documents
documents = SimpleDirectoryReader("sample_docs/petronas/").load_data()
index = VectorStoreIndex.from_documents(documents)

# Custom retriever using LlamaIndex
def llamaindex_retrieve(query: str, top_k: int = 3):
    retriever = index.as_retriever(similarity_top_k=top_k)
    return retriever.retrieve(query)

# Integrate with RAG Governor
governor = RAGTruthGovernor()
# ... custom integration
```

## Testing

```bash
# Run test suite
pytest test_rag_governance.py -v

# Expected: 10/10 tests passing
```

### Test Coverage

| Test | Description | Expected |
|------|-------------|----------|
| `test_extract_facts` | Fact extraction from text | Facts identified |
| `test_grounding_score_high` | Grounded response | Score >= 0.5 |
| `test_grounding_score_low_hallucination` | Hallucinated response | Flags detected |
| `test_retrieval_relevance` | Document retrieval | Relevant docs |
| `test_governor_seal_grounded` | Full pipeline - grounded | SEAL/PARTIAL |
| `test_governor_cooling_ledger` | Audit logging | Entries created |
| `test_void_on_low_truth` | Truth < 0.99 | VOID |
| `test_seal_on_high_truth` | All floors pass | SEAL |
| `test_citation_detection` | Source citation | Citations found |

## Demo Scenarios

```bash
# Run all demo scenarios
python demo_petronas_docs.py --all

# Hallucination detection test
python demo_petronas_docs.py --hallucination-test
```

### Scenario Results

| Scenario | Domain | Expected | Truth Check |
|----------|--------|----------|-------------|
| Oil Reserves | reserves | SEAL | Grounded in AR 2023 |
| Seismic Survey | technical | SEAL | MGS 2022 data |
| NPV Analysis | economic | SEAL | Economic analysis |
| ESG Impact | ESG | SEAL | ESG Report 2023 |
| Hallucination | test | VOID | Fabricated data |

## Files

```
examples/llamaindex_arifos_truth/
├── rag_truth_governor.py    # Core RAG + Truth pipeline
├── test_rag_governance.py   # 10 governance tests
├── demo_petronas_docs.py    # Petronas demo scenarios
├── sample_docs/             # Demo documents
│   └── petronas/
│       ├── malay_basin_overview.txt
│       └── economic_analysis.txt
├── requirements.txt
└── README.md
```

## Constitutional Floors for RAG

| Floor | Application in RAG | Threshold |
|-------|-------------------|-----------|
| **F1 Truth** | Response grounded in sources | >= 0.99 |
| **F2 Delta_S** | Reduces confusion, adds clarity | >= 0 |
| **F5 Omega_0** | Acknowledges uncertainty | [0.03, 0.05] |
| **F6 Amanah** | Traceable to source documents | LOCK |
| **F9 Anti-Hantu** | No fabricated claims | PASS |

## Enterprise Use Cases

### Petronas (Oil & Gas)
- Seismic report analysis
- Reserve estimation grounding
- Regulatory compliance verification

### Legal/Compliance
- Contract clause verification
- Regulatory document grounding
- Audit trail for decisions

### Research
- Paper citation verification
- Claim grounding in sources
- Literature review accuracy

## Related

- [Main arifOS README](../../README.md)
- [AutoGen W@W Federation](../autogen_arifos_governor/)
- [APEX PRIME Judiciary](../../arifos_core/APEX_PRIME.py)

---

**Version:** v35.1.0
**Last Updated:** 2025-12-05
**Tests:** 10 passing

DITEMPA BUKAN DIBERI
