"""arifOS Skills - 9 Constitutionally-Governed Capabilities"""

import importlib


# Import skills using importlib to handle hyphenated names
def _load_skill(name):
    try:
        return importlib.import_module(f'skills.{name}')
    except ImportError as e:
        print(f"Warning: Could not load skill {name}: {e}")
        return None

# Load all 9 skills
_vps = _load_skill('vps-docker')
_research = _load_skill('deep-research')
_git = _load_skill('git-ops')
_security = _load_skill('security-audit')
_memory = _load_skill('memory-query')
_refactor = _load_skill('code-refactor')
_deploy = _load_skill('deployment')
_recovery = _load_skill('recovery')
_check = _load_skill('constitutional-check')

# Skill Registry
SKILL_REGISTRY = {}

if _vps:
    SKILL_REGISTRY['vps-docker'] = {
        'skill': _vps.VPSDockerSkill,
        'execute': _vps.execute,
        'floor': 'F1',
        'description': 'VPS/Docker with reversibility',
    }

if _research:
    SKILL_REGISTRY['deep-research'] = {
        'skill': _research.DeepResearchSkill,
        'execute': _research.execute,
        'floor': 'F2',
        'description': 'Multi-source research with verification',
    }

if _git:
    SKILL_REGISTRY['git-ops'] = {
        'skill': _git.GitOpsSkill,
        'execute': _git.execute,
        'floor': 'F1',
        'description': 'Git operations with worktree sandbox',
    }

if _security:
    SKILL_REGISTRY['security-audit'] = {
        'skill': _security.SecurityAuditSkill,
        'execute': _security.execute,
        'floor': 'F12',
        'description': 'F12 injection defense',
    }

if _memory:
    SKILL_REGISTRY['memory-query'] = {
        'skill': _memory.MemoryQuerySkill,
        'execute': _memory.execute,
        'floor': 'F555',
        'description': 'Vector memory with freshness',
    }

if _refactor:
    SKILL_REGISTRY['code-refactor'] = {
        'skill': _refactor.CodeRefactorSkill,
        'execute': _refactor.execute,
        'floor': 'F8',
        'description': 'F8 wisdom-guided refactoring',
    }

if _deploy:
    SKILL_REGISTRY['deployment'] = {
        'skill': _deploy.DeploymentSkill,
        'execute': _deploy.execute,
        'floor': 'F11',
        'description': 'F11 authority-gated deployment',
    }

if _recovery:
    SKILL_REGISTRY['recovery'] = {
        'skill': _recovery.RecoverySkill,
        'execute': _recovery.execute,
        'floor': 'F5',
        'description': 'F5 stability-guaranteed recovery',
    }

if _check:
    SKILL_REGISTRY['constitutional-check'] = {
        'skill': _check.ConstitutionalCheckSkill,
        'execute': _check.execute,
        'floor': 'F3',
        'description': 'F3 Tri-Witness evaluation',
    }


def get_skill(name: str):
    """Get skill by name."""
    return SKILL_REGISTRY.get(name)


def list_skills():
    """List all available skills."""
    return {name: info['description'] for name, info in SKILL_REGISTRY.items()}


# Export classes if available
VPSDockerSkill = _vps.VPSDockerSkill if _vps else None
DeepResearchSkill = _research.DeepResearchSkill if _research else None
GitOpsSkill = _git.GitOpsSkill if _git else None
SecurityAuditSkill = _security.SecurityAuditSkill if _security else None
MemoryQuerySkill = _memory.MemoryQuerySkill if _memory else None
CodeRefactorSkill = _refactor.CodeRefactorSkill if _refactor else None
DeploymentSkill = _deploy.DeploymentSkill if _deploy else None
RecoverySkill = _recovery.RecoverySkill if _recovery else None
ConstitutionalCheckSkill = _check.ConstitutionalCheckSkill if _check else None

__all__ = [
    'SKILL_REGISTRY',
    'get_skill',
    'list_skills',
    'VPSDockerSkill',
    'DeepResearchSkill',
    'GitOpsSkill',
    'SecurityAuditSkill',
    'MemoryQuerySkill',
    'CodeRefactorSkill',
    'DeploymentSkill',
    'RecoverySkill',
    'ConstitutionalCheckSkill',
]
