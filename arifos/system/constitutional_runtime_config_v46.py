#!/usr/bin/env python3
"""
Constitutional Runtime Configuration v46.0
Runtime settings for constitutional governance
"""

from arifos.constitutional_constants_v46 import CONSTITUTIONAL_FLOORS

class ConstitutionalRuntimeConfig:
    """Runtime configuration for constitutional governance"""
    
    def __init__(self):
        self.version = "v46.0"
        self.authority = "Track C (Implementation)"
        
        # Constitutional thresholds (support single-value and range-based floors)
        self.constitutional_thresholds = {}
        for floor, config in CONSTITUTIONAL_FLOORS.items():
            if "threshold" in config:
                self.constitutional_thresholds[floor] = config["threshold"]
                continue

            threshold_min = config.get("threshold_min")
            threshold_max = config.get("threshold_max")
            if threshold_min is None or threshold_max is None:
                continue
            self.constitutional_thresholds[floor] = {
                "min": threshold_min,
                "max": threshold_max,
            }
        
        # Performance settings
        self.performance = {
            "constitutional_check_timeout": 0.05,  # 50ms per check
            "pipeline_timeout": 0.2,  # 200ms full pipeline
            "memory_timeout": 0.01,  # 10ms memory operations
            "hash_verification_timeout": 0.005  # 5ms per verification
        }
        
        # Security settings
        self.security = {
            "enable_fag": True,  # File Access Governance
            "enable_cryptographic_proofs": True,
            "enable_audit_trail": True,
            "888_hold_triggers": [
                "database_operations",
                "production_deployments", 
                "mass_file_changes",
                "credential_handling",
                "git_history_modification"
            ]
        }
        
        # Constitutional settings
        self.constitutional = {
            "enable_all_floors": True,
            "class_a_routing": ["111", "333", "888", "999"],
            "class_b_routing": ["111", "222", "333", "444", "555", "666", "777", "888", "999"],
            "authority_hierarchy": [
                "Human_Sovereign",
                "arifOS_Governor", 
                "Constitutional_Canon",
                "L2_PROTOCOLS",
                "Implementation"
            ]
        }
    
    def get_constitutional_threshold(self, floor: str):
        """Get constitutional threshold for specific floor"""
        return self.constitutional_thresholds.get(floor)
    
    def is_888_hold_trigger(self, operation: str) -> bool:
        """Check if operation triggers 888_HOLD"""
        return operation in self.security["888_hold_triggers"]
    
    def get_performance_timeout(self, operation: str) -> float:
        """Get performance timeout for operation"""
        return self.performance.get(f"{operation}_timeout", 1.0)

# Global runtime configuration
RUNTIME_CONFIG = ConstitutionalRuntimeConfig()

def get_runtime_config() -> ConstitutionalRuntimeConfig:
    """Get global runtime configuration"""
    return RUNTIME_CONFIG
