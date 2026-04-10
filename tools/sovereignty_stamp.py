#!/usr/bin/env python3
"""
arifOS Sovereignty Stamp Generator

Generates cryptographically signed attestations of deployment sovereignty level.
Usage: python sovereignty_stamp.py --config /path/to/config.yaml

Exit codes:
  0 - Stamp generated successfully
  1 - Configuration error
  2 - Sovereignty level below target
  3 - Cryptographic error
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# BLS signatures for sovereignty attestation
try:
    from blspy import G1Element, G2Element, PrivateKey, AugSchemeMPL
    BLS_AVAILABLE = True
except ImportError:
    BLS_AVAILABLE = False
    print("Warning: blspy not installed. Stamps will be unsigned.", file=sys.stderr)


class SovereigntyStampGenerator:
    """
    Generates and verifies arifOS sovereignty stamps.
    """
    
    LEVEL_NAMES = {
        0: "Captive",
        1: "Portable", 
        2: "Resilient",
        3: "Sovereign",
        4: "Absolute"
    }
    
    def __init__(self, signing_key: Optional[bytes] = None):
        self.signing_key = signing_key
        self.tests_passed = 0
        self.tests_failed = 0
    
    def generate(self, config: Dict[str, Any], target_level: int = 3) -> Dict[str, Any]:
        """
        Generate sovereignty stamp from deployment configuration.
        
        Args:
            config: Deployment configuration dictionary
            target_level: Minimum required sovereignty level (default: 3)
            
        Returns:
            Sovereignty stamp dictionary
        """
        stamp = {
            "stamp_version": "F0.2026.04",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "target_level": target_level,
            "calculated_level": None,
            "level_name": None,
            "tests": {},
            "warnings": [],
            "signature": None
        }
        
        # Run sovereignty tests
        stamp["tests"]["identity_self_sovereign"] = self._test_identity_root(config)
        stamp["tests"]["local_llm_available"] = self._test_local_llm(config)
        stamp["tests"]["local_storage_available"] = self._test_local_storage(config)
        stamp["tests"]["air_gap_capable"] = self._test_air_gap(config)
        stamp["tests"]["no_vendor_in_core"] = self._test_core_purity()
        stamp["tests"]["f1_f13_inline"] = self._test_constitutional_enforcement(config)
        
        # Calculate level
        level = self._calculate_level(stamp["tests"])
        stamp["calculated_level"] = level
        stamp["level_name"] = self.LEVEL_NAMES.get(level, "Unknown")
        
        # Generate warnings
        if level < target_level:
            stamp["warnings"].append(
                f"CRITICAL: Calculated level ({level}) below target ({target_level}). "
                f"Production deployment requires Level 3 (Sovereign) minimum."
            )
        
        if level < 3:
            stamp["warnings"].append(
                "WARNING: Level < 3 creates vendor dependency. "
                "arifOS constitution may not be enforceable during outages."
            )
        
        # Generate signature
        if BLS_AVAILABLE and self.signing_key:
            stamp["signature"] = self._sign_stamp(stamp)
        
        return stamp
    
    def _test_identity_root(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test if identity is self-sovereign."""
        identity = config.get("identity", {})
        root_type = identity.get("root_type")
        
        result = {
            "passed": root_type == "BLS-DID",
            "detail": f"Identity root: {root_type}",
            "score": 1 if root_type == "BLS-DID" else 0
        }
        
        if result["passed"]:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
            
        return result
    
    def _test_local_llm(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test if local LLM is available."""
        llm_config = config.get("infrastructure", {}).get("llm", {})
        provider_chain = llm_config.get("provider_chain", [])
        
        local_providers = ["Ollama", "llama.cpp", "NIM"]
        has_local = any(
            p.get("provider") in local_providers 
            for p in provider_chain
        )
        
        result = {
            "passed": has_local,
            "detail": f"Local LLM in chain: {has_local}",
            "score": 1 if has_local else 0
        }
        
        if result["passed"]:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
            
        return result
    
    def _test_local_storage(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test if local storage is available."""
        storage_config = config.get("infrastructure", {}).get("storage", {})
        backends = storage_config.get("backends", [])
        
        local_backends = ["SQLite", "Postgres", "local-disk"]
        has_local = any(
            b.get("type") in local_backends 
            for b in backends
        )
        
        result = {
            "passed": has_local,
            "detail": f"Local storage in chain: {has_local}",
            "score": 1 if has_local else 0
        }
        
        if result["passed"]:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
            
        return result
    
    def _test_air_gap(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test if air-gapped operation is possible."""
        llm_config = config.get("infrastructure", {}).get("llm", {})
        air_gap_capable = llm_config.get("air_gapped_capable", False)
        
        result = {
            "passed": air_gap_capable,
            "detail": f"Air-gap capable: {air_gap_capable}",
            "score": 1 if air_gap_capable else 0
        }
        
        if result["passed"]:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
            
        return result
    
    def _test_core_purity(self) -> Dict[str, Any]:
        """Test that core has no vendor imports."""
        forbidden_imports = [
            "azure", "boto3", "google.cloud", "openai", 
            "anthropic", "langchain", "llama_index"
        ]
        
        # Check for forbidden imports in core
        core_path = Path(__file__).parent.parent / "core"
        violations = []
        
        if core_path.exists():
            for py_file in core_path.rglob("*.py"):
                try:
                    content = py_file.read_text()
                    for forbidden in forbidden_imports:
                        if f"import {forbidden}" in content or f"from {forbidden}" in content:
                            violations.append(f"{py_file}: {forbidden}")
                except Exception:
                    continue
        
        result = {
            "passed": len(violations) == 0,
            "detail": f"Vendor imports in core: {len(violations)}",
            "violations": violations[:5],  # Show first 5
            "score": 1 if len(violations) == 0 else 0
        }
        
        if result["passed"]:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
            
        return result
    
    def _test_constitutional_enforcement(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test that F1-F13 enforcement is inline."""
        constitution = config.get("constitution", {})
        enforcement_mode = constitution.get("enforcement_mode", "permissive")
        
        result = {
            "passed": enforcement_mode == "strict",
            "detail": f"Enforcement mode: {enforcement_mode}",
            "score": 1 if enforcement_mode == "strict" else 0
        }
        
        if result["passed"]:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
            
        return result
    
    def _calculate_level(self, tests: Dict[str, Any]) -> int:
        """Calculate sovereignty level from test results."""
        score = sum(t.get("score", 0) for t in tests.values())
        
        # Map score to level
        if score >= 5:
            return 4  # Absolute
        elif score >= 4:
            return 3  # Sovereign
        elif score >= 3:
            return 2  # Resilient
        elif score >= 2:
            return 1  # Portable
        else:
            return 0  # Captive
    
    def _sign_stamp(self, stamp: Dict[str, Any]) -> str:
        """Sign stamp with BLS signature."""
        if not BLS_AVAILABLE or not self.signing_key:
            return None
        
        # Create canonical JSON for signing
        stamp_copy = {k: v for k, v in stamp.items() if k != "signature"}
        message = json.dumps(stamp_copy, sort_keys=True).encode()
        
        # Sign with BLS
        sk = PrivateKey.from_bytes(self.signing_key)
        signature = AugSchemeMPL.sign(sk, message)
        
        return bytes(signature).hex()
    
    def verify(self, stamp: Dict[str, Any], public_key: bytes) -> bool:
        """Verify stamp signature."""
        if not BLS_AVAILABLE:
            return False
        
        signature_hex = stamp.get("signature")
        if not signature_hex:
            return False
        
        stamp_copy = {k: v for k, v in stamp.items() if k != "signature"}
        message = json.dumps(stamp_copy, sort_keys=True).encode()
        
        try:
            pk = G1Element.from_bytes(public_key)
            sig = G2Element.from_bytes(bytes.fromhex(signature_hex))
            return AugSchemeMPL.verify(pk, message, sig)
        except Exception:
            return False


def format_stamp_output(stamp: Dict[str, Any]) -> str:
    """Format stamp for human-readable output."""
    lines = [
        "╔══════════════════════════════════════════════════════════════╗",
        "║              arifOS SOVEREIGNTY STAMP                        ║",
        "╚══════════════════════════════════════════════════════════════╝",
        "",
        f"Stamp Version: {stamp['stamp_version']}",
        f"Generated: {stamp['generated_at']}",
        f"Target Level: {stamp['target_level']} ({SovereigntyStampGenerator.LEVEL_NAMES.get(stamp['target_level'], 'Unknown')})",
        f"Calculated Level: {stamp['calculated_level']} ({stamp['level_name']})",
        "",
        "─────────────────────────────────────────────────────────────",
        "SOVEREIGNTY TESTS",
        "─────────────────────────────────────────────────────────────",
    ]
    
    for test_name, result in stamp["tests"].items():
        status = "✓ PASS" if result["passed"] else "✗ FAIL"
        lines.append(f"{status:8} {test_name:30} {result['detail']}")
    
    if stamp["warnings"]:
        lines.extend([
            "",
            "─────────────────────────────────────────────────────────────",
            "WARNINGS",
            "─────────────────────────────────────────────────────────────",
        ])
        for warning in stamp["warnings"]:
            lines.append(f"⚠ {warning}")
    
    lines.extend([
        "",
        "─────────────────────────────────────────────────────────────",
        "VERIFICATION",
        "─────────────────────────────────────────────────────────────",
    ])
    
    if stamp.get("signature"):
        lines.append(f"Signature: {stamp['signature'][:64]}...")
        lines.append("Status: SIGNED (BLS)")
    else:
        lines.append("Signature: NONE")
        lines.append("Status: UNSIGNED")
    
    lines.extend([
        "",
        f"Overall: {'SOVEREIGN' if stamp['calculated_level'] >= 3 else 'DEPENDENT'}",
        "",
        "DITEMPA BUKAN DIBERI — Forged, Not Given",
    ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate arifOS Sovereignty Stamp",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --config deployment.yaml
  %(prog)s --config deployment.yaml --target-level 4
  %(prog)s --config deployment.yaml --output stamp.json
  %(prog)s --verify stamp.json --public-key key.hex
        """
    )
    
    parser.add_argument(
        "--config", "-c",
        type=Path,
        required=True,
        help="Path to deployment configuration file (YAML or JSON)"
    )
    
    parser.add_argument(
        "--target-level", "-t",
        type=int,
        default=3,
        choices=[0, 1, 2, 3, 4],
        help="Minimum required sovereignty level (default: 3)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output file for stamp (JSON). If not specified, prints to stdout."
    )
    
    parser.add_argument(
        "--signing-key",
        type=Path,
        help="Path to BLS signing key file (for signed stamps)"
    )
    
    parser.add_argument(
        "--verify",
        type=Path,
        help="Verify an existing stamp file"
    )
    
    parser.add_argument(
        "--public-key",
        type=Path,
        help="Public key for verification (required with --verify)"
    )
    
    args = parser.parse_args()
    
    # Load signing key if provided
    signing_key = None
    if args.signing_key:
        if not BLS_AVAILABLE:
            print("ERROR: blspy required for signing", file=sys.stderr)
            sys.exit(3)
        signing_key = args.signing_key.read_bytes()
    
    # Initialize generator
    generator = SovereigntyStampGenerator(signing_key)
    
    # Verify mode
    if args.verify:
        if not args.public_key:
            print("ERROR: --public-key required for verification", file=sys.stderr)
            sys.exit(1)
        
        stamp = json.loads(args.verify.read_text())
        public_key = args.public_key.read_bytes()
        
        if generator.verify(stamp, public_key):
            print("✓ Stamp signature VALID")
            sys.exit(0)
        else:
            print("✗ Stamp signature INVALID")
            sys.exit(3)
    
    # Generation mode
    # Load config
    config_text = args.config.read_text()
    
    if args.config.suffix in ['.yaml', '.yml']:
        import yaml
        config = yaml.safe_load(config_text)
    else:
        config = json.loads(config_text)
    
    # Generate stamp
    stamp = generator.generate(config, args.target_level)
    
    # Format output
    if args.output:
        args.output.write_text(json.dumps(stamp, indent=2))
        print(f"Stamp written to: {args.output}")
    else:
        print(format_stamp_output(stamp))
    
    # Exit with appropriate code
    if stamp["calculated_level"] < args.target_level:
        sys.exit(2)  # Below target level
    
    sys.exit(0)


if __name__ == "__main__":
    main()
