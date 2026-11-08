import unittest
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestTimerAndHudEdgeCases(unittest.TestCase):
    def test_format_time_boundary_and_edge_cases(self):
        """
        Verify formatTime handles standard, boundary, fractional, negative,
        and non-finite inputs safely.
        """
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const cases = [
            [1500, '25:00'],
            [65, '01:05'],
            [0, '00:00'],
            [3600, '60:00'],
            [7200, '120:00'],
            [65.8, '01:05'],
            [0.9, '00:00'],
            [-1, '00:00'],
            [-100, '00:00'],
            [NaN, '00:00'],
            [Infinity, '00:00'],
            [-Infinity, '00:00'],
            [null, '00:00'],
            [undefined, '00:00'],
            ['1500', '25:00'],
            ['invalid', '00:00']
        ];

        for (const [input, expected] of cases) {
            const actual = PomodoroCore.formatTime(input);
            if (actual !== expected) {
                console.error(`FAIL formatTime(${input}): expected '${expected}', got '${actual}'`);
                process.exit(1);
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

    def test_calculate_progress_offset_clamping_and_boundaries(self):
        """
        Verify calculateProgressOffset handles full, zero, clamped,
        and invalid duration/circumference values.
        """
        js_code = """
        const { PomodoroCore } = require('./core.js');
        const C = 691.15;

        // Full time -> offset 0
        if (PomodoroCore.calculateProgressOffset(1500, 1500, C) !== 0) {
            console.error('FAIL: full time should have offset 0');
            process.exit(1);
        }

        // Zero time -> offset C
        if (PomodoroCore.calculateProgressOffset(0, 1500, C) !== C) {
            console.error('FAIL: zero time should have offset C');
            process.exit(2);
        }

        // Half time -> offset C/2
        const halfOffset = PomodoroCore.calculateProgressOffset(750, 1500, C);
        if (Math.round(halfOffset) !== Math.round(C / 2)) {
            console.error('FAIL: half time offset mismatch');
            process.exit(3);
        }

        // Clamped: timeLeft > duration -> offset 0
        if (PomodoroCore.calculateProgressOffset(2000, 1500, C) !== 0) {
            console.error('FAIL: timeLeft > duration should clamp to 0 offset');
            process.exit(4);
        }

        // Clamped: timeLeft < 0 -> offset C
        if (PomodoroCore.calculateProgressOffset(-100, 1500, C) !== C) {
            console.error('FAIL: timeLeft < 0 should clamp to full offset C');
            process.exit(5);
        }

        // Invalid duration <= 0 or NaN -> offset 0
        if (PomodoroCore.calculateProgressOffset(1500, 0, C) !== 0 ||
            PomodoroCore.calculateProgressOffset(1500, -10, C) !== 0 ||
            PomodoroCore.calculateProgressOffset(1500, NaN, C) !== 0) {
            console.error('FAIL: invalid duration should return 0');
            process.exit(6);
        }

        // Invalid circumference <= 0 or NaN -> offset 0
        if (PomodoroCore.calculateProgressOffset(1500, 1500, 0) !== 0 ||
            PomodoroCore.calculateProgressOffset(1500, 1500, -5) !== 0 ||
            PomodoroCore.calculateProgressOffset(1500, 1500, NaN) !== 0) {
            console.error('FAIL: invalid circumference should return 0');
            process.exit(7);
        }

        // NaN timeLeft -> treated as 0 -> offset C
        if (PomodoroCore.calculateProgressOffset(NaN, 1500, C) !== C) {
            console.error('FAIL: NaN timeLeft should yield full offset C');
            process.exit(8);
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

    def test_get_next_mode_cycle_transitions_and_edge_cases(self):
        """
        Verify getNextMode alternates between focus, shortBreak, and longBreak (every 4th cycle)
        and guards against non-positive cycle numbers.
        """
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Focus mode cycles 1, 2, 3 -> shortBreak
        if (PomodoroCore.getNextMode('focus', 1) !== 'shortBreak' ||
            PomodoroCore.getNextMode('focus', 2) !== 'shortBreak' ||
            PomodoroCore.getNextMode('focus', 3) !== 'shortBreak') {
            console.error('FAIL: cycles 1-3 should transition to shortBreak');
            process.exit(1);
        }

        // Focus mode cycles 4, 8, 12 -> longBreak
        if (PomodoroCore.getNextMode('focus', 4) !== 'longBreak' ||
            PomodoroCore.getNextMode('focus', 8) !== 'longBreak' ||
            PomodoroCore.getNextMode('focus', 12) !== 'longBreak') {
            console.error('FAIL: cycles 4, 8, 12 should transition to longBreak');
            process.exit(2);
        }

        // Break modes always transition to focus
        if (PomodoroCore.getNextMode('shortBreak', 4) !== 'focus' ||
            PomodoroCore.getNextMode('longBreak', 4) !== 'focus') {
            console.error('FAIL: break modes should transition to focus');
            process.exit(3);
        }

        // Guard against non-positive, NaN, and invalid cycle counts
        if (PomodoroCore.getNextMode('focus', 0) !== 'shortBreak' ||
            PomodoroCore.getNextMode('focus', -4) !== 'shortBreak' ||
            PomodoroCore.getNextMode('focus', NaN) !== 'shortBreak' ||
            PomodoroCore.getNextMode('focus', 'invalid') !== 'shortBreak') {
            console.error('FAIL: non-positive/invalid cycle counts should default to shortBreak');
            process.exit(4);
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

    def test_format_session_label_boundaries_and_fallbacks(self):
        """
        Verify formatSessionLabel pads single digits and falls back safely
        for invalid or non-numeric cycle counts.
        """
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (PomodoroCore.formatSessionLabel(1) !== 'SESSION 01 // DEEP WORK') process.exit(1);
        if (PomodoroCore.formatSessionLabel(9) !== 'SESSION 09 // DEEP WORK') process.exit(2);
        if (PomodoroCore.formatSessionLabel(10) !== 'SESSION 10 // DEEP WORK') process.exit(3);
        if (PomodoroCore.formatSessionLabel(100) !== 'SESSION 100 // DEEP WORK') process.exit(4);
        if (PomodoroCore.formatSessionLabel('4') !== 'SESSION 04 // DEEP WORK') process.exit(5);

        // Fallback cases
        if (PomodoroCore.formatSessionLabel(0) !== 'SESSION 01 // DEEP WORK') process.exit(6);
        if (PomodoroCore.formatSessionLabel(-5) !== 'SESSION 01 // DEEP WORK') process.exit(7);
        if (PomodoroCore.formatSessionLabel(NaN) !== 'SESSION 01 // DEEP WORK') process.exit(8);
        if (PomodoroCore.formatSessionLabel(null) !== 'SESSION 01 // DEEP WORK') process.exit(9);
        if (PomodoroCore.formatSessionLabel(undefined) !== 'SESSION 01 // DEEP WORK') process.exit(10);
        if (PomodoroCore.formatSessionLabel('invalid') !== 'SESSION 01 // DEEP WORK') process.exit(11);

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

    def test_validate_custom_duration_boundaries(self):
        """
        Verify validateCustomDuration validates within min/max bounds
        and falls back to default on boundary violations or invalid input.
        """
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Within range
        if (PomodoroCore.validateCustomDuration(25, 1, 90, 25) !== 25) process.exit(1);

        // Boundaries exact match
        if (PomodoroCore.validateCustomDuration(1, 1, 90, 25) !== 1) process.exit(2);
        if (PomodoroCore.validateCustomDuration(90, 1, 90, 25) !== 90) process.exit(3);

        // Out of boundaries
        if (PomodoroCore.validateCustomDuration(0, 1, 90, 25) !== 25) process.exit(4);
        if (PomodoroCore.validateCustomDuration(91, 1, 90, 25) !== 25) process.exit(5);
        if (PomodoroCore.validateCustomDuration(-10, 1, 90, 25) !== 25) process.exit(6);

        // String numbers
        if (PomodoroCore.validateCustomDuration('45', 1, 90, 25) !== 45) process.exit(7);

        // Invalid inputs fallback to default
        if (PomodoroCore.validateCustomDuration('abc', 1, 90, 25) !== 25) process.exit(8);
        if (PomodoroCore.validateCustomDuration(NaN, 1, 90, 25) !== 25) process.exit(9);
        if (PomodoroCore.validateCustomDuration(null, 1, 90, 25) !== 25) process.exit(10);
        if (PomodoroCore.validateCustomDuration(undefined, 1, 90, 25) !== 25) process.exit(11);

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

    def test_hud_badges_streak_and_focus_formatting(self):
        """
        Verify formatStreakBadge (singular/plural/flooring) and
        formatFocusTimeBadge (minutes display and fallback).
        """
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Streak badge: singular vs plural
        if (PomodoroCore.formatStreakBadge(1) !== '⚡ STREAK: 1 DAY') process.exit(1);
        if (PomodoroCore.formatStreakBadge(2) !== '⚡ STREAK: 2 DAYS') process.exit(2);
        if (PomodoroCore.formatStreakBadge(10) !== '⚡ STREAK: 10 DAYS') process.exit(3);

        // Streak badge: float flooring
        if (PomodoroCore.formatStreakBadge(3.9) !== '⚡ STREAK: 3 DAYS') process.exit(4);

        // Streak badge: fallback for non-positive or invalid
        if (PomodoroCore.formatStreakBadge(0) !== '⚡ STREAK: 1 DAY') process.exit(5);
        if (PomodoroCore.formatStreakBadge(-5) !== '⚡ STREAK: 1 DAY') process.exit(6);
        if (PomodoroCore.formatStreakBadge(NaN) !== '⚡ STREAK: 1 DAY') process.exit(7);
        if (PomodoroCore.formatStreakBadge(null) !== '⚡ STREAK: 1 DAY') process.exit(8);
        if (PomodoroCore.formatStreakBadge('invalid') !== '⚡ STREAK: 1 DAY') process.exit(9);

        // Focus time badge: 0 and positive
        if (PomodoroCore.formatFocusTimeBadge(0) !== '🎯 0 MINS TODAY') process.exit(10);
        if (PomodoroCore.formatFocusTimeBadge(45) !== '🎯 45 MINS TODAY') process.exit(11);
        if (PomodoroCore.formatFocusTimeBadge('60') !== '🎯 60 MINS TODAY') process.exit(12);

        // Focus time badge: negative and invalid fallback
        if (PomodoroCore.formatFocusTimeBadge(-20) !== '🎯 0 MINS TODAY') process.exit(13);
        if (PomodoroCore.formatFocusTimeBadge(NaN) !== '🎯 0 MINS TODAY') process.exit(14);
        if (PomodoroCore.formatFocusTimeBadge(null) !== '🎯 0 MINS TODAY') process.exit(15);
        if (PomodoroCore.formatFocusTimeBadge('xyz') !== '🎯 0 MINS TODAY') process.exit(16);

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

    def test_document_title_and_tab_label_formatting(self):
        """
        Verify formatDocumentTitle (running vs paused) and formatTabLabel
        (mode mapping and minute conversion).
        """
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Document title: running
        if (PomodoroCore.formatDocumentTitle('25:00', true) !== '(25:00) CYBERPUNK FOCUS') process.exit(1);

        // Document title: paused
        if (PomodoroCore.formatDocumentTitle('25:00', false) !== '[PAUSED] (25:00) CYBERPUNK FOCUS') process.exit(2);

        // Document title: fallbacks
        if (PomodoroCore.formatDocumentTitle('', false) !== '[PAUSED] (00:00) CYBERPUNK FOCUS') process.exit(3);
        if (PomodoroCore.formatDocumentTitle('   ', true) !== '(00:00) CYBERPUNK FOCUS') process.exit(4);
        if (PomodoroCore.formatDocumentTitle(null, false) !== '[PAUSED] (00:00) CYBERPUNK FOCUS') process.exit(5);

        // Tab label: modes
        if (PomodoroCore.formatTabLabel('focus', 1500) !== 'FOCUS (25M)') process.exit(6);
        if (PomodoroCore.formatTabLabel('shortBreak', 300) !== 'SHORT (5M)') process.exit(7);
        if (PomodoroCore.formatTabLabel('longBreak', 900) !== 'LONG (15M)') process.exit(8);

        // Tab label: rounding & boundaries
        if (PomodoroCore.formatTabLabel('focus', 65) !== 'FOCUS (1M)') process.exit(9);
        if (PomodoroCore.formatTabLabel('focus', 150) !== 'FOCUS (3M)') process.exit(10);
        if (PomodoroCore.formatTabLabel('focus', 0) !== 'FOCUS (0M)') process.exit(11);
        if (PomodoroCore.formatTabLabel('focus', -30) !== 'FOCUS (0M)') process.exit(12);

        // Tab label: unknown mode fallback
        if (PomodoroCore.formatTabLabel('unknown', 1500) !== 'FOCUS (25M)') process.exit(13);

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

    def test_audio_volume_helpers_and_remaining_seconds(self):
        """
        Verify formatVolumePercent, getVolumeIcon, and calculateRemainingSeconds
        with clamping, muting, and timing boundaries.
        """
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // formatVolumePercent
        if (PomodoroCore.formatVolumePercent(0.5, false) !== '50%') process.exit(1);
        if (PomodoroCore.formatVolumePercent(1.0, false) !== '100%') process.exit(2);
        if (PomodoroCore.formatVolumePercent(0, false) !== '0%') process.exit(3);
        if (PomodoroCore.formatVolumePercent(1.5, false) !== '100%') process.exit(4);
        if (PomodoroCore.formatVolumePercent(-0.2, false) !== '0%') process.exit(5);
        if (PomodoroCore.formatVolumePercent(0.7, true) !== '0%') process.exit(6);

        // getVolumeIcon
        if (PomodoroCore.getVolumeIcon(0.5, false) !== '🔊') process.exit(7);
        if (PomodoroCore.getVolumeIcon(0, false) !== '🔇') process.exit(8);
        if (PomodoroCore.getVolumeIcon(0.5, true) !== '🔇') process.exit(9);
        if (PomodoroCore.getVolumeIcon(0, true) !== '🔇') process.exit(10);

        // calculateRemainingSeconds
        const now = 1700000000000;
        if (PomodoroCore.calculateRemainingSeconds(now + 25000, now) !== 25) process.exit(11);
        if (PomodoroCore.calculateRemainingSeconds(now + 1400, now) !== 1) process.exit(12);
        if (PomodoroCore.calculateRemainingSeconds(now + 1600, now) !== 2) process.exit(13);
        if (PomodoroCore.calculateRemainingSeconds(now, now) !== 0) process.exit(14);
        if (PomodoroCore.calculateRemainingSeconds(now - 5000, now) !== 0) process.exit(15);
        if (PomodoroCore.calculateRemainingSeconds(NaN, now) !== 0) process.exit(16);
        if (PomodoroCore.calculateRemainingSeconds(now + 10000, NaN) !== 0) process.exit(17);

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

    def test_task_and_mission_input_contracts(self):
        """
        Verify sanitizeMission trims/truncates correctly and createTaskItem
        enforces input validation and data model integrity.
        """
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // sanitizeMission trimming & length limit
        if (PomodoroCore.sanitizeMission('   Cyberpunk Mission   ') !== 'Cyberpunk Mission') process.exit(1);
        const longText = 'X'.repeat(120);
        const sanitized = PomodoroCore.sanitizeMission(longText);
        if (sanitized.length !== 80) process.exit(2);

        // sanitizeMission invalid inputs
        if (PomodoroCore.sanitizeMission('') !== '') process.exit(3);
        if (PomodoroCore.sanitizeMission(null) !== '') process.exit(4);
        if (PomodoroCore.sanitizeMission(undefined) !== '') process.exit(5);
        if (PomodoroCore.sanitizeMission(12345) !== '') process.exit(6);

        // createTaskItem valid with explicit id
        const item1 = PomodoroCore.createTaskItem('   Run diagnostic scan   ', 42);
        if (!item1 || item1.id !== 42 || item1.text !== 'Run diagnostic scan' || item1.done !== false) {
            console.error('FAIL: createTaskItem with explicit id failed');
            process.exit(7);
        }

        // createTaskItem valid with generated id
        const item2 = PomodoroCore.createTaskItem('Deploy ICE breaker');
        if (!item2 || typeof item2.id !== 'number' || item2.id <= 0 || item2.text !== 'Deploy ICE breaker') {
            console.error('FAIL: createTaskItem with generated id failed');
            process.exit(8);
        }

        // createTaskItem empty/whitespace rejection
        if (PomodoroCore.createTaskItem('   ') !== null) process.exit(9);
        if (PomodoroCore.createTaskItem('') !== null) process.exit(10);
        if (PomodoroCore.createTaskItem(null) !== null) process.exit(11);

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


if __name__ == '__main__':
    unittest.main()
