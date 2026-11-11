import unittest
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestCalculateStreakPerformance(unittest.TestCase):
    def test_calculate_streak_no_unnecessary_date_instantiation(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Verify that calculateStreak does not instantiate Date objects for string parsing
        const fnStr = PomodoroCore.calculateStreak.toString();
        if (/new\\s+Date\\s*\\(lastDateStr\\)/.test(fnStr)) {
            console.error('FAIL: calculateStreak still instantiates new Date(lastDateStr) instead of Date.parse()');
            process.exit(2);
        }

        console.log('SUCCESS_OPTIMIZATION');
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS_OPTIMIZATION", proc.stdout)

    def test_calculate_streak_baseline_equality(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        function baselineCalculateStreak(lastDateStr, todayStr, currentStreak) {
          const validStreak = (typeof currentStreak === 'number' && !isNaN(currentStreak) && currentStreak >= 1)
            ? Math.floor(currentStreak)
            : 1;
          if (!lastDateStr || typeof lastDateStr !== 'string') return 1;
          if (lastDateStr === todayStr) return validStreak;
          const lastDate = new Date(lastDateStr);
          const today = new Date(todayStr);
          const diffTime = today - lastDate;
          if (isNaN(diffTime)) return 1;
          const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));
          if (diffDays === 1) return validStreak + 1;
          if (diffDays > 1) return 1;
          return validStreak;
        }

        const cases = [
          ['2026-11-07', '2026-11-08', 1],
          ['2026-11-07', '2026-11-09', 1],
          ['2026-11-08', '2026-11-08', 3],
          ['', '2026-11-08', 1],
          ['2026-11-07', '2026-11-08', NaN],
          ['2026-11-07', '2026-11-08', 0],
          ['2026-11-07', '2026-11-08', -5],
          ['2026-11-09', '2026-11-08', 5],
          ['2026-1-8', '2026-01-08', 3],
          ['2026-03-07', '2026-03-08', 1],
          ['2026-11-01', '2026-11-02', 1],
          [null, '2026-11-08', 1],
          [undefined, '2026-11-08', 1],
          ['invalid-date', '2026-11-08', 1],
          ['2026-11-08', 'invalid-date', 1],
          ['2026-11-08', null, 5],
          ['2026-11-08', undefined, 5],
          ['2026-11-08', 12345, 5],
          ['2026-12-31', '2027-01-01', 10],
          ['2024-02-28', '2024-02-29', 1],
          ['2024-02-29', '2024-03-01', 2]
        ];

        for (const [last, today, cur] of cases) {
          const expected = baselineCalculateStreak(last, today, cur);
          const actual = PomodoroCore.calculateStreak(last, today, cur);
          if (actual !== expected) {
            console.error(`Mismatch for [${last}, ${today}, ${cur}]: expected=${expected}, actual=${actual}`);
            process.exit(1);
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

    def test_calculate_streak_high_volume_results(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const cases = [
          ['2026-11-07', '2026-11-08', 5, 6],
          ['2026-11-08', '2026-11-08', 5, 5],
          ['2026-11-05', '2026-11-08', 5, 1],
          ['invalid-date', '2026-11-08', 5, 1]
        ];
        // Keep the original workload size while checking varied results on every call.
        const totalCalls = 200000;
        for (let i = 0; i < totalCalls; i++) {
          const [lastDate, today, streak, expected] = cases[i % cases.length];
          const actual = PomodoroCore.calculateStreak(lastDate, today, streak);
          if (actual !== expected) {
            console.error(`Incorrect streak for ${lastDate} -> ${today}: ${actual}`);
            process.exit(1);
          }
        }
        console.log('SUCCESS_HIGH_VOLUME_RESULTS');
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS_HIGH_VOLUME_RESULTS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
