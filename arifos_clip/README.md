# A CLIP – arifOS CLI Pipeline

A CLIP is a command-line pipeline (with commands `000` through `999`) for decision governance in the **arifOS** project. It enforces that changes and decisions go through a structured, multi-stage review aligned with APEX Theory and are approved by the arifOS law engine.

## Pipeline Stages (000–999)

- **000 (void):** Initialize a new session from the void (blank state) with a task description.
- **111 (sense):** Sense the context – gather initial information about the task.
- **222 (reflect):** Reflect on knowledge – recall relevant info and context.
- **333 (reason):** Reason logically – analyze the problem and outline solutions.
- **444 (evidence):** Gather evidence – verify facts and support arguments.
- **555 (empathize):** Empathize – consider human/stakeholder perspectives and ethical implications.
- **666 (align):** Align – ensure alignment with core principles, laws, and APEX values.
- **777 (forge):** Forge the output – synthesize all inputs into a final decision package.
- **888 (hold):** Hold the process – pause for human review or if an issue is detected.
- **999 (seal):** Seal the result – finalize the decision (requires authorization and arifOS approval).

Each stage corresponds to a CLI command (`000` through `999`) that performs the above actions and records the outcome.

## Usage

After installing A CLIP, use the numeric commands in sequence to carry out the governance workflow:

1. **Start a session:** `000 void "<task description>"` – Creates a new session and records the task.
2. **Progress through stages:** Run `111 sense`, `222 reflect`, `333 reason`, `444 evidence`, `555 empathize`, and `666 align` in order. Each command adds its analysis to the session log.
3. **Forge the output:** `777 forge` – Compiles all stage outputs into a final JSON "forge pack".
4. **Apply a hold (if needed):** `888 hold --reason "reason text"` – (Optional) Invoke a hold if an issue arises. This will produce a hold report and block sealing until resolved.
5. **Seal the decision:** `999 seal --apply --authority-token <TOKEN>` – Attempts to finalize the decision. By default, `999 seal` runs a dry-run check. Using `--apply` with a valid authority token will request arifOS to approve and finalize the changes.

Each command produces output to the console and updates files under the hidden directory `.arifos_clip/` (which tracks session state and artifacts). Use the `--json` flag with any command to get machine-readable JSON output instead of human-friendly text.

## Authorization & Enforcement

The **seal** stage (999) is protected by multiple safeguards:
- It **requires** an explicit `--apply` flag and a valid `--authority-token` from a human authority to attempt applying changes.
- Even with a token, the arifOS law engine must return a verdict of **SEAL** for the session, otherwise the seal will not proceed.
- If these conditions are not met, 999 will exit with a HOLD or SABAR code and no external changes will be applied.

Git hooks are provided (in `arifos_clip/hooks/`) to enforce the pipeline:
- Commits are blocked if a hold exists (pre-commit) or if the session is not sealed (commit-msg).
- Pushing to remote is blocked if any hold remains or if the session wasn't sealed by A CLIP (pre-push).

These safeguards ensure that no unreviewed or unapproved changes leave the repository.

## Installation

Include the `arifos_clip` package in your project and configure console scripts for the numeric commands (see **Packaging** below). Then install the package in your environment (e.g. with `pip install -e .`). This will make commands `000`, `111`, ..., `999` available in your shell.

## Outputs and Exit Codes

A CLIP writes all its artifacts to a dedicated folder `.arifos_clip/` in the repository:
- **Session file:** `.arifos_clip/session.json` – the central record of the session, including all stages.
- **Forge pack:** `.arifos_clip/forge/forge.json` – the compiled output after forging (777).
- **Hold bundle:** `.arifos_clip/holds/hold.json` and `.arifos_clip/holds/hold.md` – details of any hold invoked (888).

Exit codes are used to signal the pipeline state to other tools (or scripts):
- `0` – **PASS:** Stage completed successfully (no errors).
- `20` – **PARTIAL:** Pipeline completed partially (e.g. forged but not sealed).
- `30` – **SABAR:** Execution stopped awaiting action (e.g. missing authority token, waiting period).
- `40` – **VOID:** Void stage completed (session initialized).
- `88` – **HOLD:** A hold is in effect or a law violation blocked progress.
- `100` – **SEALED:** Final stage sealed successfully (fully approved).

Non-zero codes (except 100) indicate the pipeline did not yet reach a final sealed state. These codes help integrate with CI or other tools to automate checks.
