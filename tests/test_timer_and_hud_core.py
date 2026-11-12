import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestTimerAndHUDCore(unittest.TestCase):
    def test_format_streak_badge_string_numeric_parsing(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Number inputs
        if (PomodoroCore.formatStreakBadge(1) !== '⚡ STREAK: 1 DAY') {
            console.error('FAIL: 1 day');
            process.exit(1);
        }
        if (PomodoroCore.formatStreakBadge(5) !== '⚡ STREAK: 5 DAYS') {
            console.error('FAIL: 5 days');
            process.exit(2);
        }

        // Numeric string inputs (e.g. from localStorage)
        if (PomodoroCore.formatStreakBadge('5') !== '⚡ STREAK: 5 DAYS') {
            console.error('FAIL: numeric string "5" should parse to 5 DAYS');
            process.exit(3);
        }
        if (PomodoroCore.formatStreakBadge('1') !== '⚡ STREAK: 1 DAY') {
            console.error('FAIL: numeric string "1" should parse to 1 DAY');
            process.exit(4);
        }

        // Non-numeric or invalid inputs fallback to 1 DAY
        if (PomodoroCore.formatStreakBadge(0) !== '⚡ STREAK: 1 DAY') {
            console.error('FAIL: 0 streak');
            process.exit(5);
        }
        if (PomodoroCore.formatStreakBadge(null) !== '⚡ STREAK: 1 DAY') {
            console.error('FAIL: null streak');
            process.exit(6);
        }
        if (PomodoroCore.formatStreakBadge('abc') !== '⚡ STREAK: 1 DAY') {
            console.error('FAIL: abc streak');
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

    def test_hud_badges_fall_back_for_symbol_inputs(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (PomodoroCore.formatStreakBadge(Symbol('invalid')) !== '⚡ STREAK: 1 DAY') process.exit(1);
        if (PomodoroCore.formatFocusTimeBadge(Symbol('invalid')) !== '🎯 0 MINS TODAY') process.exit(2);

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

    def test_calculate_remaining_seconds_non_finite_boundaries(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const now = 1700000000000;
        if (PomodoroCore.calculateRemainingSeconds(now + 25000, now) !== 25) {
            console.error('FAIL: 25s future');
            process.exit(1);
        }
        if (PomodoroCore.calculateRemainingSeconds(now, now) !== 0) {
            console.error('FAIL: exact now');
            process.exit(2);
        }
        if (PomodoroCore.calculateRemainingSeconds(now - 5000, now) !== 0) {
            console.error('FAIL: past time');
            process.exit(3);
        }
        // Non-finite guards: Infinity should return 0, not Infinity
        if (PomodoroCore.calculateRemainingSeconds(Infinity, now) !== 0) {
            console.error('FAIL: target Infinity must return 0');
            process.exit(4);
        }
        if (PomodoroCore.calculateRemainingSeconds(now + 10000, -Infinity) !== 0) {
            console.error('FAIL: now -Infinity must return 0');
            process.exit(5);
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

    def test_calculate_progress_offset_boundaries(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const C = 691.15;
        // Normal full and zero
        if (PomodoroCore.calculateProgressOffset(1500, 1500, C) !== 0) {
            console.error('FAIL: full time offset should be 0');
            process.exit(1);
        }
        if (PomodoroCore.calculateProgressOffset(0, 1500, C) !== C) {
            console.error('FAIL: zero time offset should be C');
            process.exit(2);
        }
        // Clamping: timeLeft > duration
        if (PomodoroCore.calculateProgressOffset(2000, 1500, C) !== 0) {
            console.error('FAIL: timeLeft > duration should clamp to 0 offset');
            process.exit(3);
        }
        // Clamping: negative timeLeft
        if (PomodoroCore.calculateProgressOffset(-100, 1500, C) !== C) {
            console.error('FAIL: negative timeLeft should clamp to C');
            process.exit(4);
        }
        // Non-finite or invalid duration/circumference
        if (PomodoroCore.calculateProgressOffset(1500, 0, C) !== 0) {
            console.error('FAIL: zero duration');
            process.exit(5);
        }
        if (PomodoroCore.calculateProgressOffset(1500, Infinity, C) !== 0) {
            console.error('FAIL: Infinity duration');
            process.exit(6);
        }
        if (PomodoroCore.calculateProgressOffset(1500, 1500, Infinity) !== 0) {
            console.error('FAIL: Infinity circumference');
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

    def test_get_next_mode_transitions(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Focus cycles
        if (PomodoroCore.getNextMode('focus', 1) !== 'shortBreak') process.exit(1);
        if (PomodoroCore.getNextMode('focus', 2) !== 'shortBreak') process.exit(2);
        if (PomodoroCore.getNextMode('focus', 3) !== 'shortBreak') process.exit(3);
        if (PomodoroCore.getNextMode('focus', 4) !== 'longBreak') process.exit(4);
        if (PomodoroCore.getNextMode('focus', 8) !== 'longBreak') process.exit(5);
        if (PomodoroCore.getNextMode('focus', '4') !== 'longBreak') process.exit(6);
        if (PomodoroCore.getNextMode('focus', 0) !== 'shortBreak') process.exit(7);
        if (PomodoroCore.getNextMode('focus', -4) !== 'shortBreak') process.exit(8);

        // Break transitions back to focus
        if (PomodoroCore.getNextMode('shortBreak', 1) !== 'focus') process.exit(9);
        if (PomodoroCore.getNextMode('longBreak', 4) !== 'focus') process.exit(10);
        if (PomodoroCore.getNextMode('unknown', 4) !== 'focus') process.exit(11);

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

    def test_get_next_mode_falls_back_for_symbol_cycle_count(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (PomodoroCore.getNextMode('focus', Symbol('invalid')) !== 'shortBreak') process.exit(1);
        if (PomodoroCore.getNextMode('shortBreak', Symbol('invalid')) !== 'focus') process.exit(2);

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

    def test_format_document_title_states(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (PomodoroCore.formatDocumentTitle('25:00', true) !== '(25:00) CYBERPUNK FOCUS') process.exit(1);
        if (PomodoroCore.formatDocumentTitle('25:00', false) !== '[PAUSED] (25:00) CYBERPUNK FOCUS') process.exit(2);
        if (PomodoroCore.formatDocumentTitle('', false) !== '[PAUSED] (00:00) CYBERPUNK FOCUS') process.exit(3);
        if (PomodoroCore.formatDocumentTitle(null, true) !== '(00:00) CYBERPUNK FOCUS') process.exit(4);
        if (PomodoroCore.formatDocumentTitle('   ', true) !== '(00:00) CYBERPUNK FOCUS') process.exit(5);

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

    def test_format_session_label_boundaries(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (PomodoroCore.formatSessionLabel(1) !== 'SESSION 01 // DEEP WORK') process.exit(1);
        if (PomodoroCore.formatSessionLabel(9) !== 'SESSION 09 // DEEP WORK') process.exit(2);
        if (PomodoroCore.formatSessionLabel(10) !== 'SESSION 10 // DEEP WORK') process.exit(3);
        if (PomodoroCore.formatSessionLabel(100) !== 'SESSION 100 // DEEP WORK') process.exit(4);
        if (PomodoroCore.formatSessionLabel('5') !== 'SESSION 05 // DEEP WORK') process.exit(5);
        if (PomodoroCore.formatSessionLabel(0) !== 'SESSION 01 // DEEP WORK') process.exit(6);
        if (PomodoroCore.formatSessionLabel(-2) !== 'SESSION 01 // DEEP WORK') process.exit(7);
        if (PomodoroCore.formatSessionLabel(null) !== 'SESSION 01 // DEEP WORK') process.exit(8);
        if (PomodoroCore.formatSessionLabel('abc') !== 'SESSION 01 // DEEP WORK') process.exit(9);
        if (PomodoroCore.formatSessionLabel(Symbol('invalid')) !== 'SESSION 01 // DEEP WORK') process.exit(10);

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
