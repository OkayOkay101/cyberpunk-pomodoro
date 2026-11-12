import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestTimerStatusCore(unittest.TestCase):
    def test_get_timer_status_running_state(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (typeof PomodoroCore.getTimerStatus !== 'function') {
            console.error('FAIL: PomodoroCore.getTimerStatus is not a function');
            process.exit(1);
        }

        // Positional parameters
        const run1 = PomodoroCore.getTimerStatus(true, 1500, 1500);
        if (run1.buttonText !== 'PAUSE' || run1.statusText !== 'SYSTEM // RUNNING') process.exit(2);

        const run2 = PomodoroCore.getTimerStatus(true, 300, 1500);
        if (run2.buttonText !== 'PAUSE' || run2.statusText !== 'SYSTEM // RUNNING') process.exit(3);

        const run3 = PomodoroCore.getTimerStatus(true, 0, 1500);
        if (run3.buttonText !== 'PAUSE' || run3.statusText !== 'SYSTEM // RUNNING') process.exit(4);

        // Object parameter style
        const runObj = PomodoroCore.getTimerStatus({ isRunning: true, timeLeft: 450, duration: 1500 });
        if (runObj.buttonText !== 'PAUSE' || runObj.statusText !== 'SYSTEM // RUNNING') process.exit(5);

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

    def test_get_timer_status_paused_mid_session(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Paused state: not running and 0 < timeLeft < duration
        const pause1 = PomodoroCore.getTimerStatus(false, 750, 1500);
        if (pause1.buttonText !== 'RESUME' || pause1.statusText !== 'SYSTEM // PAUSED') process.exit(1);

        const pause2 = PomodoroCore.getTimerStatus(false, 1, 1500);
        if (pause2.buttonText !== 'RESUME' || pause2.statusText !== 'SYSTEM // PAUSED') process.exit(2);

        // Numeric string inputs
        const pauseStr = PomodoroCore.getTimerStatus(false, '600', '1500');
        if (pauseStr.buttonText !== 'RESUME' || pauseStr.statusText !== 'SYSTEM // PAUSED') process.exit(3);

        // Object parameter style
        const pauseObj = PomodoroCore.getTimerStatus({ isRunning: false, timeLeft: 500, duration: 1500 });
        if (pauseObj.buttonText !== 'RESUME' || pauseObj.statusText !== 'SYSTEM // PAUSED') process.exit(4);

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

    def test_get_timer_status_ready_and_boundary_fallback(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Ready state: at initial duration
        const ready1 = PomodoroCore.getTimerStatus(false, 1500, 1500);
        if (ready1.buttonText !== 'START' || ready1.statusText !== 'ONLINE // READY') process.exit(1);

        // Zero or negative time left (session ended/reset)
        const readyZero = PomodoroCore.getTimerStatus(false, 0, 1500);
        if (readyZero.buttonText !== 'START' || readyZero.statusText !== 'ONLINE // READY') process.exit(2);

        const readyNeg = PomodoroCore.getTimerStatus(false, -5, 1500);
        if (readyNeg.buttonText !== 'START' || readyNeg.statusText !== 'ONLINE // READY') process.exit(3);

        // Over-duration timeLeft
        const readyOver = PomodoroCore.getTimerStatus(false, 2000, 1500);
        if (readyOver.buttonText !== 'START' || readyOver.statusText !== 'ONLINE // READY') process.exit(4);

        // Invalid duration boundaries
        const badDur1 = PomodoroCore.getTimerStatus(false, 500, 0);
        if (badDur1.buttonText !== 'START' || badDur1.statusText !== 'ONLINE // READY') process.exit(5);

        const badDur2 = PomodoroCore.getTimerStatus(false, 500, -10);
        if (badDur2.buttonText !== 'START' || badDur2.statusText !== 'ONLINE // READY') process.exit(6);

        const badDur3 = PomodoroCore.getTimerStatus(false, 500, NaN);
        if (badDur3.buttonText !== 'START' || badDur3.statusText !== 'ONLINE // READY') process.exit(7);

        // Missing or null / undefined / corrupted inputs
        const nullInput = PomodoroCore.getTimerStatus(null);
        if (nullInput.buttonText !== 'START' || nullInput.statusText !== 'ONLINE // READY') process.exit(8);

        const undefInput = PomodoroCore.getTimerStatus(undefined);
        if (undefInput.buttonText !== 'START' || undefInput.statusText !== 'ONLINE // READY') process.exit(9);

        const emptyObj = PomodoroCore.getTimerStatus({});
        if (emptyObj.buttonText !== 'START' || emptyObj.statusText !== 'ONLINE // READY') process.exit(10);

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

    def test_get_timer_status_referential_caching(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Running status references must be identical
        const r1 = PomodoroCore.getTimerStatus(true, 1000, 1500);
        const r2 = PomodoroCore.getTimerStatus(true, 500, 1500);
        if (r1 !== r2) {
            console.error('FAIL: Running status object is not cached/frozen');
            process.exit(1);
        }

        // Paused status references must be identical
        const p1 = PomodoroCore.getTimerStatus(false, 800, 1500);
        const p2 = PomodoroCore.getTimerStatus(false, 200, 1500);
        if (p1 !== p2) {
            console.error('FAIL: Paused status object is not cached/frozen');
            process.exit(2);
        }

        // Ready status references must be identical
        const s1 = PomodoroCore.getTimerStatus(false, 1500, 1500);
        const s2 = PomodoroCore.getTimerStatus(false, 0, 1500);
        if (s1 !== s2) {
            console.error('FAIL: Ready status object is not cached/frozen');
            process.exit(3);
        }

        // Ensure returned objects are frozen against mutation
        try {
            r1.buttonText = 'MUTATED';
        } catch (e) {}
        if (r1.buttonText !== 'PAUSE') {
            console.error('FAIL: Status object is not frozen');
            process.exit(4);
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

    def test_index_html_wires_get_timer_status(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn(
            "PomodoroCore.getTimerStatus",
            html,
            "index.html must use PomodoroCore.getTimerStatus to decouple timer control status"
        )

    def test_timer_button_accessible_name_tracks_its_action(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="toggleBtn" aria-label="เริ่มตัวจับเวลา"', html)
        self.assertIn("toggleBtn.setAttribute('aria-label', status.buttonText === 'PAUSE' ? 'หยุดตัวจับเวลา' : status.buttonText === 'RESUME' ? 'เล่นตัวจับเวลาต่อ' : 'เริ่มตัวจับเวลา')", html)


if __name__ == "__main__":
    unittest.main()
