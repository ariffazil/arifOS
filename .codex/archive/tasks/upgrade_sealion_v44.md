# Task: Upgrade SEA-LION Integration to v44.0.0 TEARFRAME

## status
- [x] Initial Audit (Identified target files)
- [x] partial: `play_session_live.py` (Updated to v44)
- [x] partial: `README.md` (Updated to v44)
- [x] partial: `demo_mock.py` (Updated to v44)
- [ ] Update `L6_SEALION/integrations/sealion/engine.py`
- [ ] Update `L6_SEALION/integrations/sealion/judge.py`
- [ ] Update `L6_SEALION/integrations/sealion/test_sgtoxic_spin.py`
- [ ] Update `L6_SEALION/integrations/sealion/__init__.py`
- [ ] Update `L6_SEALION/README.md` (Root Layer Doc)
- [ ] Configuration Check (`config/federation.yaml` if applicable)
- [ ] Verification (Run `demo_mock.py` and `pytest`)

## implementation_plan
1.  **Audit Remaining Files**: Search for "v41", "v38Omega", and outdated year "2024" (if any) in the L6 directory.
2.  **Apply Code Upgrades**:
    -   **`engine.py`**: Update version constants and docstrings.
    -   **`judge.py`**: Ensure it references the Correct v44 APEX contract and update version metadata.
    -   **`test_sgtoxic_spin.py`**: Update test headers and version assertions if any.
    -   **`__init__.py`**: Align package version.
3.  **Documentation Synchronization**:
    -   Ensure `L6_SEALION/README.md` accurately reflects the **TEARFRAME Physics** integration (Rate limits, Streak logic) inherited from the core.
4.  **Final Verification**:
    -   Run `python integrations/sealion/demo_mock.py` to confirm the banner and logic flow.
    -   Run `pytest integrations/sealion/test_sgtoxic_spin.py` to confirm detectors are stable.

## user_review_required
> Can you review this plan? I have already updated `play_session_live.py`, `demo_mock.py`, and the integration `README.md`. I will proceed with the engines and detectors next.
