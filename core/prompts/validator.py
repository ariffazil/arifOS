"""
arifOS Production Prompt Validator

Validates that prompts and outputs conform to Horizon II production standards.

Usage:
    python validator.py --prompt salam_000_init --output-file output.json
    python validator.py --list
    python validator.py --export

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from production_pack import (
    PRODUCTION_PROMPTS,
    get_prompt,
    list_prompts,
    export_all,
    validate_output,
    CONSTITUTIONAL_GUARD,
    OMEGA_BAND,
)


def validate_prompt_structure(prompt_name: str) -> tuple[bool, list[str]]:
    """
    Validate that a prompt meets production standards.
    
    Checks:
    - Has constitutional guard
    - Declares Ω0 band
    - Has structured fields (not narrative)
    - Has explicit floor activation
    """
    prompt = get_prompt(prompt_name)
    if not prompt:
        return False, [f"Unknown prompt: {prompt_name}"]
    
    issues = []
    
    # Check 1: Constitutional Guard present (check template has placeholder)
    if "{constitutional_guard}" not in prompt.template:
        issues.append("Missing CONSTITUTIONAL GUARD placeholder")
    
    # Check 2: Ω0 band declared
    if "Ω0" not in prompt.template and "omega_band" not in prompt.template:
        issues.append("Missing Ω0 uncertainty band declaration")
    
    # Check 3: Has output fields defined
    if not prompt.required_output_fields:
        issues.append("No required_output_fields defined")
    
    # Check 4: Has floors activated
    if not prompt.floors_activated:
        issues.append("No floors_activated defined")
    
    # Check 5: No natural language identity claims (F10 check)
    forbidden_phrases = [
        "I am conscious",
        "I feel",
        "I believe",
        "my soul",
        "I experience",
    ]
    template_lower = prompt.template.lower()
    for phrase in forbidden_phrases:
        if phrase in template_lower:
            issues.append(f"F10 violation: contains '{phrase}'")
    
    # Check 6: Has structured format (indicated by field definitions)
    if "-" not in prompt.template and ":" not in prompt.template:
        issues.append("Lacks structured format (bullets/fields)")
    
    return len(issues) == 0, issues


def validate_output_completeness(output: dict, prompt_name: str) -> tuple[bool, list[str]]:
    """Validate output against prompt requirements."""
    return validate_output(output, prompt_name)


def generate_report(prompt_name: str | None = None) -> dict:
    """Generate validation report for all or specific prompt."""
    if prompt_name:
        valid, issues = validate_prompt_structure(prompt_name)
        return {
            "prompt": prompt_name,
            "valid": valid,
            "issues": issues,
            "standards_checked": [
                "constitutional_guard_present",
                "omega_band_declared",
                "output_fields_defined",
                "floors_activated",
                "f10_ontology_compliant",
                "structured_format",
            ]
        }
    
    # Report for all prompts
    results = {}
    all_valid = True
    
    for name in list_prompts():
        valid, issues = validate_prompt_structure(name)
        results[name] = {
            "valid": valid,
            "issues": issues,
        }
        if not valid:
            all_valid = False
    
    return {
        "all_valid": all_valid,
        "prompts_checked": len(results),
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="arifOS Production Prompt Validator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list
  %(prog)s --prompt salam_000_init
  %(prog)s --prompt agi_333_reason --output-file output.json
  %(prog)s --export --format json
        """
    )
    
    parser.add_argument("--list", action="store_true", help="List all production prompts")
    parser.add_argument("--prompt", type=str, help="Validate specific prompt")
    parser.add_argument("--output-file", type=str, help="JSON file to validate against prompt")
    parser.add_argument("--export", action="store_true", help="Export all prompts")
    parser.add_argument("--format", choices=["json", "markdown"], default="json", help="Export format")
    parser.add_argument("--check-all", action="store_true", help="Validate all prompts")
    
    args = parser.parse_args()
    
    if args.list:
        print("═" * 60)
        print("arifOS Production Prompts (000–999 Hardened)")
        print("═" * 60)
        for name in list_prompts():
            prompt = get_prompt(name)
            print(f"\n{name}")
            print(f"  Stage: {prompt.stage}")
            print(f"  Mode:  {prompt.mode}")
            print(f"  Floors: {', '.join(prompt.floors_activated)}")
        return 0
    
    if args.export:
        if args.format == "json":
            print(export_all())
        else:
            # Markdown format
            print("# arifOS Production Prompt Pack v1.0\n")
            for name in list_prompts():
                prompt = get_prompt(name)
                print(f"## {name}\n")
                print(f"**Stage:** {prompt.stage}  ")
                print(f"**Mode:** {prompt.mode}  ")
                print(f"**Floors:** {', '.join(prompt.floors_activated)}  \n")
                print("```")
                print(prompt.template)
                print("```\n")
                print("**Required Output Fields:**")
                for field in prompt.required_output_fields:
                    print(f"- {field}")
                print()
        return 0
    
    if args.check_all:
        report = generate_report()
        print(json.dumps(report, indent=2))
        return 0 if report["all_valid"] else 1
    
    if args.prompt:
        report = generate_report(args.prompt)
        
        if args.output_file:
            # Validate output file against prompt
            try:
                with open(args.output_file, 'r') as f:
                    output = json.load(f)
                output_valid, missing = validate_output_completeness(output, args.prompt)
                report["output_valid"] = output_valid
                report["output_issues"] = missing
            except FileNotFoundError:
                report["output_valid"] = False
                report["output_issues"] = [f"File not found: {args.output_file}"]
            except json.JSONDecodeError as e:
                report["output_valid"] = False
                report["output_issues"] = [f"Invalid JSON: {e}"]
        
        print(json.dumps(report, indent=2))
        return 0 if report["valid"] else 1
    
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
