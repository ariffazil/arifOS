"""
arifOS Thermodynamic Validator Shim
Redirects root-level imports to arifos.core.thermodynamic_validator
"""
from typing import Any, Dict, List, Optional

from .core.thermodynamic_validator import (calculate_delta_s,
                                           calculate_humility,
                                           calculate_peace_squared,
                                           validate_entropy_reduction,
                                           validate_humility,
                                           validate_peace_squared,
                                           validate_thermodynamics)
