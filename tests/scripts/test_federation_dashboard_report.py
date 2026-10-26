"""Exercise the workflow report with deterministic GitHub command responses."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASH = shutil.which("bash") if os.name != "nt" else "C:/Program Files/Git/bin/bash.exe"


@unittest.skipUnless(BASH and Path(BASH).exists(), "bash is required")
class FederationDashboardReportTests(unittest.TestCase):
    def report(self, conclusion: str, counts_available: bool = True) -> str:
        workflow = (ROOT / ".github/workflows/federation-health.yml").read_text(encoding="utf-8")
        block = workflow.split("        run: |\n", 1)[1]
        script = "\n".join(line[10:] for line in block.splitlines())
        stub = r"""
gh() {
  if [ "$1 $2" = "run list" ]; then
    printf '%s\n' "$TEST_CONCLUSION"
  elif [ "$1 $2" = "pr list" ]; then
    if [ "$TEST_COUNTS_AVAILABLE" = "yes" ]; then echo 0; else return 1; fi
  elif [ "$1 $2" = "issue create" ]; then
    return 0
  else
    return 2
  fi
}
"""
        with tempfile.TemporaryDirectory() as directory:
            env = dict(
                os.environ,
                TEST_CONCLUSION=conclusion,
                TEST_COUNTS_AVAILABLE="yes" if counts_available else "no",
            )
            result = subprocess.run(
                [BASH, "-c", stub + script],
                cwd=directory,
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            return (Path(directory) / "federation-report.md").read_text(encoding="utf-8")

    def test_successful_observations_report_green(self):
        self.assertIn("### ✅ All systems green", self.report("success"))

    def test_unverified_ci_never_reports_all_green(self):
        for conclusion in ("unknown", "", "cancelled", "failure", "timed_out"):
            with self.subTest(conclusion=conclusion):
                report = self.report(conclusion)
                self.assertNotIn("### ✅ All systems green", report)
                self.assertIn("Action required", report)
                self.assertNotIn("_none_", report)

    def test_unavailable_pr_counts_prevent_all_green(self):
        report = self.report("success", counts_available=False)
        self.assertNotIn("### ✅ All systems green", report)
        self.assertIn("Action required", report)


if __name__ == "__main__":
    unittest.main()
