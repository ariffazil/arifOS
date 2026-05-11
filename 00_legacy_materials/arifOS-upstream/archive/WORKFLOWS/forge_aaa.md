---
description: Formal process to forge the AAA Servant Wire and integrate with A-RIF Kernel
---

# Workflow: Forging The AAA Servant Wire (Trinity L3)

This workflow defines the sovereign process for sealing the AAA operational layer, transitioning from Hugging Face dependencies to a local, governed Ollama Agent Wire.

## Prerequisites
1. **Ollama Engine**: Ensure `ollama` is pulled and the `llama3.2` model is available.
2. **A-RIF Kernel**: M1-M10 modules must be configured in `C:/ariffazil/arifOS/333/ARIF/`.
3. **Dependencies**: `smolagents`, `litellm`, `datasets`, `pandas` installed in the python 3.14+ environment.

## Steps

### 1. Initialize the Mental Repository (Model Factory)
Ensure the `model_factory.py` is present in the `333/ARIF` directory to handle sovereign model selection.

### 2. Configure the Servant Wire (arif_agent.py)
Update the `aaa_mcp/arif_agent.py` to point to the `ARIF_Orchestrator` for all constitutional verdicts.

### 3. Deploy Sensory Expansion
// turbo
1. Create the M11 (TableQA) and M12 (DocQA) modules.
2. Register the tools in the `AAA_Agent` tool registry.

### 4. Hardware/Docker Synchronization
Update `docker-compose.yml` to reflect the `ollama_engine` internal endpoint and set `OLLAMA_URL` accordingly.

### 5. Constitutional Verification
Run the `ARIF_Orchestrator` test suite against the local Ollama backend to ensure the 13 Floors are enforced without external network reliance.

### 6. 999 SEAL
Seal the implementation by updating the Cooling Ledger with the new servant status.

**"DITEMPA BUKAN DIBERI"**
