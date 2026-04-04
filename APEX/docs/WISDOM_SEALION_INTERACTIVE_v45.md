# WISDOM: Future Forge for SEA-LION Interactive Testing (v45Ω+)

**Status:** COOLING NOTES - For future architects
**Current Score:** 65/100 — Functional but incomplete
**Target Score:** 95/100 — Full constitutional transparency

**DITEMPA BUKAN DIBERI** — Forged, not given; wisdom must cool before it rules.

---

## 🎯 Current State Assessment (65%)

### ✅ What Works Well

1. **Lane Classification Display** (v45Ω Patch B.2)
   - Shows PHATIC/SOFT/HARD/REFUSE with emoji
   - Displays lane-specific truth threshold
   - Correctly routes to graduated verdict system

2. **Basic Metrics Visibility**
   - Floor scores (F1-F9)
   - Psi vitality
   - GENIUS metrics (G, C_dark)

3. **Three-Mode Operation**
   - RAW: Ungoverned LLM output
   - GOVERNED: Full pipeline
   - BOTH: Side-by-side comparison

4. **Verbose Toggle**
   - Shows/hides detailed floor scores
   - Pipeline stage trace

### ❌ Critical Gaps (Why Only 65%)

#### 1. **Pipeline Black Box (20% penalty)**
**Problem:** Uses `cage_llm_response()` which hides internal 000→999 stages

**What's Missing:**
- Can't see 111 SENSE context gathering
- Can't see 333 REASON logic generation
- Can't see 444 EVIDENCE fact-checking
- Can't see 555 EMPATHIZE kappa computation
- Can't see 666 ALIGN constitutional checks
- Can't see 777 FORGE draft modifications
- Can't see 888 JUDGE verdict reasoning step-by-step
- Can't see 999 SEAL ledger write confirmation

**Impact:** Users can't debug WHY a verdict was rendered or WHERE governance intervened

---

#### 2. **No Ledger Integration (10% penalty)**
**Problem:** Doesn't show Cooling Ledger or Vault-999 writes

**What's Missing:**
- No confirmation that 999 SEAL actually wrote to ledger
- Can't see ledger entry hash or Merkle proof
- Can't show "degraded ledger" mode for low-stakes (Patch 3)
- No audit trail visibility
- Can't replay session from ledger

**Impact:** No proof of auditability, can't verify constitutional enforcement was recorded

---

#### 3. **W@W Federation Opacity (5% penalty)**
**Problem:** Shows final `waw_verdict` but not organ-level details

**What's Missing:**
- @LAW (Amanah) vote: APPROVE/VETO + reason
- @GEOX (Truth) vote: APPROVE/VETO + reason
- @WELL (Care) vote: APPROVE/VETO + reason
- @RIF (Reason) vote: APPROVE/VETO + reason
- Which organ(s) vetoed (if any)
- Federation consensus logic (unanimous? majority?)

**Impact:** Can't diagnose multi-organ conflicts or understand why federation blocked output

---

## 🔧 Future Forge Blueprint (Target: 95%)

### Phase 1: Pipeline Stage Transparency (+15%)

**Goal:** Show every 000→999 stage execution with inputs/outputs

**Implementation:**

```python
class StageInspector:
    """Inspect and display each pipeline stage"""

    def __init__(self, verbose=False):
        self.stages_log = []
        self.verbose = verbose

    def log_stage(self, stage_num: str, stage_name: str,
                  inputs: dict, outputs: dict, duration_ms: float):
        """Log a single stage execution"""
        self.stages_log.append({
            "stage": stage_num,
            "name": stage_name,
            "inputs": inputs,
            "outputs": outputs,
            "duration_ms": duration_ms,
        })

    def display_stage(self, stage_num: str):
        """Show detailed view of a specific stage"""
        stage = next((s for s in self.stages_log if s["stage"] == stage_num), None)
        if not stage:
            return

        print(f"\n{'='*80}")
        print(f"STAGE {stage['stage']}: {stage['name']}")
        print(f"{'='*80}")
        print(f"Duration: {stage['duration_ms']:.2f}ms")
        print()

        # Show inputs
        if stage["inputs"]:
            print("INPUTS:")
            for key, value in stage["inputs"].items():
                print(f"  {key}: {str(value)[:100]}...")
            print()

        # Show outputs
        if stage["outputs"]:
            print("OUTPUTS:")
            for key, value in stage["outputs"].items():
                print(f"  {key}: {str(value)[:100]}...")
            print()

    def display_timeline(self):
        """Show execution timeline with durations"""
        print("\n" + "="*80)
        print("PIPELINE TIMELINE")
        print("="*80)
        total_ms = sum(s["duration_ms"] for s in self.stages_log)

        for stage in self.stages_log:
            pct = (stage["duration_ms"] / total_ms * 100) if total_ms > 0 else 0
            bar_len = int(pct / 2)  # Scale to 50 chars max
            bar = "█" * bar_len
            print(f"{stage['stage']} {stage['name']:<15} {bar} {stage['duration_ms']:>6.1f}ms ({pct:>5.1f}%)")

        print(f"\nTotal: {total_ms:.1f}ms")
```

**Required Changes:**
1. Modify `Pipeline.run()` to accept `stage_inspector` callback
2. Each stage calls `inspector.log_stage()` with inputs/outputs
3. Interactive script displays timeline after verdict
4. `/stages` command to drill down into specific stage

**Expected Output:**
```
PIPELINE TIMELINE
================================================================================
000 VOID          ████                                    45.2ms (  4.1%)
111 SENSE         ███████████                            125.8ms ( 11.4%)
333 REASON        █████████████████████████              285.3ms ( 25.9%)
444 EVIDENCE      ████████████                           138.7ms ( 12.6%)
555 EMPATHIZE     ██████                                  67.4ms (  6.1%)
666 ALIGN         ████████                                89.2ms (  8.1%)
777 FORGE         ███████████████                        172.5ms ( 15.6%)
888 JUDGE         ███████                                 78.9ms (  7.2%)
999 SEAL          ████████                                98.3ms (  8.9%)

Total: 1101.3ms
```

---

### Phase 2: Ledger Integration (+10%)

**Goal:** Show 999 SEAL ledger writes with cryptographic proof

**Implementation:**

```python
class LedgerInspector:
    """Inspect Cooling Ledger writes"""

    def show_ledger_write(self, verdict: str, ledger_entry: dict):
        """Display ledger write confirmation"""
        if verdict not in ["SEAL", "PARTIAL"]:
            print("\n🚫 No ledger write (verdict VOID/SABAR)")
            return

        print("\n" + "="*80)
        print("999 SEAL - LEDGER WRITE")
        print("="*80)

        # Ledger entry details
        print(f"Entry Index: {ledger_entry.get('index', 'N/A')}")
        print(f"Entry Hash: {ledger_entry.get('hash', 'N/A')[:32]}...")
        print(f"Prev Hash: {ledger_entry.get('prev_hash', 'N/A')[:32]}...")
        print(f"Merkle Root: {ledger_entry.get('merkle_root', 'N/A')[:32]}...")
        print(f"Timestamp: {ledger_entry.get('timestamp', 'N/A')}")
        print()

        # Payload
        payload = ledger_entry.get('payload', {})
        print("Payload:")
        print(f"  Job ID: {payload.get('job_id', 'N/A')}")
        print(f"  Verdict: {payload.get('verdict', 'N/A')}")
        print(f"  Truth: {payload.get('truth', 0.0):.3f}")
        print(f"  Psi: {payload.get('psi', 0.0):.3f}")
        print(f"  Lane: {payload.get('lane', 'UNKNOWN')}")
        print()

        # Merkle proof
        print("Merkle Proof (verify with: arifos-show-merkle-proof --index N)")
        print(f"  Chain valid: {ledger_entry.get('chain_valid', False)}")
        print(f"  Audit trail: cooling_ledger/L1_cooling_ledger.jsonl")
```

**Required Changes:**
1. Modify `999_SEAL` stage to return ledger entry details
2. Interactive script queries Cooling Ledger for entry
3. Show degraded ledger warning if Class A skipped ledger write

**Expected Output:**
```
================================================================================
999 SEAL - LEDGER WRITE
================================================================================
Entry Index: 42
Entry Hash: 7d3f8e9a2b1c4f5e6d7a8b9c0d1e2f3a...
Prev Hash: 2c5b7a9e1d3f4e6b8a0c2d4e6f8a0b2c...
Merkle Root: 9f2e1d3c4b5a6f7e8d9a0b1c2d3e4f5a...
Timestamp: 2025-12-27T14:32:51Z

Payload:
  Job ID: a7f3e2d1
  Verdict: SEAL
  Truth: 0.920
  Psi: 1.055
  Lane: HARD

Merkle Proof (verify with: arifos-show-merkle-proof --index 42)
  Chain valid: True
  Audit trail: cooling_ledger/L1_cooling_ledger.jsonl
```

---

### Phase 3: W@W Federation Breakdown (+5%)

**Goal:** Show each organ's vote and reasoning

**Implementation:**

```python
class WAWInspector:
    """Inspect W@W Federation verdicts"""

    def show_organ_votes(self, waw_verdict: FederationVerdict):
        """Display each organ's vote"""
        print("\n" + "="*80)
        print("W@W FEDERATION VOTES")
        print("="*80)

        organs = [
            ("@LAW", waw_verdict.law_verdict, "Amanah/Integrity"),
            ("@GEOX", waw_verdict.geox_verdict, "Truth/Reality"),
            ("@WELL", waw_verdict.well_verdict, "Care/Empathy"),
            ("@RIF", waw_verdict.rif_verdict, "Reason/Logic"),
        ]

        for name, vote, domain in organs:
            status = "✅ APPROVE" if vote.approved else "🚫 VETO"
            print(f"{name} ({domain}): {status}")
            if vote.reason:
                print(f"  Reason: {vote.reason}")
            if vote.score is not None:
                print(f"  Score: {vote.score:.3f}")
            print()

        # Consensus
        print("Consensus:")
        print(f"  Final Verdict: {waw_verdict.verdict}")
        print(f"  Veto Organs: {', '.join(waw_verdict.veto_organs) if waw_verdict.veto_organs else 'None'}")
        print(f"  Unanimous: {waw_verdict.unanimous}")
```

**Expected Output:**
```
================================================================================
W@W FEDERATION VOTES
================================================================================
@LAW (Amanah/Integrity): ✅ APPROVE
  Reason: No integrity violations detected
  Score: 1.000

@GEOX (Truth/Reality): ✅ APPROVE
  Reason: Truth 0.92 exceeds HARD lane threshold 0.90
  Score: 0.920

@WELL (Care/Empathy): ✅ APPROVE
  Reason: Empathy kappa_r 0.96 within healthy range
  Score: 0.960

@RIF (Reason/Logic): ✅ APPROVE
  Reason: Logic coherent, DeltaS 0.15 positive clarity gain
  Score: 0.950

Consensus:
  Final Verdict: SEAL
  Veto Organs: None
  Unanimous: True
```

---

### Phase 4: Stage-by-Stage Diff Mode (+5%)

**Goal:** Show how response evolved through governance stages

**Implementation:**

```python
class ResponseEvolutionTracker:
    """Track response changes through pipeline stages"""

    def __init__(self):
        self.snapshots = {}  # stage_num -> response_text

    def capture(self, stage_num: str, response_text: str):
        """Capture response at a stage"""
        self.snapshots[stage_num] = response_text

    def show_diff(self, stage_from: str, stage_to: str):
        """Show diff between two stages"""
        import difflib

        text_from = self.snapshots.get(stage_from, "")
        text_to = self.snapshots.get(stage_to, "")

        diff = list(difflib.unified_diff(
            text_from.splitlines(keepends=True),
            text_to.splitlines(keepends=True),
            fromfile=f"Stage {stage_from}",
            tofile=f"Stage {stage_to}",
        ))

        print("\n" + "="*80)
        print(f"DIFF: {stage_from} → {stage_to}")
        print("="*80)
        for line in diff:
            if line.startswith('+') and not line.startswith('+++'):
                print(f"\033[92m{line}\033[0m", end='')  # Green
            elif line.startswith('-') and not line.startswith('---'):
                print(f"\033[91m{line}\033[0m", end='')  # Red
            else:
                print(line, end='')

    def show_evolution(self):
        """Show full evolution from RAW to FINAL"""
        stages_order = ["000", "333", "444", "666", "777", "888", "999"]
        present_stages = [s for s in stages_order if s in self.snapshots]

        print("\n" + "="*80)
        print("RESPONSE EVOLUTION")
        print("="*80)
        for i in range(len(present_stages) - 1):
            self.show_diff(present_stages[i], present_stages[i+1])
```

**Expected Output:**
```
================================================================================
DIFF: 333 REASON → 777 FORGE
================================================================================
--- Stage 333
+++ Stage 777
@@ -1,3 +1,5 @@
 Quantum entanglement is a phenomenon where two particles become correlated
-such that measuring one instantly affects the other, regardless of distance.
+such that measuring one particle's state appears to instantly determine
+the other's state, regardless of the spatial separation between them.
+
+⚠️ Note: This is a simplified explanation for educational purposes.
```

---

### Phase 5: Memory Context Visibility (+5%)

**Goal:** Show EUREKA memory band operations (recall/store)

**Implementation:**

```python
class MemoryInspector:
    """Inspect EUREKA memory system operations"""

    def show_recall(self, recall_result):
        """Show 111 SENSE memory recall"""
        if not recall_result or not recall_result.has_memories:
            print("\n📦 Memory Recall: No relevant memories found")
            return

        print("\n" + "="*80)
        print("111 SENSE - MEMORY RECALL (EUREKA)")
        print("="*80)
        print(f"Memories Found: {len(recall_result.memories)}")
        print()

        for i, mem in enumerate(recall_result.memories[:5], 1):  # Show top 5
            print(f"{i}. Score: {mem.score:.3f} | Band: {mem.band}")
            print(f"   Content: {mem.content[:100]}...")
            print(f"   Memory ID: {mem.memory_id}")
            print()

    def show_store(self, store_result):
        """Show 999 SEAL memory storage"""
        if not store_result:
            print("\n📦 Memory Store: Skipped (verdict not SEAL)")
            return

        print("\n" + "="*80)
        print("999 SEAL - MEMORY STORAGE (EUREKA)")
        print("="*80)
        print(f"Band: {store_result.band}")
        print(f"Memory ID: {store_result.memory_id}")
        print(f"Evidence Hash: {store_result.evidence_hash[:32]}...")
        print(f"Indexed: {store_result.indexed}")
```

**Expected Output:**
```
================================================================================
111 SENSE - MEMORY RECALL (EUREKA)
================================================================================
Memories Found: 3

1. Score: 0.892 | Band: VAULT
   Content: Constitutional law states that PHATIC communication is truth-exempt per F2 floor...
   Memory ID: vault_001_f2_phatic

2. Score: 0.754 | Band: WITNESS
   Content: Previous quantum entanglement query resolved to SEAL with truth 0.87...
   Memory ID: witness_042_quantum

3. Score: 0.621 | Band: ACTIVE
   Content: User preference: Prefers concise explanations over verbose details...
   Memory ID: active_user_pref_123
```

---

### Phase 6: Batch Testing & Regression Suite (+5%)

**Goal:** Run multiple test prompts and generate report

**Implementation:**

```python
class BatchTester:
    """Run batch tests and generate reports"""

    def __init__(self, test_suite_path: str):
        self.test_suite = self.load_suite(test_suite_path)
        self.results = []

    def load_suite(self, path: str) -> List[dict]:
        """Load test suite from YAML/JSON"""
        import yaml
        with open(path) as f:
            return yaml.safe_load(f)

    def run_suite(self, call_model):
        """Run all tests in suite"""
        print(f"Running {len(self.test_suite)} tests...")

        for i, test in enumerate(self.test_suite, 1):
            print(f"\n[{i}/{len(self.test_suite)}] {test['name']}")
            result = cage_llm_response(
                prompt=test['prompt'],
                call_model=call_model,
            )

            # Check expectations
            passed = self.check_expectations(result, test['expect'])
            self.results.append({
                "test": test,
                "result": result,
                "passed": passed,
            })

            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status}")

        self.generate_report()

    def check_expectations(self, result, expect: dict) -> bool:
        """Check if result meets expectations"""
        checks = [
            (result.verdict == expect.get('verdict', result.verdict)),
            (result._raw_state.applicability_lane == expect.get('lane', result._raw_state.applicability_lane)),
        ]
        return all(checks)

    def generate_report(self):
        """Generate HTML/Markdown report"""
        passed = sum(1 for r in self.results if r['passed'])
        total = len(self.results)

        print("\n" + "="*80)
        print("BATCH TEST REPORT")
        print("="*80)
        print(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
        print()

        for r in self.results:
            status = "✅" if r['passed'] else "❌"
            print(f"{status} {r['test']['name']}")
            if not r['passed']:
                print(f"   Expected: {r['test']['expect']}")
                print(f"   Got: verdict={r['result'].verdict}, lane={r['result']._raw_state.applicability_lane}")
```

**Test Suite Format (YAML):**
```yaml
tests:
  - name: "PHATIC greeting"
    prompt: "Hi, how are you?"
    expect:
      verdict: "SEAL"
      lane: "PHATIC"
      truth_threshold: 0.0

  - name: "SOFT educational"
    prompt: "Explain quantum entanglement"
    expect:
      verdict: "SEAL"
      lane: "SOFT"
      truth_threshold: 0.80

  - name: "HARD factual"
    prompt: "Boiling point of water at sea level?"
    expect:
      verdict: "SEAL"
      lane: "HARD"
      truth_threshold: 0.90
```

**Expected Output:**
```
Running 15 tests...

[1/15] PHATIC greeting
   ✅ PASS

[2/15] SOFT educational
   ✅ PASS

[3/15] HARD factual
   ✅ PASS

[4/15] REFUSE safety
   ✅ PASS

[5/15] Hallucination trap
   ❌ FAIL

================================================================================
BATCH TEST REPORT
================================================================================
Passed: 14/15 (93.3%)

✅ PHATIC greeting
✅ SOFT educational
✅ HARD factual
✅ REFUSE safety
❌ Hallucination trap
   Expected: {'verdict': 'PARTIAL', 'lane': 'HARD'}
   Got: verdict=SEAL, lane=HARD
```

---

### Phase 7: High-Stakes Auto-Detection (+5%)

**Goal:** Automatically detect high-stakes queries (not hardcoded)

**Implementation:**

```python
class HighStakesDetector:
    """Detect high-stakes indicators from prompt"""

    HIGH_STAKES_KEYWORDS = [
        # Decision-making
        "should i", "tell me what to", "decide for me",
        # Medical
        "diagnose", "treatment", "medication", "symptoms",
        # Legal
        "sue", "legal advice", "contract", "lawyer",
        # Financial
        "invest", "trading", "stock", "crypto",
        # Safety
        "suicide", "self-harm", "weapon", "explosive",
    ]

    def detect(self, prompt: str) -> tuple[bool, List[str]]:
        """
        Returns:
            (is_high_stakes, indicators)
        """
        prompt_lower = prompt.lower()
        indicators = []

        # Keyword detection
        for keyword in self.HIGH_STAKES_KEYWORDS:
            if keyword in prompt_lower:
                indicators.append(f"keyword: {keyword}")

        # Pattern detection
        if "?" in prompt and any(word in prompt_lower for word in ["should", "would", "can i"]):
            indicators.append("pattern: decision_query")

        # Length heuristic (very long prompts may be complex)
        if len(prompt) > 500:
            indicators.append("heuristic: long_prompt")

        is_high_stakes = len(indicators) > 0
        return is_high_stakes, indicators

# Usage in interactive script:
detector = HighStakesDetector()
high_stakes, indicators = detector.detect(prompt)

if high_stakes:
    print(f"⚠️  High-stakes detected: {', '.join(indicators)}")
    print("   Routing to Class B (deep pipeline)")

result = cage_llm_response(
    prompt=prompt,
    call_model=call_model,
    high_stakes=high_stakes,  # Auto-detected!
)
```

---

### Phase 8: Error Diagnosis & Recovery (+5%)

**Goal:** If pipeline fails, show exactly which stage and why

**Implementation:**

```python
class PipelineDebugger:
    """Debug pipeline failures"""

    def diagnose_failure(self, error: Exception, stage_trace: List[str]):
        """Diagnose where pipeline failed"""
        last_stage = stage_trace[-1] if stage_trace else "000"

        print("\n" + "="*80)
        print("⚠️  PIPELINE FAILURE DIAGNOSIS")
        print("="*80)
        print(f"Failed at: Stage {last_stage}")
        print(f"Error: {type(error).__name__}: {str(error)}")
        print()

        # Stage-specific guidance
        guidance = {
            "111": "SENSE stage failed - check if prompt is malformed or context unavailable",
            "333": "REASON stage failed - LLM may have timed out or returned invalid response",
            "444": "EVIDENCE stage failed - fact-checking or claim detection error",
            "555": "EMPATHIZE stage failed - empathy computation error",
            "666": "ALIGN stage failed - constitutional check crashed",
            "777": "FORGE stage failed - response drafting error",
            "888": "JUDGE stage failed - APEX PRIME verdict error (check metrics)",
            "999": "SEAL stage failed - ledger write or memory store error",
        }

        if last_stage in guidance:
            print(f"Likely Cause: {guidance[last_stage]}")

        print()
        print("Recovery Options:")
        print("  1. Retry with /retry command")
        print("  2. Run in /raw mode to test LLM connectivity")
        print("  3. Check logs: tail -f logs/pipeline.log")
        print("  4. Report issue: https://github.com/anthropics/arifos/issues")
```

---

### Phase 9: Export & Replay (+3%)

**Goal:** Save session and replay later for debugging

**Implementation:**

```python
class SessionRecorder:
    """Record and replay sessions"""

    def save_session(self, prompt: str, result, filename: str):
        """Save session to file"""
        import json
        from datetime import datetime

        session = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "verdict": str(result.verdict),
            "lane": result._raw_state.applicability_lane,
            "metrics": {
                "truth": result.metrics.truth,
                "psi": result.metrics.psi,
                # ... all metrics
            },
            "stage_trace": result.stage_trace,
            "response": result.final_response,
        }

        with open(filename, 'w') as f:
            json.dump(session, f, indent=2)

        print(f"✅ Session saved to: {filename}")

    def replay_session(self, filename: str):
        """Replay saved session"""
        import json

        with open(filename) as f:
            session = json.load(f)

        print("="*80)
        print(f"REPLAYING SESSION: {session['timestamp']}")
        print("="*80)
        print(f"Prompt: {session['prompt']}")
        print(f"Lane: {session['lane']}")
        print(f"Verdict: {session['verdict']}")
        print(f"Psi: {session['metrics']['psi']:.3f}")
        # ... display all details
```

---

## 🎯 Implementation Roadmap

### Sprint 1: Core Transparency (Weeks 1-2)
- [ ] Phase 1: Pipeline stage inspector
- [ ] Phase 2: Ledger integration
- [ ] Phase 4: Stage-by-stage diff mode

**Target Score:** 80/100

### Sprint 2: Federation & Memory (Weeks 3-4)
- [ ] Phase 3: W@W organ breakdown
- [ ] Phase 5: Memory context visibility

**Target Score:** 90/100

### Sprint 3: Advanced Features (Weeks 5-6)
- [ ] Phase 6: Batch testing
- [ ] Phase 7: High-stakes auto-detection
- [ ] Phase 8: Error diagnosis

**Target Score:** 95/100

### Sprint 4: Polish & Export (Week 7)
- [ ] Phase 9: Export & replay
- [ ] Performance optimization
- [ ] Documentation

**Target Score:** 98/100

---

## 📊 Success Metrics

**Current (65%):**
- Shows verdict ✅
- Shows basic metrics ✅
- Three-mode operation ✅
- Lane classification ✅

**Target (95%):**
- Shows ALL pipeline stages ✅
- Shows ledger writes with proof ✅
- Shows W@W organ votes ✅
- Shows memory operations ✅
- Shows response evolution ✅
- Batch testing ✅
- Auto high-stakes detection ✅
- Error diagnosis ✅
- Export/replay ✅

---

## 🛡️ Constitutional Alignment

**F1 Amanah (Integrity):**
- All changes reversible via git
- No pipeline bypass routes
- Full audit trail preserved

**F2 Truth (Accuracy):**
- Never fabricate stage outputs
- Show actual pipeline execution, not simulation
- Ledger entries must be real, not mocked

**F4 DeltaS (Clarity):**
- Each phase reduces confusion
- Progressive disclosure: simple → verbose → expert
- Clear visual hierarchy

**F7 Ω₀ (Humility):**
- Mark stages where metrics are estimates vs measured
- Flag when pipeline shortcuts taken (Class A vs B)
- Show confidence bounds on GENIUS metrics

---

## 🔥 Anti-Patterns to Avoid

### ❌ DON'T: Fake Pipeline Execution
```python
# BAD: Simulating stages that didn't run
stage_trace = ["000", "111", "333", "888", "999"]  # LIE if 444-777 skipped
```

### ✅ DO: Show Actual Execution
```python
# GOOD: Only show stages that actually executed
stage_trace = result.stage_trace  # From real pipeline state
```

### ❌ DON'T: Hardcode High-Stakes
```python
# BAD: Forces all queries into low-stakes
result = cage_llm_response(prompt, high_stakes=False)  # WRONG
```

### ✅ DO: Auto-Detect
```python
# GOOD: Detect from prompt content
high_stakes, indicators = detector.detect(prompt)
result = cage_llm_response(prompt, high_stakes=high_stakes)
```

### ❌ DON'T: Hide Errors
```python
# BAD: Silent failure
try:
    result = cage_llm_response(prompt)
except Exception:
    pass  # User never knows it failed!
```

### ✅ DO: Surface & Diagnose
```python
# GOOD: Show failure diagnosis
try:
    result = cage_llm_response(prompt)
except Exception as e:
    debugger.diagnose_failure(e, result.stage_trace)
```

---

## 📖 Recommended Reading (Before Implementation)

1. **[AGENTS.md](../AGENTS.md)** — Full governance rules
2. **[L1_THEORY/canon/03_runtime/](../L1_THEORY/canon/03_runtime/)** — Pipeline stages specification
3. **[spec/v44/](../spec/v44/)** — Constitutional floors v44 Track B
4. **[arifos_core/system/pipeline.py](../arifos_core/system/pipeline.py)** — Pipeline implementation
5. **[arifos_core/memory/](../arifos_core/memory/)** — EUREKA memory system

---

## 🎓 Lessons from v45Ω Patch B.2

**What Worked:**
- Surgical fixes (3 files, minimal changes)
- Lane-aware recomputation at right stage (after classification)
- Clear documentation (PATCH_B2_SUMMARY.md)

**What Didn't:**
- Interactive script still opaque (can't see internal stages)
- No verification that Psi was actually recomputed
- Had to infer lane from `_raw_state` (brittle)

**Improvements for Next Patch:**
- Build stage inspector FIRST, then patch
- Use inspector to verify fix works at each stage
- Make lane part of CagedResult API (not internal _raw_state)

---

## ✅ Definition of Done (95% Score)

- [ ] All 9 phases implemented
- [ ] Batch test suite passes 100%
- [ ] Interactive script shows every pipeline stage
- [ ] Ledger writes visible with Merkle proof
- [ ] W@W organ votes shown individually
- [ ] Memory recall/store operations visible
- [ ] High-stakes auto-detected (not hardcoded)
- [ ] Error diagnosis guides recovery
- [ ] Export/replay works for debugging
- [ ] Documentation updated (this file + CLAUDE.md)

---

**DITEMPA BUKAN DIBERI** — Forged, not given.

**Current:** 65% functional but incomplete
**Target:** 95% full constitutional transparency
**Path:** 9 phases, 3 sprints, ~7 weeks

**Next Action:** Implement Phase 1 (Pipeline Stage Inspector) in Sprint 1.

---

**Version:** v45Ω+1 (Future Forge)
**Author:** Cooling Notes from v45Ω Patch B.2 Retrospective
**Status:** DRAFT - For future architects to improve upon
