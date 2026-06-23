class CoolingLedger:
    def __init__(self):
        pass

    def record_sabar(self, intent, recheck_condition):
        if not recheck_condition:
            raise ValueError("Cooling Ledger item must have recheck condition.")
        return "COOLING"
