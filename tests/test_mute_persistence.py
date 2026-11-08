import unittest
import subprocess


class TestMuteStatePersistence(unittest.TestCase):
    def test_mute_toggle_returns_persistable_storage_values(self):
        js_code = """
        const { PomodoroCore } = require('./test-runner.js');

        const unmuteFromZero = PomodoroCore.calculateMuteToggle(true, 0);
        if (!unmuteFromZero.storage) {
            console.error('FAIL: mute toggle does not expose storage values');
            process.exit(1);
        }
        if (unmuteFromZero.storage.muted !== 'false' || unmuteFromZero.storage.volume !== '0.5') {
            console.error('FAIL: unmute-from-zero persisted ' + JSON.stringify(unmuteFromZero.storage));
            process.exit(1);
        }

        const muteFromActive = PomodoroCore.calculateMuteToggle(false, 0.7);
        if (muteFromActive.storage.muted !== 'true' || muteFromActive.storage.volume !== '0.7') {
            console.error('FAIL: mute persisted ' + JSON.stringify(muteFromActive.storage));
            process.exit(1);
        }

        console.log('SUCCESS');
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
