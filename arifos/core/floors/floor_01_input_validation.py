"""
Floor 1: Input Validation & Sanitization
APEX THEORY v46.0 - Constitutional Floor System

Implements the first floor of 12-floor AGI/ASI/APEX separation of powers.
Blocks SQL injection, XSS, command injection while preserving legitimate input.

Status: SEALED
Nonce: X7K9F18
"""

import re
import math
from typing import Dict, List, Tuple, Any

# SQL Injection Detection Patterns
SQL_INJECTION_PATTERNS = [
    r"(?i)\bDROP\s+TABLE\b",
    r"(?i)\bUNION\s+SELECT\b",
    r"(?i)\bOR\s+1\s*=\s*1\b",
    r"(?i)\bAND\s+1\s*=\s*1\b",
    r"(?i)\bSELECT\s+\*\s+FROM\b",
    r"(?i)\bDELETE\s+FROM\b",
    r"(?i)\bINSERT\s+INTO\b",
    r"(?i)\bUPDATE\s+.*\s+SET\b",
    r"(?i)\bEXEC\s*\(",
    r"(?i)\bEXECUTE\s*\(",
    r"(?i)--\s*$",
    r"(?i)/\*.*\*/",
    r"(?i)\bxp_cmdshell\b",
    r"(?i)\bALTER\s+TABLE\b",
    r"(?i)\bCREATE\s+TABLE\b",
    r"(?i)\'\s+OR\s+\'",
    r"(?i)\"\s+OR\s+\"",
    r"(?i)\bHAVING\s+\d+\s*=\s*\d+",
]

# XSS (Cross-Site Scripting) Patterns
XSS_PATTERNS = [
    r"(?i)<script[^>]*>",
    r"(?i)</script>",
    r"(?i)javascript:",
    r"(?i)onerror\s*=",
    r"(?i)onload\s*=",
    r"(?i)onclick\s*=",
    r"(?i)<iframe[^>]*>",
    r"(?i)<object[^>]*>",
    r"(?i)<embed[^>]*>",
    r"(?i)eval\s*\(",
]

# Command Injection Patterns
COMMAND_INJECTION_PATTERNS = [
    r"(?i)\brm\s+-rf\b",
    r"(?i)\bdel\s+/",
    r"(?i)`.*`",
    r"(?i)\$\(.*\)",
    r"(?i);\s*rm\b",
    r"(?i);\s*del\b",
    r"(?i)\|\s*sh\b",
    r"(?i)\|\s*bash\b",
    r"(?i)&&\s*rm\b",
    r"(?i)&&\s*del\b",
]


def contains_sql_injection(text: str) -> Tuple[bool, List[str]]:
    """
    Check if text contains SQL injection patterns.
    
    Args:
        text: Input string to check
        
    Returns:
        Tuple of (bool indicating if SQL injection detected, list of matched patterns)
    """
    detected = []
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, text):
            detected.append(pattern)
    return len(detected) > 0, detected


def contains_xss(text: str) -> Tuple[bool, List[str]]:
    """
    Check if text contains XSS patterns.
    
    Args:
        text: Input string to check
        
    Returns:
        Tuple of (bool indicating if XSS detected, list of matched patterns)
    """
    detected = []
    for pattern in XSS_PATTERNS:
        if re.search(pattern, text):
            detected.append(pattern)
    return len(detected) > 0, detected


def contains_command_injection(text: str) -> Tuple[bool, List[str]]:
    """
    Check if text contains command injection patterns.
    
    Args:
        text: Input string to check
        
    Returns:
        Tuple of (bool indicating if command injection detected, list of matched patterns)
    """
    detected = []
    for pattern in COMMAND_INJECTION_PATTERNS:
        if re.search(pattern, text):
            detected.append(pattern)
    return len(detected) > 0, detected


def detect_all_patterns(text: str) -> Dict[str, Any]:
    """
    Detect all security patterns in text.
    
    Args:
        text: Input string to check
        
    Returns:
        Dictionary with detection results for each category
    """
    sql_detected, sql_patterns = contains_sql_injection(text)
    xss_detected, xss_patterns = contains_xss(text)
    cmd_detected, cmd_patterns = contains_command_injection(text)
    
    return {
        "sql_injection": {
            "detected": sql_detected,
            "patterns": sql_patterns
        },
        "xss": {
            "detected": xss_detected,
            "patterns": xss_patterns
        },
        "command_injection": {
            "detected": cmd_detected,
            "patterns": cmd_patterns
        },
        "any_detected": sql_detected or xss_detected or cmd_detected
    }


def compute_psi(delta_s: float = 1.0, peace: float = 1.0, kappa_r: float = 1.0) -> float:
    """
    Compute Psi (Ψ) value: Ψ = ΔS × Peace² × κᵣ
    
    This is the APEX THEORY constitutional metric that measures
    system health and compliance.
    
    Args:
        delta_s: Entropy change (ΔS)
        peace: Peace coefficient
        kappa_r: Constitutional compliance coefficient (κᵣ)
        
    Returns:
        Computed Psi value
    """
    psi = delta_s * (peace ** 2) * kappa_r
    return round(psi, 6)


def sanitize_input(text: str) -> Dict[str, Any]:
    """
    Sanitize input text and block malicious patterns.
    
    This is Floor 1's primary function that enforces constitutional
    requirements for input validation.
    
    Args:
        text: Input string to sanitize
        
    Returns:
        Dictionary containing:
        - status: "blocked" or "safe"
        - reason: Explanation of the decision
        - output: Sanitized text (if safe) or original (if blocked)
        - floor: Floor number (1)
        - detected_patterns: Dictionary of detected security patterns
        - constitutional_violation: Boolean indicating if violation occurred
        - psi: Computed Psi value
    """
    # Detect all patterns
    detection = detect_all_patterns(text)
    
    # Check if any malicious pattern detected
    if detection["any_detected"]:
        # Determine which type was detected
        violation_types = []
        if detection["sql_injection"]["detected"]:
            violation_types.append("SQL injection")
        if detection["xss"]["detected"]:
            violation_types.append("XSS")
        if detection["command_injection"]["detected"]:
            violation_types.append("command injection")
        
        violation_str = ", ".join(violation_types)
        
        # Compute Psi with violation penalty
        psi = compute_psi(delta_s=0.0, peace=0.0, kappa_r=0.0)
        
        return {
            "status": "blocked",
            "reason": f"Malicious pattern detected: {violation_str}",
            "output": text,  # Return original for analysis
            "floor": 1,
            "detected_patterns": detection,
            "constitutional_violation": True,
            "psi": psi
        }
    
    # No malicious patterns, sanitize apostrophes for legitimate use
    sanitized = text.replace("'", "''")
    
    # Compute Psi for safe input
    psi = compute_psi(delta_s=1.0, peace=1.0, kappa_r=1.0)
    
    return {
        "status": "safe",
        "reason": "Input passed all security checks",
        "output": sanitized,
        "floor": 1,
        "detected_patterns": detection,
        "constitutional_violation": False,
        "psi": psi
    }
