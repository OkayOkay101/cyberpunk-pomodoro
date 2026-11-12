import unittest
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestStreakEdgeCases(unittest.TestCase):
    def test_symbol_today_date_falls_back_to_one(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const streak = PomodoroCore.calculateStreak('2026-11-07', Symbol('today'), 4);
        if (streak !== 1) {
            console.error('FAIL: invalid today date should reset streak to 1, got ' + streak);
            process.exit(1);
        }

        console.log('SUCCESS');
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_non_finite_stored_streak_falls_back_to_one(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const oversizedStoredStreak = '9'.repeat(400);
        const refreshed = PomodoroCore.refreshDailyStats(
          '2026-11-08', '2026-11-08', '25', oversizedStoredStreak
        );
        if (refreshed.currentStreak !== 1) {
            console.error('FAIL: non-finite stored streak should fall back to 1, got ' + refreshed.currentStreak);
            process.exit(1);
        }
        if (PomodoroCore.calculateStreak('2026-11-07', '2026-11-08', Infinity) !== 2) {
            console.error('FAIL: non-finite streak should use fallback 1 before incrementing');
            process.exit(2);
        }

        console.log('SUCCESS');
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_streak_future_last_date_does_not_increment(self):
        """
        If lastDateStr is in the future (data corruption or timezone issue),
        streak should not increment. Current behavior returns validStreak.
        """
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // lastDate is tomorrow, today is today -> diffDays = -1
        // Should not increment streak, should return current streak (or 1)
        const streak = PomodoroCore.calculateStreak('2026-11-09', '2026-11-08', 5);
        // Current implementation returns validStreak (5) for diffDays <= 0
        // This test documents current behavior
        if (streak !== 5) {
            console.error('FAIL: expected streak 5 for future lastDate, got ' + streak);
            process.exit(1);
        }

        console.log('SUCCESS');
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_streak_same_day_different_format(self):
        """
        Test that streak handles date strings consistently.
        """
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Same day with leading zeros
        const streak1 = PomodoroCore.calculateStreak('2026-1-8', '2026-01-08', 3);
        // Non-padded month/day might not match string comparison
        // getLocalDateString always pads, so this tests robustness
        if (streak1 !== 3) {
            console.error('FAIL: expected streak 3 for same day different format, got ' + streak1);
            process.exit(1);
        }

        console.log('SUCCESS');
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_get_local_date_string_invalid_input(self):
        """
        Test getLocalDateString with invalid date input.
        """
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Invalid date should not crash
        const result1 = PomodoroCore.getLocalDateString(new Date('invalid'));
        if (!/^\\d{4}-\\d{2}-\\d{2}$/.test(result1)) {
            console.error('FAIL: invalid date input returned malformed string: ' + result1);
            process.exit(1);
        }

        // Null input uses default (current date)
        const result2 = PomodoroCore.getLocalDateString(null);
        if (!/^\\d{4}-\\d{2}-\\d{2}$/.test(result2)) {
            console.error('FAIL: null input returned malformed string: ' + result2);
            process.exit(2);
        }

        console.log('SUCCESS');
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_streak_dst_boundary_simulation(self):
        """
        Simulate DST boundary by using dates that would have different offsets.
        Since we parse YYYY-MM-DD as UTC, this tests that the calculation
        is consistent regardless of DST.
        """
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // These dates straddle a typical DST transition (March/November)
        // But since we parse as UTC, DST shouldn't affect the day count
        const streak1 = PomodoroCore.calculateStreak('2026-03-07', '2026-03-08', 1);  // DST start in US
        if (streak1 !== 2) {
            console.error('FAIL: DST start boundary streak should be 2, got ' + streak1);
            process.exit(1);
        }

        const streak2 = PomodoroCore.calculateStreak('2026-11-01', '2026-11-02', 1);  // DST end in US
        if (streak2 !== 2) {
            console.error('FAIL: DST end boundary streak should be 2, got ' + streak2);
            process.exit(2);
        }

        console.log('SUCCESS');
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_daily_focus_mins_future_date(self):
        """
        Test calculateDailyFocusMins with future lastDateStr.
        Should return 0 since dates don't match.
        """
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const mins = PomodoroCore.calculateDailyFocusMins('2026-11-09', '2026-11-08', '45');
        if (mins !== 0) {
            console.error('FAIL: expected 0 for future lastDate, got ' + mins);
            process.exit(1);
        }

        console.log('SUCCESS');
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
