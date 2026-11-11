import json
import re
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class TestRemainingSecondsBenchmark(unittest.TestCase):
    def test_baseline_matches_production_for_subsecond_durations(self):
        benchmark = (REPO_ROOT / "bench" / "bench_remaining_seconds.js").read_text(encoding="utf-8")
        match = re.search(
            r"function baselineCalculateRemainingSeconds\([^)]*\) \{.*?\n\}",
            benchmark,
            re.DOTALL,
        )
        self.assertIsNotNone(match, "Could not locate the benchmark baseline implementation")

        script = f"""
        const {{ PomodoroCore }} = require('./core.js');
        const baselineSource = {json.dumps(match.group(0))};
        eval(baselineSource);
        const now = 1731110000000;
        for (const remainingMs of [499, 1, 500]) {{
          const baseline = baselineCalculateRemainingSeconds(now + remainingMs, now);
          const production = PomodoroCore.calculateRemainingSeconds(now + remainingMs, now);
          if (baseline !== production) {{
            throw new Error(`Mismatch for ${{remainingMs}}ms: baseline ${{baseline}}, production ${{production}}`);
          }}
        }}
        """
        proc = subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)


if __name__ == "__main__":
    unittest.main()
