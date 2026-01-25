"""
Stakeholder Ecosystem Mapper
Maps all affected parties for multi-dimensional empathy analysis

Authority: Muhammad Arif bin Fazil
Floor: F5 (Empathy)
Version: v52.0.0-SEAL
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class StakeholderCategory(Enum):
    PRIMARY = "primary"        # Direct users
    SECONDARY = "secondary"    # Indirect users (family, dependents)
    TERTIARY = "tertiary"      # Operators, maintainers
    QUATERNARY = "quaternary"  # Society, environment
    SILENT = "silent"          # Non-human (data, privacy, environment)

@dataclass
class Stakeholder:
    id: str
    category: StakeholderCategory
    vulnerability: float  # 0.0 to 1.0
    impact_radius: int    # How many steps from operation
    influence: float      # Ability to affect outcome
    awareness: float      # Knowledge of impact
    consent: Optional[bool] = None  # Did they consent?

class StakeholderMapper:
    """
    Maps complete stakeholder ecosystem for operation
    """
    
    def __init__(self):
        self.operation_context = {}
        
    async def map_ecosystem(self, 
                          operation: Dict[str, Any],
                          session_id: str) -> Dict[str, List[Stakeholder]]:
        """
        Main mapping function - identifies ALL affected parties
        """
        operation_type = operation.get("type", "unknown")
        operation_target = operation.get("target", "")
        
        stakeholders = {
            StakeholderCategory.PRIMARY: [],
            StakeholderCategory.SECONDARY: [],
            StakeholderCategory.TERTIARY: [],
            StakeholderCategory.QUATERNARY: [],
            StakeholderCategory.SILENT: []
        }
        
        # Map based on operation type
        mapper = self._get_mapper(operation_type)
        await mapper(operation, stakeholders)
        
        # Calculate ecosystem metrics
        ecosystem_metrics = self._calculate_metrics(stakeholders)
        
        return {
            "stakeholders": stakeholders,
            "metrics": ecosystem_metrics,
            "operation_id": operation.get("id"),
            "session_id": session_id
        }
    
    def _get_mapper(self, operation_type: str):
        """Get appropriate mapper for operation type"""
        mappers = {
            "file_write": self._map_file_write,
            "database_query": self._map_database_query,
            "api_call": self._map_api_call,
            "system_command": self._map_system_command,
            "ui_change": self._map_ui_change,
            "default": self._map_default
        }
        return mappers.get(operation_type, mappers["default"])
    
    async def _map_file_write(self, operation: Dict, stakeholders: Dict):
        """Map stakeholders for file write operations"""
        file_path = operation.get("target", "")
        
        # Primary: Users of this file
        stakeholders[StakeholderCategory.PRIMARY].append(
            Stakeholder(
                id=f"dev_{file_path}",
                category=StakeholderCategory.PRIMARY,
                vulnerability=0.6,  # Developers can be vulnerable to bugs
                impact_radius=1,
                influence=0.8,
                awareness=0.9,
                consent=None
            )
        )
        
        # Secondary: End users affected by this file
        stakeholders[StakeholderCategory.SECONDARY].append(
            Stakeholder(
                id=f"users_{file_path}",
                category=StakeholderCategory.SECONDARY,
                vulnerability=0.8,  # Users most vulnerable
                impact_radius=2,
                influence=0.1,  # Users have little direct influence
                awareness=0.3,  # Often unaware of implementation changes
                consent=None
            )
        )
        
        # Tertiary: Code reviewers, ops team
        stakeholders[StakeholderCategory.TERTIARY].append(
            Stakeholder(
                id=f"ops_{file_path}",
                category=StakeholderCategory.TERTIARY,
                vulnerability=0.4,
                impact_radius=3,
                influence=0.6,
                awareness=0.8,
                consent=None
            )
        )
        
        # Silent: Code integrity, future maintainers
        stakeholders[StakeholderCategory.SILENT].append(
            Stakeholder(
                id=f"integrity_{file_path}",
                category=StakeholderCategory.SILENT,
                vulnerability=0.7,  # Code can be silently corrupted
                impact_radius=0,  # Direct impact
                influence=0.0,  # Code can't advocate for itself
                awareness=0.0,
                consent=None
            )
        )
    
    async def _map_database_query(self, operation: Dict, stakeholders: Dict):
        """Map stakeholders for database operations"""
        # Primary: Database itself (data integrity)
        stakeholders[StakeholderCategory.SILENT].append(
            Stakeholder(
                id="database_integrity",
                category=StakeholderCategory.SILENT,
                vulnerability=0.9,  # Data corruption is catastrophic
                impact_radius=0,
                influence=0.0,
                awareness=0.0,
                consent=None
            )
        )
        
        # Primary: Users whose data is accessed
        stakeholders[StakeholderCategory.PRIMARY].append(
            Stakeholder(
                id="data_subjects",
                category=StakeholderCategory.PRIMARY,
                vulnerability=0.9,  # Privacy vulnerability
                impact_radius=1,
                influence=0.2,
                awareness=0.4,
                consent=None
            )
        )
        
        # Secondary: Their families (if personal data)
        if operation.get("sensitivity") == "high":
            stakeholders[StakeholderCategory.SECONDARY].append(
                Stakeholder(
                    id="family_data_subjects",
                    category=StakeholderCategory.SECONDARY,
                    vulnerability=0.7,
                    impact_radius=2,
                    influence=0.1,
                    awareness=0.2,
                    consent=None
                )
            )
        
        # Tertiary: DBAs, compliance officers
        stakeholders[StakeholderCategory.TERTIARY].append(
            Stakeholder(
                id="dba_team",
                category=StakeholderCategory.TERTIARY,
                vulnerability=0.5,
                impact_radius=3,
                influence=0.7,
                awareness=0.9,
                consent=None
            )
        )
        
        # Quaternary: Society (privacy norms, trust)
        stakeholders[StakeholderCategory.QUATERNARY].append(
            Stakeholder(
                id="societal_trust",
                category=StakeholderCategory.QUATERNARY,
                vulnerability=0.3,  # Societal values shift slowly
                impact_radius=4,
                influence=0.05,
                awareness=0.6,
                consent=None
            )
        )
    
    async def _map_system_command(self, operation: Dict, stakeholders: Dict):
        """Map stakeholders for system-level commands"""
        command = operation.get("command", "")
        
        # Quaternary: System stability (affects everyone)
        stakeholders[StakeholderCategory.QUATERNARY].append(
            Stakeholder(
                id="system_stability",
                category=StakeholderCategory.QUATERNARY,
                vulnerability=0.8,  # System failure affects many
                impact_radius=4,
                influence=0.0,  # System can't self-advocate
                awareness=0.0,
                consent=None
            )
        )
        
        # Primary: Immediate users
        stakeholders[StakeholderCategory.PRIMARY].append(
            Stakeholder(
                id="system_users",
                category=StakeholderCategory.PRIMARY,
                vulnerability=0.7,  # Dependent on system
                impact_radius=1,
                influence=0.3,
                awareness=0.7,
                consent=None
            )
        )
        
        # Tertiary: System administrators
        stakeholders[StakeholderCategory.TERTIARY].append(
            Stakeholder(
                id="sysadmins",
                category=StakeholderCategory.TERTIARY,
                vulnerability=0.5,
                impact_radius=3,
                influence=0.8,
                awareness=0.9,
                consent=None
            )
        )
        
        # Silent: System logs, audit trails
        stakeholders[StakeholderCategory.SILENT].append(
            Stakeholder(
                id="system_audit",
                category=StakeholderCategory.SILENT,
                vulnerability=0.6,  # Logs can be tampered
                impact_radius=0,
                influence=0.0,
                awareness=0.0,
                consent=None
            )
        )
    
    async def _map_ui_change(self, operation: Dict, stakeholders: Dict):
        """Map stakeholders for UI/UX changes"""
        # Primary: End users
        stakeholders[StakeholderCategory.PRIMARY].append(
            Stakeholder(
                id="end_users",
                category=StakeholderCategory.PRIMARY,
                vulnerability=0.85,  # Users most vulnerable to UI changes
                impact_radius=1,
                influence=0.2,  # Limited influence on design
                awareness=0.4,  # Often unaware of upcoming changes
                consent=None
            )
        )
        
        # Secondary: Users with disabilities
        if operation.get("accessibility_impact") == "high":
            stakeholders[StakeholderCategory.SECONDARY].append(
                Stakeholder(
                    id="users_with_disabilities",
                    category=StakeholderCategory.SECONDARY,
                    vulnerability=0.95,  # Highest vulnerability
                    impact_radius=2,
                    influence=0.1,
                    awareness=0.3,
                    consent=None
                )
            )
        
        # Tertiary: UI/UX team, support team
        stakeholders[StakeholderCategory.TERTIARY].append(
            Stakeholder(
                id="ux_team",
                category=StakeholderCategory.TERTIARY,
                vulnerability=0.4,
                impact_radius=3,
                influence=0.7,
                awareness=0.9,
                consent=None
            )
        )
        
        # Quaternary: Brand reputation
        stakeholders[StakeholderCategory.QUATERNARY].append(
            Stakeholder(
                id="brand_trust",
                category=StakeholderCategory.QUATERNARY,
                vulnerability=0.6,  # Brand damage is hard to repair
                impact_radius=4,
                influence=0.0,
                awareness=0.0,
                consent=None
            )
        )
    
    async def _map_default(self, operation: Dict, stakeholders: Dict):
        """Default mapper for unknown operation types"""
        stakeholders[StakeholderCategory.PRIMARY].append(
            Stakeholder(
                id="operator",
                category=StakeholderCategory.PRIMARY,
                vulnerability=0.6,
                impact_radius=1,
                influence=0.5,
                awareness=0.7,
                consent=None
            )
        )
        
        stakeholders[StakeholderCategory.SILENT].append(
            Stakeholder(
                id="system_integrity",
                category=StakeholderCategory.SILENT,
                vulnerability=0.5,
                impact_radius=0,
                influence=0.0,
                awareness=0.0,
                consent=None
            )
        )
    
    def _calculate_metrics(self, stakeholders: Dict) -> Dict[str, float]:
        """Calculate ecosystem-level metrics"""
        all_stakeholders = []
        for category, stakeholder_list in stakeholders.items():
            all_stakeholders.extend(stakeholder_list)
        
        if not all_stakeholders:
            return {}
        
        # Weighted vulnerability (considering impact radius)
        weighted_vuln = sum(
            s.vulnerability / (s.impact_radius + 1) 
            for s in all_stakeholders
        ) / len(all_stakeholders)
        
        # Ecosystem diversity (more categories = more complex empathy needed)
        active_categories = sum(
            1 for category, stakeholder_list in stakeholders.items() 
            if stakeholder_list
        )
        diversity = active_categories / len(StakeholderCategory)
        
        # Average influence distribution
        avg_influence = sum(s.influence for s in all_stakeholders) / len(all_stakeholders)
        
        # Silent stakeholder count (easily overlooked)
        silent_count = len(stakeholders[StakeholderCategory.SILENT])
        
        # Most vulnerable in ecosystem
        most_vulnerable = max(all_stakeholders, key=lambda s: s.vulnerability)
        
        return {
            "weighted_vulnerability": round(weighted_vuln, 3),
            "ecosystem_diversity": round(diversity, 3),
            "avg_influence": round(avg_influence, 3),
            "silent_stakeholders": silent_count,
            "most_vulnerable_id": most_vulnerable.id,
            "most_vulnerable_score": round(most_vulnerable.vulnerability, 3),
            "total_stakeholders": len(all_stakeholders)
        }

# Singleton instance
_mapper = StakeholderMapper()

async def map_stakeholder_ecosystem(operation: Dict[str, Any], session_id: str) -> Dict:
    """Convenience function for external use"""
    return await _mapper.map_ecosystem(operation, session_id)

if __name__ == "__main__":
    # Test the mapper
    async def test():
        test_op = {
            "type": "file_write",
            "target": "src/auth.py",
            "id": "test_001"
        }
        
        result = await map_stakeholder_ecosystem(test_op, "test_session")
        print(json.dumps(result, indent=2, default=str))
    
    asyncio.run(test())
