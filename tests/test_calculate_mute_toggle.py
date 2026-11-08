import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestCalculateMuteToggle(unittest.TestCase):
    """Comprehensive edge case tests for PomodoroCore.calculateMuteToggle."""

    def _run_node(self, js_code: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )

    def test_unmute_from_zero_volume_defaults_to_half(self):
        """Unmuting when savedVol is 0 should default to 0.5 volume."""
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const result = PomodoroCore.calculateMuteToggle(true, 0);
        if (result.isMuted !== false) process.exit(1);
        if (result.targetVol !== 0.5) process.exit(2);
        if (result.savedVol !== 0.5) process.exit(3);
        if (result.storage.muted !== 'false') process.exit(4);
        if (result.storage.volume !== '0.5') process.exit(5);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_unmute_preserves_positive_volume(self):
        """Unmuting should preserve the saved volume when > 0."""
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const cases = [
            [0.1, 0.1],
            [0.3, 0.3],
            [0.5, 0.5],
            [0.7, 0.7],
            [1.0, 1.0]
        ];

        for (const [input, expected] of cases) {
            const result = PomodoroCore.calculateMuteToggle(true, input);
            if (result.isMuted !== false) process.exit(1);
            if (result.targetVol !== expected) process.exit(2);
            if (result.savedVol !== expected) process.exit(3);
            if (result.storage.muted !== 'false') process.exit(4);
            if (result.storage.volume !== String(expected)) process.exit(5);
        }

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_mute_preserves_saved_volume_sets_target_zero(self):
        """Muting should preserve savedVol and set targetVol to 0."""
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const cases = [0, 0.1, 0.3, 0.5, 0.7, 1.0];

        for (const vol of cases) {
            const result = PomodoroCore.calculateMuteToggle(false, vol);
            if (result.isMuted !== true) process.exit(1);
            if (result.targetVol !== 0) process.exit(2);
            if (result.savedVol !== vol) process.exit(3);
            if (result.storage.muted !== 'true') process.exit(4);
            if (result.storage.volume !== String(vol)) process.exit(5);
        }

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_unmute_handles_invalid_saved_vol_fallbacks(self):
        """Unmuting with invalid savedVol should fall back to 0.5."""
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const invalidInputs = [NaN, null, undefined, 'invalid', '', '   ', [], {}, true, false];

        for (const input of invalidInputs) {
            const result = PomodoroCore.calculateMuteToggle(true, input);
            if (result.isMuted !== false) process.exit(1);
            if (result.targetVol !== 0.5) process.exit(2);
            if (result.savedVol !== 0.5) process.exit(3);
            if (result.storage.muted !== 'false') process.exit(4);
            if (result.storage.volume !== '0.5') process.exit(5);
        }

        // String numbers should parse correctly
        const resultStr = PomodoroCore.calculateMuteToggle(true, '0.8');
        if (resultStr.targetVol !== 0.8 || resultStr.savedVol !== 0.8) process.exit(6);

        const resultStrZero = PomodoroCore.calculateMuteToggle(true, '0');
        if (resultStrZero.targetVol !== 0.5 || resultStrZero.savedVol !== 0.5) process.exit(7);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_mute_handles_invalid_saved_vol_fallbacks(self):
        """Muting with invalid savedVol should fall back to 0.5 for storage."""
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const invalidInputs = [NaN, null, undefined, 'invalid', '', '   ', [], {}, true, false];

        for (const input of invalidInputs) {
            const result = PomodoroCore.calculateMuteToggle(false, input);
            if (result.isMuted !== true) process.exit(1);
            if (result.targetVol !== 0) process.exit(2);
            if (result.savedVol !== 0.5) process.exit(3);
            if (result.storage.muted !== 'true') process.exit(4);
            if (result.storage.volume !== '0.5') process.exit(5);
        }

        // String numbers should parse correctly
        const resultStr = PomodoroCore.calculateMuteToggle(false, '0.8');
        if (resultStr.savedVol !== 0.8) process.exit(6);
        if (resultStr.storage.volume !== '0.8') process.exit(7);

        // Negative string clamps to 0
        const resultNeg = PomodoroCore.calculateMuteToggle(false, '-0.5');
        if (resultNeg.savedVol !== 0) process.exit(8);
        if (resultNeg.storage.volume !== '0') process.exit(9);

        // >1 string clamps to 1
        const resultHigh = PomodoroCore.calculateMuteToggle(false, '1.5');
        if (resultHigh.savedVol !== 1) process.exit(10);
        if (resultHigh.storage.volume !== '1') process.exit(11);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_roundtrip_mute_unmute_preserves_volume(self):
        """Mute then unmute should restore original volume."""
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const testVolumes = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0];

        for (const vol of testVolumes) {
            let state = { isMuted: false, savedVol: vol };

            // Mute
            const muted = PomodoroCore.calculateMuteToggle(state.isMuted, state.savedVol);
            state.isMuted = muted.isMuted;
            state.savedVol = muted.savedVol;

            // Unmute
            const unmuted = PomodoroCore.calculateMuteToggle(state.isMuted, state.savedVol);
            state.isMuted = unmuted.isMuted;
            state.savedVol = unmuted.savedVol;

            if (state.isMuted !== false) process.exit(1);
            if (state.savedVol !== vol) process.exit(2);
        }

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_roundtrip_from_muted_zero_volume(self):
        """Starting muted with 0 volume: unmute->mute->unmute should stabilize at 0.5."""
        js_code = """
        const { PomodoroCore } = require('./core.js');

        let state = { isMuted: true, savedVol: 0 };

        // First unmute: 0 -> 0.5
        const r1 = PomodoroCore.calculateMuteToggle(state.isMuted, state.savedVol);
        state.isMuted = r1.isMuted;
        state.savedVol = r1.savedVol;
        if (state.savedVol !== 0.5) process.exit(1);

        // Mute: preserves 0.5
        const r2 = PomodoroCore.calculateMuteToggle(state.isMuted, state.savedVol);
        state.isMuted = r2.isMuted;
        state.savedVol = r2.savedVol;
        if (state.savedVol !== 0.5) process.exit(2);

        // Unmute: preserves 0.5
        const r3 = PomodoroCore.calculateMuteToggle(state.isMuted, state.savedVol);
        state.isMuted = r3.isMuted;
        state.savedVol = r3.savedVol;
        if (state.savedVol !== 0.5) process.exit(3);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_clamping_on_unmute(self):
        """Unmute should clamp savedVol to [0, 1] range."""
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Negative volume clamps to 0, then defaults to 0.5 on unmute
        const r1 = PomodoroCore.calculateMuteToggle(true, -0.5);
        if (r1.targetVol !== 0.5 || r1.savedVol !== 0.5) process.exit(1);

        // Volume > 1 clamps to 1
        const r2 = PomodoroCore.calculateMuteToggle(true, 1.5);
        if (r2.targetVol !== 1 || r2.savedVol !== 1) process.exit(2);

        // Volume exactly at boundaries
        const r3 = PomodoroCore.calculateMuteToggle(true, -100);
        if (r3.targetVol !== 0.5) process.exit(3);

        const r4 = PomodoroCore.calculateMuteToggle(true, 100);
        if (r4.targetVol !== 1) process.exit(4);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_clamping_on_mute(self):
        """Mute should clamp savedVol to [0, 1] range for storage."""
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Negative volume clamps to 0
        const r1 = PomodoroCore.calculateMuteToggle(false, -0.5);
        if (r1.savedVol !== 0) process.exit(1);
        if (r1.storage.volume !== '0') process.exit(2);

        // Volume > 1 clamps to 1
        const r2 = PomodoroCore.calculateMuteToggle(false, 1.5);
        if (r2.savedVol !== 1) process.exit(3);
        if (r2.storage.volume !== '1') process.exit(4);

        // Volume exactly at boundaries
        const r3 = PomodoroCore.calculateMuteToggle(false, -100);
        if (r3.storage.volume !== '0') process.exit(5);

        const r4 = PomodoroCore.calculateMuteToggle(false, 100);
        if (r4.storage.volume !== '1') process.exit(6);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_storage_values_are_strings(self):
        """Storage object should always contain string values."""
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const cases = [
            [true, 0],
            [true, 0.5],
            [true, 1],
            [false, 0],
            [false, 0.7],
            [false, 1],
            [true, NaN],
            [false, null]
        ];

        for (const [isMuted, vol] of cases) {
            const result = PomodoroCore.calculateMuteToggle(isMuted, vol);
            if (typeof result.storage.muted !== 'string') process.exit(1);
            if (typeof result.storage.volume !== 'string') process.exit(2);
            if (result.storage.muted !== String(result.isMuted)) process.exit(3);
            if (result.storage.volume !== String(result.savedVol)) process.exit(4);
        }

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)


if __name__ == "__main__":
    unittest.main()