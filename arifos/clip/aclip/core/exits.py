# Exit code definitions (for reference and future use)

PASS = 0       # Stage success
PARTIAL = 20   # Pipeline partially complete (not sealed)
SABAR = 30     # Waiting for external input (authority, time, etc.)
VOID = 40      # Session initialized
HOLD = 88      # Hold triggered or required
SEALED = 100   # Pipeline sealed successfully

EXIT_CODES = {
    "PASS": PASS,
    "PARTIAL": PARTIAL,
    "SABAR": SABAR,
    "VOID": VOID,
    "HOLD": HOLD,
    "SEALED": SEALED
}
