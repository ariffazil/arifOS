"""
Agent Loader - Model-Agnostic Role Assignment System

Loads LLM agents based on config/agents.yaml configuration.
Enforces separation of powers through session isolation.

Version: v47.0
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class AgentRole(Enum):
    """Constitutional agent roles (immutable)."""
    ARCHITECT = "architect"
    ENGINEER = "engineer"
    AUDITOR = "auditor"
    VALIDATOR = "validator"


@dataclass
class AgentConfig:
    """Configuration for a single agent role."""

    # Role identity (immutable - L1 Canon)
    role: str
    symbol: str
    job: str

    # LLM assignment (mutable - Technology)
    llm_provider: str
    llm_model: str
    api_key_env: str

    # Workspace mapping
    workspace: Path

    # Identity files
    identity_file: Path

    # Constitutional assignment (immutable - L1 Canon)
    floors: List[str]
    pipeline_stages: List[int]
    geometry: str

    # Responsibilities
    responsibilities: List[str]
    forbidden: List[str]

    # Optional fields (must come after required fields)
    workspace_alt: Optional[Path] = None
    identity_detailed: Optional[Path] = None
    boundaries_file: Optional[Path] = None

    def __post_init__(self):
        """Convert string paths to Path objects."""
        if isinstance(self.workspace, str):
            self.workspace = Path(self.workspace)
        if self.workspace_alt and isinstance(self.workspace_alt, str):
            self.workspace_alt = Path(self.workspace_alt)
        if isinstance(self.identity_file, str):
            self.identity_file = Path(self.identity_file)
        if self.identity_detailed and isinstance(self.identity_detailed, str):
            self.identity_detailed = Path(self.identity_detailed)
        if self.boundaries_file and isinstance(self.boundaries_file, str):
            self.boundaries_file = Path(self.boundaries_file)


class AgentLoader:
    """Load and manage model-agnostic agents."""

    def __init__(self, config_path: str = "config/agents.yaml"):
        """
        Initialize agent loader.

        Args:
            config_path: Path to agents configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.repo_root = self._find_repo_root()

    def _find_repo_root(self) -> Path:
        """Find repository root directory."""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists() or (current / "AGENTS.md").exists():
                return current
            current = current.parent
        return Path.cwd()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load agent configuration from YAML.

        Returns:
            Parsed configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config is invalid
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Agent config not found: {self.config_path}\n"
                f"Expected location: {self.config_path.absolute()}\n"
                f"Run: python scripts/setup_agent_config.py"
            )

        try:
            with open(self.config_path) as f:
                config = yaml.safe_load(f)

            if not config:
                raise ValueError("Config file is empty")

            if "agents" not in config:
                raise ValueError("Config missing 'agents' section")

            return config

        except yaml.YAMLError as e:
            raise yaml.YAMLError(
                f"Invalid YAML in {self.config_path}: {e}"
            )

    def get_agent_config(self, role: str) -> AgentConfig:
        """
        Get configuration for an agent role.

        Args:
            role: Agent role name ('architect', 'engineer', 'auditor', 'validator')

        Returns:
            AgentConfig with all settings for that role

        Raises:
            ValueError: If role is unknown or config is invalid
        """
        agents = self.config["agents"]

        if role not in agents:
            available = list(agents.keys())
            raise ValueError(
                f"Unknown role: '{role}'\n"
                f"Available roles: {available}\n"
                f"Check config/agents.yaml"
            )

        agent = agents[role]

        try:
            return AgentConfig(
                role=agent["role"],
                symbol=agent["symbol"],
                job=agent["job"],
                llm_provider=agent["llm"]["provider"],
                llm_model=agent["llm"]["model"],
                api_key_env=agent["llm"]["api_key_env"],
                workspace=agent["workspace"],
                workspace_alt=agent.get("workspace_alt"),
                identity_file=agent["identity_file"],
                identity_detailed=agent.get("identity_detailed"),
                boundaries_file=agent.get("boundaries_file"),
                floors=agent["floors"],
                pipeline_stages=agent["pipeline_stages"],
                geometry=agent["geometry"],
                responsibilities=agent["responsibilities"],
                forbidden=agent["forbidden"]
            )
        except KeyError as e:
            raise ValueError(
                f"Invalid config for role '{role}': missing field {e}\n"
                f"Check config/agents.yaml structure"
            )

    def load_identity(self, role: str) -> str:
        """
        Load identity file content for a role.

        Args:
            role: Agent role name

        Returns:
            Identity file content as string

        Raises:
            FileNotFoundError: If identity file doesn't exist
        """
        config = self.get_agent_config(role)
        identity_path = self.repo_root / config.identity_file

        if not identity_path.exists():
            raise FileNotFoundError(
                f"Identity file not found: {identity_path}\n"
                f"Role: {role}\n"
                f"Expected: {config.identity_file}\n"
                f"Run: python scripts/setup_agent_config.py"
            )

        with open(identity_path, encoding='utf-8') as f:
            return f.read()

    def get_api_key(self, role: str) -> str:
        """
        Get API key for agent's LLM provider.

        Args:
            role: Agent role name

        Returns:
            API key from environment

        Raises:
            EnvironmentError: If API key not set
        """
        config = self.get_agent_config(role)
        api_key = os.getenv(config.api_key_env)

        if not api_key:
            raise EnvironmentError(
                f"API key not set: {config.api_key_env}\n"
                f"Required for: {config.role} ({config.llm_provider}/{config.llm_model})\n"
                f"Set with: export {config.api_key_env}=your_key_here\n"
                f"Or add to .env file"
            )

        return api_key

    def validate_workspace(self, role: str) -> bool:
        """
        Validate that workspace directory exists.

        Args:
            role: Agent role name

        Returns:
            True if workspace exists

        Raises:
            FileNotFoundError: If workspace doesn't exist
        """
        config = self.get_agent_config(role)
        workspace_path = self.repo_root / config.workspace

        if not workspace_path.exists():
            raise FileNotFoundError(
                f"Workspace not found: {workspace_path}\n"
                f"Role: {role}\n"
                f"Expected: {config.workspace}\n"
                f"Create with: mkdir -p {workspace_path}"
            )

        return True

    def list_available_roles(self) -> List[str]:
        """
        List all available agent roles in config.

        Returns:
            List of role names
        """
        return list(self.config["agents"].keys())

    def get_session_config(self) -> Dict[str, Any]:
        """
        Get session isolation configuration.

        Returns:
            Session isolation settings
        """
        return self.config.get("session_isolation", {
            "enforce_separation": True,
            "max_concurrent_sessions": 4,
            "session_timeout": 3600,
            "memory_isolation": True,
            "prevent_cross_role_access": True
        })

    def get_governance_config(self) -> Dict[str, Any]:
        """
        Get constitutional governance configuration.

        Returns:
            Governance settings
        """
        return self.config.get("governance", {
            "require_checkpoint": True,
            "enforce_handoff_protocol": True,
            "audit_trail": True,
            "validate_track_alignment": True,
            "enforce_floors": True
        })

    def validate_all_agents(self) -> Dict[str, bool]:
        """
        Validate configuration for all agents.

        Returns:
            Dictionary mapping role names to validation status
        """
        results = {}

        for role in self.list_available_roles():
            try:
                # Validate config structure
                config = self.get_agent_config(role)

                # Check workspace exists
                self.validate_workspace(role)

                # Check identity file exists
                identity_path = self.repo_root / config.identity_file
                if not identity_path.exists():
                    results[role] = False
                    continue

                # Check API key is set
                try:
                    self.get_api_key(role)
                except EnvironmentError:
                    # API key not set is a warning, not a failure
                    # (agent can still be configured, just not usable yet)
                    pass

                results[role] = True

            except Exception:
                results[role] = False

        return results

    def get_agent_summary(self, role: str) -> str:
        """
        Get human-readable summary of agent configuration.

        Args:
            role: Agent role name

        Returns:
            Formatted summary string
        """
        config = self.get_agent_config(role)

        return f"""
Agent: {config.role} ({config.symbol})
Job: {config.job}
LLM: {config.llm_provider}/{config.llm_model}
Workspace: {config.workspace}
Identity: {config.identity_file}
Floors: {', '.join(config.floors)}
Stages: {', '.join(str(s) for s in config.pipeline_stages)}
Geometry: {config.geometry}
""".strip()

    def __repr__(self) -> str:
        """String representation of loader."""
        roles = self.list_available_roles()
        return f"AgentLoader(config={self.config_path}, roles={roles})"


# =============================================================================
# LLM Client Factory (Optional - for future integration)
# =============================================================================

class LLMClientFactory:
    """
    Factory for creating LLM client instances.

    Note: This is a placeholder for future integration.
    Actual LLM client creation depends on provider SDKs.
    """

    @staticmethod
    def create_client(provider: str, model: str, api_key: str):
        """
        Create LLM client for specified provider.

        Args:
            provider: Provider name (anthropic, google, openai, moonshot)
            model: Model name
            api_key: API key for authentication

        Returns:
            LLM client instance (implementation-specific)

        Raises:
            ValueError: If provider is unsupported
        """
        if provider == "anthropic":
            return LLMClientFactory._create_anthropic_client(model, api_key)
        elif provider == "google":
            return LLMClientFactory._create_google_client(model, api_key)
        elif provider == "openai":
            return LLMClientFactory._create_openai_client(model, api_key)
        elif provider == "moonshot":
            return LLMClientFactory._create_moonshot_client(model, api_key)
        else:
            raise ValueError(
                f"Unsupported provider: {provider}\n"
                f"Supported: anthropic, google, openai, moonshot"
            )

    @staticmethod
    def _create_anthropic_client(model: str, api_key: str):
        """Create Anthropic (Claude) client."""
        try:
            from anthropic import Anthropic
            return Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError(
                "Anthropic SDK not installed.\n"
                "Install with: pip install anthropic"
            )

    @staticmethod
    def _create_google_client(model: str, api_key: str):
        """Create Google (Gemini) client."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            return genai.GenerativeModel(model)
        except ImportError:
            raise ImportError(
                "Google Generative AI SDK not installed.\n"
                "Install with: pip install google-generativeai"
            )

    @staticmethod
    def _create_openai_client(model: str, api_key: str):
        """Create OpenAI client."""
        try:
            from openai import OpenAI
            return OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError(
                "OpenAI SDK not installed.\n"
                "Install with: pip install openai"
            )

    @staticmethod
    def _create_moonshot_client(model: str, api_key: str):
        """Create Moonshot (Kimi) client (OpenAI-compatible API)."""
        try:
            from openai import OpenAI
            return OpenAI(
                api_key=api_key,
                base_url="https://api.moonshot.cn/v1"
            )
        except ImportError:
            raise ImportError(
                "OpenAI SDK required for Moonshot.\n"
                "Install with: pip install openai"
            )


# =============================================================================
# Standalone Usage Examples
# =============================================================================

if __name__ == "__main__":
    """
    Standalone usage examples for testing agent loader.
    """

    print("=" * 80)
    print("Agent Loader - Model-Agnostic System v47.0")
    print("=" * 80)
    print()

    try:
        # Initialize loader
        loader = AgentLoader()
        print(f"[OK] Loaded config: {loader.config_path}")
        print(f"[OK] Repository root: {loader.repo_root}")
        print()

        # List available roles
        roles = loader.list_available_roles()
        print(f"Available roles: {roles}")
        print()

        # Validate all agents
        print("Validating agent configurations...")
        validation_results = loader.validate_all_agents()

        for role, valid in validation_results.items():
            status = "[OK] VALID" if valid else "[FAIL] INVALID"
            print(f"  {role}: {status}")
        print()

        # Show detailed config for each role
        for role in roles:
            try:
                print("-" * 80)
                summary = loader.get_agent_summary(role)
                print(summary)
                print()

                # Try to load identity
                try:
                    identity = loader.load_identity(role)
                    print(f"Identity file: {len(identity)} characters")
                except FileNotFoundError as e:
                    print(f"[WARN] Identity file not found: {e}")

                # Check API key
                try:
                    loader.get_api_key(role)
                    print(f"[OK] API key set")
                except EnvironmentError:
                    config = loader.get_agent_config(role)
                    print(f"[WARN] API key not set: {config.api_key_env}")

                print()

            except Exception as e:
                print(f"[FAIL] Error loading {role}: {e}")
                print()

        print("=" * 80)
        print("Session Isolation Config:")
        print(loader.get_session_config())
        print()

        print("Governance Config:")
        print(loader.get_governance_config())
        print("=" * 80)

    except Exception as e:
        print(f"[FAIL] Fatal error: {e}")
        import traceback
        traceback.print_exc()
