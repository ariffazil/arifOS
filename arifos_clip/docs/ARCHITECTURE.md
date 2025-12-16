# A CLIP Architecture

**Layer A - Constitution Surface:** High-level governance definitions and interfaces.
- **AGENTS.md:** Defines the conceptual agent roles (Observer, Logician, Empath, etc.) that correspond to stages.
- **commands/**: Contains documentation (Markdown) for each CLI command (000-999), describing usage and intent.
- **agents/**: Detailed profiles for key agent roles (sense, reflect, reason, empathize, align).

**Precedence:** Repo root `AGENTS.md` is Tier-1 law (applies everywhere). `arifos_clip/AGENTS.md` is scoped stage-role guidance for this subtree only.

**Layer B – Executors:** The CLI stage executors in `aclip/cli/`. Each pipeline stage has a Python module (e.g., `000_void.py`, `111_sense.py`, ..., `999_seal.py`) implementing that stage's logic. These executors handle argument parsing (via dispatchers) and coordinate reading/writing session data.

**Layer C – Bridge:** The interface to the arifOS governance engine, in `aclip/bridge/`.
- **arifos_client.py:** Provides functions to call arifOS (e.g., to get a verdict on sealing). This layer ensures A CLIP does not replicate law logic but delegates to arifOS.
- **verdicts.py:** Defines verdict constants (e.g., `VERDICT_SEAL`, `VERDICT_HOLD`) and maps verdicts to exit codes.
- **authority.py:** Handles validation of authority tokens (ensuring a human has authorized the action).
- **time.py:** (Optional) Utilities for time-based governance (e.g., enforcing a cooling period before certain actions, as per Phoenix-72).

**Layer D – Enforcement:** Git hooks and internal checks that enforce the pipeline process.
- **hooks/**: Contains Git hook scripts (`pre-commit`, `commit-msg`, `pre-push`) that prevent bypassing A CLIP rules. For example, they block commits if a hold is unresolved or block pushes if the session isn't sealed.
- Within CLI code, enforcement includes requiring `--apply` and tokens for sealing, and preventing sealing if any hold exists or if arifOS has not approved.

**Layer E – Decision Artifacts:** Outputs and records of decisions in `.arifos_clip/`.
- **Session JSON (`session.json`):** The canonical record of the session (task, status, and a list of all stage results – the "stage JSON envelope").
- **Forge pack (`forge.json`):** A consolidated JSON produced at stage 777 containing the task, all steps, and intermediate results.
- **Hold bundle (`holds/`):** If a hold is triggered, a `hold.json` (machine-readable) and `hold.md` (human-readable) are generated to document the issue and freeze the pipeline.
- **(Optional)** Additional outputs (if needed, could be in `aclip/outputs/`) for storing any artifacts each stage creates, but by default all data is kept in the session JSON.

**Layer F – Proof (Tests):** Automated tests under `tests/` validate that A CLIP operates correctly and invariants hold.
- Tests cover a full pipeline run, enforcement of holds and authority, and hook behavior to ensure the system is robust against misuse.

## Protocols & Data Formats

**Stage JSON Envelope (Session Structure):** Each pipeline stage appends an entry to the `steps` array in `.arifos_clip/session.json`. Each entry is a JSON object with:
- `stage`: Numeric code of the stage (e.g., 111).
- `name`: Verb name of the stage (e.g., "sense").
- `input`: The input or context considered (often the previous stage's output or the initial task).
- `output`: A summary of the stage's output or decision.
- `exit_code`: The exit code resulting from that stage's execution.
- `timestamp`: ISO8601 timestamp when the stage was executed.

For example, after 000 and 111 stages, `session.json` might contain:
```json
{
  "id": "20251213111230",
  "task": "Example task",
  "status": "ACTIVE",
  "steps": [
    {
      "stage": 0,
      "name": "void",
      "input": "Example task",
      "output": null,
      "exit_code": 40,
      "timestamp": "2025-12-13T23:12:30.123456"
    },
    {
      "stage": 111,
      "name": "sense",
      "input": null,
      "output": "Context sensed and recorded.",
      "exit_code": 0,
      "timestamp": "2025-12-13T23:13:00.456789"
    }
  ]
}
```

This envelope provides a full audit trail of how a decision was formed.

**Exit Codes Specification:** A CLIP uses specific exit codes for machine interpretation of outcomes:
- `0` – PASS: Stage completed successfully (no issues at this stage).
- `20` – PARTIAL: Pipeline execution is partially complete (through forge, but not sealed).
- `30` – SABAR: (Malay: "patience") Execution is paused waiting for something (e.g., waiting for authority token or cooling period).
- `40` – VOID: The void stage (000) executed – session initialized.
- `88` – HOLD: A hold is in effect or a critical issue was encountered (requires manual resolution).
- `100` – SEALED: The final stage executed and the output was sealed/applied successfully.

These codes allow integration with CI or other automation: for example, a CI pipeline might treat code 0, 20, 30 as non-final (needs attention or further action), 88 as a failure requiring human review, and 100 as a successful completion of the governance process.

**Session File (session.json):** Lives in the repository root's `.arifos_clip/` directory. It contains keys:
- `id`: Unique session identifier (e.g., timestamp or UUID).
- `task`: The problem/task description provided at 000.
- `status`: Current status of the session (e.g., "VOID", "ACTIVE" during processing, "HOLD" if paused, "SEALED" if finalized).
- `steps`: Array of stage result objects (the stage envelope described above).
- Additional fields may appear when sealed (e.g., `sealed_at` timestamp, `authority` token used).

This file is updated at each stage, providing a single source of truth for the session state.

**HOLD Bundle Format:** When a hold is triggered:
- `hold.json`: JSON file containing at least:
  - `session_id`: ID of the session.
  - `reason`: Textual reason for the hold.
  - `timestamp`: When the hold was triggered.
  - `resolved`: Flag (always false when created; could be true if a hold is later cleared).
- `hold.md`: A Markdown file explaining the hold in human-friendly terms (including the session ID and reason). It typically includes instructions or notes for the human reviewer.

These files are intended for auditors or decision-makers to review what went wrong and why the process was halted. The presence of any file in `.arifos_clip/holds/` is treated by hooks as an unresolved hold.

## Core Invariants

Several core invariants are encoded in A CLIP's design and tests:

1. **No Silent Apply:** The system never applies or finalizes changes without explicit approval. By default, 999 seal performs a check and does nothing permanent. Only when `--apply` is provided and all other conditions (authority token + arifOS SEAL verdict) are met will the session be sealed. This prevents any automated or accidental finalization.

2. **Authority & Verdict Required to Seal:** Even with `--apply`, sealing requires a valid human authority token and a positive verdict from arifOS. The code checks for both. If either is missing or negative:
   - Missing token → the command exits with code 30 (SABAR), indicating it's waiting on authority.
   - Negative verdict or no law engine → the command exits with code 88 (HOLD), indicating a hard stop (e.g., law violation or system unavailable).
   
   This ensures a two-tier approval: human and machine (law engine).

3. **Hold Blocks Progress:** Once a hold (888) is triggered, the pipeline is effectively frozen. The presence of a hold file or a session status of HOLD will cause:
   - 999 seal to refuse operation (exit 88) until the hold is resolved.
   - Git hooks to prevent commits or pushes.
   
   This invariant guarantees that issues flagged by the pipeline get human attention before any final action.

4. **Delegation to arifOS (No Law Reimplementation):** A CLIP does not replicate the logic of floors, verdict calculations, GENIUS/EUREKA metrics, or time-based rules. All such logic is expected to reside in arifOS. The `aclip.bridge.arifos_client` module calls arifOS for verdicts. If arifOS is not available (import fails) or errors, A CLIP treats it as a HOLD condition (reason: "arifOS not available"). This keeps A CLIP simple and focused on orchestration, and ensures the single source of truth for governance rules is arifOS itself.

5. **All Artifacts in .arifos_clip:** A CLIP writes all session and decision artifacts to the `.arifos_clip/` directory. It does not modify files outside this directory unless the final seal is authorized. (In practice, sealing could trigger code generation, commits, or other side-effects, but those are not implemented in this CLI and would require arifOS integration or explicit user action.) The Git hooks further ensure that no code is pushed without corresponding `.arifos_clip/` artifacts, linking repository changes to governance records.

By adhering to these invariants, A CLIP creates a trustworthy chain-of-governance for any changes, from the initial void to the final seal, all while requiring human insight and law-engine oversight at critical junctures.
