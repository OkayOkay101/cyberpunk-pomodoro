import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestTimerStateCycleSafeInteger(unittest.TestCase):
    def test_timer_state_and_backup_reject_cycle_count_above_safe_integer(self):
        js_code = """
        const assert = require('assert');
        const { PomodoroCore } = require('./core.js');
        const timer = {
          mode: 'focus', duration: 1500, timeLeft: 900, isRunning: false,
          targetEndTime: null, cycleCount: Number.MAX_SAFE_INTEGER + 1
        };

        assert.strictEqual(PomodoroCore.parseTimerState(JSON.stringify(timer), Date.now()), null);

        const backup = {
          version: PomodoroCore.DATA_BACKUP_VERSION,
          data: { cp_timer_state: JSON.stringify(timer) }
        };
        assert.strictEqual(PomodoroCore.validateDataBackup(backup, Date.now()), null);
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")


if __name__ == "__main__":
    unittest.main()
