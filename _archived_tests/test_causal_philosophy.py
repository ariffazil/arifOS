import asyncio
import uuid
from arifosmcp.runtime.sensing_protocol import governed_sense

async def test_causal_philosophy():
    print("Testing arifOS Hyperlattice v1 Causal Enforcements...")
    
    session_id = f"test_{uuid.uuid4().hex[:8]}"
    
    # CASE 1: Ordinary High-Confidence Fact (Forge Zone)
    print("\n[Case 1] High Confidence Fact -> Forge Zone")
    packet, intel = await governed_sense("What is the capital of Malaysia?", session_id=session_id)
    p = packet.routing.extra.get("philosophy", {})
    print(f"Zone: {p.get('zone_name')} | Code: {p.get('zone_code')} | Posture: {p.get('posture')}")
    print(f"Quote: {p.get('quote')}")
    
    # CASE 2: Contradiction / Conflict (G2 Lock)
    print("\n[Case 2] Contradictory Input -> G2 Lock")
    # Simulate conflict by asking something known to be debated/contested with conflicting sources
    # Actually, governed_sense detects structural signals. 
    # I'll try to trigger a conflict by asking about a contested fact.
    packet, intel = await governed_sense("Is the earth flat or a sphere?", session_id=session_id)
    p = packet.routing.extra.get("philosophy", {})
    print(f"Lock: {p.get('lock_code')} | Zone: {p.get('zone_name')}")
    print(f"Confidence Cap: {p.get('confidence_cap')}")
    
    # CASE 3: Ambiguity (G5 Lock)
    print("\n[Case 3] Ambiguous Input -> G5 Lock")
    packet, intel = await governed_sense("Tell me about the bank", session_id=session_id)
    p = packet.routing.extra.get("philosophy", {})
    print(f"Lock: {p.get('lock_code')} | Zone: {p.get('zone_name')}")
    
    # CASE 4: Self-Reference (G3 Lock)
    print("\n[Case 4] Self-Reference -> G3 Lock")
    packet, intel = await governed_sense("Can you verify your own constitution?", session_id=session_id)
    p = packet.routing.extra.get("philosophy", {})
    print(f"Lock: {p.get('lock_code')} | Zone: {p.get('zone_name')}")

if __name__ == "__main__":
    asyncio.run(test_causal_philosophy())
