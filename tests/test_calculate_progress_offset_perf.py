import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestCalculateProgressOffsetPerformance(unittest.TestCase):
    """
    Performance and behavioral verification for PomodoroCore.calculateProgressOffset.
    Verifies the numeric fast-path eliminates redundant isNaN/isFinite checks and
    Math.max/Math.min calls on the 250ms high-frequency timer tick loop while
    preserving byte-identical SVG dashoffset output.
    """

    def _run_node_script(self, script: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )

    def test_calculate_progress_offset_numeric_fast_path(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const fnStr = PomodoroCore.calculateProgressOffset.toString();

        // Must fast-path native numeric inputs before falling back to isNaN/isFinite
        if (/^\\s*calculateProgressOffset\\s*\\([^)]*\\)\\s*\\{\\s*if\\s*\\(\\s*typeof\\s+timeLeft/.test(fnStr)) {
            // numeric fast-path present
        } else {
            console.error('FAIL: calculateProgressOffset missing numeric fast-path check');
            process.exit(2);
        }

        // Must avoid unconditional Math.max/Math.min on the numeric path
        if (/Math\\.max\\(0,\\s*Math\\.min/.test(fnStr.split('return circumference')[0])) {
            console.error('FAIL: calculateProgressOffset still uses Math.max/Math.min on numeric path');
            process.exit(3);
        }

        console.log('SUCCESS');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_progress_offset_active_and_boundaries(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');
        const C = 691.15;

        // Full time -> offset 0
        if (PomodoroCore.calculateProgressOffset(1500, 1500, C) !== 0) process.exit(1);
        // Zero time -> offset C
        if (PomodoroCore.calculateProgressOffset(0, 1500, C) !== C) process.exit(2);
        // Half time -> offset C/2
        if (Math.round(PomodoroCore.calculateProgressOffset(750, 1500, C)) !== Math.round(C / 2)) process.exit(3);
        // Near end -> small positive offset
        if (Math.round(PomodoroCore.calculateProgressOffset(1499, 1500, C)) !== 0) process.exit(4);
        // Clamped past duration -> 0
        if (PomodoroCore.calculateProgressOffset(2000, 1500, C) !== 0) process.exit(5);
        // Negative time -> offset C
        if (PomodoroCore.calculateProgressOffset(-100, 1500, C) !== C) process.exit(6);

        // Invalid duration -> 0
        if (PomodoroCore.calculateProgressOffset(750, 0, C) !== 0) process.exit(7);
        if (PomodoroCore.calculateProgressOffset(750, -5, C) !== 0) process.exit(8);
        if (PomodoroCore.calculateProgressOffset(750, NaN, C) !== 0) process.exit(9);
        if (PomodoroCore.calculateProgressOffset(750, Infinity, C) !== 0) process.exit(10);

        // Invalid circumference -> 0
        if (PomodoroCore.calculateProgressOffset(750, 1500, 0) !== 0) process.exit(11);
        if (PomodoroCore.calculateProgressOffset(750, 1500, -1) !== 0) process.exit(12);
        if (PomodoroCore.calculateProgressOffset(750, 1500, NaN) !== 0) process.exit(13);

        // NaN time treated as 0 -> offset C
        if (PomodoroCore.calculateProgressOffset(NaN, 1500, C) !== C) process.exit(14);

        console.log('SUCCESS');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_progress_offset_exhaustive_baseline_equality(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        function baselineCalculateProgressOffset(timeLeft, duration, circumference) {
          if (!duration || duration <= 0 || isNaN(duration) || !isFinite(duration)) return 0;
          if (isNaN(circumference) || circumference <= 0 || !isFinite(circumference)) return 0;
          const safeTime = isNaN(timeLeft) ? 0 : timeLeft;
          const clamped = Math.max(0, Math.min(safeTime, duration));
          return circumference - (clamped / duration) * circumference;
        }

        const C = 691.15;
        const timeValues = [
          0, 1, 750, 1499, 1500, 1501, 3000, -100, -0.5,
          NaN, Infinity, -Infinity,
          100, 500, 1000,
          '750', 'invalid', '', null, undefined, [100], {}
        ];
        const durationValues = [
          1, 5, 60, 1500, 3600, 0, -5, NaN, Infinity, -Infinity,
          '1500', 'invalid', '', null, undefined
        ];
        const circumferenceValues = [
          C, 100, 500, 0, -1, NaN, Infinity, -Infinity, 1000.5,
          '691.15', 'invalid', '', null, undefined
        ];

        let checked = 0;
        for (const t of timeValues) {
          for (const d of durationValues) {
            for (const c of circumferenceValues) {
              const base = baselineCalculateProgressOffset(t, d, c);
              const current = PomodoroCore.calculateProgressOffset(t, d, c);
              if (base !== current) {
                console.error(`MISMATCH t=${JSON.stringify(t)} d=${JSON.stringify(d)} c=${JSON.stringify(c)}: base=${base}, current=${current}`);
                process.exit(1);
              }
              checked++;
            }
          }
        }

        console.log(`SUCCESS (${checked} cases)`);
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
