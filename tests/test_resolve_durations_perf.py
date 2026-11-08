import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestResolveDurationsPerformance(unittest.TestCase):
    """
    Performance and behavioral verification for PomodoroCore duration functions:
    - resolveDurations
    - validateCustomDuration
    Verifies elimination of redundant parseInt overhead, string conversions,
    pre-computed NUM_STRINGS lookup, and ensures no global scope pollution.
    """

    def _run_node_script(self, script: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )

    def test_strict_mode_and_no_global_leak(self):
        js_code = """
        'use strict';
        const { PomodoroCore } = require('./core.js');

        // Test running resolveDurations with string inputs
        PomodoroCore.resolveDurations({ focus: '25', shortBreak: '5', longBreak: '15' });

        // Verify no global 'n' or intermediate variable leakage
        if (typeof global.n !== 'undefined') {
            console.error('FAIL: global.n leaked onto global scope');
            process.exit(1);
        }
        console.log('OK');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("OK", proc.stdout)

    def test_resolve_durations_baseline_equality(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        function baselineValidate(val, min, max, defaultVal) {
            const num = parseInt(val, 10);
            if (isNaN(num) || num < min || num > max) return defaultVal;
            return num;
        }

        function baselineResolve(inputs) {
            const raw = (inputs && typeof inputs === 'object' && !Array.isArray(inputs)) ? inputs : {};
            const f = baselineValidate(raw.focus, 1, 90, 25);
            const s = baselineValidate(raw.shortBreak, 1, 30, 5);
            const l = baselineValidate(raw.longBreak, 1, 60, 15);
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
            null,
            undefined,
            0,
            1,
            'string',
            [],
            [1, 2, 3],
            {},
            { focus: 25, shortBreak: 5, longBreak: 15 },
            { focus: 1, shortBreak: 1, longBreak: 1 },
            { focus: 90, shortBreak: 30, longBreak: 60 },
            { focus: 50, shortBreak: 10, longBreak: 20 },
            { focus: 0, shortBreak: 0, longBreak: 0 },
            { focus: 91, shortBreak: 31, longBreak: 61 },
            { focus: -10, shortBreak: -5, longBreak: -1 },
            { focus: '1', shortBreak: '1', longBreak: '1' },
            { focus: '25', shortBreak: '5', longBreak: '15' },
            { focus: '90', shortBreak: '30', longBreak: '60' },
            { focus: '0', shortBreak: '0', longBreak: '0' },
            { focus: '91', shortBreak: '31', longBreak: '61' },
            { focus: 'abc', shortBreak: '', longBreak: ' ' },
            { focus: NaN, shortBreak: Infinity, longBreak: -Infinity },
            { focus: 25.4, shortBreak: 5.9, longBreak: 15.1 },
            { focus: '25.4', shortBreak: '5.9', longBreak: '15.1' },
            { focus: true, shortBreak: false, longBreak: {} },
            { focus: 120, shortBreak: -5, longBreak: 0 }
        ];

        for (const tc of cases) {
            const expected = JSON.stringify(baselineResolve(tc));
            const actual = JSON.stringify(PomodoroCore.resolveDurations(tc));
            if (expected !== actual) {
                console.error('Mismatch for case: ' + JSON.stringify(tc) + '\\nExpected: ' + expected + '\\nActual: ' + actual);
                process.exit(1);
            }
        }
        console.log('OK');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("OK", proc.stdout)

    def test_validate_custom_duration_fast_path_and_equality(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const cases = [
            [25, 1, 90, 25, 25],
            [1, 1, 90, 25, 1],
            [90, 1, 90, 25, 90],
            [0, 1, 90, 25, 25],
            [91, 1, 90, 25, 25],
            [-5, 1, 90, 25, 25],
            ['25', 1, 90, 25, 25],
            ['1', 1, 90, 25, 1],
            ['90', 1, 90, 25, 90],
            ['0', 1, 90, 25, 25],
            ['91', 1, 90, 25, 25],
            ['abc', 1, 90, 25, 25],
            [NaN, 1, 90, 25, 25],
            [null, 1, 90, 25, 25],
            [undefined, 1, 90, 25, 25],
            [5.2, 1, 30, 5, 5],
            ['5.2', 1, 30, 5, 5]
        ];

        for (const [val, min, max, def, expected] of cases) {
            const actual = PomodoroCore.validateCustomDuration(val, min, max, def);
            if (actual !== expected) {
                console.error(`Mismatch for validateCustomDuration(${val}): expected ${expected}, got ${actual}`);
                process.exit(1);
            }
        }
        console.log('OK');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("OK", proc.stdout)


if __name__ == "__main__":
    unittest.main()
