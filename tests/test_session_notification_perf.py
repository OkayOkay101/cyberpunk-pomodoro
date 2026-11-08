import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestSessionNotificationPerformance(unittest.TestCase):
    """
    Performance and behavioral verification for PomodoroCore.getSessionNotification
    and PomodoroCore.parseCycleCount.
    Verifies elimination of redundant parseInt string coercion, dynamic template string
    allocations, and object heap churn via numeric fast-path and pre-computed
    FOCUS_NOTIFICATIONS lookup table.
    """

    def _run_node_script(self, script: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )

    def test_session_notification_fast_path_and_lookup(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const fnStr = PomodoroCore.getSessionNotification.toString();
        const parseFnStr = PomodoroCore.parseCycleCount.toString();

        // Check that parseCycleCount does not unconditionally call parseInt at entry
        if (/^\\s*parseCycleCount\\s*\\([^)]*\\)\\s*\\{\\s*const\\s+parsed\\s*=\\s*parseInt/.test(parseFnStr)) {
            console.error('FAIL: parseCycleCount unconditionally calls parseInt without numeric fast-path');
            process.exit(2);
        }
        if (!/FOCUS_NOTIFICATIONS/.test(fnStr)) {
            console.error('FAIL: getSessionNotification does not use FOCUS_NOTIFICATIONS lookup table');
            process.exit(3);
        }

        // Standard notification payload verification
        const n1 = PomodoroCore.getSessionNotification('focus', 1);
        if (n1.title !== 'FOCUS COMPLETE // CYBERPUNK POMODORO') process.exit(4);
        if (n1.body !== 'จบ Session 1 เรียบร้อยแล้ว ได้เวลาพักผ่อน!') process.exit(5);
        if (n1.soundType !== 'focus_end') process.exit(6);

        const n4 = PomodoroCore.getSessionNotification('focus', 4);
        if (n4.body !== 'จบ Session 4 เรียบร้อยแล้ว ได้เวลาพักผ่อน!') process.exit(7);

        // Object cache reuse and immutability for standard cycles (1..100)
        const n1Again = PomodoroCore.getSessionNotification('focus', 1);
        if (n1 !== n1Again) {
            console.error('FAIL: getSessionNotification should reuse cached immutable object for cycle 1');
            process.exit(8);
        }

        try {
            n1.title = 'MUTATED';
        } catch (e) {}
        if (n1.title !== 'FOCUS COMPLETE // CYBERPUNK POMODORO') {
            console.error('FAIL: cached focus notification object must be frozen');
            process.exit(9);
        }

        console.log('SUCCESS');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_session_notification_exhaustive_baseline_equality(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const BASE_BREAK_NOTIFICATION = Object.freeze({
            title: 'BREAK FINISHED // BACK TO MATRIX',
            body: 'หมดเวลาพักแล้ว พร้อมกลับมาลุยภารกิจต่อหรือยัง?',
            soundType: 'break_end'
        });

        function baselineParseCycleCount(cycleCount) {
            const parsed = parseInt(cycleCount, 10);
            return (!isNaN(parsed) && parsed >= 1) ? parsed : 1;
        }

        function baselineGetSessionNotification(modeOrParams, cycleCount) {
            let mode = modeOrParams;
            let cycle = cycleCount;

            if (modeOrParams && typeof modeOrParams === 'object') {
              mode = modeOrParams.mode;
              cycle = modeOrParams.cycleCount;
            }

            if (mode === 'focus') {
              const validCycle = baselineParseCycleCount(cycle);
              return {
                title: 'FOCUS COMPLETE // CYBERPUNK POMODORO',
                body: `จบ Session ${validCycle} เรียบร้อยแล้ว ได้เวลาพักผ่อน!`,
                soundType: 'focus_end'
              };
            }

            return BASE_BREAK_NOTIFICATION;
        }

        const testModes = [
            'focus', 'shortBreak', 'longBreak', 'unknown',
            '', '   ', null, undefined, NaN, Infinity, -Infinity, 0, 1, {}, [], true, false
        ];

        const testCycles = [
            1, 2, 3, 4, 10, 50, 100, 101, 250,
            0, -1, -10,
            0.5, 1.2, 3.9, 4.5, 99.9, 100.1, -0.5,
            '1', '4', '08', '100', '101', '0', '-5', '2.5', '99.9',
            '1 session', '4sessions', '004', ' 10 ',
            null, undefined, NaN, Infinity, -Infinity,
            '', '   ', 'corrupted', {}, [], [4], true, false
        ];

        for (const m of testModes) {
            for (const c of testCycles) {
                const base = baselineGetSessionNotification(m, c);
                const opt = PomodoroCore.getSessionNotification(m, c);
                if (base.title !== opt.title || base.body !== opt.body || base.soundType !== opt.soundType) {
                    console.error(`Mismatch for mode=${JSON.stringify(m)}, cycle=${JSON.stringify(c)}`);
                    process.exit(10);
                }

                const baseParse = baselineParseCycleCount(c);
                const optParse = PomodoroCore.parseCycleCount(c);
                if (baseParse !== optParse) {
                    console.error(`parseCycleCount mismatch for ${JSON.stringify(c)}`);
                    process.exit(11);
                }
            }
        }

        // Test object parameter style
        for (const m of ['focus', 'shortBreak', 'longBreak', 'unknown', null]) {
            for (const c of [1, 2, 4, 10, 100, 101, '5', 'corrupted', null]) {
                const base = baselineGetSessionNotification({ mode: m, cycleCount: c });
                const opt = PomodoroCore.getSessionNotification({ mode: m, cycleCount: c });
                if (base.title !== opt.title || base.body !== opt.body || base.soundType !== opt.soundType) {
                    console.error(`Mismatch for object parameter {mode: ${m}, cycleCount: ${c}}`);
                    process.exit(12);
                }
            }
        }

        console.log('SUCCESS');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
