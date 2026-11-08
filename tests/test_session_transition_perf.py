import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestSessionTransitionPerformance(unittest.TestCase):
    """
    Performance and behavioral verification for PomodoroCore.calculateCompletedSession.
    Verifies elimination of redundant getNextMode function calls, parseInt string coercion
    on numbers, dynamic string allocations for session storage stats, and trims via
    pre-computed FOCUS_SESSION_LOOKUP and NUM_STRINGS lookup tables with numeric fast-path.
    """

    def _run_node_script(self, script: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )

    def test_session_transition_uses_lookup_tables(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const fnStr = PomodoroCore.calculateCompletedSession.toString();

        if (!/FOCUS_SESSION_LOOKUP/.test(fnStr)) {
            console.error('FAIL: calculateCompletedSession does not use FOCUS_SESSION_LOOKUP table');
            process.exit(2);
        }
        if (!/NUM_STRINGS/.test(fnStr)) {
            console.error('FAIL: calculateCompletedSession does not use NUM_STRINGS table');
            process.exit(3);
        }

        // Standard cycle 1 focus completion
        const res1 = PomodoroCore.calculateCompletedSession('focus', 1, 1500, 0, 2, '2026-11-09');
        if (res1.nextMode !== 'shortBreak') process.exit(4);
        if (res1.nextCycleCount !== 2) process.exit(5);
        if (res1.addedFocusMins !== 25) process.exit(6);
        if (res1.nextTotalFocusMins !== 25) process.exit(7);
        if (res1.toastMessage !== 'SHORT BREAK STARTED') process.exit(8);
        if (res1.storage.cp_cycle !== '2') process.exit(9);
        if (res1.storage.cp_streak !== '2') process.exit(10);
        if (res1.storage.cp_focus_mins_today !== '25') process.exit(11);
        if (res1.storage.cp_last_date !== '2026-11-09') process.exit(12);

        // Long break trigger at cycle 4
        const res4 = PomodoroCore.calculateCompletedSession('focus', 4, 1500, 75, 3, '2026-11-09');
        if (res4.nextMode !== 'longBreak') process.exit(13);
        if (res4.nextCycleCount !== 5) process.exit(14);
        if (res4.toastMessage !== 'LONG BREAK STARTED') process.exit(15);
        if (res4.storage.cp_cycle !== '5') process.exit(16);

        // Break session completion -> returns to focus mode
        const resBreak = PomodoroCore.calculateCompletedSession('shortBreak', 2, 1500, 25, 2, '2026-11-09');
        if (resBreak.nextMode !== 'focus') process.exit(17);
        if (resBreak.nextCycleCount !== 2) process.exit(18);
        if (resBreak.addedFocusMins !== 0) process.exit(19);
        if (resBreak.nextTotalFocusMins !== 25) process.exit(20);
        if (resBreak.toastMessage !== 'FOCUS SESSION STARTED') process.exit(21);
        if (Object.keys(resBreak.storage).length !== 0) process.exit(22);

        console.log('SUCCESS');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_session_transition_cycles_above_lookup_table(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Cycles beyond pre-computed lookup table (> 100) must remain functional and correct
        const res104 = PomodoroCore.calculateCompletedSession('focus', 104, 1500, 2600, 10, '2026-11-09');
        if (res104.nextMode !== 'longBreak' || res104.nextCycleCount !== 105 || res104.toastMessage !== 'LONG BREAK STARTED') {
            process.exit(1);
        }
        if (res104.storage.cp_cycle !== '105') process.exit(2);

        const res105 = PomodoroCore.calculateCompletedSession('focus', 105, 1500, 2625, 10, '2026-11-09');
        if (res105.nextMode !== 'shortBreak' || res105.nextCycleCount !== 106 || res105.toastMessage !== 'SHORT BREAK STARTED') {
            process.exit(3);
        }
        if (res105.storage.cp_cycle !== '106') process.exit(4);

        console.log('SUCCESS');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
