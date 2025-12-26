"""
arifOS v35Omega + LlamaIndex: RAG Truth Governor

Constitutional governance for Retrieval-Augmented Generation:
- F1 Truth Floor: Verify responses cite retrieved sources (>= 0.99)
- Hallucination Detection: Flag fabricated data not in documents
- Grounding Verification: Ensure claims are traceable to source docs

Usage:
    python rag_truth_governor.py "What are the oil reserves in Malay Basin?"

Architecture:
    User Query
        |
        v
    LlamaIndex RAG (Vector Retrieval)
        |
        v
    Retrieved Documents (context nodes)
        |
        v
    arifOS Pipeline (000-999)
        |
        v
    F1 Truth Verification (citation check)
        |
        v
    SEAL (grounded) / VOID (hallucination)
"""

from __future__ import annotations

import os
import sys
import re
from dataclasses import dataclass, field
from typing import List, Optional, Callable, Any
from pathlib import Path

# Add parent to path for arifos_core imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from arifos_core.enforcement.metrics import Metrics
from arifos_core.system.apex_prime import APEXPrime
from arifos_core.utils.eye_sentinel import EyeSentinel


# ==============================================================================
# Document and Retrieval Types
# ==============================================================================

@dataclass
class Document:
    """Simple document representation for RAG."""
    id: str
    text: str
    metadata: dict = field(default_factory=dict)

    @property
    def source(self) -> str:
        return self.metadata.get("source", self.id)


@dataclass
class RetrievedNode:
    """A retrieved document node with relevance score."""
    document: Document
    score: float  # Relevance score (0.0 - 1.0)

    @property
    def text(self) -> str:
        return self.document.text

    @property
    def source(self) -> str:
        return self.document.source


@dataclass
class RAGResult:
    """Result from RAG query with governance verdict."""
    query: str
    response: str
    retrieved_nodes: List[RetrievedNode]
    metrics: Metrics
    verdict: str
    grounding_score: float  # How well response is grounded in sources
    citations_found: List[str]  # Sources cited in response
    hallucination_flags: List[str]  # Potential hallucinations detected


# ==============================================================================
# Simple In-Memory Vector Store (Demo)
# ==============================================================================

class SimpleVectorStore:
    """
    Simple in-memory vector store for demo purposes.

    In production, replace with:
    - LlamaIndex VectorStoreIndex
    - Pinecone, Weaviate, Chroma, etc.
    """

    def __init__(self):
        self.documents: List[Document] = []

    def add_document(self, doc: Document) -> None:
        """Add a document to the store."""
        self.documents.append(doc)

    def add_documents(self, docs: List[Document]) -> None:
        """Add multiple documents."""
        self.documents.extend(docs)

    def retrieve(self, query: str, top_k: int = 3) -> List[RetrievedNode]:
        """
        Simple keyword-based retrieval (demo).

        In production, use proper vector similarity search.
        """
        query_terms = set(query.lower().split())

        scored_docs = []
        for doc in self.documents:
            doc_terms = set(doc.text.lower().split())
            # Simple Jaccard-like overlap score
            overlap = len(query_terms & doc_terms)
            score = overlap / max(len(query_terms), 1)
            scored_docs.append((doc, score))

        # Sort by score descending
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        # Return top_k as RetrievedNodes
        return [
            RetrievedNode(document=doc, score=score)
            for doc, score in scored_docs[:top_k]
            if score > 0
        ]


# ==============================================================================
# Truth Verification (F1 Floor)
# ==============================================================================

class TruthVerifier:
    """
    Verify that LLM responses are grounded in retrieved documents.

    F1 Truth Floor: Response must cite sources with >= 0.99 accuracy.
    """

    # Fact patterns that should be verifiable
    FACT_PATTERNS = [
        r'\b\d+(?:\.\d+)?\s*(?:billion|million|thousand|km|meters|barrels|tonnes)\b',
        r'\b(?:19|20)\d{2}\b',  # Years
        r'\b\d+(?:\.\d+)?%\b',  # Percentages
        r'\bRM\s*\d+',  # Malaysian Ringgit amounts
        r'\b[A-Z][a-z]+\s+Basin\b',  # Basin names
    ]

    def __init__(self):
        self.fact_patterns = [re.compile(p, re.IGNORECASE) for p in self.FACT_PATTERNS]

    def extract_facts(self, text: str) -> List[str]:
        """Extract factual claims from text."""
        facts = []
        for pattern in self.fact_patterns:
            matches = pattern.findall(text)
            facts.extend(matches)
        return facts

    def verify_grounding(
        self,
        response: str,
        retrieved_nodes: List[RetrievedNode],
    ) -> tuple[float, List[str], List[str]]:
        """
        Verify response is grounded in retrieved documents.

        Returns:
            (grounding_score, citations_found, hallucination_flags)
        """
        # Extract facts from response
        response_facts = self.extract_facts(response)

        # Combine all retrieved text
        source_text = " ".join(node.text for node in retrieved_nodes)
        source_facts = self.extract_facts(source_text)

        # Check which response facts appear in sources
        grounded_facts = []
        ungrounded_facts = []

        for fact in response_facts:
            fact_lower = fact.lower()
            if any(fact_lower in src.lower() for src in source_facts):
                grounded_facts.append(fact)
            elif fact_lower in source_text.lower():
                grounded_facts.append(fact)
            else:
                ungrounded_facts.append(fact)

        # Calculate grounding score
        total_facts = len(response_facts)
        if total_facts == 0:
            # No specific facts to verify - moderate confidence
            grounding_score = 0.95
        else:
            grounded_count = len(grounded_facts)
            grounding_score = grounded_count / total_facts

        # Identify cited sources
        citations = []
        for node in retrieved_nodes:
            source_name = node.source
            if source_name.lower() in response.lower():
                citations.append(source_name)

        # Flag hallucinations
        hallucination_flags = []
        for fact in ungrounded_facts:
            hallucination_flags.append(f"Ungrounded fact: {fact}")

        return grounding_score, citations, hallucination_flags

    def compute_truth_score(
        self,
        grounding_score: float,
        retrieval_relevance: float,
    ) -> float:
        """
        Compute F1 Truth floor score.

        Combines:
        - Grounding score (how well response cites sources)
        - Retrieval relevance (how relevant are the sources)
        """
        # Weight grounding more heavily
        truth = 0.7 * grounding_score + 0.3 * retrieval_relevance
        return min(1.0, max(0.0, truth))


# ==============================================================================
# RAG Truth Governor
# ==============================================================================

class RAGTruthGovernor:
    """
    LlamaIndex RAG with arifOS Constitutional Governance.

    Every RAG query passes through:
    1. Document retrieval (vector similarity)
    2. LLM response generation
    3. F1 Truth verification (grounding check)
    4. APEX PRIME verdict (SEAL/VOID/SABAR)
    5. Cooling Ledger audit
    """

    def __init__(
        self,
        vector_store: Optional[SimpleVectorStore] = None,
        llm_generate: Optional[Callable[[str, str], str]] = None,
        sentinel: Optional[EyeSentinel] = None,
        high_stakes: bool = True,
    ):
        self.vector_store = vector_store or SimpleVectorStore()
        self.llm_generate = llm_generate or self._demo_llm_generate
        self.sentinel = sentinel or EyeSentinel()
        self.high_stakes = high_stakes
        self.verifier = TruthVerifier()
        self.cooling_ledger: List[dict] = []

    def _demo_llm_generate(self, query: str, context: str) -> str:
        """
        Demo LLM generator for testing.

        In production, replace with actual LLM call.
        """
        # Simple context-aware response
        if "malay basin" in query.lower() or "oil" in query.lower():
            return (
                "Based on the retrieved documents, the Malay Basin is a major "
                "hydrocarbon province located offshore Peninsular Malaysia. "
                "The basin covers approximately 80,000 km2 and contains proven "
                "reserves of approximately 3.6 billion barrels of oil equivalent. "
                "Primary reservoirs are in the Oligocene-Miocene sandstones. "
                "Source: Petronas Annual Report 2023."
            )
        elif "seismic" in query.lower():
            return (
                "Seismic data analysis for the region indicates promising "
                "subsurface structures. The 3D seismic surveys conducted in 2022 "
                "identified multiple prospects with estimated recoverable reserves "
                "of 500 million barrels. Uncertainty band: 15-20% (Omega_0 = 0.04). "
                "Source: Malaysian Geological Survey."
            )
        else:
            return (
                f"Based on the available documents, I can provide information "
                f"related to your query: {query}. The retrieved context suggests "
                f"this relates to geological or petroleum data. "
                f"Please verify specific figures with primary sources."
            )

    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store."""
        self.vector_store.add_documents(documents)

    def query(self, question: str, top_k: int = 3) -> RAGResult:
        """
        Execute governed RAG query.

        Flow:
        1. Retrieve relevant documents
        2. Generate LLM response with context
        3. Verify grounding (F1 Truth)
        4. Compute constitutional metrics
        5. Get APEX PRIME verdict

        Args:
            question: User query
            top_k: Number of documents to retrieve

        Returns:
            RAGResult with verdict and audit info
        """
        print(f"\n{'='*60}")
        print("RAG TRUTH GOVERNOR: Constitutional RAG Pipeline")
        print(f"{'='*60}")
        print(f"Query: {question}\n")

        # Step 1: Retrieve documents
        print("--- Step 1: Document Retrieval ---")
        retrieved_nodes = self.vector_store.retrieve(question, top_k=top_k)

        if not retrieved_nodes:
            print("  No relevant documents found")
            avg_relevance = 0.0
        else:
            avg_relevance = sum(n.score for n in retrieved_nodes) / len(retrieved_nodes)
            for i, node in enumerate(retrieved_nodes):
                print(f"  [{i+1}] {node.source} (score: {node.score:.2f})")
        print()

        # Step 2: Generate response with context
        print("--- Step 2: LLM Response Generation ---")
        context = "\n\n".join([
            f"Document: {node.source}\n{node.text}"
            for node in retrieved_nodes
        ])
        response = self.llm_generate(question, context)
        print(f"  Response: {response[:100]}...")
        print()

        # Step 3: Verify grounding (F1 Truth)
        print("--- Step 3: F1 Truth Verification ---")
        grounding_score, citations, hallucinations = self.verifier.verify_grounding(
            response, retrieved_nodes
        )
        truth_score = self.verifier.compute_truth_score(grounding_score, avg_relevance)

        print(f"  Grounding Score: {grounding_score:.2f}")
        print(f"  Citations Found: {citations}")
        print(f"  Hallucination Flags: {len(hallucinations)}")
        print(f"  F1 Truth Score: {truth_score:.2f}")
        print()

        # Step 4: Compute constitutional metrics
        print("--- Step 4: Constitutional Metrics ---")
        metrics = Metrics(
            truth=truth_score,
            delta_s=0.15 if truth_score >= 0.99 else 0.05,
            peace_squared=1.2,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.96,
            rasa=True,
            anti_hantu=True,
        )

        # Adjust metrics based on hallucinations
        if hallucinations:
            metrics = Metrics(
                truth=max(0.0, truth_score - 0.1 * len(hallucinations)),
                delta_s=-0.1,  # Hallucinations add confusion
                peace_squared=metrics.peace_squared,
                kappa_r=metrics.kappa_r,
                omega_0=metrics.omega_0,
                amanah=metrics.amanah,
                tri_witness=metrics.tri_witness,
                rasa=metrics.rasa,
                anti_hantu=metrics.anti_hantu,
            )

        print(f"  Truth: {metrics.truth:.2f}")
        print(f"  Delta_S: {metrics.delta_s:.2f}")
        print(f"  Omega_0: {metrics.omega_0:.2f}")
        print()

        # Step 5: @EYE Sentinel audit
        print("--- Step 5: @EYE Sentinel Audit ---")
        eye_report = self.sentinel.audit(
            draft_text=response,
            metrics=metrics,
            context={"query": question, "sources": [n.source for n in retrieved_nodes]},
        )

        blocking_issues = eye_report.has_blocking_issue()
        print(f"  Blocking Issues: {blocking_issues}")
        print(f"  Alerts: {len(eye_report.alerts)}")
        print()

        # Step 6: APEX PRIME verdict
        print("--- Step 6: APEX PRIME Verdict ---")
        prime = APEXPrime(high_stakes=self.high_stakes)
        verdict = prime.judge(metrics, eye_blocking=blocking_issues)

        print(f"  Verdict: {verdict}")
        print()

        # Build result
        result = RAGResult(
            query=question,
            response=response,
            retrieved_nodes=retrieved_nodes,
            metrics=metrics,
            verdict=verdict,
            grounding_score=grounding_score,
            citations_found=citations,
            hallucination_flags=hallucinations,
        )

        # Log to cooling ledger
        ledger_entry = {
            "query": question,
            "response": response,
            "sources": [n.source for n in retrieved_nodes],
            "truth": metrics.truth,
            "grounding": grounding_score,
            "verdict": verdict,
            "hallucinations": hallucinations,
        }
        self.cooling_ledger.append(ledger_entry)

        # Summary
        print(f"{'='*60}")
        print("RAG VERDICT SUMMARY")
        print(f"{'='*60}")
        print(f"Query: {question}")
        print(f"Verdict: {verdict}")
        print(f"F1 Truth: {metrics.truth:.2f} (threshold: >= 0.99)")
        print(f"Grounding: {grounding_score:.2%}")
        print(f"Sources: {len(retrieved_nodes)}")
        print(f"Citations: {len(citations)}")
        print(f"Hallucinations: {len(hallucinations)}")
        print(f"{'='*60}\n")

        return result


# ==============================================================================
# Demo Documents (Petronas/Geological)
# ==============================================================================

def create_petronas_documents() -> List[Document]:
    """Create sample Petronas/geological documents for demo."""
    return [
        Document(
            id="petronas_ar_2023_01",
            text=(
                "The Malay Basin is Malaysia's most prolific hydrocarbon province, "
                "located offshore Peninsular Malaysia. The basin covers approximately "
                "80,000 km2 and has been producing oil and gas since 1978. "
                "As of 2023, proven reserves stand at approximately 3.6 billion "
                "barrels of oil equivalent. Primary reservoirs are found in "
                "Oligocene-Miocene sandstones at depths of 1,500-3,500 meters."
            ),
            metadata={"source": "Petronas Annual Report 2023", "type": "financial"},
        ),
        Document(
            id="mgs_seismic_2022",
            text=(
                "3D seismic surveys conducted in 2022 across the central Malay Basin "
                "identified 15 new prospects with combined estimated recoverable "
                "reserves of 500 million barrels. Survey coverage extended to "
                "4,200 km2 with data quality rated as excellent. Uncertainty in "
                "reserve estimates is 15-20% due to limited well control in "
                "deeper prospects below 4 km."
            ),
            metadata={"source": "Malaysian Geological Survey", "type": "technical"},
        ),
        Document(
            id="petronas_esg_2023",
            text=(
                "Environmental impact assessments for Malay Basin operations "
                "cover marine biodiversity, fishing community impacts, and "
                "carbon emissions. Current operations maintain compliance with "
                "Malaysian Environmental Quality Act. Carbon intensity reduced "
                "by 12% since 2020. Community investment programs totaling "
                "RM 150 million support local fishing communities."
            ),
            metadata={"source": "Petronas ESG Report 2023", "type": "ESG"},
        ),
        Document(
            id="economic_analysis_2023",
            text=(
                "Economic analysis of Malay Basin development projects indicates "
                "NPV of RM 45-60 billion over a 10-year horizon under current "
                "oil price assumptions ($70-85/barrel Brent). Internal rate of "
                "return projected at 18-22%. Direct employment: 15,000 jobs. "
                "Indirect employment: 45,000 jobs across supply chain."
            ),
            metadata={"source": "Petronas Economic Analysis 2023", "type": "economic"},
        ),
    ]


# ==============================================================================
# Main Entry Point
# ==============================================================================

def main():
    """Run RAG Truth Governor demo."""
    import argparse

    parser = argparse.ArgumentParser(
        description="RAG Truth Governor: Constitutional RAG Pipeline"
    )
    parser.add_argument(
        "query",
        nargs="?",
        default="What are the oil reserves in the Malay Basin?",
        help="Query to process",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of documents to retrieve (default: 3)",
    )

    args = parser.parse_args()

    # Initialize governor with demo documents
    governor = RAGTruthGovernor()
    governor.add_documents(create_petronas_documents())

    # Execute governed query
    result = governor.query(args.query, top_k=args.top_k)

    # Final output
    print("\n" + "="*60)
    print("FINAL RESULT")
    print("="*60)
    print(f"Query: {result.query}")
    print(f"Verdict: {result.verdict}")
    print(f"Response: {result.response}")
    print(f"Grounding: {result.grounding_score:.2%}")

    return result


if __name__ == "__main__":
    main()
