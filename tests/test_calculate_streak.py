import os
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestCalculateStreak(unittest.TestCase):
    def test_streak_basic_consecutive_days(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Day 1 -> Day 2 (consecutive)
        const streak1 = PomodoroCore.calculateStreak('2026-11-07', '2026-11-08', 1);
        if (streak1 !== 2) {
            console.error('FAIL: expected streak 2 for consecutive days, got ' + streak1);
            process.exit(1);
        }

        // Day 1 -> Day 3 (gap of 1 day, streak resets)
        const streak2 = PomodoroCore.calculateStreak('2026-11-07', '2026-11-09', 1);
        if (streak2 !== 1) {
            console.error('FAIL: expected streak 1 for gap > 1 day, got ' + streak2);
            process.exit(2);
        }

        // Same day (no change)
        const streak3 = PomodoroCore.calculateStreak('2026-11-08', '2026-11-08', 3);
        if (streak3 !== 3) {
            console.error('FAIL: expected streak 3 for same day, got ' + streak3);
            process.exit(3);
        }

        // No last date (first time)
        const streak4 = PomodoroCore.calculateStreak('', '2026-11-08', 1);
        if (streak4 !== 1) {
            console.error('FAIL: expected streak 1 for no last date, got ' + streak4);
            process.exit(4);
        }

        // Invalid currentStreak (should default to 1)
        const streak5 = PomodoroCore.calculateStreak('2026-11-07', '2026-11-08', NaN);
        if (streak5 !== 2) {
            console.error('FAIL: expected streak 2 for invalid currentStreak, got ' + streak5);
            process.exit(5);
        }

        const streak6 = PomodoroCore.calculateStreak('2026-11-07', '2026-11-08', 0);
        if (streak6 !== 2) {
            console.error('FAIL: expected streak 2 for zero currentStreak, got ' + streak6);
            process.exit(6);
        }

        const streak7 = PomodoroCore.calculateStreak('2026-11-07', '2026-11-08', -5);
        if (streak7 !== 2) {
            console.error('FAIL: expected streak 2 for negative currentStreak, got ' + streak7);
            process.exit(7);
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

    def test_streak_timezone_edge_case(self):
        """
        Verify streak behavior using local dates under a non-UTC timezone.
        """
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // These instants fall on different local dates in Los Angeles,
        // although both are on November 8 in UTC.
        const lastDate = PomodoroCore.getLocalDateString(new Date('2026-11-08T07:30:00Z'));
        const today = PomodoroCore.getLocalDateString(new Date('2026-11-08T08:30:00Z'));
        if (lastDate !== '2026-11-07' || today !== '2026-11-08') {
            console.error('FAIL: expected consecutive Los Angeles local dates, got ' + lastDate + ' and ' + today);
            process.exit(1);
        }

        // Both dates are local date strings, streak should increment
        const streak = PomodoroCore.calculateStreak(lastDate, today, 1);
        if (streak !== 2) {
            console.error('FAIL: streak should be 2 for consecutive local dates, got ' + streak);
            process.exit(1);
        }

        console.log('SUCCESS');
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            env={**os.environ, "TZ": "America/Los_Angeles"}
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_daily_focus_mins(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Same day -> returns stored minutes
        const mins1 = PomodoroCore.calculateDailyFocusMins('2026-11-08', '2026-11-08', '45');
        if (mins1 !== 45) {
            console.error('FAIL: expected 45 mins for same day, got ' + mins1);
            process.exit(1);
        }

        // Different day -> returns 0
        const mins2 = PomodoroCore.calculateDailyFocusMins('2026-11-07', '2026-11-08', '45');
        if (mins2 !== 0) {
            console.error('FAIL: expected 0 mins for different day, got ' + mins2);
            process.exit(2);
        }

        // No last date -> returns 0
        const mins3 = PomodoroCore.calculateDailyFocusMins('', '2026-11-08', '45');
        if (mins3 !== 0) {
            console.error('FAIL: expected 0 mins for no last date, got ' + mins3);
            process.exit(3);
        }

        // Invalid stored mins -> returns 0
        const mins4 = PomodoroCore.calculateDailyFocusMins('2026-11-08', '2026-11-08', 'abc');
        if (mins4 !== 0) {
            console.error('FAIL: expected 0 mins for invalid stored, got ' + mins4);
            process.exit(4);
        }

        const mins5 = PomodoroCore.calculateDailyFocusMins('2026-11-08', '2026-11-08', '-10');
        if (mins5 !== 0) {
            console.error('FAIL: expected 0 mins for negative stored, got ' + mins5);
            process.exit(5);
        }

        const mins6 = PomodoroCore.calculateDailyFocusMins('2026-11-08', '2026-11-08', '0');
        if (mins6 !== 0) {
            console.error('FAIL: expected 0 mins for zero stored, got ' + mins6);
            process.exit(6);
        }

        // Corrupted persisted values must not be partially parsed as real minutes.
        for (const invalid of ['45junk', '1e2', '45.5', '9'.repeat(400)]) {
            if (PomodoroCore.calculateDailyFocusMins('2026-11-08', '2026-11-08', invalid) !== 0) {
                console.error('FAIL: expected 0 mins for malformed stored value', invalid);
                process.exit(7);
            }
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

    def test_get_local_date_string_format(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const dateStr = PomodoroCore.getLocalDateString(new Date('2026-11-08T12:00:00'));
        if (dateStr !== '2026-11-08') {
            console.error('FAIL: expected 2026-11-08, got ' + dateStr);
            process.exit(1);
        }

        // Test with date object at midnight UTC
        const dateStr2 = PomodoroCore.getLocalDateString(new Date('2026-11-08T00:00:00Z'));
        // This depends on local timezone, but should be a valid YYYY-MM-DD
        if (!/^\\d{4}-\\d{2}-\\d{2}$/.test(dateStr2)) {
            console.error('FAIL: invalid date format: ' + dateStr2);
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


if __name__ == "__main__":
    unittest.main()
