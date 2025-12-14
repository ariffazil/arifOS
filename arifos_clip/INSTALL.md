# A CLIP Installation & Quick Start

## Prerequisites

- Python 3.8+
- pip
- arifOS repository cloned

## Installation

### Step 1: Install Package
```bash
cd /path/to/arifOS
pip install -e .
```

This installs arifOS + A CLIP and makes commands `000`, `111`, ..., `999` available globally.

### Step 2: Verify Installation
```bash
000 --help
999 --help
```

You should see the argparse help for each command.

### Step 3: Enable Git Hooks (Optional but Recommended)
```bash
# From arifOS root
cp arifos_clip/hooks/pre-commit .git/hooks/
cp arifos_clip/hooks/commit-msg .git/hooks/
cp arifos_clip/hooks/pre-push .git/hooks/

# Make executable (Unix/Mac)
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/commit-msg
chmod +x .git/hooks/pre-push
```

**Note:** On Windows, Git hooks work but don't need chmod.

---

## Quick Start - Your First Pipeline

### Example: Adding a New Feature

```bash
# 1. Initialize session
000 void "Add new metric calculator module"

# Session created at .arifos_clip/session.json
# Exit code: 40 (VOID)

# 2. Sense stage - gather context
111 sense

# Prompts you to describe what you know about the task
# Exit code: 0 (PASS)

# 3. Reflect stage - recall relevant knowledge
222 reflect

# Consider past experiences, related modules, patterns
# Exit code: 0 (PASS)

# 4. Reason stage - logical analysis
333 reason

# Break down the problem, outline solution steps
# Exit code: 0 (PASS)

# 5. Evidence stage - verify facts
444 evidence

# Check data, references, documentation
# Exit code: 0 (PASS)

# 6. Empathize stage - stakeholder perspectives
555 empathize

# Consider who's affected, user needs, ethical implications
# Exit code: 0 (PASS)

# 7. Align stage - check principles
666 align

# Ensure alignment with APEX values, laws, regulations
# Exit code: 0 (PASS)

# 8. Forge stage - compile decision
777 forge

# Creates .arifos_clip/forge/forge.json
# Exit code: 20 (PARTIAL - forged but not sealed)

# 9. Seal stage (dry-run first)
999 seal

# Checks if sealing is allowed (queries arifOS)
# Exit code: 30 (SABAR - awaiting authority) or 88 (HOLD - law issue)

# 10. Seal with authority (when ready)
999 seal --apply --authority-token YOUR_TOKEN

# If arifOS approves (SEAL verdict), session is finalized
# Exit code: 100 (SEALED)
```

### Handling Issues - The Hold Stage

If you detect an issue at any point:

```bash
888 hold --reason "Security review needed before proceeding"
```

This creates:
- `.arifos_clip/holds/hold.json`
- `.arifos_clip/holds/hold.md`

The pipeline is now frozen. You cannot seal until the hold is resolved (files deleted).

---

## Command Reference

### Core Commands

| Command | Verb | Usage |
|---------|------|-------|
| `000` | void | `000 void "<task description>"` |
| `111` | sense | `111 sense` |
| `222` | reflect | `222 reflect` |
| `333` | reason | `333 reason` |
| `444` | evidence | `444 evidence` |
| `555` | empathize | `555 empathize` |
| `666` | align | `666 align` |
| `777` | forge | `777 forge` |
| `888` | hold | `888 hold [--reason "text"]` |
| `999` | seal | `999 seal [--apply --authority-token TOKEN]` |

### Common Flags

- `--json`: Output result as JSON (all commands)
- `--reason`: Specify reason for hold (888 only)
- `--apply`: Actually apply the seal (999 only)
- `--authority-token`: Human authority token (999 with --apply)

---

## Artifacts Generated

A CLIP creates a `.arifos_clip/` directory in your repository root:

```
.arifos_clip/
├── session.json          # Full session state + audit trail
├── forge/
│   └── forge.json        # Compiled decision package
└── holds/                # (If hold triggered)
    ├── hold.json         # Machine-readable
    └── hold.md           # Human-readable
```

**Note:** Add `.arifos_clip/` to `.gitignore` if you don't want to commit session artifacts.

---

## Exit Codes

A CLIP uses specific exit codes for automation:

| Code | Name | Meaning |
|------|------|---------|
| 0 | PASS | Stage completed successfully |
| 20 | PARTIAL | Forged but not sealed |
| 30 | SABAR | Awaiting authority/time |
| 40 | VOID | Session initialized |
| 88 | HOLD | Issue detected, manual review needed |
| 100 | SEALED | Fully approved and finalized |

Use these in scripts:
```bash
000 void "Task"
if [ $? -eq 40 ]; then
    echo "Session initialized"
fi
```

---

## Integration with arifOS

A CLIP delegates law enforcement to arifOS via the bridge layer:

```python
# arifos_clip/aclip/bridge/arifos_client.py
def request_verdict(session):
    # Calls arifOS law engine
    verdict = arifos_core.evaluate_session(session.data)
    return (verdict, None)
```

To enable full governance:

1. Implement `arifos_core.evaluate_session()` in arifOS core
2. Connect to APEX_PRIME for floor evaluation
3. Link to Memory Write Policy Engine for EUREKA compliance

Until then, A CLIP will report "arifOS not available" and return HOLD (88) on seal attempts.

---

## Testing

Run the MVP test suite:

```bash
# From arifOS root
python arifos_clip/tests/test_mvp_flow.py

# Or with pytest
pytest arifos_clip/tests/ -v
```

---

## Troubleshooting

### Commands not found after installation

```bash
# Reinstall in editable mode
pip install -e . --force-reinstall

# Check if scripts are registered
pip show -f arifos | grep "000"
```

### Session already exists error

```bash
# If you want to start fresh, remove the session
rm -rf .arifos_clip

# Then start new session
000 void "New task"
```

### Hold blocking progress

```bash
# View hold reason
cat .arifos_clip/holds/hold.md

# Resolve the issue, then remove hold files
rm -rf .arifos_clip/holds

# Now you can proceed
```

### arifOS not available error

This is expected until `arifos_core.evaluate_session()` is implemented. A CLIP is designed to be safe-by-default: if the law engine isn't available, it refuses to seal (HOLD).

---

## Git Hook Behavior

### pre-commit
Blocks commits if any hold exists:
```bash
git commit -m "Fix bug"
# Output: "Commit blocked: unresolved A CLIP HOLD exists."
```

### commit-msg
Requires session to be sealed AND commit message to include "SEALED":
```bash
git commit -m "Add feature"
# Output: "Commit blocked: session not sealed by A CLIP."

git commit -m "SEALED: Add feature (Session 20251214120000)"
# Allowed (if session is sealed)
```

### pre-push
Blocks pushes without sealed session + artifacts:
```bash
git push origin main
# Output: "Push blocked: session not sealed by A CLIP."
```

---

## What's Next?

1. **Test the Pipeline:** Run through a full 000→999 workflow
2. **Integrate with arifOS:** Connect to APEX_PRIME + Memory Write Policy
3. **Extend Stages:** Add custom logic to each stage module
4. **CI Integration:** Use exit codes in GitHub Actions or other CI

---

**DITEMPA BUKAN DIBERI** - Forged, not given.

For full documentation, see:
- [arifos_clip/README.md](README.md)
- [arifos_clip/docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [arifos_clip/FORGE_RECEIPT.md](FORGE_RECEIPT.md)
