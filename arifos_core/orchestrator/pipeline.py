"""
arifOS Pipeline Orchestrator (v49)

Coordinates 000→999 metabolic loop across 4 servers (VAULT/AGI/ASI/APEX).

Architecture:
- Routes queries through constitutional stages
- Manages inter-server communication
- Enforces verdict propagation (SEAL/PARTIAL/VOID/SABAR)
- Coordinates Phoenix-72 cooling tiers

Authority: Δ (Architect)
Version: v49.0.0
"""

import asyncio
from typing import Any, Dict, Optional

import httpx


class Pipeline:
    """
    Pipeline Orchestrator - Routes queries through 000→999 loop.

    Flow: VAULT(000) → AGI(111/222/333) → APEX(444) → ASI(555/666) → APEX(777/888/889) → VAULT(999)
    """

    def __init__(
        self,
        vault_url: str = "http://localhost:9000",
        agi_url: str = "http://localhost:9001",
        asi_url: str = "http://localhost:9002",
        apex_url: str = "http://localhost:9003",
    ):
        self.vault_url = vault_url
        self.agi_url = agi_url
        self.asi_url = asi_url
        self.apex_url = apex_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def route(self, query: str, user_id: str) -> Dict[str, Any]:
        """
        Main routing function - executes full 000→999 pipeline.

        Args:
            query: User query
            user_id: User identifier

        Returns:
            Final verdict and output from 999 VAULT
        """
        # Stage 000: INIT
        init_result = await self.vault_init(query, user_id)
        if init_result["verdict"] != "SEAL":
            return init_result  # Early exit if VOID/SABAR

        session_id = init_result["session_id"]
        context = {"user_id": user_id, "session_id": session_id}
        floor_scores = init_result["floor_scores"]

        # Stage 111: SENSE (AGI)
        sense_result = await self.agi_process(query, session_id, "111_SENSE", context, floor_scores)
        if sense_result["verdict"] == "VOID":
            return await self.vault_store(session_id, query, sense_result)

        floor_scores.update(sense_result["floor_scores"])

        # Stage 222: THINK (AGI)
        think_result = await self.agi_process(query, session_id, "222_THINK", context, floor_scores)
        if think_result["verdict"] == "VOID":
            return await self.vault_store(session_id, query, think_result)

        floor_scores.update(think_result["floor_scores"])

        # Stage 333: ATLAS (AGI)
        atlas_result = await self.agi_process(query, session_id, "333_ATLAS", context, floor_scores)
        floor_scores.update(atlas_result["floor_scores"])

        # Stage 444: EVIDENCE (APEX)
        evidence_result = await self.apex_process(
            query, session_id, "444_EVIDENCE", context, floor_scores,
            agi_output={"sense": sense_result, "think": think_result, "atlas": atlas_result}
        )
        floor_scores.update(evidence_result["floor_scores"])

        # Stage 555: EMPATHY (ASI)
        empathy_result = await self.asi_process(query, session_id, "555_EMPATHY", context, floor_scores)
        if empathy_result["verdict"] == "VOID":
            return await self.vault_store(session_id, query, empathy_result)

        floor_scores.update(empathy_result["floor_scores"])

        # Stage 666: ACT (ASI)
        act_result = await self.asi_process(query, session_id, "666_ACT", context, floor_scores)
        floor_scores.update(act_result["floor_scores"])

        # Stage 777: EUREKA (APEX)
        eureka_result = await self.apex_process(
            query, session_id, "777_EUREKA", context, floor_scores
        )
        floor_scores.update(eureka_result["floor_scores"])

        # Stage 888: SEAL (APEX)
        seal_result = await self.apex_process(
            query, session_id, "888_SEAL", context, floor_scores
        )
        floor_scores.update(seal_result["floor_scores"])

        # Stage 889: PROOF (APEX) - if SEAL
        zkpc_receipt = None
        if seal_result["verdict"] == "SEAL":
            proof_result = await self.apex_process(
                query, session_id, "889_PROOF", context, floor_scores
            )
            zkpc_receipt = proof_result.get("zkpc_receipt")

        # Stage 999: VAULT (final storage)
        final_result = await self.vault_store(
            session_id, query, seal_result, zkpc_receipt=zkpc_receipt
        )

        return final_result

    async def vault_init(self, query: str, user_id: str) -> Dict[str, Any]:
        """Call VAULT 000 INIT."""
        response = await self.client.post(
            f"{self.vault_url}/init",
            json={"query": query, "user_id": user_id}
        )
        return response.json()

    async def agi_process(
        self, query: str, session_id: str, stage: str,
        context: Dict, floor_scores: Dict
    ) -> Dict[str, Any]:
        """Call AGI server (111/222/333)."""
        response = await self.client.post(
            f"{self.agi_url}/process",
            json={
                "session_id": session_id,
                "query": query,
                "stage": stage,
                "context": context,
                "floor_scores": floor_scores,
            }
        )
        return response.json()

    async def asi_process(
        self, query: str, session_id: str, stage: str,
        context: Dict, floor_scores: Dict
    ) -> Dict[str, Any]:
        """Call ASI server (555/666)."""
        response = await self.client.post(
            f"{self.asi_url}/process",
            json={
                "session_id": session_id,
                "query": query,
                "stage": stage,
                "context": context,
                "floor_scores": floor_scores,
            }
        )
        return response.json()

    async def apex_process(
        self, query: str, session_id: str, stage: str,
        context: Dict, floor_scores: Dict,
        agi_output: Optional[Dict] = None,
        asi_output: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Call APEX server (444/777/888/889)."""
        response = await self.client.post(
            f"{self.apex_url}/process",
            json={
                "session_id": session_id,
                "query": query,
                "stage": stage,
                "context": context,
                "floor_scores": floor_scores,
                "agi_output": agi_output,
                "asi_output": asi_output,
            }
        )
        return response.json()

    async def vault_store(
        self, session_id: str, query: str, result: Dict,
        zkpc_receipt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Call VAULT 999 VAULT (final storage)."""
        response = await self.client.post(
            f"{self.vault_url}/store",
            json={
                "session_id": session_id,
                "query": query,
                "verdict": result.get("verdict", "UNKNOWN"),
                "floor_scores": result.get("floor_scores", {}),
                "stage_outputs": result.get("output", {}),
                "zkpc_receipt": zkpc_receipt,
            }
        )
        return response.json()

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
