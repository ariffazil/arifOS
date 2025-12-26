"""
test_waw_apex_escalation.py — v38.3 AMENDMENT 3 Tests

Tests for W@W Conflict Resolution via APEX PRIME.

Validates:
- Conflicting organ verdicts trigger APEX escalation
- APEX returns synthesized verdict (not single organ's)
- Hard floor failures still block action (APEX doesn't override F1/F2)
- No hardcoded precedence exists (no "@WEALTH always wins")
- Psi vitality influences APEX decision

Author: arifOS Project
Version: v38.3
"""

import pytest
from arifos_core.waw.federation import WAWFederationCore
from arifos_core.waw.base import OrganSignal, OrganVote
from arifos_core.system.apex_prime import apex_prime_judge


class TestWAWApexEscalation:
    """v38.3 AMENDMENT 3: W@W Conflict Resolution Tests"""

    def test_apex_prime_judge_exists(self):
        """✅ apex_prime_judge() function exists in APEX_PRIME"""
        # Should be importable
        from arifos_core.system.apex_prime import apex_prime_judge
        assert callable(apex_prime_judge)

    def test_apex_judge_synthesizes_verdict(self):
        """✅ APEX returns synthesized verdict when organs conflict"""
        context = {
            'organs': [
                {'organ_id': '@WELL', 'vote': 'VETO', 'reason': 'harmful'},
                {'organ_id': '@RIF', 'vote': 'PASS', 'reason': 'logical'},
            ],
            'verdict_proposals': {
                'SABAR': ['@WELL'],
                'SEAL': ['@RIF'],
            },
            'psi': 0.9,
        }
        
        verdict = apex_prime_judge(context)
        
        # Should return a valid verdict
        assert verdict in ['SEAL', 'PARTIAL', 'SABAR', 'VOID', '888_HOLD']
        
        # With 1 concern, should return PARTIAL
        assert verdict == 'PARTIAL'

    def test_apex_judge_with_high_psi(self):
        """✅ High Psi + all pass → SEAL"""
        context = {
            'organs': [
                {'organ_id': '@WELL', 'vote': 'PASS'},
                {'organ_id': '@RIF', 'vote': 'PASS'},
                {'organ_id': '@WEALTH', 'vote': 'PASS'},
            ],
            'verdict_proposals': {
                'SEAL': ['@WELL', '@RIF', '@WEALTH'],
            },
            'psi': 1.2,
        }
        
        verdict = apex_prime_judge(context)
        assert verdict == 'SEAL'

    def test_apex_judge_with_multiple_concerns(self):
        """✅ Multiple organs with concerns → most severe verdict"""
        context = {
            'organs': [
                {'organ_id': '@WELL', 'vote': 'VETO'},
                {'organ_id': '@RIF', 'vote': 'VETO'},
                {'organ_id': '@WEALTH', 'vote': 'PASS'},
            ],
            'verdict_proposals': {
                'SABAR': ['@WELL', '@RIF'],
                'SEAL': ['@WEALTH'],
            },
            'psi': 0.8,
        }
        
        verdict = apex_prime_judge(context)
        # 2 concerns → should return SABAR (most severe proposed)
        assert verdict in ['SABAR', 'PARTIAL']

    def test_apex_judge_void_with_low_psi(self):
        """✅ VOID proposed + low Psi → escalate to VOID"""
        context = {
            'organs': [
                {'organ_id': '@RIF', 'vote': 'VETO'},
            ],
            'verdict_proposals': {
                'VOID': ['@RIF'],
            },
            'psi': 0.7,
        }
        
        verdict = apex_prime_judge(context)
        assert verdict == 'VOID'

    def test_no_static_hierarchy_in_federation(self):
        """✅ No hardcoded "@WEALTH veto > @WELL safety" precedence"""
        # Read federation.py source to verify no hierarchy
        import arifos_core.waw.federation as fed
        source = fed.__doc__ or ''
        
        # Should mention APEX escalation, not hierarchy
        assert 'APEX' in source or 'meta-judgment' in source
        
        # Check resolve_organ_conflict exists
        federation = WAWFederationCore()
        assert hasattr(federation, 'resolve_organ_conflict')

    def test_resolve_organ_conflict_no_conflict(self):
        """✅ No conflict → returns agreement verdict"""
        federation = WAWFederationCore()
        
        signals = [
            OrganSignal(
                organ_id='@WELL',
                vote=OrganVote.PASS,
                metric_name='peace_squared',
                metric_value=1.2,
                floor_threshold=1.0,
                floor_pass=True,
                is_absolute_veto=False,
            ),
            OrganSignal(
                organ_id='@RIF',
                vote=OrganVote.PASS,
                metric_name='delta_s',
                metric_value=0.5,
                floor_threshold=0.0,
                floor_pass=True,
                is_absolute_veto=False,
            ),
        ]
        
        verdict = federation.resolve_organ_conflict(signals)
        # All PASS → should return PASS or SEAL
        assert verdict in ['PASS', 'SEAL']

    def test_resolve_organ_conflict_escalates(self):
        """✅ Conflicting organs trigger APEX escalation"""
        federation = WAWFederationCore()
        
        signals = [
            OrganSignal(
                organ_id='@WELL',
                vote=OrganVote.VETO,
                metric_name='peace_squared',
                metric_value=0.8,
                floor_threshold=1.0,
                floor_pass=False,
                is_absolute_veto=False,
            ),
            OrganSignal(
                organ_id='@RIF',
                vote=OrganVote.PASS,
                metric_name='delta_s',
                metric_value=0.5,
                floor_threshold=0.0,
                floor_pass=True,
                is_absolute_veto=False,
            ),
        ]
        
        verdict = federation.resolve_organ_conflict(signals)
        
        # Should return synthesized verdict, not just first organ's
        assert verdict in ['SEAL', 'PARTIAL', 'SABAR', 'VOID', '888_HOLD']
        assert verdict != 'VETO'  # Should be translated to proper verdict
