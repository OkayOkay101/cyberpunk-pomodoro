import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestCalculateRemainingSecondsPerformance(unittest.TestCase):
    """
    Performance and behavioral verification for PomodoroCore.calculateRemainingSeconds.
    Verifies elimination of redundant Number() conversions, redundant isNaN/isFinite checks,
    and redundant Math.max calls in the 250ms high-frequency timer tick loop via numeric fast-path.
    """

    def _run_node_script(self, script: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )

    def test_calculate_remaining_seconds_fast_path(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const fnStr = PomodoroCore.calculateRemainingSeconds.toString();

        // Must not unconditionally call Number(targetEndTimeMs) or Number(nowMs) at entry
        if (/^\\s*calculateRemainingSeconds\\s*\\([^)]*\\)\\s*\\{\\s*const\\s+target\\s*=\\s*Number/.test(fnStr)) {
            console.error('FAIL: calculateRemainingSeconds unconditionally calls Number() without numeric fast-path');
            process.exit(2);
        }

        // Must use typeof === 'number' fast-path
        if (!/typeof\\s+targetEndTimeMs\\s*===\\s*['"]number['"]/.test(fnStr)) {
            console.error('FAIL: calculateRemainingSeconds missing numeric fast-path check');
            process.exit(3);
        }

        console.log('SUCCESS');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_remaining_seconds_active_and_boundaries(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const now = 1731110000000;

        // Future countdown intervals
        if (PomodoroCore.calculateRemainingSeconds(now + 25000, now) !== 25) process.exit(1);
        if (PomodoroCore.calculateRemainingSeconds(now + 60000, now) !== 60) process.exit(2);
        if (PomodoroCore.calculateRemainingSeconds(now + 1500000, now) !== 1500) process.exit(3);

        // Positive remaining time rounds up so completion cannot fire early
        if (PomodoroCore.calculateRemainingSeconds(now + 1500, now) !== 2) process.exit(4);
        if (PomodoroCore.calculateRemainingSeconds(now + 1499, now) !== 2) process.exit(5);
        if (PomodoroCore.calculateRemainingSeconds(now + 500, now) !== 1) process.exit(6);
        if (PomodoroCore.calculateRemainingSeconds(now + 499, now) !== 1) process.exit(7);
        if (PomodoroCore.calculateRemainingSeconds(now + 1, now) !== 1) process.exit(8);

        console.log('SUCCESS');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_remaining_seconds_expired_and_past(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const now = 1731110000000;

        // Exact current time
        if (PomodoroCore.calculateRemainingSeconds(now, now) !== 0) process.exit(1);

        // Past times
        if (PomodoroCore.calculateRemainingSeconds(now - 1, now) !== 0) process.exit(2);
        if (PomodoroCore.calculateRemainingSeconds(now - 500, now) !== 0) process.exit(3);
        if (PomodoroCore.calculateRemainingSeconds(now - 1000, now) !== 0) process.exit(4);
        if (PomodoroCore.calculateRemainingSeconds(now - 50000, now) !== 0) process.exit(5);

        // Negative numbers
        if (PomodoroCore.calculateRemainingSeconds(-1000, 0) !== 0) process.exit(6);
        if (PomodoroCore.calculateRemainingSeconds(-1000, -500) !== 0) process.exit(7);
        if (PomodoroCore.calculateRemainingSeconds(-500, -1000) !== 1) process.exit(8);

        console.log('SUCCESS');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_remaining_seconds_non_finite_and_corrupted(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const now = 1731110000000;

        // Non-finite guards
        if (PomodoroCore.calculateRemainingSeconds(Infinity, now) !== 0) process.exit(1);
        if (PomodoroCore.calculateRemainingSeconds(-Infinity, now) !== 0) process.exit(2);
        if (PomodoroCore.calculateRemainingSeconds(now + 10000, Infinity) !== 0) process.exit(3);
        if (PomodoroCore.calculateRemainingSeconds(now + 10000, -Infinity) !== 0) process.exit(4);
        if (PomodoroCore.calculateRemainingSeconds(NaN, now) !== 0) process.exit(5);
        if (PomodoroCore.calculateRemainingSeconds(now + 10000, NaN) !== 0) process.exit(6);
        if (PomodoroCore.calculateRemainingSeconds(NaN, NaN) !== 0) process.exit(7);

        // Numeric string inputs
        if (PomodoroCore.calculateRemainingSeconds(String(now + 25000), String(now)) !== 25) process.exit(8);
        if (PomodoroCore.calculateRemainingSeconds('25000', '0') !== 25) process.exit(9);
        if (PomodoroCore.calculateRemainingSeconds(String(now - 5000), String(now)) !== 0) process.exit(10);

        // Corrupted / fallback inputs
        if (PomodoroCore.calculateRemainingSeconds('invalid', now) !== 0) process.exit(11);
        if (PomodoroCore.calculateRemainingSeconds(now + 10000, 'invalid') !== 0) process.exit(12);
        if (PomodoroCore.calculateRemainingSeconds('', now) !== 0) process.exit(13);
        if (PomodoroCore.calculateRemainingSeconds('   ', now) !== 0) process.exit(14);
        if (PomodoroCore.calculateRemainingSeconds(null, now) !== 0) process.exit(15);
        if (PomodoroCore.calculateRemainingSeconds(undefined, now) !== 0) process.exit(16);
        if (PomodoroCore.calculateRemainingSeconds({}, now) !== 0) process.exit(17);
        if (PomodoroCore.calculateRemainingSeconds([], now) !== 0) process.exit(18);

        console.log('SUCCESS');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_remaining_seconds_exhaustive_baseline_equality(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        function baselineCalculateRemainingSeconds(targetEndTimeMs, nowMs) {
          const target = Number(targetEndTimeMs);
          const now = Number(nowMs);
          if (isNaN(target) || isNaN(now) || !isFinite(target) || !isFinite(now) || target <= now) return 0;
          return Math.ceil((target - now) / 1000);
        }

        const baseNow = 1731110000000;
        const testTargets = [
          baseNow + 25000, baseNow + 1500, baseNow + 1499, baseNow + 500, baseNow + 499, baseNow + 1,
          baseNow, baseNow - 1, baseNow - 1000, baseNow - 50000,
          0, -1000, 1000,
          NaN, Infinity, -Infinity,
          String(baseNow + 25000), String(baseNow), String(baseNow - 5000),
          '25000', '-5000', '0', 'invalid', '', '   ',
          null, undefined, true, false, {}, [], [baseNow + 1000]
        ];

        const testNows = [
          baseNow, baseNow + 1000, baseNow - 1000,
          0, -1000, 1000,
          NaN, Infinity, -Infinity,
          String(baseNow), String(baseNow - 5000),
          'invalid', '', '   ',
          null, undefined, true, false, {}, []
        ];

        for (const t of testTargets) {
          for (const n of testNows) {
            const base = baselineCalculateRemainingSeconds(t, n);
            const current = PomodoroCore.calculateRemainingSeconds(t, n);
            if (base !== current) {
              console.error(`MISMATCH for target=${JSON.stringify(t)}, now=${JSON.stringify(n)}: base=${base}, current=${current}`);
              process.exit(1);
            }
          }
        }

        console.log('SUCCESS');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
