import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestDurationsConfig(unittest.TestCase):
    def test_resolve_durations_defaults_and_valid_values(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (typeof PomodoroCore.resolveDurations !== 'function') {
            console.error('FAIL: PomodoroCore.resolveDurations is not a function');
            process.exit(1);
        }

        // Test with defaults (empty object, undefined, null)
        const emptyResult = PomodoroCore.resolveDurations({});
        if (emptyResult.focus !== 1500 || emptyResult.shortBreak !== 300 || emptyResult.longBreak !== 900) {
            console.error('FAIL: default seconds mismatch', emptyResult);
            process.exit(2);
        }
        if (emptyResult.minutes.focus !== 25 || emptyResult.minutes.shortBreak !== 5 || emptyResult.minutes.longBreak !== 15) {
            console.error('FAIL: default minutes mismatch', emptyResult.minutes);
            process.exit(3);
        }
        if (emptyResult.storage.cp_cfg_focus !== '25' || emptyResult.storage.cp_cfg_short !== '5' || emptyResult.storage.cp_cfg_long !== '15') {
            console.error('FAIL: default storage mismatch', emptyResult.storage);
            process.exit(4);
        }

        // Test with null and undefined
        const nullResult = PomodoroCore.resolveDurations(null);
        if (nullResult.focus !== 1500) {
            console.error('FAIL: null inputs should yield defaults');
            process.exit(5);
        }

        const undefResult = PomodoroCore.resolveDurations(undefined);
        if (undefResult.focus !== 1500) {
            console.error('FAIL: undefined inputs should yield defaults');
            process.exit(6);
        }

        // Test with custom valid numbers
        const custom = PomodoroCore.resolveDurations({ focus: 50, shortBreak: 10, longBreak: 25 });
        if (custom.focus !== 3000 || custom.shortBreak !== 600 || custom.longBreak !== 1500) {
            console.error('FAIL: custom seconds mismatch', custom);
            process.exit(7);
        }
        if (custom.minutes.focus !== 50 || custom.minutes.shortBreak !== 10 || custom.minutes.longBreak !== 25) {
            console.error('FAIL: custom minutes mismatch', custom.minutes);
            process.exit(8);
        }
        if (custom.storage.cp_cfg_focus !== '50' || custom.storage.cp_cfg_short !== '10' || custom.storage.cp_cfg_long !== '25') {
            console.error('FAIL: custom storage mismatch', custom.storage);
            process.exit(9);
        }

        // Test with numeric string inputs
        const stringInput = PomodoroCore.resolveDurations({ focus: '45', shortBreak: '8', longBreak: '20' });
        if (stringInput.focus !== 2700 || stringInput.shortBreak !== 480 || stringInput.longBreak !== 1200) {
            console.error('FAIL: numeric string parsing mismatch', stringInput);
            process.exit(10);
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

    def test_resolve_durations_boundary_and_invalid_inputs(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Out-of-bounds inputs: focus (1-90), shortBreak (1-30), longBreak (1-60)
        const outOfBounds = PomodoroCore.resolveDurations({
            focus: 120,    // > 90 -> defaults to 25
            shortBreak: 0, // < 1 -> defaults to 5
            longBreak: -5  // < 1 -> defaults to 15
        });

        if (outOfBounds.minutes.focus !== 25 || outOfBounds.focus !== 1500) {
            console.error('FAIL: focus > 90 should default to 25');
            process.exit(1);
        }
        if (outOfBounds.minutes.shortBreak !== 5 || outOfBounds.shortBreak !== 300) {
            console.error('FAIL: shortBreak < 1 should default to 5');
            process.exit(2);
        }
        if (outOfBounds.minutes.longBreak !== 15 || outOfBounds.longBreak !== 900) {
            console.error('FAIL: longBreak < 1 should default to 15');
            process.exit(3);
        }

        // Upper boundary checks
        const upperCheck = PomodoroCore.resolveDurations({
            focus: 90,
            shortBreak: 30,
            longBreak: 60
        });
        if (upperCheck.minutes.focus !== 90 || upperCheck.focus !== 5400) process.exit(4);
        if (upperCheck.minutes.shortBreak !== 30 || upperCheck.shortBreak !== 1800) process.exit(5);
        if (upperCheck.minutes.longBreak !== 60 || upperCheck.longBreak !== 3600) process.exit(6);

        // Lower boundary checks
        const lowerCheck = PomodoroCore.resolveDurations({
            focus: 1,
            shortBreak: 1,
            longBreak: 1
        });
        if (lowerCheck.minutes.focus !== 1 || lowerCheck.focus !== 60) process.exit(7);
        if (lowerCheck.minutes.shortBreak !== 1 || lowerCheck.shortBreak !== 60) process.exit(8);
        if (lowerCheck.minutes.longBreak !== 1 || lowerCheck.longBreak !== 60) process.exit(9);

        // Non-numeric and corrupted inputs
        const corrupted = PomodoroCore.resolveDurations({
            focus: 'corrupted',
            shortBreak: NaN,
            longBreak: null
        });
        if (corrupted.minutes.focus !== 25 || corrupted.minutes.shortBreak !== 5 || corrupted.minutes.longBreak !== 15) {
            console.error('FAIL: corrupted inputs should yield defaults');
            process.exit(10);
        }

        // Decimal inputs (should truncate/parse integer)
        const decimals = PomodoroCore.resolveDurations({
            focus: '25.9',
            shortBreak: 5.2,
            longBreak: 15.8
        });
        if (decimals.minutes.focus !== 25 || decimals.minutes.shortBreak !== 5 || decimals.minutes.longBreak !== 15) {
            console.error('FAIL: decimal inputs should truncate to integers');
            process.exit(11);
        }

        // Primitive and array inputs
        const arrayInput = PomodoroCore.resolveDurations(['some', 'array']);
        if (arrayInput.minutes.focus !== 25) process.exit(12);

        const stringInput = PomodoroCore.resolveDurations('primitive-string');
        if (stringInput.minutes.focus !== 25) process.exit(13);

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

    def test_index_html_wires_resolve_durations(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn(
            "PomodoroCore.resolveDurations",
            html,
            "index.html must use PomodoroCore.resolveDurations to decouple duration logic"
        )


if __name__ == "__main__":
    unittest.main()
