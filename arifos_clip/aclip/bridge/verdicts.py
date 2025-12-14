# Verdict constants and mapping

# Possible verdict values from arifOS
VERDICT_SEAL = "SEAL"
VERDICT_HOLD = "HOLD"
VERDICT_PASS = "PASS"
VERDICT_PARTIAL = "PARTIAL"
VERDICT_SABAR = "SABAR"
VERDICT_VOID = "VOID"

# Map verdict labels to A CLIP exit codes
verdict_to_exit_code = {
    VERDICT_PASS: 0,
    VERDICT_PARTIAL: 20,
    VERDICT_SABAR: 30,
    VERDICT_VOID: 40,
    VERDICT_HOLD: 88,
    VERDICT_SEAL: 100
}
