"""
arifos/runtime/reforge.py — The Metabolic Metabolic Engine
AUTOMATED ENTROPY REDUCTION & CONSTITUTIONAL AUDIT.
"""

import os

from arifos.runtime.DNA import DENSITY_TARGET, VERSION


class MetabolicForge:
    def __init__(self, root_dir: str):
        self.root = root_dir
        self.audit_report = {
            "version": VERSION,
            "pruned": [],
            "metrics": {},
            "warnings": []
        }

    def scan_for_entropy(self):
        """Finds logic-less files and archives for pruning."""
        targets = []
        for root, _, files in os.walk(self.root):
            if "venv" in root or "node_modules" in root or ".archive" in root:
                continue
            for f in files:
                path = os.path.join(root, f)
                # target empty inits or old hardened duplicates
                if f == "__init__.py" and os.path.getsize(path) < 10:
                    targets.append(path)
                if "hardened" in f.lower() and f != "kernel.py":
                    targets.append(path)
        self.audit_report["pruned"] = targets
        return targets

    def calculate_density(self) -> dict:
        """Calculates Intelligence Density (LOC/File)."""
        loc, fcount = 0, 0
        for root, _, files in os.walk(self.root):
            if any(x in root for x in ["venv", "node_modules", ".git", ".archive"]):
                continue
            for f in files:
                if f.endswith((".py", ".js", ".html", ".css")):
                    fcount += 1
                    with open(os.path.join(root, f), encoding='utf-8', errors='ignore') as file:
                        loc += len(file.readlines())
        
        density = round(loc / max(1, fcount), 2)
        self.audit_report["metrics"] = {
            "loc": loc,
            "file_count": fcount,
            "density": density,
            "delta_i": round(density / DENSITY_TARGET * 100, 2)
        }
        return self.audit_report["metrics"]

    def stage_metabolism(self):
        """Moves targets to VAULT999/STAGING."""
        staging_dir = os.path.join(self.root, "VAULT999", "STAGING")
        os.makedirs(staging_dir, exist_ok=True)
        
        for t in self.audit_report["pruned"]:
            name = os.path.basename(t)
            dest = os.path.join(staging_dir, f"{name}.staged")
            try:
                os.rename(t, dest)
            except Exception as e:
                self.audit_report["warnings"].append(f"Failed to move {name}: {str(e)}")

    def run(self):
        print(f"--- arifOS Metabolic Reforge v{VERSION} ---")
        self.scan_for_entropy()
        metrics = self.calculate_density()
        print(f"Intelligence Density: {metrics['density']} ({metrics['delta_i']}% of Target)")
        print(f"Files targeted for pruning: {len(self.audit_report['pruned'])}")
        
        if self.audit_report["pruned"]:
            self.stage_metabolism()
            print("Staging complete. Review VAULT999/STAGING for metabolic seal.")

if __name__ == "__main__":
    _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    forge = MetabolicForge(_root)
    forge.run()
