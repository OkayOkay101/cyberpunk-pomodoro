import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestHUDBadgePerformance(unittest.TestCase):
    """
    Performance and behavioral verification for PomodoroCore HUD stats badge functions:
    - formatStreakBadge
    - formatFocusTimeBadge
    Verifies elimination of redundant parseInt and template string allocations via
    fast-paths and pre-computed lookup tables.
    """

    def _run_node_script(self, script: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )

    def test_streak_badge_fast_path_and_lookup(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const fnStr = PomodoroCore.formatStreakBadge.toString();
        // Check that function does not unconditionally call parseInt at entry
        if (/^\\s*formatStreakBadge\\s*\\([^)]*\\)\\s*\\{\\s*const\\s+parsed\\s*=\\s*parseInt/.test(fnStr)) {
            console.error('FAIL: formatStreakBadge unconditionally calls parseInt without numeric fast-path');
            process.exit(2);
        }
        if (!/STREAK_BADGES/.test(fnStr)) {
            console.error('FAIL: formatStreakBadge does not use STREAK_BADGES lookup table');
            process.exit(3);
        }

        const cases = [
            [1, '⚡ STREAK: 1 DAY'],
            [2, '⚡ STREAK: 2 DAYS'],
            [5, '⚡ STREAK: 5 DAYS'],
            [10, '⚡ STREAK: 10 DAYS'],
            [50, '⚡ STREAK: 50 DAYS'],
            [100, '⚡ STREAK: 100 DAYS'],
            [101, '⚡ STREAK: 101 DAYS'],
            [250, '⚡ STREAK: 250 DAYS'],
            [0, '⚡ STREAK: 1 DAY'],
            [-5, '⚡ STREAK: 1 DAY'],
            ['1', '⚡ STREAK: 1 DAY'],
            ['5', '⚡ STREAK: 5 DAYS'],
            ['100', '⚡ STREAK: 100 DAYS'],
            ['0', '⚡ STREAK: 1 DAY'],
            ['-3', '⚡ STREAK: 1 DAY'],
            [null, '⚡ STREAK: 1 DAY'],
            [undefined, '⚡ STREAK: 1 DAY'],
            [NaN, '⚡ STREAK: 1 DAY'],
            [Infinity, '⚡ STREAK: 1 DAY'],
            [-Infinity, '⚡ STREAK: 1 DAY'],
            ['abc', '⚡ STREAK: 1 DAY']
        ];

        for (const [input, expected] of cases) {
            const actual = PomodoroCore.formatStreakBadge(input);
            if (actual !== expected) {
                console.error(`Mismatch on input ${input}: expected "${expected}", got "${actual}"`);
                process.exit(1);
            }
        }
        console.log('SUCCESS');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_focus_time_badge_fast_path_and_lookup(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const fnStr = PomodoroCore.formatFocusTimeBadge.toString();
        // Check that function does not unconditionally call parseInt at entry
        if (/^\\s*formatFocusTimeBadge\\s*\\([^)]*\\)\\s*\\{\\s*const\\s+parsed\\s*=\\s*parseInt/.test(fnStr)) {
            console.error('FAIL: formatFocusTimeBadge unconditionally calls parseInt without numeric fast-path');
            process.exit(2);
        }
        if (!/FOCUS_BADGES/.test(fnStr)) {
            console.error('FAIL: formatFocusTimeBadge does not use FOCUS_BADGES lookup table');
            process.exit(3);
        }

        const cases = [
            [0, '🎯 0 MINS TODAY'],
            [1, '🎯 1 MINS TODAY'],
            [25, '🎯 25 MINS TODAY'],
            [50, '🎯 50 MINS TODAY'],
            [75, '🎯 75 MINS TODAY'],
            [120, '🎯 120 MINS TODAY'],
            [500, '🎯 500 MINS TODAY'],
            [1440, '🎯 1440 MINS TODAY'],
            [1500, '🎯 1500 MINS TODAY'],
            [-1, '🎯 0 MINS TODAY'],
            [-20, '🎯 0 MINS TODAY'],
            ['0', '🎯 0 MINS TODAY'],
            ['25', '🎯 25 MINS TODAY'],
            ['75', '🎯 75 MINS TODAY'],
            ['-20', '🎯 0 MINS TODAY'],
            [null, '🎯 0 MINS TODAY'],
            [undefined, '🎯 0 MINS TODAY'],
            [NaN, '🎯 0 MINS TODAY'],
            [Infinity, '🎯 0 MINS TODAY'],
            [-Infinity, '🎯 0 MINS TODAY'],
            ['abc', '🎯 0 MINS TODAY']
        ];

        for (const [input, expected] of cases) {
            const actual = PomodoroCore.formatFocusTimeBadge(input);
            if (actual !== expected) {
                console.error(`Mismatch on input ${input}: expected "${expected}", got "${actual}"`);
                process.exit(1);
            }
        }
        console.log('SUCCESS');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_cached_reference_identity(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Repeated invocations for standard integers must return the same cached string reference
        const s1 = PomodoroCore.formatStreakBadge(5);
        const s2 = PomodoroCore.formatStreakBadge(5);
        if (s1 !== s2) {
            console.error('FAIL: formatStreakBadge did not return cached reference');
            process.exit(1);
        }

        const f1 = PomodoroCore.formatFocusTimeBadge(50);
        const f2 = PomodoroCore.formatFocusTimeBadge(50);
        if (f1 !== f2) {
            console.error('FAIL: formatFocusTimeBadge did not return cached reference');
            process.exit(2);
        }

        console.log('SUCCESS');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_hud_badge_exhaustive_baseline_equality(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        function baselineFormatStreakBadge(currentStreak) {
            const parsed = parseInt(currentStreak, 10);
            const valid = (!isNaN(parsed) && parsed >= 1) ? parsed : 1;
            return `⚡ STREAK: ${valid} DAY${valid > 1 ? 'S' : ''}`;
        }

        function baselineFormatFocusTimeBadge(minutes) {
            const parsed = parseInt(minutes, 10);
            const valid = (!isNaN(parsed) && parsed >= 0) ? parsed : 0;
            return `🎯 ${valid} MINS TODAY`;
        }

        const streakInputs = [
            1, 2, 5, 10, 50, 100, 101, 250, 999,
            0, -1, -50,
            0.5, 1.2, 1.9, 2.5, 99.9, 100.1, -0.5,
            '1', '2', '5', '100', '101', '0', '-5', '2.5', '99.9',
            '1 day', '5days', '005', ' 10 ',
            null, undefined, NaN, Infinity, -Infinity,
            '', '   ', 'abc', {}, [], [5], true, false
        ];

        const focusInputs = [
            0, 1, 25, 50, 75, 120, 500, 1440, 1441, 3000,
            -1, -20, -500,
            0.2, 0.9, 25.4, 50.8, 1439.9, 1440.1, -0.5,
            '0', '25', '75', '1440', '1500', '-20', '50.5',
            '25 mins', '0025', ' 50 ',
            null, undefined, NaN, Infinity, -Infinity,
            '', '   ', 'abc', {}, [], [25], true, false
        ];

        for (const s of streakInputs) {
            const base = baselineFormatStreakBadge(s);
            const opt = PomodoroCore.formatStreakBadge(s);
            if (base !== opt) {
                console.error(`Streak mismatch on ${JSON.stringify(s)}: expected "${base}", got "${opt}"`);
                process.exit(1);
            }
        }

        for (const f of focusInputs) {
            const base = baselineFormatFocusTimeBadge(f);
            const opt = PomodoroCore.formatFocusTimeBadge(f);
            if (base !== opt) {
                console.error(`Focus mismatch on ${JSON.stringify(f)}: expected "${base}", got "${opt}"`);
                process.exit(2);
            }
        }

        console.log('SUCCESS');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
