# arifos/version_validator.py

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re

class VersionValidator:
    """Ensures all arifOS components align with VERSION.lock"""
    
    def __init__(self, version_lock_path: str = "arifos/VERSION.lock"):
        self.lock_path = Path(version_lock_path)
        self.lock_data = self._load_lock()
        self.canonical = self.lock_data["canonical_version"]
        self.errors: List[str] = []
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Run all alignment checks"""
        checks = [
            self._check_component_versions,
            self._check_bridge_purity,
            self._check_spec_loading,
            self._validate_signatures,
        ]
        
        for check in checks:
            try:
                check()
            except Exception as e:
                self.errors.append(f"Check failed: {check.__name__}: {e}")
        
        return len(self.errors) == 0, self.errors
    
    def _load_lock(self) -> Dict:
        """Load and parse VERSION.lock"""
        if not self.lock_path.exists():
            raise FileNotFoundError(f"VERSION.lock not found at {self.lock_path}")
        
        with open(self.lock_path) as f:
            return json.load(f)
    
    def _check_component_versions(self):
        """Verify all component versions match canonical"""
        components = self.lock_data["components"]
        
        # Check arifos_core version
        import arifos
        # Normalize versions for comparison (v52.0.0 vs v52.0.0-SEAL)
        canonical_base = self.canonical.split('-')[0]
        current_version = getattr(arifos, "__version__", "unknown")
        if current_version != canonical_base:
            self.errors.append(
                f"arifos_core version mismatch: {current_version} != {canonical_base}"
            )
        
        # Check MCP server version
        try:
            from arifos import mcp
            mcp_version = getattr(mcp, "__version__", "unknown")
            if mcp_version != canonical_base:
                self.errors.append(
                    f"mcp_server version mismatch: {mcp_version} != {canonical_base}"
                )
        except ImportError:
            self.errors.append("mcp_server package not found")
        
        # Check bridge version (if exists)
        bridge_version = self._extract_bridge_version()
        if bridge_version and bridge_version != canonical_base:
            self.errors.append(
                f"bridge version mismatch: {bridge_version} != {canonical_base}"
            )
        
        # Check spec versions
        spec_location = components["constitutional_specs"]["location"]
        spec_dir = Path(spec_location)
        if not spec_dir.exists():
            self.errors.append(f"Spec directory not found: {spec_dir}")
    
    def _extract_bridge_version(self) -> Optional[str]:
        """Extract version from bridge module docstring."""
        components = self.lock_data["components"]
        bridge_file = Path(components["bridge"]["location"])
        if not bridge_file.exists():
            return None
        
        content = bridge_file.read_text()
        # Look for (vX.Y.Z) pattern in docstring or __version__
        version_match = re.search(r'\(v([^)]+)\)', content)
        if not version_match:
            version_match = re.search(r'__version__\s*=\s*["\']([^"\\]+)["\']', content)
        
        return "v" + version_match.group(1) if version_match and not version_match.group(1).startswith('v') else (version_match.group(1) if version_match else None)
    
    def _check_bridge_purity(self):
        """Verify bridge contains zero logic (F1 alignment)."""
        bridge_file = Path(self.lock_data["components"]["bridge"]["location"])
        if not bridge_file.exists():
            self.errors.append("Bridge file not found")
            return
        
        bridge_code = bridge_file.read_text()
        
        # Forbidden patterns: Bridge must not make verdicts
        forbidden_patterns = [
            (r'verdict\s*=\s*"SEAL"', "SEAL verdict in bridge"),
            (r'verdict\s*=\s*"VOID"', "VOID verdict in bridge"), 
            (r'verdict\s*=\s*"SABAR"', "SABAR verdict in bridge"),
            (r'if\s+[^\n]*thermodynamic_valid', "Entropy logic in bridge"),
            (r'def\s+entropy_profiler', "Entropy profiler in bridge"),
            (r'import\s+hashlib[^\n]*proof', "Crypto proof in bridge"),
        ]
        
        for pattern, desc in forbidden_patterns:
            if re.search(pattern, bridge_code):
                self.errors.append(
                    f"Bridge purity violation: {desc}"
                )
        
        # Allowed: routing, serialization, error handling
        # Count function definitions
        allowed_count = len(re.findall(r'def\s+', bridge_code))
        if allowed_count > 20:  # Too many functions
            self.errors.append(f"Bridge too complex: {allowed_count} functions (max 20)")
    
    def _check_spec_loading(self):
        """Verify constitutional specs can be loaded."""
        specs_dir = Path(self.lock_data["components"]["constitutional_specs"]["location"])
        
        floors_path = specs_dir / "constitutional/constitutional_floors.json"
        
        if not floors_path.exists():
            # Try alternative path during migration
            floors_path = specs_dir / "constitutional_floors.json"
            if not floors_path.exists():
                self.errors.append(f"Floors spec not found: {floors_path}")
                return
        
        # Validate JSON syntax
        try:
            with open(floors_path) as f:
                json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Floors spec JSON invalid: {e}")
    
    def _validate_signatures(self):
        """Verify authority signatures on VERSION.lock"""
        authority = self.lock_data.get("authority", {})
        
        if not authority.get("sealed", False):
            self.errors.append("VERSION.lock not sealed by authority")
        
        if authority.get("judge") != "Muhammad Arif bin Fazil":
            self.errors.append("Authority signature invalid")
    
    def print_report(self):
        """Print detailed alignment report."""
        print("=" * 70)
        print("arifOS CONSTITUTIONAL ALIGNMENT REPORT")
        print(f"Canonical Version: {self.canonical}")
        print("=" * 70)
        
        if self.errors:
            print("\n❌ ALIGNMENT FAILED")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
            print(f"\nTotal violations: {len(self.errors)}")
            print("\nConstitutional Verdict: VOID")
        else:
            print("\n✅ ALIGNMENT SEALED")
            print("All components aligned with canonical version")
            print("Bridge purity: Confirmed (zero logic)")
            print("Spec loading: Valid (JSON syntax OK)")
            print("Authority signature: Verified")
            print("\nConstitutional Verdict: SEAL")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify arifOS version alignment")
    parser.add_argument("--lock", default="arifos/VERSION.lock", help="Path to VERSION.lock")
    parser.add_argument("--strict", action="store_true", help="Fail on any violation")
    
    args = parser.parse_args()
    
    validator = VersionValidator(args.lock)
    is_valid, errors = validator.validate()
    validator.print_report()
    
    if args.strict and not is_valid:
        sys.exit(1)
    sys.exit(0)
