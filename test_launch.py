#!/usr/bin/env python3
"""Quick test launcher"""

import os
import sys

# Set API key
os.environ['SEALION_API_KEY'] = 'sk-bf_BClVray-kkgqWBpgwog'

# Launch unified interface
os.system('python L6_SEALION/cli/sealion_unified_interface.py --cli')
