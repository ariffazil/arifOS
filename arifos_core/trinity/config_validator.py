#!/usr/bin/env python3
"""
Constitutional Configuration Validator

Validates agent configurations against Track A/B/C constitutional requirements.
Ensures all agent assignments comply with the 12-floor governance system.

Version: v47.0
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json

# Add arifos_core to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from arifos_core.trinity.agent_loader import AgentLoader, AgentConfig


class ConfigValidationError(Exception):
    """Raised when configuration violates constitutional requirements."""
    pass


class ConfigValidator:
    """
    Validates agent configurations against constitutional law.

    Checks:
    - All required roles are defined
    - Workspace paths exist
    - Identity files exist
    - Floor assignments are valid
    - LLM providers are supported
    - Session isolation constraints
    - Track A/B/C alignment
    """

    # Constitutional requirements
    REQUIRED_ROLES = ["architect", "engineer", "auditor", "validator"]
    VALID_FLOORS = [f"F{i}" for i in range(1, 13)]
    VALID_PROVIDERS = ["anthropic", "google", "openai", "moonshot"]

    # Floor requirements per role (constitutional law)
    ROLE_FLOOR_REQUIREMENTS = {
        "architect": {
            "required": ["F4", "F7"],  # Clarity, Humility
            "description": "Architect requires F4 (Clarity) and F7 (Humility)"
        },
        "engineer": {
            "required": ["F1", "F2", "F5"],  # Amanah, Truth, Peace²
            "description": "Engineer requires F1 (Amanah), F2 (Truth), F5 (Peace²)"
        },
        "auditor": {
            "required": ["F8"],  # Tri-Witness
            "description": "Auditor requires F8 (Tri-Witness)"
        },
        "validator": {
            "required": list(VALID_FLOORS),  # All floors
            "description": "Validator requires all 12 floors"
        }
    }

    def __init__(self, config_path: str = "config/agents.yaml"):
        """
        Initialize validator.

        Args:
            config_path: Path to agent configuration file
        """
        self.config_path = Path(config_path)
        self.loader = None
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """
        Run full validation suite.

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []

        # Check config file exists
        if not self.config_path.exists():
            self.errors.append(f"Configuration file not found: {self.config_path}")
            return False, self.errors, self.warnings

        # Load configuration
        try:
            self.loader = AgentLoader(str(self.config_path))
        except Exception as e:
            self.errors.append(f"Failed to load configuration: {e}")
            return False, self.errors, self.warnings

        # Run validation checks
        self._validate_required_roles()
        self._validate_role_configurations()
        self._validate_floor_assignments()
        self._validate_workspaces()
        self._validate_identity_files()
        self._validate_llm_providers()
        self._validate_session_isolation()

        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings

    def _validate_required_roles(self):
        """Check all required roles are defined."""
        configured_roles = set(self.loader.config.get("agents", {}).keys())
        missing_roles = set(self.REQUIRED_ROLES) - configured_roles

        if missing_roles:
            self.errors.append(
                f"Missing required roles: {', '.join(sorted(missing_roles))}"
            )

    def _validate_role_configurations(self):
        """Validate each role's configuration."""
        for role in self.REQUIRED_ROLES:
            try:
                config = self.loader.get_agent_config(role)

                # Check required fields
                if not config.role:
                    self.errors.append(f"Role '{role}' missing 'role' field")
                if not config.llm_provider:
                    self.errors.append(f"Role '{role}' missing 'llm_provider' field")
                if not config.llm_model:
                    self.errors.append(f"Role '{role}' missing 'llm_model' field")
                if not config.workspace:
                    self.errors.append(f"Role '{role}' missing 'workspace' field")
                if not config.identity_file:
                    self.errors.append(f"Role '{role}' missing 'identity_file' field")

            except KeyError:
                # Already caught by _validate_required_roles
                pass
            except Exception as e:
                self.errors.append(f"Error validating role '{role}': {e}")

    def _validate_floor_assignments(self):
        """Validate floor assignments match constitutional requirements."""
        for role in self.REQUIRED_ROLES:
            try:
                config = self.loader.get_agent_config(role)
                assigned_floors = set(config.floors)

                # Get constitutional requirements
                requirements = self.ROLE_FLOOR_REQUIREMENTS.get(role)
                if not requirements:
                    self.warnings.append(
                        f"No floor requirements defined for role '{role}'"
                    )
                    continue

                required_floors = set(requirements["required"])
                missing_floors = required_floors - assigned_floors

                if missing_floors:
                    self.errors.append(
                        f"Role '{role}' missing required floors: "
                        f"{', '.join(sorted(missing_floors))}. "
                        f"{requirements['description']}"
                    )

                # Check for invalid floors
                invalid_floors = assigned_floors - set(self.VALID_FLOORS)
                if invalid_floors:
                    self.errors.append(
                        f"Role '{role}' has invalid floors: "
                        f"{', '.join(sorted(invalid_floors))}"
                    )

            except KeyError:
                pass  # Already caught
            except Exception as e:
                self.errors.append(
                    f"Error validating floors for role '{role}': {e}"
                )

    def _validate_workspaces(self):
        """Check workspace directories exist."""
        for role in self.REQUIRED_ROLES:
            try:
                config = self.loader.get_agent_config(role)

                if not config.workspace.exists():
                    self.warnings.append(
                        f"Workspace directory not found for role '{role}': "
                        f"{config.workspace}"
                    )

                if config.workspace_alt and not config.workspace_alt.exists():
                    self.warnings.append(
                        f"Alternative workspace not found for role '{role}': "
                        f"{config.workspace_alt}"
                    )

            except KeyError:
                pass
            except Exception as e:
                self.errors.append(
                    f"Error validating workspace for role '{role}': {e}"
                )

    def _validate_identity_files(self):
        """Check identity files exist and are readable."""
        for role in self.REQUIRED_ROLES:
            try:
                config = self.loader.get_agent_config(role)

                if not config.identity_file.exists():
                    self.errors.append(
                        f"Identity file not found for role '{role}': "
                        f"{config.identity_file}"
                    )
                    continue

                # Try to load identity
                try:
                    identity = self.loader.load_identity(role)
                    if not identity or len(identity.strip()) == 0:
                        self.warnings.append(
                            f"Identity file is empty for role '{role}': "
                            f"{config.identity_file}"
                        )
                except Exception as e:
                    self.errors.append(
                        f"Cannot read identity file for role '{role}': {e}"
                    )

            except KeyError:
                pass
            except Exception as e:
                self.errors.append(
                    f"Error validating identity for role '{role}': {e}"
                )

    def _validate_llm_providers(self):
        """Validate LLM provider configurations."""
        for role in self.REQUIRED_ROLES:
            try:
                config = self.loader.get_agent_config(role)

                # Check provider is valid
                if config.llm_provider not in self.VALID_PROVIDERS:
                    self.errors.append(
                        f"Role '{role}' has invalid LLM provider: "
                        f"'{config.llm_provider}'. Valid providers: "
                        f"{', '.join(self.VALID_PROVIDERS)}"
                    )

                # Check API key environment variable
                if config.api_key_env:
                    import os
                    if not os.getenv(config.api_key_env):
                        self.warnings.append(
                            f"Environment variable '{config.api_key_env}' "
                            f"not set for role '{role}'"
                        )

            except KeyError:
                pass
            except Exception as e:
                self.errors.append(
                    f"Error validating LLM provider for role '{role}': {e}"
                )

    def _validate_session_isolation(self):
        """Check session isolation constraints."""
        # Build LLM usage map
        llm_map: Dict[str, List[str]] = {}

        for role in self.REQUIRED_ROLES:
            try:
                config = self.loader.get_agent_config(role)
                llm_key = f"{config.llm_provider}/{config.llm_model}"

                if llm_key not in llm_map:
                    llm_map[llm_key] = []
                llm_map[llm_key].append(role)

            except KeyError:
                pass

        # Check for same LLM assigned to multiple roles
        for llm_key, roles in llm_map.items():
            if len(roles) > 1:
                self.warnings.append(
                    f"Same LLM '{llm_key}' assigned to multiple roles: "
                    f"{', '.join(roles)}. Session isolation will prevent "
                    f"simultaneous use."
                )

    def generate_report(self) -> str:
        """
        Generate human-readable validation report.

        Returns:
            Formatted validation report
        """
        lines = []
        lines.append("=" * 80)
        lines.append("Agent Configuration Validation Report")
        lines.append("=" * 80)
        lines.append("")

        # Summary
        if len(self.errors) == 0 and len(self.warnings) == 0:
            lines.append("[OK] Configuration is valid")
            lines.append("")
        else:
            if self.errors:
                lines.append(f"[FAIL] {len(self.errors)} error(s) found")
            if self.warnings:
                lines.append(f"[WARN] {len(self.warnings)} warning(s) found")
            lines.append("")

        # Errors
        if self.errors:
            lines.append("Errors:")
            lines.append("-" * 80)
            for i, error in enumerate(self.errors, 1):
                lines.append(f"{i}. {error}")
            lines.append("")

        # Warnings
        if self.warnings:
            lines.append("Warnings:")
            lines.append("-" * 80)
            for i, warning in enumerate(self.warnings, 1):
                lines.append(f"{i}. {warning}")
            lines.append("")

        # Configuration summary
        if self.loader:
            lines.append("Configuration Summary:")
            lines.append("-" * 80)
            for role in self.REQUIRED_ROLES:
                try:
                    config = self.loader.get_agent_config(role)
                    lines.append(f"  {role.upper()}:")
                    lines.append(f"    LLM: {config.llm_provider}/{config.llm_model}")
                    lines.append(f"    Workspace: {config.workspace}")
                    lines.append(f"    Identity: {config.identity_file}")
                    lines.append(f"    Floors: {', '.join(config.floors)}")
                    lines.append("")
                except KeyError:
                    lines.append(f"  {role.upper()}: NOT CONFIGURED")
                    lines.append("")

        lines.append("=" * 80)
        return "\n".join(lines)


def main():
    """Command-line entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate agent configuration against constitutional requirements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m arifos_core.trinity.config_validator
  python -m arifos_core.trinity.config_validator --config custom/agents.yaml
  python -m arifos_core.trinity.config_validator --json

Constitutional Context:
  This validator ensures all agent configurations comply with the 12-floor
  constitutional governance system. It checks:

  - Required roles are defined (Architect, Engineer, Auditor, Validator)
  - Floor assignments match constitutional requirements
  - Workspace and identity files exist
  - LLM providers are valid
  - Session isolation constraints are documented

  Exit codes:
    0 - Configuration is valid
    1 - Validation errors found
    2 - Validation warnings only
        """
    )

    parser.add_argument(
        '--config',
        default='config/agents.yaml',
        help='Path to agent configuration file (default: config/agents.yaml)'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )

    args = parser.parse_args()

    # Run validation
    validator = ConfigValidator(config_path=args.config)
    is_valid, errors, warnings = validator.validate()

    # Output results
    if args.json:
        result = {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "config_path": str(validator.config_path)
        }
        print(json.dumps(result, indent=2))
    else:
        report = validator.generate_report()
        print(report)

    # Exit with appropriate code
    if errors:
        return 1
    elif warnings:
        return 2
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
