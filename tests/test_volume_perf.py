import unittest
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestVolumeBehaviorAndEquality(unittest.TestCase):
    """
    Behavioral tests for PomodoroCore volume functions (clampVolume, formatVolumePercent, getVolumeIcon).
    Tests verify public contracts, edge cases, boundaries, and baseline equality without coupling
    to internal implementation details.
    """

    def _run_node_script(self, script: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )

    def test_clamp_volume_numeric_range_and_boundaries(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Valid ranges
        if (PomodoroCore.clampVolume(0.0) !== 0.0) process.exit(1);
        if (PomodoroCore.clampVolume(0.5) !== 0.5) process.exit(2);
        if (PomodoroCore.clampVolume(1.0) !== 1.0) process.exit(3);
        if (PomodoroCore.clampVolume(0.25) !== 0.25) process.exit(4);
        if (PomodoroCore.clampVolume(0.75) !== 0.75) process.exit(5);

        // Clamping out-of-bounds
        if (PomodoroCore.clampVolume(-0.01) !== 0.0) process.exit(6);
        if (PomodoroCore.clampVolume(-1.5) !== 0.0) process.exit(7);
        if (PomodoroCore.clampVolume(-100) !== 0.0) process.exit(8);
        if (PomodoroCore.clampVolume(-Infinity) !== 0.0) process.exit(9);
        if (PomodoroCore.clampVolume(1.01) !== 1.0) process.exit(10);
        if (PomodoroCore.clampVolume(2.5) !== 1.0) process.exit(11);
        if (PomodoroCore.clampVolume(999) !== 1.0) process.exit(12);
        if (PomodoroCore.clampVolume(Infinity) !== 1.0) process.exit(13);

        console.log('OK');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("OK", proc.stdout)

    def test_clamp_volume_strings_and_fallbacks(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Numeric strings parse correctly
        if (PomodoroCore.clampVolume('0') !== 0.0) process.exit(1);
        if (PomodoroCore.clampVolume('0.5') !== 0.5) process.exit(2);
        if (PomodoroCore.clampVolume('1') !== 1.0) process.exit(3);
        if (PomodoroCore.clampVolume('1.8') !== 1.0) process.exit(4);
        if (PomodoroCore.clampVolume('-0.4') !== 0.0) process.exit(5);

        // Invalid inputs fallback to 0.5
        const invalidInputs = [
            NaN,
            'abc', '0.5px', '', '   ',
            null, undefined, true, false, Symbol('volume'),
            [], {}, function() {}
        ];

        for (const input of invalidInputs) {
            const result = PomodoroCore.clampVolume(input);
            if (result !== 0.5) {
                console.error('Expected fallback 0.5 for input:', input, 'got:', result);
                process.exit(6);
            }
        }

        console.log('OK');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("OK", proc.stdout)

    def test_format_volume_percent_behavior(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Muted returns 'MUTED'
        if (PomodoroCore.formatVolumePercent(0.5, true) !== 'MUTED') process.exit(1);
        if (PomodoroCore.formatVolumePercent(1.0, true) !== 'MUTED') process.exit(2);
        if (PomodoroCore.formatVolumePercent(0.0, true) !== 'MUTED') process.exit(3);

        // Standard percentage conversions
        if (PomodoroCore.formatVolumePercent(0.0, false) !== '0%') process.exit(4);
        if (PomodoroCore.formatVolumePercent(0.5, false) !== '50%') process.exit(5);
        if (PomodoroCore.formatVolumePercent(1.0, false) !== '100%') process.exit(6);
        if (PomodoroCore.formatVolumePercent(0.25, false) !== '25%') process.exit(7);
        if (PomodoroCore.formatVolumePercent(0.75, false) !== '75%') process.exit(8);

        // Rounding
        if (PomodoroCore.formatVolumePercent(0.333, false) !== '33%') process.exit(9);
        if (PomodoroCore.formatVolumePercent(0.666, false) !== '67%') process.exit(10);

        // Out-of-bounds clamped
        if (PomodoroCore.formatVolumePercent(-0.5, false) !== '0%') process.exit(11);
        if (PomodoroCore.formatVolumePercent(1.5, false) !== '100%') process.exit(12);

        // Fallbacks
        if (PomodoroCore.formatVolumePercent('invalid', false) !== '50%') process.exit(13);
        if (PomodoroCore.formatVolumePercent(null, false) !== '50%') process.exit(14);

        console.log('OK');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("OK", proc.stdout)

    def test_get_volume_icon_behavior(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Muted returns 🔇 regardless of volume
        if (PomodoroCore.getVolumeIcon(1.0, true) !== '🔇') process.exit(1);
        if (PomodoroCore.getVolumeIcon(0.5, true) !== '🔇') process.exit(2);
        if (PomodoroCore.getVolumeIcon(0.0, true) !== '🔇') process.exit(3);

        // Unmuted zero returns 🔇
        if (PomodoroCore.getVolumeIcon(0.0, false) !== '🔇') process.exit(4);
        if (PomodoroCore.getVolumeIcon(-0.5, false) !== '🔇') process.exit(5);

        // Unmuted non-zero returns 🔊
        if (PomodoroCore.getVolumeIcon(0.01, false) !== '🔊') process.exit(6);
        if (PomodoroCore.getVolumeIcon(0.5, false) !== '🔊') process.exit(7);
        if (PomodoroCore.getVolumeIcon(1.0, false) !== '🔊') process.exit(8);

        console.log('OK');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("OK", proc.stdout)

    def test_volume_exhaustive_baseline_equality(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Baseline reference implementations
        function baselineClampVolume(vol) {
            const num = parseFloat(vol);
            if (isNaN(num)) return 0.5;
            return Math.max(0, Math.min(1, num));
        }

        function baselineFormatVolumePercent(vol, isMuted) {
            if (isMuted) return 'MUTED';
            const clamped = baselineClampVolume(vol);
            return `${Math.round(clamped * 100)}%`;
        }

        function baselineGetVolumeIcon(vol, isMuted) {
            const clamped = baselineClampVolume(vol);
            return (isMuted || clamped === 0) ? '🔇' : '🔊';
        }

        const testVolumes = [
            0.0, 0.5, 1.0, 0.25, 0.75, 0.85, 0.01, 0.99,
            1.8, -0.4, -0.0, 2.5, -100, 1000,
            NaN, Infinity, -Infinity,
            '0.5', '1.0', '0.0', '0.85', '1.8', '-0.4',
            'invalid', '', '   ', '0.5px', 'abc',
            null, undefined, true, false, [], {}
        ];

        for (const vol of testVolumes) {
            const baseClamp = baselineClampVolume(vol);
            const optClamp = PomodoroCore.clampVolume(vol);
            if (baseClamp !== optClamp) {
                console.error(`clampVolume mismatch on ${vol}: expected ${baseClamp}, got ${optClamp}`);
                process.exit(1);
            }

            for (const muted of [true, false, undefined, null, 1, 0]) {
                const baseFmt = baselineFormatVolumePercent(vol, muted);
                const optFmt = PomodoroCore.formatVolumePercent(vol, muted);
                if (baseFmt !== optFmt) {
                    console.error(`formatVolumePercent mismatch on vol=${vol}, muted=${muted}: expected "${baseFmt}", got "${optFmt}"`);
                    process.exit(2);
                }

                const baseIcon = baselineGetVolumeIcon(vol, muted);
                const optIcon = PomodoroCore.getVolumeIcon(vol, muted);
                if (baseIcon !== optIcon) {
                    console.error(`getVolumeIcon mismatch on vol=${vol}, muted=${muted}: expected "${baseIcon}", got "${optIcon}"`);
                    process.exit(3);
                }
            }
        }

        console.log('SUCCESS');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
