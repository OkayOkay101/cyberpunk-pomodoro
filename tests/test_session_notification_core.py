import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestSessionNotificationCore(unittest.TestCase):
    def _run_node(self, js_code: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )

    def test_parse_cycle_count_valid_and_boundaries(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (typeof PomodoroCore.parseCycleCount !== 'function') {
            console.error('FAIL: parseCycleCount is not a function');
            process.exit(1);
        }

        // Standard positive numbers
        if (PomodoroCore.parseCycleCount(1) !== 1) process.exit(2);
        if (PomodoroCore.parseCycleCount(4) !== 4) process.exit(3);
        if (PomodoroCore.parseCycleCount(100) !== 100) process.exit(4);

        // Numeric string inputs (from localStorage)
        if (PomodoroCore.parseCycleCount('1') !== 1) process.exit(5);
        if (PomodoroCore.parseCycleCount('5') !== 5) process.exit(6);
        if (PomodoroCore.parseCycleCount('08') !== 8) process.exit(7);

        // Strings beyond the safe integer range must not round to a different cycle.
        if (PomodoroCore.parseCycleCount('9007199254740993') !== 1) process.exit(15);

        // Boundary fallbacks: 0, negative numbers, NaN, null, undefined, strings
        if (PomodoroCore.parseCycleCount(0) !== 1) process.exit(8);
        if (PomodoroCore.parseCycleCount(-3) !== 1) process.exit(9);
        if (PomodoroCore.parseCycleCount(NaN) !== 1) process.exit(10);
        if (PomodoroCore.parseCycleCount(null) !== 1) process.exit(11);
        if (PomodoroCore.parseCycleCount(undefined) !== 1) process.exit(12);
        if (PomodoroCore.parseCycleCount('corrupted') !== 1) process.exit(13);
        if (PomodoroCore.parseCycleCount('9'.repeat(400)) !== 1) process.exit(14);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_get_session_notification_focus_mode(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (typeof PomodoroCore.getSessionNotification !== 'function') {
            console.error('FAIL: getSessionNotification is not a function');
            process.exit(1);
        }

        // Focus session 1
        const n1 = PomodoroCore.getSessionNotification('focus', 1);
        if (n1.title !== 'FOCUS COMPLETE // CYBERPUNK POMODORO') process.exit(2);
        if (n1.body !== 'จบ Session 1 เรียบร้อยแล้ว ได้เวลาพักผ่อน!') process.exit(3);
        if (n1.soundType !== 'focus_end') process.exit(4);

        // Focus session 4
        const n4 = PomodoroCore.getSessionNotification('focus', 4);
        if (n4.title !== 'FOCUS COMPLETE // CYBERPUNK POMODORO') process.exit(5);
        if (n4.body !== 'จบ Session 4 เรียบร้อยแล้ว ได้เวลาพักผ่อน!') process.exit(6);
        if (n4.soundType !== 'focus_end') process.exit(7);

        // Focus with string cycle count
        const nStr = PomodoroCore.getSessionNotification('focus', '5');
        if (nStr.body !== 'จบ Session 5 เรียบร้อยแล้ว ได้เวลาพักผ่อน!') process.exit(8);

        // Focus with invalid cycle count falls back to session 1
        const nBad = PomodoroCore.getSessionNotification('focus', 0);
        if (nBad.body !== 'จบ Session 1 เรียบร้อยแล้ว ได้เวลาพักผ่อน!') process.exit(9);

        const nNull = PomodoroCore.getSessionNotification('focus', null);
        if (nNull.body !== 'จบ Session 1 เรียบร้อยแล้ว ได้เวลาพักผ่อน!') process.exit(10);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_get_session_notification_break_modes(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Short break
        const nShort = PomodoroCore.getSessionNotification('shortBreak', 1);
        if (nShort.title !== 'BREAK FINISHED // BACK TO MATRIX') process.exit(1);
        if (nShort.body !== 'หมดเวลาพักแล้ว พร้อมกลับมาลุยภารกิจต่อหรือยัง?') process.exit(2);
        if (nShort.soundType !== 'break_end') process.exit(3);

        // Long break
        const nLong = PomodoroCore.getSessionNotification('longBreak', 4);
        if (nLong.title !== 'BREAK FINISHED // BACK TO MATRIX') process.exit(4);
        if (nLong.body !== 'หมดเวลาพักแล้ว พร้อมกลับมาลุยภารกิจต่อหรือยัง?') process.exit(5);
        if (nLong.soundType !== 'break_end') process.exit(6);

        // Unknown / fallback modes
        const nUnknown = PomodoroCore.getSessionNotification('unknown', 1);
        if (nUnknown.title !== 'BREAK FINISHED // BACK TO MATRIX') process.exit(7);
        if (nUnknown.soundType !== 'break_end') process.exit(8);

        const nNull = PomodoroCore.getSessionNotification(null, 1);
        if (nNull.title !== 'BREAK FINISHED // BACK TO MATRIX') process.exit(9);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_get_session_notification_object_parameter_style(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const focusObj = PomodoroCore.getSessionNotification({ mode: 'focus', cycleCount: 3 });
        if (focusObj.title !== 'FOCUS COMPLETE // CYBERPUNK POMODORO') process.exit(1);
        if (focusObj.body !== 'จบ Session 3 เรียบร้อยแล้ว ได้เวลาพักผ่อน!') process.exit(2);
        if (focusObj.soundType !== 'focus_end') process.exit(3);

        const breakObj = PomodoroCore.getSessionNotification({ mode: 'shortBreak' });
        if (breakObj.title !== 'BREAK FINISHED // BACK TO MATRIX') process.exit(4);
        if (breakObj.soundType !== 'break_end') process.exit(5);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_get_session_notification_break_immutability(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const b1 = PomodoroCore.getSessionNotification('shortBreak', 1);
        const b2 = PomodoroCore.getSessionNotification('longBreak', 4);

        // Break notification objects should referentially match and be frozen
        if (b1 !== b2) {
            console.error('FAIL: break notifications should reuse immutable cached instance');
            process.exit(1);
        }

        try {
            b1.title = 'MUTATED';
        } catch (e) {}
        if (b1.title !== 'BREAK FINISHED // BACK TO MATRIX') {
            console.error('FAIL: break notification is not frozen');
            process.exit(2);
        }

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_index_html_wires_session_notification_and_cycle_parser(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn(
            "PomodoroCore.getSessionNotification",
            html,
            "index.html must use PomodoroCore.getSessionNotification to decouple session completion payloads"
        )
        self.assertIn(
            "PomodoroCore.parseCycleCount",
            html,
            "index.html must use PomodoroCore.parseCycleCount to safely parse cycle count from storage"
        )


if __name__ == "__main__":
    unittest.main()
