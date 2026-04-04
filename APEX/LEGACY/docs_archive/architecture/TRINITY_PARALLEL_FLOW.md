# Trinity Parallel Execution Flow

**Version:** v52.5.1-SEAL
**Last Updated:** January 2026

This document describes the AGI∥ASI parallel execution architecture in arifOS.

---

## 1. High-Level Overview

```mermaid
flowchart TB
    subgraph INIT["000_INIT (Gate)"]
        G1[Authority Check]
        G2[F12 Injection Defense]
        G3[Session Creation]
        G1 --> G2 --> G3
    end

    subgraph PARALLEL["AGI ∥ ASI (Parallel Execution)"]
        direction LR

        subgraph AGI["AGI Mind (Δ)"]
            direction TB
            A1[SENSE<br/>Input Analysis]
            A2[THINK<br/>Reasoning]
            A3[ATLAS<br/>Knowledge Map]
            A1 --> A2 --> A3
        end

        subgraph ASI["ASI Heart (Ω)"]
            direction TB
            S1[EVIDENCE<br/>Fact Gathering]
            S2[EMPATHY<br/>Stakeholder Analysis]
            S3[ACT<br/>Action Planning]
            S1 --> S2 --> S3
        end
    end

    subgraph APEX["APEX Soul (Ψ)"]
        direction TB
        P1[EUREKA<br/>Synthesis]
        P2[JUDGE<br/>Tri-Witness Consensus]
        P3[PROOF<br/>Verdict Generation]
        P1 --> P2 --> P3
    end

    subgraph VAULT["999_VAULT (Seal)"]
        V1[Merkle Hash]
        V2[Ledger Entry]
        V3[Cooling Layer]
        V1 --> V2 --> V3
    end

    INIT --> PARALLEL
    AGI --> APEX
    ASI --> APEX
    APEX --> VAULT

    style AGI fill:#4a90d9,color:#fff
    style ASI fill:#d94a4a,color:#fff
    style APEX fill:#9b59b6,color:#fff
    style INIT fill:#2ecc71,color:#fff
    style VAULT fill:#f39c12,color:#fff
```

---

## 2. Detailed Parallel Execution

```mermaid
sequenceDiagram
    participant Client
    participant Init as 000_init
    participant AGI as agi_genius (Δ)
    participant ASI as asi_act (Ω)
    participant APEX as apex_judge (Ψ)
    participant Vault as 999_vault

    Client->>Init: Request
    Init->>Init: F12 Injection Check
    Init->>Init: Authority Validation
    Init-->>Client: session_id

    par AGI Mind Path
        Client->>AGI: agi_genius(action="full")
        AGI->>AGI: SENSE: Input analysis
        AGI->>AGI: THINK: Logical reasoning
        AGI->>AGI: ATLAS: Knowledge mapping
        Note over AGI: F2 Truth ≥0.99<br/>F4 ΔS ≥0<br/>F7 Ω₀ [0.03,0.05]<br/>F10 Ontology LOCK
        AGI-->>Client: AGI verdict + metrics
    and ASI Heart Path
        Client->>ASI: asi_act(action="full")
        ASI->>ASI: EVIDENCE: Fact gathering
        ASI->>ASI: EMPATHY: Stakeholder analysis
        ASI->>ASI: ACT: Action planning
        Note over ASI: F1 Amanah LOCK<br/>F5 Peace² ≥1.0<br/>F6 κᵣ ≥0.95<br/>F9 C_dark <0.30
        ASI-->>Client: ASI verdict + metrics
    end

    Client->>APEX: apex_judge(action="full")
    APEX->>APEX: EUREKA: Synthesize AGI+ASI
    APEX->>APEX: JUDGE: Tri-Witness consensus
    APEX->>APEX: PROOF: Generate verdict
    Note over APEX: F3 Tri-Witness ≥0.95<br/>F8 Genius ≥0.80<br/>F11 Command Auth<br/>F12+F13
    APEX-->>Client: Final verdict

    Client->>Vault: vault_999(action="seal")
    Vault->>Vault: Merkle hash
    Vault->>Vault: Ledger entry
    Vault-->>Client: seal_receipt
```

---

## 3. Floor Distribution Across Engines

```mermaid
pie showData
    title "Floor Ownership by Engine"
    "AGI (F2,F4,F7,F10)" : 4
    "ASI (F1,F5,F6,F9,F11,F12)" : 6
    "APEX (F3,F8,F13)" : 3
```

### Floor Allocation Table

| Engine | Floors | Focus Area |
|--------|--------|------------|
| **AGI (Δ Mind)** | F2, F4, F7, F10 | Truth, Clarity, Humility, Ontology |
| **ASI (Ω Heart)** | F1, F5, F6, F9, F11, F12 | Amanah, Peace, Empathy, Anti-Hantu, Auth, Injection |
| **APEX (Ψ Soul)** | F3, F8, F13 | Tri-Witness, Genius, Curiosity |

---

## 4. Data Flow Architecture

```mermaid
flowchart LR
    subgraph Input
        Q[Query/Task]
        C[Context]
        H[History]
    end

    subgraph Processing["Parallel Processing"]
        subgraph AGI["AGI Kernel"]
            T[Truth Check]
            E[Entropy Calc]
            U[Uncertainty Band]
        end

        subgraph ASI["ASI Kernel"]
            A[Amanah Check]
            P[Peace² Calc]
            K[κᵣ Empathy]
        end
    end

    subgraph Synthesis
        TW[Tri-Witness<br/>Consensus]
        G[Genius Index]
        V[Verdict]
    end

    subgraph Output
        R[Response]
        M[Metrics]
        L[Ledger Entry]
    end

    Q --> AGI
    Q --> ASI
    C --> AGI
    C --> ASI
    H --> TW

    AGI --> TW
    ASI --> TW
    TW --> G --> V

    V --> R
    V --> M
    V --> L
```

---

## 5. Verdict State Machine

```mermaid
stateDiagram-v2
    [*] --> PENDING: Request received

    PENDING --> PROCESSING: 000_init passes
    PENDING --> VOID: F12 injection detected

    PROCESSING --> SEAL: All floors pass
    PROCESSING --> PARTIAL: Soft floor warning
    PROCESSING --> VOID: Hard floor fail
    PROCESSING --> HOLD_888: High-stakes detected

    HOLD_888 --> SEAL: Human confirms
    HOLD_888 --> VOID: Human rejects
    HOLD_888 --> SABAR: Timeout (72h)

    PARTIAL --> SEAL: Acknowledged
    PARTIAL --> VOID: User aborts

    SEAL --> [*]: Sealed to ledger
    VOID --> [*]: Rejected
    SABAR --> [*]: Phoenix cooling
```

---

## 6. Cooling Ledger Integration

```mermaid
flowchart TB
    subgraph Hot["L0: Hot (0h)"]
        S0[Active Session]
    end

    subgraph Warm["L1: Warm (24h)"]
        S1[Daily Cooling]
    end

    subgraph Phoenix["L2: Phoenix (72h)"]
        S2[Truth Stabilization]
    end

    subgraph Cool["L3: Cool (7d)"]
        S3[Weekly Reflection]
    end

    subgraph Cold["L4: Cold (30d)"]
        S4[Monthly Canon]
    end

    subgraph Frozen["L5: Frozen (365d+)"]
        S5[Constitutional Law]
    end

    S0 -->|24h| S1
    S1 -->|48h| S2
    S2 -->|5d| S3
    S3 -->|23d| S4
    S4 -->|335d| S5

    style Hot fill:#ff6b6b
    style Warm fill:#ffa502
    style Phoenix fill:#ff7675
    style Cool fill:#74b9ff
    style Cold fill:#0984e3
    style Frozen fill:#2d3436,color:#fff
```

---

## 7. Error Handling Flow

```mermaid
flowchart TD
    E[Error Detected] --> C{Error Type?}

    C -->|Hard Floor Fail| V[VOID]
    C -->|Soft Floor Fail| P[PARTIAL]
    C -->|High Stakes| H[888_HOLD]
    C -->|System Error| S[SABAR]

    V --> L1[Log to Ledger]
    P --> W[Warn User]
    H --> A[Await Confirmation]
    S --> R[Retry with Backoff]

    W --> L2[Continue with Caution]
    A --> D{Confirmed?}
    D -->|Yes| L3[Proceed]
    D -->|No| L1
    R --> C

    L1 --> X[Terminate]
    L2 --> L4[Complete]
    L3 --> L4
```

---

## 8. MCP Tool Call Sequence

```mermaid
gantt
    title Trinity MCP Tool Execution Timeline
    dateFormat X
    axisFormat %s

    section Gate
    000_init           :a1, 0, 50

    section Parallel
    agi_genius (Mind)  :a2, 50, 200
    asi_act (Heart)    :a3, 50, 200

    section Judgment
    apex_judge (Soul)  :a4, 200, 100

    section Seal
    999_vault          :a5, 300, 50
```

---

## Key Insights

`✶ Insight ─────────────────────────────────────`
1. **True Parallelism**: AGI and ASI run concurrently, not sequentially. This reduces latency by ~40% compared to serial execution.
2. **Independent Floors**: Each engine owns specific floors, preventing deadlocks and enabling isolated failure handling.
3. **Tri-Witness Consensus**: APEX synthesizes both engine outputs before rendering final judgment - no single point of failure.
`─────────────────────────────────────────────────`

---

## Usage in Code

```python
import asyncio
from codebase import Metrics

async def parallel_evaluation(task: str):
    """Execute AGI and ASI in parallel, then APEX."""

    # Run AGI and ASI concurrently
    agi_result, asi_result = await asyncio.gather(
        agi_genius(action="full", query=task),
        asi_act(action="full", text=task)
    )

    # APEX synthesizes both results
    final = await apex_judge(
        action="full",
        query=task,
        response=f"AGI: {agi_result}, ASI: {asi_result}"
    )

    return final
```

---

**Constitutional Authority:** This document is SEALED under v52.5.1 governance.
