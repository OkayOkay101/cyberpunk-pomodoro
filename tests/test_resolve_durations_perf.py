import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestResolveDurationsPerformance(unittest.TestCase):
    def test_resolve_durations_avoids_repeated_string_conversions(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const fnStr = PomodoroCore.resolveDurations.toString();
        // The unoptimized implementation repeatedly converts numbers to strings using String(f) on every call
        if (/cp_cfg_focus:\\s*String\\(f\\)/.test(fnStr)) {
            console.error('FAIL: resolveDurations still calls String(f) dynamically instead of using precomputed NUM_STRINGS lookup');
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

    def test_resolve_durations_exact_equality_with_baseline(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        function baselineValidateCustomDuration(val, min, max, defaultVal) {
            const num = parseInt(val, 10);
            if (isNaN(num) || num < min || num > max) return defaultVal;
            return num;
        }

        function baselineResolveDurations(inputs) {
            const raw = (inputs && typeof inputs === 'object' && !Array.isArray(inputs)) ? inputs : {};
            const f = baselineValidateCustomDuration(raw.focus, 1, 90, 25);
            const s = baselineValidateCustomDuration(raw.shortBreak, 1, 30, 5);
            const l = baselineValidateCustomDuration(raw.longBreak, 1, 60, 15);
            return {
                focus: f * 60,
                shortBreak: s * 60,
                longBreak: l * 60,
                minutes: { focus: f, shortBreak: s, longBreak: l },
                storage: {
                    cp_cfg_focus: String(f),
                    cp_cfg_short: String(s),
                    cp_cfg_long: String(l)
                }
            };
        }

        const cases = [
            undefined,
            null,
            {},
            [],
            [1, 2, 3],
            'invalid-string',
            12345,
            false,
            true,
            { focus: 25, shortBreak: 5, longBreak: 15 },
            { focus: '25', shortBreak: '5', longBreak: '15' },
            { focus: 50, shortBreak: 10, longBreak: 25 },
            { focus: '50', shortBreak: '10', longBreak: '25' },
            { focus: 1, shortBreak: 1, longBreak: 1 },
            { focus: 90, shortBreak: 30, longBreak: 60 },
            { focus: 120, shortBreak: 0, longBreak: -5 },
            { focus: -10, shortBreak: 50, longBreak: 100 },
            { focus: NaN, shortBreak: Infinity, longBreak: -Infinity },
            { focus: 'abc', shortBreak: null, longBreak: undefined },
            { focus: '45min', shortBreak: '8min', longBreak: '20min' },
            { focus: 25.9, shortBreak: 5.2, longBreak: 15.8 },
            { focus: ' 25 ', shortBreak: ' 5 ', longBreak: ' 15 ' },
            { otherKey: 99 }
        ];

        for (const c of cases) {
            const expected = baselineResolveDurations(c);
            const actual = PomodoroCore.resolveDurations(c);
            if (JSON.stringify(actual) !== JSON.stringify(expected)) {
                console.error(`Equality mismatch on ${JSON.stringify(c)}: expected=${JSON.stringify(expected)}, actual=${JSON.stringify(actual)}`);
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

    def test_resolve_durations_high_volume_throughput(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const iters = 200000;
        const start = performance.now();
        for (let i = 0; i < iters; i++) {
            PomodoroCore.resolveDurations();
            PomodoroCore.resolveDurations({ focus: '25', shortBreak: '5', longBreak: '15' });
            PomodoroCore.resolveDurations({ focus: 50, shortBreak: 10, longBreak: 20 });
        }
        const elapsed = performance.now() - start;

        // 600,000 calls should easily complete in well under 1000ms
        if (elapsed > 1000) {
            console.error(`Throughput failed: 600k calls took ${elapsed.toFixed(2)}ms (expected < 1000ms)`);
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
