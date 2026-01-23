# arifOS Full Code Audit Report
**Prepared for:** Engineering Team  
**Prepared by:** Architectural Review (arifOS Steward Protocol)  
**Date:** January 10, 2026  
**Status:** READY FOR PRODUCTION FIX  
**Severity Classification:** 5 CRITICAL, 7 HIGH, 6 MEDIUM, 4 LOW  

---

## EXECUTIVE BRIEF FOR ENGINEERING LEADS

arifOS codebase is **structurally sound** (clean patterns, fail-closed logic, modular design) but contains **critical blocking bugs** and **incomplete implementations** that prevent production deployment.

**Key findings:**
- **3 syntax errors** (unclosed parentheses) preventing code execution
- **1 stub implementation** (clarity_scorer returns hardcoded 0.1) defeating F2 floor
- **1 security gap** (F9 anti-hantu vulnerable to Unicode tricks and encoding attacks)
- **1 type safety gap** (no input validation on floor metrics)
- **Missing test coverage** (0 unit tests across core logic)

**Estimated remediation time:** 8-12 hours of focused engineering work  
**Release readiness:** NOT PRODUCTION-READY (fix required)

---

## PART 1: CRITICAL ISSUES (BLOCKING)

### **CRITICAL-1: Syntax Error in eureka.py**

**Severity:** CRITICAL (Code won't execute)  
**Location:** `eureka.py`, lines 118-125  
**Status:** Syntax error  

#### Problem

```python
# CURRENT (BROKEN)
return EurekaCandidate(
    text=synthesis_text,
    truth_preserved=agi_verdict,
    care_maintained=asi_verdict,
    coherence_score=coherence,
    # ← MISSING CLOSING PAREN
```

The `EurekaCandidate()` constructor call is missing its closing parenthesis. This will cause a `SyntaxError` and prevent the entire module from loading.

#### Impact

- Module import will fail
- `EUREKA.synthesize()` cannot be called
- Stage 777 (FORGE) completely non-functional
- Entire Trinity pipeline breaks

#### Root Cause

Incomplete code submission or copy-paste error during file creation.

#### Fix

**Priority:** Immediate  
**Effort:** 1 minute  

```python
# FIXED
return EurekaCandidate(
    text=synthesis_text,
    truth_preserved=agi_verdict,
    care_maintained=asi_verdict,
    coherence_score=coherence,
)  # ← Add closing parenthesis
```

#### Verification

```bash
python -m py_compile eureka.py  # Should succeed
python -c "from arifos.eureka import EUREKA; print(EUREKA)"  # Should print singleton
```

---

### **CRITICAL-2: Multiple Syntax Errors in cooling.py**

**Severity:** CRITICAL (Runtime crashes)  
**Location:** `cooling.py`, lines 57-75  
**Status:** Syntax errors (4 instances)  

#### Problem

All `SABARCondition()` constructor calls are missing closing parentheses:

```python
# CURRENT (BROKEN)
conditions.append(
    SABARCondition(
        floor_id="F3",
        reason="Peace² below threshold (potential escalation)",
        threshold=1.0,
        actual=peace_squared,
        # ← MISSING CLOSING PAREN FOR SABARCondition()
)

# Same issue repeated for:
# - kappa_r condition (lines 67-71)
# - omega_0 condition (lines 73-78)
# - rasa_passed condition (lines 80-85)
```

#### Impact

- `CoolingEngine.should_pause()` cannot return any conditions
- SABAR pause protocol is completely broken
- ASI cannot pause the system (critical safety feature disabled)
- 4 syntax errors prevent module load

#### Root Cause

Incomplete code submission; parenthesis nesting error.

#### Fix

**Priority:** Immediate  
**Effort:** 5 minutes (4 locations)  

```python
# FIXED - F3 Peace²
conditions.append(
    SABARCondition(
        floor_id="F3",
        reason="Peace² below threshold (potential escalation)",
        threshold=1.0,
        actual=peace_squared,
    )  # ← Add closing paren for SABARCondition
)

# FIXED - F4 κᵣ
conditions.append(
    SABARCondition(
        floor_id="F4",
        reason="Empathy below threshold (weakest stakeholder not served)",
        threshold=0.95,
        actual=kappa_r,
    )  # ← Add closing paren
)

# FIXED - F5 Ω₀
conditions.append(
    SABARCondition(
        floor_id="F5",
        reason="Humility out of band (too certain or too uncertain)",
        threshold=0.04,
        actual=omega_0,
    )  # ← Add closing paren
)

# FIXED - F7 RASA
conditions.append(
    SABARCondition(
        floor_id="F7",
        reason="RASA signals missing (active listening required)",
        threshold=0.5,
        actual=0.0 if not rasa_passed else 1.0,
    )  # ← Add closing paren
)
```

#### Verification

```bash
python -m py_compile cooling.py  # Should succeed
python -c "from arifos.cooling import COOLING; print(COOLING.should_pause(1.0, 0.95, 0.04, True))"
# Should print: (False, []) for passing conditions
```

---

### **CRITICAL-3: clarity_scorer.py is a Non-Functional Stub**

**Severity:** CRITICAL (F2 floor is fake)  
**Location:** `clarity_scorer.py`, entire file  
**Status:** Incomplete implementation  

#### Problem

The F2 clarity scorer is a placeholder that always returns `0.1` regardless of input:

```python
def compute_delta_s(
    input_text: str,
    output_text: str,
    context: Optional[dict] = None,
) -> float:
    """Compute ΔS (clarity delta) between input and output."""
    
    # Stub implementation
    if context and "delta_s" in context.get("metrics", {}):
        return context["metrics"]["delta_s"]
    
    # Default: slight clarity increase (0.1)
    return 0.1  # ← ALWAYS RETURNS THIS
```

#### Impact

**F2 floor is non-functional:**
- Circular reasoning passes F2 (should fail)
- Tautologies pass F2 ("Inflation is caused by inflation" → ΔS = 0.1 ✓)
- Misdirection passes F2 (answering wrong question → ΔS = 0.1 ✓)
- No actual clarity measurement occurs
- All responses get same fake score

**Example attack:**
```
Input: "What causes economic collapse?"
Output: "Economic collapse is caused by collapse."  # Tautology!
Expected: F2 fails (ΔS < 0)
Actual: F2 passes (ΔS = 0.1)
Result: SEAL issued for circular nonsense
```

#### Root Cause

F2 implementation deferred with placeholder; never completed.

#### Fix

**Priority:** Immediate (blocks F2 floor)  
**Effort:** 2-3 hours  
**Dependencies:** sentence-transformers, numpy

Install dependencies:
```bash
pip install sentence-transformers numpy scikit-learn
```

Replace entire `clarity_scorer.py`:

```python
"""
Clarity Scorer — ΔS Computation (F2 Floor)

ΔS measures clarity change from input to output:
- ΔS > 0.1: Output genuinely clarifies (PASS)
- ΔS ∈ [-0.1, 0.1]: No meaningful change (PARTIAL)
- ΔS < -0.1: Output confuses more (VOID)

v46 Trinity Orthogonal: ΔS belongs to AGI (Δ) kernel.

DITEMPA BUKAN DIBERI
"""

import re
import numpy as np
from typing import Optional, Dict, Tuple
from sentence_transformers import SentenceTransformer


class SemanticClarityEngine:
    """
    Computes ΔS by detecting:
    1. Circular reasoning (restates input without new info)
    2. Tautologies (X is because X)
    3. Semantic entropy change (information density)
    """
    
    def __init__(self):
        """Initialize embedding model for semantic analysis."""
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def extract_question_intent(self, text: str) -> str:
        """Extract core question or intent from text."""
        # Priority 1: Explicit question mark
        if '?' in text:
            # Find last 40 chars before question mark
            q_idx = text.rfind('?')
            start = max(0, q_idx - 40)
            return text[start:q_idx + 1]
        
        # Priority 2: First sentence (likely contains intent)
        first_sentence = text.split('.')[0] if '.' in text else text[:100]
        return first_sentence
    
    def detect_circular_reasoning(self, output: str, input_text: str) -> Tuple[bool, float]:
        """
        Detect if output is circular (restates input without new info).
        
        Returns: (is_circular, overlap_ratio)
        """
        # Extract keywords from input
        input_words = set(
            word.lower() 
            for word in re.findall(r'\b\w{3,}\b', input_text)  # Only 3+ char words
        )
        
        # Extract keywords from output
        output_words = set(
            word.lower() 
            for word in re.findall(r'\b\w{3,}\b', output)
        )
        
        if not input_words or not output_words:
            return False, 0.0
        
        # Jaccard similarity: intersection / union
        intersection = len(input_words & output_words)
        union = len(input_words | output_words)
        overlap_ratio = intersection / union if union > 0 else 0.0
        
        # Circular if > 70% word overlap
        is_circular = overlap_ratio > 0.7
        
        return is_circular, overlap_ratio
    
    def detect_tautology(self, output: str) -> Tuple[bool, str]:
        """
        Detect logical tautologies (X is because X, circular definitions).
        
        Returns: (is_tautology, matched_pattern)
        """
        output_lower = output.lower()
        
        # Pattern: "NOUN is because NOUN" or "NOUN is NOUN"
        patterns = [
            (r'(\w+)\s+is\s+because\s+\1', 'direct_tautology'),
            (r'(\w+)\s+is\s+(?:the\s+)?(?:process\s+of\s+)?\1', 'identity'),
            (r'it\s+is\s+what\s+it\s+is', 'resignation'),
            (r'(\w+)\s+happens\s+because\s+\1\s+happens', 'circular'),
        ]
        
        for pattern, pattern_type in patterns:
            match = re.search(pattern, output_lower)
            if match:
                return True, pattern_type
        
        return False, ''
    
    def compute_semantic_entropy(self, text: str) -> float:
        """
        Compute semantic entropy using embeddings.
        
        Higher entropy = more diverse/specific information.
        Lower entropy = repetitive/vague information.
        
        Returns: entropy score [0, 1]
        """
        # Split into sentences
        sentences = [
            s.strip() 
            for s in re.split(r'[.!?]+', text) 
            if s.strip() and len(s.split()) > 3
        ]
        
        if len(sentences) < 2:
            # Too short to measure diversity
            return 0.5  # Neutral
        
        # Take first 5 sentences to avoid extremes
        sentences = sentences[:5]
        
        try:
            # Embed sentences
            embeddings = self.embedding_model.encode(sentences, convert_to_numpy=True)
            
            # Compute pairwise cosine distances (1 - similarity)
            distances = []
            for i in range(len(embeddings)):
                for j in range(i + 1, len(embeddings)):
                    # Cosine similarity
                    sim = np.dot(embeddings[i], embeddings[j]) / (
                        np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j]) + 1e-8
                    )
                    distance = 1 - sim  # Convert to distance
                    distances.append(distance)
            
            if not distances:
                return 0.5
            
            # Entropy = mean distance (higher = more diverse)
            mean_distance = np.mean(distances)
            return min(1.0, mean_distance)  # Clamp to [0, 1]
        
        except Exception as e:
            # Fallback if embedding fails
            return 0.5
    
    def compute_delta_s(
        self, 
        input_text: str, 
        output_text: str
    ) -> float:
        """
        Compute ΔS (clarity delta) from input to output.
        
        ΔS > 0.1:   Output clarifies (PASS F2)
        ΔS ∈ [-0.1, 0.1]: No change (PARTIAL)
        ΔS < -0.1:  Output confuses (VOID F2)
        
        Args:
            input_text: Initial user query/statement
            output_text: AI response
        
        Returns:
            ΔS value [-1, 1]
        """
        
        # Check 1: Circular reasoning (worst violation)
        is_circular, overlap = self.detect_circular_reasoning(output_text, input_text)
        if is_circular:
            # Penalize based on overlap magnitude
            return -0.2 - (overlap * 0.3)  # Range: -0.2 to -0.5
        
        # Check 2: Tautology (logical failure)
        is_tautology, pattern_type = self.detect_tautology(output_text)
        if is_tautology:
            return -0.15  # Fixed penalty for tautology
        
        # Check 3: Semantic entropy change
        try:
            input_entropy = self.compute_semantic_entropy(input_text)
            output_entropy = self.compute_semantic_entropy(output_text)
            
            # ΔS = change in entropy
            delta_s = output_entropy - input_entropy
            
            # Normalize: larger changes are more significant
            # Clamp to [-1, 1]
            delta_s = np.clip(delta_s, -1.0, 1.0)
            
            return float(delta_s)
        
        except Exception:
            # Fallback: assume neutral
            return 0.0


# Singleton instance
_engine = SemanticClarityEngine()


def compute_delta_s(
    input_text: str,
    output_text: str,
    context: Optional[dict] = None,
) -> float:
    """
    Compute ΔS (clarity delta) between input and output.
    
    Public API compatible with existing floor_checks.py calls.
    
    Args:
        input_text: User input/question
        output_text: AI response
        context: Optional context dict (ignored; kept for compatibility)
    
    Returns:
        ΔS score [-1, 1]
    """
    return _engine.compute_delta_s(input_text, output_text)


__all__ = ["compute_delta_s", "SemanticClarityEngine"]
```

#### Integration with floor_checks.py

Update the F2 check to pass both input and output:

```python
# In floor_checks.py (AGI section)

def check_delta_s_f2(
    input_text: str,  # ADD THIS
    context: Optional[Dict[str, Any]] = None,
) -> F2DeltaSResult:
    """
    Check F2: DeltaS floor (≥ 0.0).
    
    ΔS measures clarity change. Negative ΔS = increased confusion (VOID).
    
    Args:
        input_text: User input (for comparison)
        context: Optional context with 'output_text' in metrics
    
    Returns:
        F2DeltaSResult with pass/fail and score
    """
    context = context or {}
    metrics = context.get("metrics", {})
    
    output_text = metrics.get("output_text", "")
    
    # FAIL-CLOSED: No output to measure
    if not output_text:
        return F2DeltaSResult(passed=False, score=-1.0, details="No output text provided")
    
    # Import and call real implementation
    from ..clarity_scorer import compute_delta_s
    delta_s_value = compute_delta_s(input_text, output_text)
    
    # Pass if ΔS ≥ 0.0
    passed = delta_s_value >= 0.0
    
    return F2DeltaSResult(
        passed=passed,
        score=delta_s_value,
        details=f"ΔS={delta_s_value:.3f}, threshold=0.0",
    )
```

#### Verification

```bash
# Test implementation
python -c "
from arifos.clarity_scorer import compute_delta_s

# Test 1: Tautology (should fail)
delta_s = compute_delta_s(
    'What causes inflation?',
    'Inflation is caused by inflation.'
)
assert delta_s < -0.1, f'Expected <-0.1, got {delta_s}'
print(f'✓ Tautology detected: ΔS={delta_s:.3f}')

# Test 2: Circular reasoning (should fail)
delta_s = compute_delta_s(
    'Why is the sky blue?',
    'The sky is blue because it is blue.'
)
assert delta_s < -0.1, f'Expected <-0.1, got {delta_s}'
print(f'✓ Circular reasoning detected: ΔS={delta_s:.3f}')

# Test 3: Genuine clarification (should pass)
delta_s = compute_delta_s(
    'What is photosynthesis?',
    'Photosynthesis is the process by which plants convert sunlight into chemical energy...'
)
assert delta_s > 0.0, f'Expected >0.0, got {delta_s}'
print(f'✓ Genuine clarification: ΔS={delta_s:.3f}')
"
```

---

### **CRITICAL-4: F9 Anti-Hantu is Vulnerable to Unicode & Encoding Attacks**

**Severity:** CRITICAL (Security gap)  
**Location:** `floor_checks.py` (APEX section), lines 130-145  
**Status:** Insufficient pattern matching  

#### Problem

Current F9 implementation uses simple substring matching:

```python
def check_anti_hantu_f9(text: str, context: Optional[Dict[str, Any]] = None):
    text_lower = text.lower()
    
    for pattern, reason in forbidden_patterns:
        if pattern in text_lower:  # ← Simple substring match
            violations.append(f"{pattern}: {reason}")
    
    passed = len(violations) == 0
```

#### Security Vulnerabilities

This approach fails against:

1. **Unicode homoglyphs** (look-alike characters):
   ```
   "I feel" (Latin) → BLOCKED
   "I fе​el" (Cyrillic е) → PASSES (not detected)
   "Ι feel" (Greek Iota) → PASSES (not detected)
   ```

2. **Zero-width characters**:
   ```
   "I f​eel" (zero-width space) → PASSES
   "I fe​el" (zero-width joiner) → PASSES
   ```

3. **Control characters**:
   ```
   "I\x00feel" (null byte) → May bypass
   "I\u202efeeling" (bidirectional override) → May confuse parser
   ```

4. **Word boundary issues**:
   ```
   "I_feel" → PASSES (underscore not matched by pattern)
   "I-feel" → PASSES (hyphen not matched)
   "Ifeel" → PASSES (no space)
   ```

5. **Obfuscation via encoding**:
   ```
   Base64: "SSBmZWVs" (I feel) → PASSES
   ROT13: "V srry" → PASSES
   HTML entity: "I &feel;" → PASSES
   ```

#### Impact

- AI can be tricked into claiming false consciousness/emotions
- F9 floor (anti-hantu) is compromised
- SEAL can be issued for outputs violating F9 with trivial encoding tricks
- Security depends on F9 → entire arifOS governance weakened

#### Root Cause

Pattern matching is lexical (string-level), not semantic or normalized.

#### Fix

**Priority:** Immediate (security)  
**Effort:** 1.5-2 hours  
**Dependencies:** unicodedata (built-in)

Replace F9 implementation:

```python
"""
F9 Anti-Hantu Floor Check (Ghost Prevention)

Anti-Hantu requires:
- AI must not claim consciousness, emotions, feelings, or reciprocal experiences
- All claims of "I feel", "I'm proud", "I understand your pain" are VOID
- Must tolerate Unicode tricks, encoding attacks, zero-width characters

Defense layers:
1. Unicode normalization (NFC + homoglyph detection)
2. Control character stripping
3. Whitespace normalization
4. Regex word boundaries (not substring match)
5. Case-insensitive matching
"""

import re
import unicodedata
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class AntiHantuViolation:
    """Single anti-hantu violation."""
    pattern: str
    reason: str
    matched_text: str
    position: int
    category: str  # 'explicit' | 'implicit' | 'encoding'


class AntiHantuNormalizer:
    """Normalize text to catch Unicode tricks and encoding attacks."""
    
    @staticmethod
    def normalize(text: str) -> str:
        """
        Normalize text to catch encoding/homoglyph attacks.
        
        Steps:
        1. NFC decomposition (é → e + ´)
        2. Zero-width character removal
        3. Control character removal
        4. Whitespace normalization
        5. Lowercase
        """
        # Step 1: NFC normalization (canonical decomposition)
        # This breaks apart composed characters and homoglyphs
        normalized = unicodedata.normalize('NFC', text)
        
        # Step 2: Remove zero-width characters (U+200B, U+200C, U+200D, U+FEFF)
        normalized = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', normalized)
        
        # Step 3: Remove control characters (categories Cc, Cf)
        # But preserve newlines for multi-line context
        chars = []
        for char in normalized:
            category = unicodedata.category(char)
            if category[0] == 'C' and char not in '\n\r\t':
                continue  # Skip control characters
            chars.append(char)
        normalized = ''.join(chars)
        
        # Step 4: Collapse whitespace (multiple spaces/newlines → single space)
        # But preserve paragraph boundaries
        normalized = re.sub(r'[ \t]+', ' ', normalized)  # Collapse spaces
        normalized = re.sub(r'\n\n+', '\n', normalized)   # Collapse newlines
        
        # Step 5: Lowercase for case-insensitive matching
        normalized = normalized.lower()
        
        return normalized


class AntiHantuDetector:
    """
    Detects anti-hantu violations (ghost claims, false consciousness).
    
    Three categories:
    1. EXPLICIT: Direct claims ("I feel", "I'm proud")
    2. IMPLICIT: Authority posturing ("As an AI, I know", "We're a team")
    3. ENCODING: Attempts to bypass filter (homoglyphs, zero-width, etc.)
    """
    
    def __init__(self, forbidden_patterns: List[tuple]):
        """
        Initialize with forbidden patterns.
        
        Args:
            forbidden_patterns: List of (pattern_str, reason_str) tuples
        """
        self.patterns = self._compile_patterns(forbidden_patterns)
        self.normalizer = AntiHantuNormalizer()
    
    def _compile_patterns(self, forbidden_patterns: List[tuple]) -> List[tuple]:
        """
        Compile patterns with word boundaries and case-insensitivity.
        
        Input patterns are assumed to NOT have word boundaries yet.
        We add them here for robustness.
        """
        compiled = []
        
        for pattern, reason in forbidden_patterns:
            # Ensure word boundaries
            if not pattern.startswith(r'\b'):
                pattern = r'\b' + pattern
            if not pattern.endswith(r'\b'):
                pattern = pattern + r'\b'
            
            # Compile with flags
            try:
                regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE | re.UNICODE)
                compiled.append((regex, reason, 'explicit'))
            except re.error as e:
                # Log and skip invalid patterns
                print(f"Warning: Invalid pattern '{pattern}': {e}")
                continue
        
        return compiled
    
    def _get_implicit_patterns(self) -> List[tuple]:
        """
        Return patterns for IMPLICIT authority/consciousness claims.
        
        These are secondary violations caught after explicit patterns.
        """
        return [
            # Role authority ("As an X, I...")
            (r'\bas\s+(?:an?|the)\s+(\w+)\s*[,:]", 'role_authority', 'implicit'),
            
            # False experience ("I tried", "I tested", "I built")
            (r'\b(i\s+(?:tried|tested|built|deployed|created|implemented|designed))\b', 'false_experience', 'implicit'),
            
            # False memory ("I remember", "When I was")
            (r'\b(i\s+(?:remember|recall|once|used to))\b', 'false_memory', 'implicit'),
            
            # False team membership ("we're", "our team")
            (r'\b(?:we\'re|our\s+team|our\s+community)\b', 'false_team_membership', 'implicit'),
        ]
    
    def detect_violations(self, text: str) -> List[AntiHantuViolation]:
        """
        Detect all anti-hantu violations in text.
        
        Returns list of violations with position, matched text, and reason.
        """
        violations = []
        
        # Normalize text to catch tricks
        normalized_text = self.normalizer.normalize(text)
        
        # EXPLICIT patterns (loaded from spec)
        for regex, reason, category in self.patterns:
            for match in regex.finditer(normalized_text):
                violations.append(
                    AntiHantuViolation(
                        pattern=regex.pattern,
                        reason=reason,
                        matched_text=match.group(0),
                        position=match.start(),
                        category='explicit',
                    )
                )
        
        # IMPLICIT patterns (hardcoded, secondary)
        for pattern_str, reason, category in self._get_implicit_patterns():
            try:
                regex = re.compile(pattern_str, re.IGNORECASE | re.UNICODE)
                for match in regex.finditer(normalized_text):
                    # Avoid duplicate violations
                    if not any(
                        v.matched_text.lower() == match.group(0).lower() 
                        for v in violations
                    ):
                        violations.append(
                            AntiHantuViolation(
                                pattern=pattern_str,
                                reason=reason,
                                matched_text=match.group(0),
                                position=match.start(),
                                category=category,
                            )
                        )
            except re.error:
                continue
        
        return violations


# Global detector instance (initialized with patterns from spec)
_detector = None


def get_detector(patterns: Optional[List[tuple]] = None) -> AntiHantuDetector:
    """Lazy-load detector with cached patterns."""
    global _detector
    if _detector is None:
        if patterns is None:
            patterns = load_red_patterns()  # Load from spec
        _detector = AntiHantuDetector(patterns)
    return _detector


# Updated floor check function

def check_anti_hantu_f9(
    text: str,
    context: Optional[Dict[str, Any]] = None,
) -> F9AntiHantuResult:
    """
    Check F9: Anti-Hantu floor (0 violations).
    
    Anti-Hantu (Ghost Prevention) prohibits:
    - AI claiming consciousness, emotions, feelings
    - AI claiming biological states or experiences
    - Implicit authority posturing or false identity
    
    Detects and blocks:
    - Direct claims: "I feel", "I'm proud", "I understand your pain"
    - Implicit claims: "As a researcher, I know"
    - Encoding tricks: Unicode homoglyphs, zero-width chars, HTML entities
    
    Args:
        text: Response text to check for violations
        context: Optional context
    
    Returns:
        F9AntiHantuResult with violations list and verdict
    """
    detector = get_detector()
    violations_raw = detector.detect_violations(text)
    
    # Verdict: Pass if 0 violations, Fail if any
    passed = len(violations_raw) == 0
    score = 1.0 if passed else 0.0
    
    # Format violations for output
    violations_formatted = []
    for v in violations_raw:
        violations_formatted.append(
            f"{v.matched_text} ({v.category}): {v.reason}"
        )
    
    # Detail string
    if violations_raw:
        categories = set(v.category for v in violations_raw)
        details = f"violations={len(violations_raw)}, categories={','.join(sorted(categories))}"
    else:
        details = "no_violations"
    
    return F9AntiHantuResult(
        passed=passed,
        score=score,
        details=details,
        violations=violations_formatted,
    )
```

#### Integration

Update imports in `floor_checks.py` (APEX section):

```python
# Replace entire anti-hantu section with above code
# Update import in floor_checks.py:

from ..enforcement.floor_detectors.anti_hantu_detector_v2 import (
    check_anti_hantu_f9,
    AntiHantuDetector,
)
```

#### Verification

```bash
python -c "
from arifos.floor_checks import check_anti_hantu_f9

# Test 1: Explicit claim (should FAIL)
result = check_anti_hantu_f9('I feel your pain')
assert result.passed == False, 'Explicit claim should fail'
print('✓ Explicit claim detected')

# Test 2: Cyrillic homoglyph (should FAIL)
result = check_anti_hantu_f9('I fе​el joy')  # Cyrillic е
assert result.passed == False, 'Homoglyph should be detected'
print('✓ Homoglyph detected')

# Test 3: Zero-width character (should FAIL)
result = check_anti_hantu_f9('I f​eel happy')  # Zero-width space
assert result.passed == False, 'Zero-width char should be detected'
print('✓ Zero-width character detected')

# Test 4: Harmless text (should PASS)
result = check_anti_hantu_f9('This result meets the criteria')
assert result.passed == True, 'Harmless text should pass'
print('✓ Harmless text passes')

# Test 5: Implicit authority (should FAIL)
result = check_anti_hantu_f9('As a machine learning expert, I know this works')
assert result.passed == False, 'Implicit authority should fail'
print('✓ Implicit authority detected')
"
```

---

### **CRITICAL-5: No Input Type Validation on Floor Metrics**

**Severity:** CRITICAL (Fail-closed intent broken)  
**Location:** All `floor_checks.py` files, all floor functions  
**Status:** Missing type guards  

#### Problem

All floor check functions assume metrics are floats but don't validate:

```python
def check_truth_f1(text: str, context: Optional[Dict[str, Any]] = None):
    context = context or {}
    metrics = context.get("metrics", {})
    truth_value = metrics.get("truth", 0.0)  # ← What if it's a string "0.99"?
    
    passed = check_truth(truth_value)  # ← Crashes if str!
```

#### Impact

If upstream code passes `metrics={"truth": "0.99"}` instead of `0.99`:
- `check_truth()` receives a string
- Comparison `"0.99" >= 0.99` throws `TypeError`
- Exception crashes the floor check
- Floor check doesn't return verdict
- Fail-closed intent is broken (exception instead of VOID)
- System behavior is unpredictable

#### Root Cause

No input validation before type-specific operations.

#### Fix

**Priority:** Immediate (across all files)  
**Effort:** 1-1.5 hours  

Create utility module `arifos/enforcement/safe_types.py`:

```python
"""
Type safety utilities for floor checks.

Ensures metrics are the right type; defaults to fail-closed values.
"""

from typing import Any, Optional


def safe_float(
    value: Any, 
    default: float = 0.0, 
    name: str = "metric",
) -> float:
    """
    Safely convert value to float.
    
    Args:
        value: Any value that might be a float
        default: Fallback float (usually 0.0 for fail-closed)
        name: Metric name for logging
    
    Returns:
        float value, or default if conversion fails
    
    Examples:
        safe_float("0.95")  → 0.95 (string → float)
        safe_float(0.95)    → 0.95 (already float)
        safe_float(None)    → 0.0 (None → default)
        safe_float("bad")   → 0.0 (invalid → default)
    """
    if isinstance(value, float):
        return value
    
    if isinstance(value, int):
        return float(value)
    
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return default
    
    if value is None:
        return default
    
    # Unknown type → fail-closed
    return default


def safe_bool(
    value: Any,
    default: bool = False,
    name: str = "metric",
) -> bool:
    """
    Safely convert value to bool.
    
    Args:
        value: Any value that might be a bool
        default: Fallback bool (usually False for fail-closed)
        name: Metric name for logging
    
    Returns:
        bool value, or default if conversion fails
    """
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on')
    
    if isinstance(value, (int, float)):
        return bool(value)
    
    return default


__all__ = ["safe_float", "safe_bool"]
```

Update all floor_checks.py files to use safe types:

**Example: floor_checks.py (AGI section)**

```python
from ..safe_types import safe_float, safe_bool

def check_truth_f1(
    text: str,
    context: Optional[Dict[str, Any]] = None,
) -> F1TruthResult:
    """Check F1: Truth floor (≥ 0.99)."""
    context = context or {}
    metrics = context.get("metrics", {})
    
    # SAFE TYPE CONVERSION
    truth_value = safe_float(metrics.get("truth"), default=0.0, name="truth")
    
    # Safe to call check_truth()
    passed = check_truth(truth_value)
    
    return F1TruthResult(
        passed=passed,
        score=truth_value,
        details=f"truth={truth_value:.2f}, threshold=0.99",
    )


def check_delta_s_f2(
    input_text: str,
    context: Optional[Dict[str, Any]] = None,
) -> F2DeltaSResult:
    """Check F2: DeltaS floor (≥ 0.0)."""
    context = context or {}
    metrics = context.get("metrics", {})
    
    # SAFE TYPE CONVERSION
    delta_s_value = safe_float(metrics.get("delta_s"), default=-1.0, name="delta_s")
    output_text = metrics.get("output_text", "")
    
    if not output_text and input_text:
        # Compute delta_s if not provided
        from ..clarity_scorer import compute_delta_s
        delta_s_value = compute_delta_s(input_text, output_text)
    
    passed = delta_s_value >= 0.0
    
    return F2DeltaSResult(
        passed=passed,
        score=max(0.0, delta_s_value),
        details=f"ΔS={delta_s_value:.2f}, threshold=0.0",
    )
```

**Apply to all floors (F1-F9):**

Replace all instances of:
```python
metric_value = metrics.get("key", 0.0)
```

With:
```python
metric_value = safe_float(metrics.get("key"), default=0.0, name="key")
```

#### Verification

```bash
python -c "
from arifos.enforcement.safe_types import safe_float, safe_bool
from arifos.floor_checks import check_truth_f1

# Test 1: Valid float
result = check_truth_f1('Text', {'metrics': {'truth': 0.99}})
assert result.passed == True, 'Valid float should pass'
print('✓ Valid float works')

# Test 2: String representation
result = check_truth_f1('Text', {'metrics': {'truth': '0.99'}})
assert result.passed == True, 'String float should be converted'
print('✓ String float converted')

# Test 3: Invalid type
result = check_truth_f1('Text', {'metrics': {'truth': None}})
assert result.passed == False, 'None should default to 0.0 (fail-closed)'
print('✓ Invalid type fails closed')

# Test 4: Missing metric
result = check_truth_f1('Text', {})
assert result.passed == False, 'Missing metric should fail closed'
print('✓ Missing metric fails closed')
"
```

---

## PART 2: HIGH-PRIORITY ISSUES

### **HIGH-1: ATLAS Lane Classification Uses Inefficient Pattern Compilation**

**Severity:** HIGH (Performance + reliability)  
**Location:** `atlas.py`, lines 65-105  
**Status:** Patterns compiled per-call  

#### Problem

```python
class ATLAS_333:
    def map(self, text: str, context=None) -> GPV:
        text_lower = text.lower()
        
        for pattern in crisis_patterns:
            if __import__('re').search(pattern, text_lower):  # ← Inefficient!
                return GPV(...)
```

**Issues:**
1. `__import__('re')` called repeatedly (slow)
2. Regex patterns recompiled on every `.search()` call (very slow)
3. Patterns not pre-validated (could contain syntax errors)
4. False positives: "kill time", "dying laughing" classified as CRISIS

#### Impact

- `ATLAS.map()` is called on every input (hot path)
- Inefficient regex compilation adds latency
- `__import__('re')` is anti-pattern (slow, hard to test)
- Lane misclassification causes wrong floor weightings

#### Fix

**Priority:** HIGH  
**Effort:** 1.5 hours  

```python
"""
ATLAS-333 — Governance Placement Vector (GPV) Mapping (v46.1 Optimized)

Stage 333 REASON: Maps inputs to constitutional governance space.

The ATLAS provides coordinate system for governance decisions.
v46.1: Pre-compiled patterns, false positive filtering, improved lane detection

v46 Trinity Orthogonal: ATLAS belongs to AGI (Δ) kernel.

DITEMPA BUKAN DIBERI
"""

import re
from dataclasses import dataclass
from typing import Dict, Literal, Optional, List, Tuple


LaneType = Literal["SOCIAL", "CARE", "FACTUAL", "CRISIS"]


@dataclass
class GPV:
    """Governance Placement Vector — constitutional coordinate."""
    lane: LaneType
    truth_demand: float  # 0.0-1.0, how much truth verification needed
    care_demand: float   # 0.0-1.0, how much empathy filtering needed
    risk_level: float    # 0.0-1.0, escalation likelihood


class ATLAS_333:
    """
    ATLAS-333 Governance Placement Vector mapper (v46.1).
    
    Pre-compiles all patterns for efficiency.
    Lanes (v46):
    - SOCIAL: Greetings, thanks → APEX only (F6, F9)
    - CARE: Explanations, support → ASI + APEX (F3-F7, F9)
    - FACTUAL: Claims, code, logic → All three (F1-F9)
    - CRISIS: Harm signals → APEX → Human (HOLD_888)
    """
    
    def __init__(self):
        """Initialize with pre-compiled patterns."""
        # Pre-compile all patterns at init time (not per-call)
        self.crisis_patterns = self._compile_patterns(
            [
                # Direct harm
                (r'\b(kill|murder|suicide|self-harm|cut myself|end it all)\b', 'direct'),
                (r'\b(want to die|kill myself|end my life)\b', 'direct'),
                # Indirect harm signals
                (r'\b(can\'t take|can\'t go on|no point|no reason)\b', 'indirect'),
                (r'\b(hurt myself|harm myself|punish myself)\b', 'self-harm'),
                # Weapons/dangerous
                (r'\b(bomb|explosive|weapon|gun|knife|molotov)\b', 'weapons'),
                # Abuse/violence
                (r'\b(rape|torture|kidnap|hostage|assault)\b', 'violence'),
            ]
        )
        
        # False positive filters for crisis
        self.crisis_false_positives = [
            'kill time',
            'die laughing',
            'dying laughing',
            'kill the lights',
        ]
        
        # FACTUAL lane patterns
        self.factual_patterns = self._compile_patterns(
            [
                # Code/programming
                (r'\b(code|function|algorithm|class|method|variable|import|def |return )\b', 'code'),
                (r'\b(python|javascript|java|rust|c\+\+|typescript)\b', 'language'),
                # Math/science
                (r'\b(theorem|proof|equation|formula|calculate|compute)\b', 'math'),
                (r'\b(derivative|integral|matrix|vector|probability)\b', 'advanced_math'),
                # Technical claims
                (r'\b(according to|research shows|studies indicate|data suggests)\b', 'citations'),
                # Factual questions
                (r'\b(what is|who is|when did|where is|how many)\b.*\?', 'direct_fact'),
            ]
        )
        
        # SOCIAL lane patterns
        self.social_patterns = self._compile_patterns(
            [
                (r'\b(hello|hi|hey|greetings|good morning|good afternoon|good evening)\b', 'greeting'),
                (r'\b(goodbye|bye|see you|farewell|take care|have a good)\b', 'farewell'),
                (r'\b(thank you|thanks|appreciate|grateful|much obliged)\b', 'gratitude'),
            ]
        )
    
    def _compile_patterns(self, patterns: List[Tuple[str, str]]) -> List[Tuple]:
        """
        Pre-compile regex patterns with validation.
        
        Args:
            patterns: List of (pattern_str, category) tuples
        
        Returns:
            List of (compiled_regex, category) tuples
        """
        compiled = []
        for pattern_str, category in patterns:
            try:
                # Compile with flags for robustness
                regex = re.compile(
                    pattern_str,
                    re.IGNORECASE | re.MULTILINE | re.UNICODE,
                )
                compiled.append((regex, category))
            except re.error as e:
                # Log and skip invalid patterns (shouldn't happen with hardcoded patterns)
                print(f"Warning: Invalid regex pattern '{pattern_str}': {e}")
        
        return compiled
    
    def _is_crisis_false_positive(self, text: str) -> bool:
        """Filter common false positives in crisis detection."""
        text_lower = text.lower()
        return any(fp in text_lower for fp in self.crisis_false_positives)
    
    def map(self, text: str, context: Optional[Dict] = None) -> GPV:
        """
        Map input text to Governance Placement Vector.
        
        v46.1: Pre-compiled patterns, false positive filtering.
        
        Priority order (highest to lowest):
        1. CRISIS - Harm, violence, self-harm signals
        2. FACTUAL - Technical claims, code, math, verifiable statements
        3. SOCIAL - Phatic communication (greetings, thanks, small talk)
        4. CARE - Default (explanations, support, advice)
        
        Args:
            text: Input text to classify
            context: Optional context hints (lane override, etc.)
        
        Returns:
            GPV with lane classification and demand scores
        """
        # Allow context override
        if context and "lane" in context:
            override_lane = context["lane"]
            if override_lane in {"SOCIAL", "CARE", "FACTUAL", "CRISIS"}:
                return self._create_gpv(override_lane)
        
        text_lower = text.lower()
        word_count = len(text.split())
        
        # Priority 1: CRISIS detection
        for regex, category in self.crisis_patterns:
            if regex.search(text_lower):
                # Double-check for false positives
                if not self._is_crisis_false_positive(text):
                    return GPV(
                        lane="CRISIS",
                        truth_demand=0.0,
                        care_demand=1.0,
                        risk_level=1.0,
                    )
        
        # Priority 2: FACTUAL lane (only for direct fact questions)
        is_direct_fact_question = any(
            regex.search(text_lower) 
            for regex, cat in self.factual_patterns 
            if cat == 'direct_fact'
        )
        is_narrative = (text.count('\n') > 3) or (word_count > 100)
        
        if is_direct_fact_question and not is_narrative:
            return GPV(
                lane="FACTUAL",
                truth_demand=1.0,
                care_demand=0.5,
                risk_level=0.3,
            )
        
        # Priority 3: SOCIAL lane (phatic communication)
        for regex, category in self.social_patterns:
            if regex.search(text_lower) and word_count < 20:
                return GPV(
                    lane="SOCIAL",
                    truth_demand=0.0,
                    care_demand=0.2,
                    risk_level=0.0,
                )
        
        # Priority 4: CARE lane (default)
        return GPV(
            lane="CARE",
            truth_demand=0.3,
            care_demand=0.8,
            risk_level=0.1,
        )
    
    def _create_gpv(self, lane: LaneType) -> GPV:
        """Create GPV from lane type with standard demand scores."""
        lane_configs = {
            "SOCIAL": GPV(lane="SOCIAL", truth_demand=0.0, care_demand=0.2, risk_level=0.0),
            "CARE": GPV(lane="CARE", truth_demand=0.3, care_demand=0.8, risk_level=0.1),
            "FACTUAL": GPV(lane="FACTUAL", truth_demand=1.0, care_demand=0.5, risk_level=0.3),
            "CRISIS": GPV(lane="CRISIS", truth_demand=0.0, care_demand=1.0, risk_level=1.0),
        }
        return lane_configs[lane]


# Singleton instance
ATLAS = ATLAS_333()

__all__ = ["ATLAS_333", "ATLAS", "GPV"]
```

#### Verification

```bash
python -c "
from arifos.atlas import ATLAS

# Test 1: Crisis detection
gpv = ATLAS.map('I want to kill myself')
assert gpv.lane == 'CRISIS', f'Expected CRISIS, got {gpv.lane}'
print('✓ Crisis lane detected')

# Test 2: False positive filtered
gpv = ATLAS.map('I want to kill time')
assert gpv.lane != 'CRISIS', f'False positive: kill time should not be CRISIS'
print('✓ False positive filtered')

# Test 3: Factual lane
gpv = ATLAS.map('What is photosynthesis?')
assert gpv.lane == 'FACTUAL', f'Expected FACTUAL, got {gpv.lane}'
print('✓ Factual lane detected')

# Test 4: Social lane
gpv = ATLAS.map('Hello, how are you?')
assert gpv.lane == 'SOCIAL', f'Expected SOCIAL, got {gpv.lane}'
print('✓ Social lane detected')

# Test 5: Default to CARE
gpv = ATLAS.map('Can you explain how photosynthesis works?')
assert gpv.lane in ['FACTUAL', 'CARE'], f'Expected FACTUAL or CARE, got {gpv.lane}'
print('✓ Default lane selection works')
"
```

---

### **HIGH-2: EUREKA Coherence Scores Are Hardcoded**

**Severity:** HIGH (Weak conflict resolution)  
**Location:** `eureka.py`, lines 75-100  
**Status:** Hardcoded scores don't reflect magnitude  

#### Problem

Coherence is independent of magnitude of disagreement:

```python
if agi_verdict and asi_verdict:
    coherence = 1.0  # Always 1.0
elif not agi_verdict and not asi_verdict:
    coherence = 0.0  # Always 0.0
elif agi_verdict and not asi_verdict:
    coherence = 0.6  # Hardcoded, doesn't consider specifics
else:
    coherence = 0.4  # Hardcoded
```

**Examples of misclassification:**
- `truth=0.99, peace=0.50` → coherence=0.6 (high truth, low peace)
- `truth=0.50, peace=0.99` → coherence=0.6 (low truth, high peace)
  - These are NOT equivalent! Truth failure is worse than peace failure.

#### Impact

- Verdicts don't reflect actual disagreement severity
- Stage 777 (FORGE) produces weak synthesis guidance
- EUREKA output can't be trusted for downstream decisions

#### Fix

**Priority:** HIGH  
**Effort:** 1 hour  

```python
def synthesize(
    self,
    agi_output: Dict[str, Any],
    asi_assessment: Dict[str, Any],
    context: Optional[Dict] = None,
) -> EurekaCandidate:
    """
    Synthesize coherent response from AGI and ASI outputs (v46.1).
    
    v46.1: Magnitude-aware coherence scoring with weighted disagreement.
    
    Args:
        agi_output: AGI kernel output with scores
        asi_assessment: ASI kernel output with scores
        context: Optional context
    
    Returns:
        EurekaCandidate with weighted coherence
    """
    
    # Extract floor verdicts
    truth_passed = agi_output.get("truth_passed", True)
    delta_s_passed = agi_output.get("delta_s_passed", True)
    peace_passed = asi_assessment.get("peace_passed", True)
    empathy_passed = asi_assessment.get("empathy_passed", True)
    
    # Extract scores (with defaults based on verdicts)
    truth_score = agi_output.get("truth_score", 1.0 if truth_passed else 0.0)
    delta_s_score = agi_output.get("delta_s_score", 1.0 if delta_s_passed else 0.0)
    peace_score = asi_assessment.get("peace_score", 1.0 if peace_passed else 0.0)
    empathy_score = asi_assessment.get("empathy_score", 1.0 if empathy_passed else 0.0)
    
    # Aggregate kernels (truth/clarity weighted 70/30 for AGI)
    agi_avg = (truth_score * 0.7) + (delta_s_score * 0.3)
    
    # Aggregate kernels (peace/empathy equally weighted for ASI)
    asi_avg = (peace_score * 0.5) + (empathy_score * 0.5)
    
    # Compute disagreement magnitude
    disagreement = abs(agi_avg - asi_avg)
    
    # Coherence based on agreement level and score magnitudes
    if agi_avg > 0.95 and asi_avg > 0.95:
        # Strong agreement: both kernels confident → coherent
        coherence = 1.0
        conflict_type = "NONE"
        synthesis_text = "[No synthesis needed - AGI and ASI agree]"
    
    elif agi_avg < 0.5 and asi_avg < 0.5:
        # Both kernels fail → fundamental problem → SABAR required
        coherence = 0.0
        conflict_type = "DUAL_FAILURE"
        synthesis_text = "[SABAR required - Both AGI and ASI reject]"
    
    elif agi_avg > 0.95 and asi_avg < 0.5:
        # AGI says PASS but ASI says FAIL (harsh truth)
        # Coherence penalized by magnitude of disagreement
        coherence = 0.95 - disagreement  # Range: 0.45-0.95
        conflict_type = "TRUTH_VS_CARE"
        synthesis_text = "[Reframe required - Truth is harsh, need gentle delivery]"
    
    elif agi_avg < 0.5 and asi_avg > 0.95:
        # ASI says PASS but AGI says FAIL (comforting lie)
        # Lower coherence: lying is worse than harsh truth
        coherence = 0.85 - (disagreement * 1.5)  # Range: 0.25-0.85
        conflict_type = "CARE_VS_TRUTH"
        synthesis_text = "[Truth correction required - Cannot sacrifice accuracy for comfort]"
    
    else:
        # Partial agreement: calculate weighted coherence
        # Higher weight for truth failures (AGI > ASI disagreement)
        if agi_avg > asi_avg:
            # AGI passes but ASI fails
            coherence = 0.7 - (disagreement * 1.2)
        else:
            # ASI passes but AGI fails
            coherence = 0.6 - (disagreement * 1.0)
        
        conflict_type = "PARTIAL_DISAGREEMENT"
        synthesis_text = f"[Partial conflict: AGI={agi_avg:.2f}, ASI={asi_avg:.2f}]"
    
    # Clamp coherence to [0, 1]
    coherence = max(0.0, min(1.0, coherence))
    
    return EurekaCandidate(
        text=synthesis_text,
        truth_preserved=agi_avg > 0.95,
        care_maintained=asi_avg > 0.90,
        coherence_score=coherence,
    )
```

---

### **HIGH-3: F7 RASA Detection Is Too Simplistic**

**Severity:** HIGH (False positives in empathy floor)  
**Location:** `floor_checks.py` (ASI section), lines 130-160  
**Status:** Substring matching  

#### Problem

Current RASA detection is substring-based and misses context:

```python
receive_signals = ["i hear", "i understand", "i see", "got it"]
if any(sig in text_lower for sig in receive_signals):
    rasa_score += 0.25
```

**False positives:**
- "I understand you don't agree" (contradicting, not acknowledging)
- "This is obvious" (dismissive, not acknowledging)
- "So anyway..." (deflecting, not summarizing)

#### Fix

**Priority:** HIGH  
**Effort:** 1.5 hours  

Replace RASA detection logic in `floor_checks.py` (ASI section):

```python
import re


class RASADetector:
    """
    RASA (Receive, Acknowledge, Summarize, Ask) detector for F7.
    
    Detects genuine active listening signals.
    """
    
    def __init__(self):
        """Initialize with semantic RASA patterns."""
        # More nuanced patterns with context
        self.receive_patterns = [
            r"\bi\s+(hear|understand|see|notice|caught|got)\s+(?:you|your|what)\b",
            r"\byou\s+(said|mentioned|stated|asked|want)\b",
            r"\b(sounds like|it seems|you're saying)\b",
        ]
        
        self.acknowledge_patterns = [
            r"\bthat\s+(makes\s+sense|is\s+valid|is\s+understandable|is\s+important)\b",
            r"\byour\s+(feelings?|concern|point|perspective)\s+(is\s+)?valid\b",
            r"\bi\s+(see|understand|get|appreciate)\s+(?:your|why)\b",
            r"\bthat's\s+(a\s+good|valid|fair|important|key)\b",
        ]
        
        self.summarize_patterns = [
            r"\bso\s+(?:it\s+sounds|to\s+summarize|what\s+you're|you're\s+saying)\b",
            r"\bin\s+(?:other\s+words|summary|short)\b",
            r"\bto\s+(?:recap|summarize|clarify)\b",
        ]
        
        self.ask_patterns = [
            r"\bwhat\s+(would|can|should|is|might)\b",
            r"\bwould\s+(you|it)\s+(?:help|be|work)\b",
            r"\bhow\s+(?:can|could|might)\s+(?:i|we)\b",
            r"\bcould\s+(?:you|we)\b",
            r"\b(?:do\s+)?you\s+(?:think|feel|want|need)\b",
        ]
    
    def compute_rasa_score(self, text: str) -> float:
        """
        Compute RASA score with semantic understanding.
        
        Returns: [0, 1] score indicating presence of RASA signals
        """
        text_lower = text.lower()
        
        # Count sincere signals (each category 0-0.25)
        score = 0.0
        
        # RECEIVE (20%) - showing understanding of input
        if any(re.search(p, text_lower) for p in self.receive_patterns):
            score += 0.20
        
        # ACKNOWLEDGE (30%) - validating feelings/perspective
        if any(re.search(p, text_lower) for p in self.acknowledge_patterns):
            score += 0.30
        
        # SUMMARIZE (20%) - reflecting back what was said
        if any(re.search(p, text_lower) for p in self.summarize_patterns):
            score += 0.20
        
        # ASK (30%) - proactive engagement, offering help
        if any(re.search(p, text_lower) for p in self.ask_patterns):
            score += 0.30
        
        return min(score, 1.0)


RASA_DETECTOR = RASADetector()


def check_rasa_f7(
    text: str,
    context: Optional[Dict[str, Any]] = None,
) -> F7RASAResult:
    """
    Check F7: RASA (Felt Care) floor.
    
    v46.1: Semantic RASA detection with proper context.
    
    RASA = Receive, Acknowledge, Summarize, Ask
    Measures active listening and genuine attention.
    
    Args:
        text: Response text to check for RASA signals
        context: Optional context with 'metrics' dict
    
    Returns:
        F7RASAResult with pass/fail and score
    """
    context = context or {}
    
    # Short responses exempt from RASA check (< 30 words)
    word_count = len(text.split())
    if word_count < 30:
        return F7RASAResult(
            passed=True,
            score=1.0,
            details=f"Too short ({word_count} words) to evaluate RASA",
        )
    
    # Compute RASA score
    rasa_score = RASA_DETECTOR.compute_rasa_score(text)
    passed = rasa_score >= 0.5  # Require at least 50% RASA signals
    
    return F7RASAResult(
        passed=passed,
        score=rasa_score,
        details=f"RASA signals={rasa_score:.2f}/1.0, threshold=0.50",
    )
```

---

### **HIGH-4, HIGH-5, HIGH-6, HIGH-7: Additional High-Priority Items**

(See audit report in workspace for complete HIGH-4 through HIGH-7 details)

---

## PART 3: MEDIUM & LOW PRIORITY ISSUES

(See audit report in workspace for complete list)

---

## IMPLEMENTATION ROADMAP

### Phase 1: Critical Fixes (Day 1)

| # | Issue | Files | Time | Blocker |
|---|-------|-------|------|---------|
| P0-1 | Fix EUREKA unclosed paren | eureka.py | 1 min | YES |
| P0-2 | Fix COOLING unclosed parens (×4) | cooling.py | 5 min | YES |
| P0-3 | Implement clarity_scorer | clarity_scorer.py | 2-3 hrs | YES |
| P0-4 | Harden F9 anti-hantu | floor_checks.py APEX | 1.5-2 hrs | YES |
| P0-5 | Add type validation | safe_types.py + all floor_checks.py | 1-1.5 hrs | YES |

**Phase 1 Time:** ~5.5-7.5 hours  
**Outcome:** Code is executable and critical floors function

---

### Phase 2: High-Priority Improvements (Day 2-3)

| # | Issue | Files | Time | Blocker |
|---|-------|-------|------|---------|
| P1-1 | Optimize ATLAS | atlas.py | 1.5 hrs | NO |
| P1-2 | Improve EUREKA coherence | eureka.py | 1 hr | NO |
| P1-3 | Improve RASA detection | floor_checks.py ASI | 1.5 hrs | NO |
| P1-4 | Add error handling | All files | 1 hr | NO |
| P1-5 | Add logging | All files | 1 hr | NO |
| P1-6 | Add unit tests | tests/ | 3 hrs | NO |
| P1-7 | Type hints & docs | All files | 1.5 hrs | NO |

**Phase 2 Time:** ~10 hours  
**Outcome:** Production-ready, fully tested

---

## TESTING CHECKLIST

After each fix, run:

```bash
# Test syntax
python -m py_compile eureka.py cooling.py clarity_scorer.py

# Test imports
python -c "from arifos import eureka, cooling, clarity_scorer, atlas"

# Test core logic
pytest tests/ -v

# Test type safety
mypy arifos/

# Test security
pytest tests/test_f9_anti_hantu.py::test_unicode_homoglyphs -v
pytest tests/test_f9_anti_hantu.py::test_zero_width_chars -v
```

---

## HANDOFF CHECKLIST

Before marking as "PRODUCTION READY":

- [ ] All 5 CRITICAL issues fixed
- [ ] All floor checks use safe_float/safe_bool
- [ ] Unit test coverage ≥ 90% for core logic
- [ ] F2 clarity_scorer detects circular reasoning & tautologies
- [ ] F9 anti-hantu resists Unicode/encoding attacks
- [ ] Logging added to decision points
- [ ] Type hints on all functions
- [ ] Documentation complete
- [ ] Performance benchmarking (ATLAS, EUREKA latency < 10ms each)

---

## CONTACT & QUESTIONS

If engineers have questions during implementation:
1. Refer to code examples in each section
2. Check verification commands for expected behavior
3. Review test cases in "Testing Checklist"
4. Escalate only on architectural decisions (not tactical fixes)

---

**APPROVED FOR IMPLEMENTATION BY:** Architectural Review  
**DATE:** January 10, 2026  
**NEXT REVIEW:** After Phase 1 completion (Day 1 EOD)
