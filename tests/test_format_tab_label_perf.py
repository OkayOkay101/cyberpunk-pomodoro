import unittest
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestFormatTabLabelPerformance(unittest.TestCase):
    def test_format_tab_label_behavior_and_edge_cases(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const cases = [
          // Standard modes & standard durations
          [['focus', 1500], 'FOCUS (25M)'],
          [['shortBreak', 300], 'SHORT (5M)'],
          [['longBreak', 900], 'LONG (15M)'],

          // Unknown / fallback modes
          [['unknown', 1500], 'FOCUS (25M)'],
          [['customMode', 600], 'FOCUS (10M)'],
          [['', 1500], 'FOCUS (25M)'],
          [[null, 1500], 'FOCUS (25M)'],
          [[undefined, 1500], 'FOCUS (25M)'],
          [[123, 1500], 'FOCUS (25M)'],
          [[{}, 1500], 'FOCUS (25M)'],

          // Durations: zeros and negative values
          [['focus', 0], 'FOCUS (0M)'],
          [['focus', -1], 'FOCUS (0M)'],
          [['focus', -500], 'FOCUS (0M)'],

          // Durations: non-numeric / invalid inputs
          [['focus', NaN], 'FOCUS (0M)'],
          [['focus', null], 'FOCUS (0M)'],
          [['focus', undefined], 'FOCUS (0M)'],
          [['focus', 'not-a-number'], 'FOCUS (0M)'],
          [[undefined, undefined], 'FOCUS (0M)'],

          // Durations: string numbers and edge rounding
          [['focus', '1200'], 'FOCUS (20M)'],
          [['shortBreak', '60'], 'SHORT (1M)'],
          [['longBreak', '1800'], 'LONG (30M)'],
          [['focus', 29], 'FOCUS (0M)'],
          [['focus', 30], 'FOCUS (1M)'],
          [['focus', 59], 'FOCUS (1M)'],
          [['focus', 60], 'FOCUS (1M)'],
          [['focus', 89], 'FOCUS (1M)'],
          [['focus', 90], 'FOCUS (2M)'],
          [['focus', 1499], 'FOCUS (25M)'],
          [['focus', 3600], 'FOCUS (60M)']
        ];

        for (const [args, expected] of cases) {
          const actual = PomodoroCore.formatTabLabel(args[0], args[1]);
          if (actual !== expected) {
            console.error('Mismatch: args=' + JSON.stringify(args) + ' expected=' + expected + ' actual=' + actual);
            process.exit(1);
          }
        }
        console.log('SUCCESS_BEHAVIOR');
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS_BEHAVIOR", proc.stdout)

    def test_format_tab_label_baseline_equality(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        function baselineFormatTabLabel(mode, durationSeconds) {
          const labels = {
            focus: 'FOCUS',
            shortBreak: 'SHORT',
            longBreak: 'LONG'
          };
          const label = labels[mode] || 'FOCUS';
          const num = Number(durationSeconds);
          const mins = (!isNaN(num) && num > 0) ? Math.round(num / 60) : 0;
          return `${label} (${mins}M)`;
        }

        const modes = ['focus', 'shortBreak', 'longBreak', 'unknown', '', null, undefined];
        const durations = [
          0, 1, 15, 29, 30, 45, 59, 60, 89, 90, 300, 900, 1500, 3600,
          -1, -60, NaN, Infinity, -Infinity, null, undefined, '300', 'invalid'
        ];

        for (const mode of modes) {
          for (const dur of durations) {
            const expected = baselineFormatTabLabel(mode, dur);
            const actual = PomodoroCore.formatTabLabel(mode, dur);
            if (actual !== expected) {
              console.error(`Equality mismatch on [${mode}, ${dur}]: expected="${expected}", actual="${actual}"`);
              process.exit(1);
            }
          }
        }
        console.log('SUCCESS_EQUALITY');
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS_EQUALITY", proc.stdout)

    def test_format_tab_label_high_volume_throughput(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const iters = 100000;
        const start = performance.now();
        for (let i = 0; i < iters; i++) {
          PomodoroCore.formatTabLabel('focus', 1500);
          PomodoroCore.formatTabLabel('shortBreak', 300);
          PomodoroCore.formatTabLabel('longBreak', 900);
        }
        const elapsed = performance.now() - start;

        // 300,000 calls should easily finish in well under 1000ms
        if (elapsed > 1000) {
          console.error(`Throughput failed: 300k calls took ${elapsed.toFixed(2)}ms (expected < 1000ms)`);
          process.exit(1);
        }
        console.log(`SUCCESS_THROUGHPUT: ${elapsed.toFixed(2)}ms`);
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS_THROUGHPUT", proc.stdout)


if __name__ == "__main__":
    unittest.main()
