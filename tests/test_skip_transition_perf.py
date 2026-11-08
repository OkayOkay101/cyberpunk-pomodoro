import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestSkipTransitionPerformance(unittest.TestCase):
    """
    Performance and behavioral verification for PomodoroCore.calculateSkipTransition.
    Verifies elimination of dynamic object heap churn, redundant getNextMode / parseInt coercion,
    and redundant getModeToastMessage lookup via numeric fast-path and pre-computed
    FOCUS_SKIP_LOOKUP and BREAK_SKIP_LOOKUP tables.
    """

    def _run_node_script(self, script: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )

    def test_skip_transition_fast_path_and_lookup(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const fnStr = PomodoroCore.calculateSkipTransition.toString();

        if (!/FOCUS_SKIP_LOOKUP/.test(fnStr) && !/BREAK_SKIP_LOOKUP/.test(fnStr)) {
            console.error('FAIL: calculateSkipTransition does not use pre-computed skip lookup tables');
            process.exit(2);
        }

        // Standard skip payload verification
        const s1 = PomodoroCore.calculateSkipTransition('focus', 1);
        if (s1.nextMode !== 'shortBreak') process.exit(3);
        if (s1.toastMessage !== 'SHORT BREAK') process.exit(4);
        if (s1.cycleCount !== 1) process.exit(5);

        const s4 = PomodoroCore.calculateSkipTransition('focus', 4);
        if (s4.nextMode !== 'longBreak') process.exit(6);
        if (s4.toastMessage !== 'LONG BREAK') process.exit(7);
        if (s4.cycleCount !== 4) process.exit(8);

        // Object cache reuse and immutability for standard cycles (1..100)
        const s1Again = PomodoroCore.calculateSkipTransition('focus', 1);
        if (s1 !== s1Again) {
            console.error('FAIL: calculateSkipTransition should reuse cached immutable object for cycle 1');
            process.exit(9);
        }

        const s4Again = PomodoroCore.calculateSkipTransition('focus', 4);
        if (s4 !== s4Again) {
            console.error('FAIL: calculateSkipTransition should reuse cached immutable object for cycle 4');
            process.exit(10);
        }

        const breakAgain = PomodoroCore.calculateSkipTransition('shortBreak', 2);
        const breakAgain2 = PomodoroCore.calculateSkipTransition('shortBreak', 2);
        if (breakAgain !== breakAgain2) {
            console.error('FAIL: calculateSkipTransition should reuse cached immutable object for break mode');
            process.exit(11);
        }

        // Verify immutability
        try {
            s1.nextMode = 'MUTATED';
        } catch (e) {}
        if (s1.nextMode !== 'shortBreak') {
            console.error('FAIL: Pre-computed skip object must be frozen against mutation');
            process.exit(12);
        }

        console.log('SUCCESS');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_skip_transition_cycles_above_lookup_table(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Cycles beyond pre-computed lookup table (> 100) must remain functional and correct
        const s104 = PomodoroCore.calculateSkipTransition('focus', 104);
        if (s104.nextMode !== 'longBreak' || s104.toastMessage !== 'LONG BREAK' || s104.cycleCount !== 104) {
            process.exit(1);
        }

        const s105 = PomodoroCore.calculateSkipTransition('focus', 105);
        if (s105.nextMode !== 'shortBreak' || s105.toastMessage !== 'SHORT BREAK' || s105.cycleCount !== 105) {
            process.exit(2);
        }

        const sBreak105 = PomodoroCore.calculateSkipTransition('shortBreak', 105);
        if (sBreak105.nextMode !== 'focus' || sBreak105.toastMessage !== 'FOCUS MODE' || sBreak105.cycleCount !== 105) {
            process.exit(3);
        }

        console.log('SUCCESS');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
