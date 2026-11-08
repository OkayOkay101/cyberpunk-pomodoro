import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestSkipTransitionCore(unittest.TestCase):
    def _run_node(self, js_code: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )

    def test_calculate_skip_transition_from_focus_mode(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (typeof PomodoroCore.calculateSkipTransition !== 'function') {
            console.error('FAIL: calculateSkipTransition is not a function');
            process.exit(1);
        }

        // Cycle 1 focus skip -> short break, cycle count preserved (1)
        const res1 = PomodoroCore.calculateSkipTransition('focus', 1);
        if (res1.nextMode !== 'shortBreak') process.exit(2);
        if (res1.toastMessage !== 'SHORT BREAK') process.exit(3);
        if (res1.cycleCount !== 1) process.exit(4);

        // Cycle 2 focus skip -> short break, cycle count preserved (2)
        const res2 = PomodoroCore.calculateSkipTransition('focus', 2);
        if (res2.nextMode !== 'shortBreak') process.exit(5);
        if (res2.toastMessage !== 'SHORT BREAK') process.exit(6);
        if (res2.cycleCount !== 2) process.exit(7);

        // Cycle 3 focus skip -> short break, cycle count preserved (3)
        const res3 = PomodoroCore.calculateSkipTransition('focus', 3);
        if (res3.nextMode !== 'shortBreak') process.exit(8);
        if (res3.toastMessage !== 'SHORT BREAK') process.exit(9);
        if (res3.cycleCount !== 3) process.exit(10);

        // Cycle 4 focus skip -> long break, cycle count preserved (4)
        const res4 = PomodoroCore.calculateSkipTransition('focus', 4);
        if (res4.nextMode !== 'longBreak') process.exit(11);
        if (res4.toastMessage !== 'LONG BREAK') process.exit(12);
        if (res4.cycleCount !== 4) process.exit(13);

        // Cycle 8 focus skip -> long break, cycle count preserved (8)
        const res8 = PomodoroCore.calculateSkipTransition('focus', 8);
        if (res8.nextMode !== 'longBreak') process.exit(14);
        if (res8.toastMessage !== 'LONG BREAK') process.exit(15);
        if (res8.cycleCount !== 8) process.exit(16);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_skip_transition_from_break_modes(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Short break skip -> focus mode, cycle count preserved (2)
        const resShort = PomodoroCore.calculateSkipTransition('shortBreak', 2);
        if (resShort.nextMode !== 'focus') process.exit(1);
        if (resShort.toastMessage !== 'FOCUS MODE') process.exit(2);
        if (resShort.cycleCount !== 2) process.exit(3);

        // Long break skip -> focus mode, cycle count preserved (4)
        const resLong = PomodoroCore.calculateSkipTransition('longBreak', 4);
        if (resLong.nextMode !== 'focus') process.exit(4);
        if (resLong.toastMessage !== 'FOCUS MODE') process.exit(5);
        if (resLong.cycleCount !== 4) process.exit(6);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_skip_transition_object_and_positional_arguments(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Positional invocation
        const resPos = PomodoroCore.calculateSkipTransition('focus', 4);
        if (resPos.nextMode !== 'longBreak' || resPos.toastMessage !== 'LONG BREAK' || resPos.cycleCount !== 4) {
            process.exit(1);
        }

        // Object invocation with currentMode & cycleCount
        const resObj1 = PomodoroCore.calculateSkipTransition({ currentMode: 'focus', cycleCount: 4 });
        if (resObj1.nextMode !== 'longBreak' || resObj1.toastMessage !== 'LONG BREAK' || resObj1.cycleCount !== 4) {
            process.exit(2);
        }

        // Object invocation with mode & cycleCount
        const resObj2 = PomodoroCore.calculateSkipTransition({ mode: 'shortBreak', cycleCount: 3 });
        if (resObj2.nextMode !== 'focus' || resObj2.toastMessage !== 'FOCUS MODE' || resObj2.cycleCount !== 3) {
            process.exit(3);
        }

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_skip_transition_boundary_and_corrupted_inputs(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Unknown mode falls back safely to focus
        const resBadMode = PomodoroCore.calculateSkipTransition('invalidMode', 3);
        if (resBadMode.nextMode !== 'focus' || resBadMode.toastMessage !== 'FOCUS MODE' || resBadMode.cycleCount !== 3) {
            process.exit(1);
        }

        const resNullMode = PomodoroCore.calculateSkipTransition(null, 2);
        if (resNullMode.nextMode !== 'focus' || resNullMode.toastMessage !== 'FOCUS MODE' || resNullMode.cycleCount !== 2) {
            process.exit(2);
        }

        // Corrupted cycle count falls back to 1
        const resBadCycle = PomodoroCore.calculateSkipTransition('focus', 'corrupted');
        if (resBadCycle.nextMode !== 'shortBreak' || resBadCycle.toastMessage !== 'SHORT BREAK' || resBadCycle.cycleCount !== 1) {
            process.exit(3);
        }

        const resNaNCycle = PomodoroCore.calculateSkipTransition('focus', NaN);
        if (resNaNCycle.nextMode !== 'shortBreak' || resNaNCycle.cycleCount !== 1) {
            process.exit(4);
        }

        const resNegCycle = PomodoroCore.calculateSkipTransition('focus', -4);
        if (resNegCycle.nextMode !== 'shortBreak' || resNegCycle.cycleCount !== 1) {
            process.exit(5);
        }

        // Numeric string cycle count parses correctly
        const resStrCycle = PomodoroCore.calculateSkipTransition('focus', '4');
        if (resStrCycle.nextMode !== 'longBreak' || resStrCycle.toastMessage !== 'LONG BREAK' || resStrCycle.cycleCount !== 4) {
            process.exit(6);
        }

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_get_mode_toast_message_mappings_and_fallbacks(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (typeof PomodoroCore.getModeToastMessage !== 'function') {
            console.error('FAIL: getModeToastMessage is not a function');
            process.exit(1);
        }

        // Standard mappings
        if (PomodoroCore.getModeToastMessage('focus') !== 'FOCUS MODE') process.exit(2);
        if (PomodoroCore.getModeToastMessage('shortBreak') !== 'SHORT BREAK') process.exit(3);
        if (PomodoroCore.getModeToastMessage('longBreak') !== 'LONG BREAK') process.exit(4);

        // Fallback for null, undefined, empty, or unknown
        if (PomodoroCore.getModeToastMessage(null) !== 'FOCUS MODE') process.exit(5);
        if (PomodoroCore.getModeToastMessage(undefined) !== 'FOCUS MODE') process.exit(6);
        if (PomodoroCore.getModeToastMessage('') !== 'FOCUS MODE') process.exit(7);
        if (PomodoroCore.getModeToastMessage('unknown') !== 'FOCUS MODE') process.exit(8);
        if (PomodoroCore.getModeToastMessage(123) !== 'FOCUS MODE') process.exit(9);

        // Prototype pollution resistance
        if (PomodoroCore.getModeToastMessage('__proto__') !== 'FOCUS MODE') process.exit(10);
        if (PomodoroCore.getModeToastMessage('constructor') !== 'FOCUS MODE') process.exit(11);
        if (PomodoroCore.getModeToastMessage('prototype') !== 'FOCUS MODE') process.exit(12);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_index_html_wires_skip_transition_core(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn(
            "PomodoroCore.calculateSkipTransition",
            html,
            "index.html must use PomodoroCore.calculateSkipTransition to decouple skip transition logic"
        )
        self.assertIn(
            "PomodoroCore.getModeToastMessage",
            html,
            "index.html must use PomodoroCore.getModeToastMessage to decouple mode toast messages"
        )


if __name__ == "__main__":
    unittest.main()
