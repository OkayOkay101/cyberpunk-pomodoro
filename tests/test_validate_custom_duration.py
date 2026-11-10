import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestValidateCustomDuration(unittest.TestCase):
    """Comprehensive edge case tests for PomodoroCore.validateCustomDuration."""

    def _run_node(self, js_code: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )

    def test_validate_custom_duration_valid_numeric_inputs(self):
        """Valid numbers within bounds should pass through unchanged."""
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (typeof PomodoroCore.validateCustomDuration !== 'function') {
            console.error('FAIL: validateCustomDuration is not a function');
            process.exit(1);
        }

        // Standard valid inputs
        if (PomodoroCore.validateCustomDuration(25, 1, 90, 25) !== 25) process.exit(2);
        if (PomodoroCore.validateCustomDuration(1, 1, 90, 25) !== 1) process.exit(3);
        if (PomodoroCore.validateCustomDuration(90, 1, 90, 25) !== 90) process.exit(4);
        if (PomodoroCore.validateCustomDuration(50, 1, 90, 25) !== 50) process.exit(5);

        // Short break bounds (1-30)
        if (PomodoroCore.validateCustomDuration(5, 1, 30, 5) !== 5) process.exit(6);
        if (PomodoroCore.validateCustomDuration(1, 1, 30, 5) !== 1) process.exit(7);
        if (PomodoroCore.validateCustomDuration(30, 1, 30, 5) !== 30) process.exit(8);

        // Long break bounds (1-60)
        if (PomodoroCore.validateCustomDuration(15, 1, 60, 15) !== 15) process.exit(9);
        if (PomodoroCore.validateCustomDuration(1, 1, 60, 15) !== 1) process.exit(10);
        if (PomodoroCore.validateCustomDuration(60, 1, 60, 15) !== 60) process.exit(11);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_validate_custom_duration_string_numbers(self):
        """Numeric strings should parse correctly within bounds."""
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Valid numeric strings
        if (PomodoroCore.validateCustomDuration('25', 1, 90, 25) !== 25) process.exit(1);
        if (PomodoroCore.validateCustomDuration('1', 1, 90, 25) !== 1) process.exit(2);
        if (PomodoroCore.validateCustomDuration('90', 1, 90, 25) !== 90) process.exit(3);
        if (PomodoroCore.validateCustomDuration('05', 1, 90, 25) !== 5) process.exit(4);  // Leading zero
        if (PomodoroCore.validateCustomDuration('  25  ', 1, 90, 25) !== 25) process.exit(5);  // Whitespace
        if (PomodoroCore.validateCustomDuration('+25', 1, 90, 25) !== 25) process.exit(6);  // Leading plus

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_validate_custom_duration_out_of_bounds_returns_default(self):
        """Values outside min/max range should return default."""
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Below minimum
        if (PomodoroCore.validateCustomDuration(0, 1, 90, 25) !== 25) process.exit(1);
        if (PomodoroCore.validateCustomDuration(-1, 1, 90, 25) !== 25) process.exit(2);
        if (PomodoroCore.validateCustomDuration(-100, 1, 90, 25) !== 25) process.exit(3);

        // Above maximum
        if (PomodoroCore.validateCustomDuration(91, 1, 90, 25) !== 25) process.exit(4);
        if (PomodoroCore.validateCustomDuration(100, 1, 90, 25) !== 25) process.exit(5);
        if (PomodoroCore.validateCustomDuration(999, 1, 90, 25) !== 25) process.exit(6);

        // String out of bounds
        if (PomodoroCore.validateCustomDuration('0', 1, 90, 25) !== 25) process.exit(7);
        if (PomodoroCore.validateCustomDuration('100', 1, 90, 25) !== 25) process.exit(8);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_validate_custom_duration_invalid_types_return_default(self):
        """Non-numeric types should return default."""
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const invalidInputs = [
            null,
            undefined,
            NaN,
            true,
            false,
            [],
            {},
            function() {},
            Symbol('test'),
            ''
        ];

        for (const input of invalidInputs) {
            const result = PomodoroCore.validateCustomDuration(input, 1, 90, 25);
            if (result !== 25) {
                console.error('Expected default 25 for input:', input, 'got:', result);
                process.exit(1);
            }
        }

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_validate_custom_duration_malformed_strings_return_default(self):
        """Malformed numeric strings should return default."""
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const malformedInputs = [
            'abc',
            '25px',       // Trailing non-digits -> reject
            '25.5',       // Decimal -> reject
            '0.5',        // Decimal < 1 -> reject
            '25,5',       // Comma decimal separator -> reject
            '  ',         // Whitespace only -> reject
            '\\t\\n',     // Tab/newline -> reject
            '25px30',     // Trailing non-digits -> reject
            'INF',        // Non-numeric -> reject
            '-Infinity',  // Non-numeric -> reject
            'NaN',        // Non-numeric -> reject
            '0x10',       // Hex -> reject
            '1e2',        // Scientific notation -> reject
            '25abc',      // Trailing non-digits -> reject
            '+25.5',      // Decimal with plus -> reject
            '-25.5',      // Negative decimal -> reject
        ];

        for (const input of malformedInputs) {
            const result = PomodoroCore.validateCustomDuration(input, 1, 90, 25);
            if (result !== 25) {
                console.error('Expected default 25 for malformed input:', JSON.stringify(input), 'got:', result);
                process.exit(1);
            }
        }

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_validate_custom_duration_decimal_rejection(self):
        """Decimal strings should be rejected (return default)."""
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Decimals are rejected - not valid integers
        if (PomodoroCore.validateCustomDuration('25.9', 1, 90, 25) !== 25) process.exit(1);
        if (PomodoroCore.validateCustomDuration('25.1', 1, 90, 25) !== 25) process.exit(2);

        // Decimals < 1
        if (PomodoroCore.validateCustomDuration('0.9', 1, 90, 25) !== 25) process.exit(3);
        if (PomodoroCore.validateCustomDuration('0.5', 1, 90, 25) !== 25) process.exit(4);

        // Decimal at max bound
        if (PomodoroCore.validateCustomDuration('90.9', 1, 90, 25) !== 25) process.exit(5);

        // Negative decimals
        if (PomodoroCore.validateCustomDuration('-0.5', 1, 90, 25) !== 25) process.exit(6);
        if (PomodoroCore.validateCustomDuration('-25.5', 1, 90, 25) !== 25) process.exit(7);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_validate_custom_duration_special_numeric_values(self):
        """Infinity, -Infinity should return default."""
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (PomodoroCore.validateCustomDuration(Infinity, 1, 90, 25) !== 25) process.exit(1);
        if (PomodoroCore.validateCustomDuration(-Infinity, 1, 90, 25) !== 25) process.exit(2);
        if (PomodoroCore.validateCustomDuration('Infinity', 1, 90, 25) !== 25) process.exit(3);
        if (PomodoroCore.validateCustomDuration('-Infinity', 1, 90, 25) !== 25) process.exit(4);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_validate_custom_duration_custom_default_values(self):
        """Different default values should be respected."""
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Custom defaults
        if (PomodoroCore.validateCustomDuration('invalid', 1, 90, 30) !== 30) process.exit(1);
        if (PomodoroCore.validateCustomDuration(null, 1, 30, 10) !== 10) process.exit(2);
        if (PomodoroCore.validateCustomDuration(100, 1, 60, 20) !== 20) process.exit(3);
        if (PomodoroCore.validateCustomDuration(0, 5, 10, 7) !== 7) process.exit(4);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_validate_custom_duration_boundary_edge_cases(self):
        """Test exact boundary values and off-by-one."""
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Exact min boundary
        if (PomodoroCore.validateCustomDuration(1, 1, 90, 25) !== 1) process.exit(1);
        if (PomodoroCore.validateCustomDuration('1', 1, 90, 25) !== 1) process.exit(2);

        // Exact max boundary
        if (PomodoroCore.validateCustomDuration(90, 1, 90, 25) !== 90) process.exit(3);
        if (PomodoroCore.validateCustomDuration('90', 1, 90, 25) !== 90) process.exit(4);

        // Just below min
        if (PomodoroCore.validateCustomDuration(0, 1, 90, 25) !== 25) process.exit(5);
        if (PomodoroCore.validateCustomDuration('0', 1, 90, 25) !== 25) process.exit(6);

        // Just above max
        if (PomodoroCore.validateCustomDuration(91, 1, 90, 25) !== 25) process.exit(7);
        if (PomodoroCore.validateCustomDuration('91', 1, 90, 25) !== 25) process.exit(8);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_validate_custom_duration_strict_integer_validation(self):
        """Verify strict integer validation - reject non-integer strings."""
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Trailing non-digits -> reject
        if (PomodoroCore.validateCustomDuration('25abc', 1, 90, 25) !== 25) process.exit(1);
        if (PomodoroCore.validateCustomDuration('25px', 1, 90, 25) !== 25) process.exit(2);

        // Leading non-digits -> reject
        if (PomodoroCore.validateCustomDuration('abc25', 1, 90, 25) !== 25) process.exit(3);

        // Leading + sign with integer -> accept
        if (PomodoroCore.validateCustomDuration('+25', 1, 90, 25) !== 25) process.exit(4);

        // Hex strings -> reject
        if (PomodoroCore.validateCustomDuration('0x10', 1, 90, 25) !== 25) process.exit(5);

        // Octal-like (leading zero) - accepted as decimal integer
        if (PomodoroCore.validateCustomDuration('010', 1, 90, 25) !== 10) process.exit(6);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_index_html_uses_validate_custom_duration_via_resolve_durations(self):
        """Verify index.html uses the validation through resolveDurations."""
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn(
            "PomodoroCore.resolveDurations",
            html,
            "index.html must use PomodoroCore.resolveDurations which uses validateCustomDuration"
        )


if __name__ == "__main__":
    unittest.main()