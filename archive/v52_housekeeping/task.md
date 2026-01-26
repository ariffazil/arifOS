# Task: AAA Cluster Deployment (v52.2)

**Objective:** Deploy the AAA Cluster (Axis-Arif-Apex) to Railway.
**Strategy:** 3 Separate Containers (Clean Build).
**Constraint:** Zero Energy spent on fixing the legacy Monolith. We build the new world, not patch the old one.
**Mechanism:** "Loop Bootstrap" (Recovery over Restart).

## Phase 1: Preparation (Current)
- [x] Analyze Deployment Infrastructure (`aaa_deployment_directive_confirmed.md`)
- [x] Lock Legacy Code (`implementation_plan.md`)
- [x] Align Workflow Files (`task.md`, `ACT.md`)

## Phase 2: Implementation (Complete)
- [x] Generate Entry Points (`axis.py`, `arif.py`, `apex.py`, `gateway.py`)
- [x] Create Dockerfiles (`Dockerfile.axis`, `Dockerfile.arif`, `Dockerfile.apex`, `Dockerfile.gateway`)
- [x] Create `railway.json` for Multi-Service Deployment
- [x] Implement Circuit Breaker in Gateway (Fix 307 Redirect Bug Here)

## Phase 3: Deployment & Verification
- [ ] Deploy to Railway (v52.2-aaa-cluster)
- [ ] Verify Endpoints (HTTPS)
- [ ] Run Integration Tests (Simulate Failure)
