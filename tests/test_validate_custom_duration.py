import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestValidateCustomDuration(unittest.TestCase):
    """Unit tests for PomodoroCore.validateCustomDuration function."""

    def _run_node(self, js_code: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )

    def test_validate_custom_duration_valid_inputs(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (typeof PomodoroCore.validateCustomDuration !== 'function') {
            console.error('FAIL: validateCustomDuration is not a function');
            process.exit(1);
        }

        // Valid numeric inputs within bounds
        if (PomodoroCore.validateCustomDuration(25, 1, 90, 25) !== 25) process.exit(2);
        if (PomodoroCore.validateCustomDuration(1, 1, 90, 25) !== 1) process.exit(3);
        if (PomodoroCore.validateCustomDuration(90, 1, 90, 25) !== 90) process.exit(4);
        if (PomodoroCore.validateCustomDuration(5, 1, 30, 5) !== 5) process.exit(5);
        if (PomodoroCore.validateCustomDuration(15, 1, 60, 15) !== 15) process.exit(6);

        // Numeric string inputs (from localStorage/config)
        if (PomodoroCore.validateCustomDuration('25', 1, 90, 25) !== 25) process.exit(7);
        if (PomodoroCore.validateCustomDuration('5', 1, 30, 5) !== 5) process.exit(8);
        if (PomodoroCore.validateCustomDuration('15', 1, 60, 15) !== 15) process.exit(9);
        if (PomodoroCore.validateCustomDuration(' 45 ', 1, 90, 25) !== 45) process.exit(10);

        // Decimal strings are REJECTED (stricter validation) - fallback to default
        if (PomodoroCore.validateCustomDuration('25.9', 1, 90, 25) !== 25) process.exit(11);
        if (PomodoroCore.validateCustomDuration('5.2', 1, 30, 5) !== 5) process.exit(12);
        if (PomodoroCore.validateCustomDuration('15.8', 1, 60, 15) !== 15) process.exit(13);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_validate_custom_duration_out_of_bounds(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Below minimum
        if (PomodoroCore.validateCustomDuration(0, 1, 90, 25) !== 25) process.exit(1);
        if (PomodoroCore.validateCustomDuration(-1, 1, 90, 25) !== 25) process.exit(2);
        if (PomodoroCore.validateCustomDuration(-100, 1, 90, 25) !== 25) process.exit(3);

        // Above maximum
        if (PomodoroCore.validateCustomDuration(91, 1, 90, 25) !== 25) process.exit(4);
        if (PomodoroCore.validateCustomDuration(120, 1, 90, 25) !== 25) process.exit(5);
        if (PomodoroCore.validateCustomDuration(999, 1, 90, 25) !== 25) process.exit(6);

        // Out of bounds string numbers
        if (PomodoroCore.validateCustomDuration('0', 1, 90, 25) !== 25) process.exit(7);
        if (PomodoroCore.validateCustomDuration('-5', 1, 90, 25) !== 25) process.exit(8);
        if (PomodoroCore.validateCustomDuration('120', 1, 90, 25) !== 25) process.exit(9);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_validate_custom_duration_invalid_and_fallback(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Non-numeric strings fallback to default
        const invalidStrings = ['abc', 'invalid', '', '   ', '25px', '1.5.6'];
        for (const s of invalidStrings) {
            if (PomodoroCore.validateCustomDuration(s, 1, 90, 25) !== 25) {
                console.error('FAIL: string "' + s + '" should fallback to default');
                process.exit(1);
            }
        }

        // Null, undefined, NaN fallback to default
        if (PomodoroCore.validateCustomDuration(null, 1, 90, 25) !== 25) process.exit(2);
        if (PomodoroCore.validateCustomDuration(undefined, 1, 90, 25) !== 25) process.exit(3);
        if (PomodoroCore.validateCustomDuration(NaN, 1, 90, 25) !== 25) process.exit(4);

        // Boolean inputs fallback to default
        if (PomodoroCore.validateCustomDuration(true, 1, 90, 25) !== 25) process.exit(5);
        if (PomodoroCore.validateCustomDuration(false, 1, 90, 25) !== 25) process.exit(6);

        // Object and array inputs (non-string, non-number types rejected)
        if (PomodoroCore.validateCustomDuration({}, 1, 90, 25) !== 25) process.exit(7);
        if (PomodoroCore.validateCustomDuration([], 1, 90, 25) !== 25) process.exit(8);
        if (PomodoroCore.validateCustomDuration([5], 1, 90, 25) !== 25) process.exit(9);
        if (PomodoroCore.validateCustomDuration([5, 6], 1, 90, 25) !== 25) process.exit(10);

        // Function input
        if (PomodoroCore.validateCustomDuration(function(){}, 1, 90, 25) !== 25) process.exit(11);

        // Infinity
        if (PomodoroCore.validateCustomDuration(Infinity, 1, 90, 25) !== 25) process.exit(12);
        if (PomodoroCore.validateCustomDuration(-Infinity, 1, 90, 25) !== 25) process.exit(13);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_validate_custom_duration_different_bounds(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Short break bounds (1-30)
        if (PomodoroCore.validateCustomDuration(5, 1, 30, 5) !== 5) process.exit(1);
        if (PomodoroCore.validateCustomDuration(1, 1, 30, 5) !== 1) process.exit(2);
        if (PomodoroCore.validateCustomDuration(30, 1, 30, 5) !== 30) process.exit(3);
        if (PomodoroCore.validateCustomDuration(0, 1, 30, 5) !== 5) process.exit(4);
        if (PomodoroCore.validateCustomDuration(31, 1, 30, 5) !== 5) process.exit(5);

        // Long break bounds (1-60)
        if (PomodoroCore.validateCustomDuration(15, 1, 60, 15) !== 15) process.exit(6);
        if (PomodoroCore.validateCustomDuration(1, 1, 60, 15) !== 1) process.exit(7);
        if (PomodoroCore.validateCustomDuration(60, 1, 60, 15) !== 60) process.exit(8);
        if (PomodoroCore.validateCustomDuration(0, 1, 60, 15) !== 15) process.exit(9);
        if (PomodoroCore.validateCustomDuration(61, 1, 60, 15) !== 15) process.exit(10);

        // Custom default values
        if (PomodoroCore.validateCustomDuration(10, 1, 90, 999) !== 10) process.exit(11);
        if (PomodoroCore.validateCustomDuration('invalid', 1, 90, 999) !== 999) process.exit(12);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_validate_custom_duration_baseline_equality(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        function baselineValidateCustomDuration(val, min, max, defaultVal) {
            if (typeof val === 'string') {
                const trimmed = val.trim();
                if (!/^\\d+$/.test(trimmed)) return defaultVal;
            } else if (typeof val !== 'number') {
                return defaultVal;
            }
            const num = parseInt(val, 10);
            if (isNaN(num) || num < min || num > max) return defaultVal;
            return num;
        }

        const testValues = [
            0, 1, 5, 10, 25, 30, 45, 60, 90, 91, 120, -1, -10, 999,
            1.5, 5.9, 25.2, 59.9,
            '0', '1', '5', '25', '30', '45', '60', '90', '91', '-1', '-5', ' 25 ',
            '25.9', '5.2', '15.8', 'abc', 'invalid', '', '   ', '25px', '1.5.6',
            null, undefined, NaN, Infinity, -Infinity,
            true, false, {}, [], [5], [5, 6], function(){}
        ];

        const bounds = [
            [1, 90, 25],
            [1, 30, 5],
            [1, 60, 15],
            [5, 20, 10]
        ];

        for (const [min, max, def] of bounds) {
            for (const val of testValues) {
                const expected = baselineValidateCustomDuration(val, min, max, def);
                const actual = PomodoroCore.validateCustomDuration(val, min, max, def);
                if (expected !== actual) {
                    console.error('Mismatch: val=' + JSON.stringify(val) + ', min=' + min + ', max=' + max + ', def=' + def + ' expected=' + expected + ' actual=' + actual);
                    process.exit(1);
                }
            }
        }

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)


if __name__ == "__main__":
    unittest.main()