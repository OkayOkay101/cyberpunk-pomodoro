import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestResetCore(unittest.TestCase):
    def _run_node(self, js_code: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )

    def test_calculate_reset_action_when_running_and_not_confirming(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (typeof PomodoroCore.calculateResetAction !== 'function') {
            console.error('FAIL: calculateResetAction is not a function');
            process.exit(1);
        }

        const res = PomodoroCore.calculateResetAction(true, false);
        if (res.needsConfirmation !== true) process.exit(2);
        if (res.buttonText !== 'CONFIRM?') process.exit(3);
        if (res.confirming !== true) process.exit(4);
        if (res.timeoutMs !== 2500) process.exit(5);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_reset_action_when_already_confirming(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Second click during confirmation window triggers reset
        const res1 = PomodoroCore.calculateResetAction(true, true);
        if (res1.needsConfirmation !== false) process.exit(1);
        if (res1.buttonText !== 'RESET') process.exit(2);
        if (res1.confirming !== false) process.exit(3);
        if (res1.timeoutMs !== 0) process.exit(4);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_reset_action_when_not_running(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // When paused or stopped, resets immediately without confirmation
        const resPaused = PomodoroCore.calculateResetAction(false, false);
        if (resPaused.needsConfirmation !== false) process.exit(1);
        if (resPaused.buttonText !== 'RESET') process.exit(2);
        if (resPaused.confirming !== false) process.exit(3);
        if (resPaused.timeoutMs !== 0) process.exit(4);

        const resPausedWithStaleConfirm = PomodoroCore.calculateResetAction(false, true);
        if (resPausedWithStaleConfirm.needsConfirmation !== false) process.exit(5);
        if (resPausedWithStaleConfirm.buttonText !== 'RESET') process.exit(6);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_reset_action_object_params(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const resObj1 = PomodoroCore.calculateResetAction({ isRunning: true, isConfirming: false });
        if (resObj1.needsConfirmation !== true) process.exit(1);
        if (resObj1.buttonText !== 'CONFIRM?') process.exit(2);

        const resObj2 = PomodoroCore.calculateResetAction({ isRunning: true, confirming: true });
        if (resObj2.needsConfirmation !== false) process.exit(3);
        if (resObj2.buttonText !== 'RESET') process.exit(4);

        const resObj3 = PomodoroCore.calculateResetAction({ isRunning: false, isConfirming: false });
        if (resObj3.needsConfirmation !== false) process.exit(5);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_reset_action_edge_cases(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Missing or nullish inputs
        const resNull = PomodoroCore.calculateResetAction(null, null);
        if (resNull.needsConfirmation !== false) process.exit(1);
        if (resNull.buttonText !== 'RESET') process.exit(2);

        const resUndef = PomodoroCore.calculateResetAction(undefined);
        if (resUndef.needsConfirmation !== false) process.exit(3);

        const resEmpty = PomodoroCore.calculateResetAction({});
        if (resEmpty.needsConfirmation !== false) process.exit(4);

        // Coercion from numbers/strings
        const resTruthy = PomodoroCore.calculateResetAction(1, 0);
        if (resTruthy.needsConfirmation !== true) process.exit(5);

        const resBothTruthy = PomodoroCore.calculateResetAction(1, 1);
        if (resBothTruthy.needsConfirmation !== false) process.exit(6);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_cycle_reset_focus_mode(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (typeof PomodoroCore.calculateCycleReset !== 'function') {
            console.error('FAIL: calculateCycleReset is not a function');
            process.exit(1);
        }

        const res = PomodoroCore.calculateCycleReset('focus');
        if (res.nextCycleCount !== 1) process.exit(2);
        if (res.sessionLabel !== 'SESSION 01 // DEEP WORK') process.exit(3);
        if (res.soundType !== 'break_end') process.exit(4);
        if (res.feedbackText !== 'DONE!') process.exit(5);
        if (res.feedbackAriaLabel !== 'รีเซ็ตรอบเป็น 01 สำเร็จ') process.exit(6);
        if (res.feedbackTimeoutMs !== 1200) process.exit(7);
        if (!res.storage || res.storage.cp_cycle !== '1') process.exit(8);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_cycle_reset_break_modes(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const resShort = PomodoroCore.calculateCycleReset('shortBreak');
        if (resShort.nextCycleCount !== 1) process.exit(1);
        if (resShort.sessionLabel !== 'RECHARGE // SHORT BREAK') process.exit(2);
        if (resShort.soundType !== 'break_end') process.exit(3);
        if (resShort.storage.cp_cycle !== '1') process.exit(4);

        const resLong = PomodoroCore.calculateCycleReset('longBreak');
        if (resLong.nextCycleCount !== 1) process.exit(5);
        if (resLong.sessionLabel !== 'REST // LONG BREAK') process.exit(6);
        if (resLong.soundType !== 'break_end') process.exit(7);
        if (resLong.storage.cp_cycle !== '1') process.exit(8);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_cycle_reset_object_params(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const resObj1 = PomodoroCore.calculateCycleReset({ currentMode: 'focus' });
        if (resObj1.nextCycleCount !== 1) process.exit(1);
        if (resObj1.sessionLabel !== 'SESSION 01 // DEEP WORK') process.exit(2);

        const resObj2 = PomodoroCore.calculateCycleReset({ mode: 'shortBreak' });
        if (resObj2.nextCycleCount !== 1) process.exit(3);
        if (resObj2.sessionLabel !== 'RECHARGE // SHORT BREAK') process.exit(4);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_cycle_reset_fallbacks_and_safety(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const resNull = PomodoroCore.calculateCycleReset(null);
        if (resNull.nextCycleCount !== 1) process.exit(1);
        if (resNull.sessionLabel !== 'SESSION 01 // DEEP WORK') process.exit(2);

        const resUndef = PomodoroCore.calculateCycleReset(undefined);
        if (resUndef.nextCycleCount !== 1) process.exit(3);
        if (resUndef.sessionLabel !== 'SESSION 01 // DEEP WORK') process.exit(4);

        const resNum = PomodoroCore.calculateCycleReset(999);
        if (resNum.nextCycleCount !== 1) process.exit(5);
        if (resNum.sessionLabel !== 'SESSION 01 // DEEP WORK') process.exit(6);

        // Prototype pollution resistance
        const resProto = PomodoroCore.calculateCycleReset('__proto__');
        if (resProto.nextCycleCount !== 1) process.exit(7);
        if (resProto.sessionLabel !== 'SESSION 01 // DEEP WORK') process.exit(8);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_index_html_wires_reset_core(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn(
            "PomodoroCore.calculateResetAction",
            html,
            "index.html must use PomodoroCore.calculateResetAction to decouple reset action logic"
        )
        self.assertIn(
            "PomodoroCore.calculateCycleReset",
            html,
            "index.html must use PomodoroCore.calculateCycleReset to decouple cycle reset logic"
        )


if __name__ == "__main__":
    unittest.main()
