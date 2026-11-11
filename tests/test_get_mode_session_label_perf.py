import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestGetModeSessionLabelPerformance(unittest.TestCase):
    """
    Performance and behavioral verification for PomodoroCore.getModeSessionLabel
    and PomodoroCore.formatSessionLabel.
    Verifies elimination of redundant parseInt numeric-to-string coercion,
    intermediate template string allocations, and dynamic dispatch via
    pre-computed SESSION_LABELS lookup table and numeric fast-path.
    """

    def _run_node_script(self, script: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )

    def test_get_mode_session_label_fast_path_and_lookup(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const fnStr = PomodoroCore.getModeSessionLabel.toString();

        // Must check focus mode and typeof cycleCount === 'number'
        if (!/typeof\\s+cycleCount\\s*===\\s*['"]number['"]/.test(fnStr)) {
            console.error('FAIL: getModeSessionLabel missing numeric fast-path check');
            process.exit(2);
        }

        // Must use pre-computed SESSION_LABELS lookup table
        if (!/SESSION_LABELS/.test(fnStr)) {
            console.error('FAIL: getModeSessionLabel missing SESSION_LABELS lookup table');
            process.exit(3);
        }

        console.log('SUCCESS');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_format_session_label_fast_path(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const fnStr = PomodoroCore.formatSessionLabel.toString();

        // Must not unconditionally call parseInt at entry
        if (/^\\s*formatSessionLabel\\s*\\([^)]*\\)\\s*\\{\\s*const\\s+parsed\\s*=\\s*parseInt/.test(fnStr)) {
            console.error('FAIL: formatSessionLabel unconditionally calls parseInt without numeric fast-path');
            process.exit(2);
        }

        // Must use pre-computed SESSION_LABELS
        if (!/SESSION_LABELS/.test(fnStr)) {
            console.error('FAIL: formatSessionLabel missing SESSION_LABELS lookup table');
            process.exit(3);
        }

        console.log('SUCCESS');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_get_mode_session_label_behavioral_equivalence(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Verify standard modes and cycles
        if (PomodoroCore.getModeSessionLabel('focus', 1) !== 'SESSION 01 // DEEP WORK') process.exit(1);
        if (PomodoroCore.getModeSessionLabel('focus', 4) !== 'SESSION 04 // DEEP WORK') process.exit(2);
        if (PomodoroCore.getModeSessionLabel('focus', 10) !== 'SESSION 10 // DEEP WORK') process.exit(3);
        if (PomodoroCore.getModeSessionLabel('focus', 99) !== 'SESSION 99 // DEEP WORK') process.exit(4);
        if (PomodoroCore.getModeSessionLabel('focus', 100) !== 'SESSION 100 // DEEP WORK') process.exit(5);
        if (PomodoroCore.getModeSessionLabel('focus', 105) !== 'SESSION 105 // DEEP WORK') process.exit(6);

        // Verify break modes
        if (PomodoroCore.getModeSessionLabel('shortBreak', 1) !== 'RECHARGE // SHORT BREAK') process.exit(7);
        if (PomodoroCore.getModeSessionLabel('shortBreak', 4) !== 'RECHARGE // SHORT BREAK') process.exit(8);
        if (PomodoroCore.getModeSessionLabel('longBreak', 4) !== 'REST // LONG BREAK') process.exit(9);
        if (PomodoroCore.getModeSessionLabel('longBreak', 8) !== 'REST // LONG BREAK') process.exit(10);

        // Fallbacks for unknown modes or non-string modes
        if (PomodoroCore.getModeSessionLabel('unknown', 1) !== 'SESSION 01 // DEEP WORK') process.exit(11);
        if (PomodoroCore.getModeSessionLabel(null, 2) !== 'SESSION 02 // DEEP WORK') process.exit(12);
        if (PomodoroCore.getModeSessionLabel(undefined, 3) !== 'SESSION 03 // DEEP WORK') process.exit(13);

        // Boundary and invalid cycle counts
        if (PomodoroCore.getModeSessionLabel('focus', 0) !== 'SESSION 01 // DEEP WORK') process.exit(14);
        if (PomodoroCore.getModeSessionLabel('focus', -5) !== 'SESSION 01 // DEEP WORK') process.exit(15);
        if (PomodoroCore.getModeSessionLabel('focus', '5') !== 'SESSION 05 // DEEP WORK') process.exit(16);
        if (PomodoroCore.getModeSessionLabel('focus', '09') !== 'SESSION 09 // DEEP WORK') process.exit(17);
        if (PomodoroCore.getModeSessionLabel('focus', 'invalid') !== 'SESSION 01 // DEEP WORK') process.exit(18);
        if (PomodoroCore.getModeSessionLabel('focus', null) !== 'SESSION 01 // DEEP WORK') process.exit(19);
        if (PomodoroCore.getModeSessionLabel('focus', undefined) !== 'SESSION 01 // DEEP WORK') process.exit(20);
        if (PomodoroCore.getModeSessionLabel('focus', NaN) !== 'SESSION 01 // DEEP WORK') process.exit(21);
        if (PomodoroCore.getModeSessionLabel('focus', 4.8) !== 'SESSION 04 // DEEP WORK') process.exit(22);

        // Identity check: must return reference-equal string for identical standard cycle
        const refA = PomodoroCore.getModeSessionLabel('focus', 5);
        const refB = PomodoroCore.getModeSessionLabel('focus', 5);
        if (refA !== refB) {
            console.error('FAIL: getModeSessionLabel returned different string instances for cycle 5');
            process.exit(23);
        }

        console.log('SUCCESS');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_session_labels_preserve_large_cycle_counts(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');
        const cases = [2147483648, 2147483649, 4294967296];

        for (const cycleCount of cases) {
            const expected = `SESSION ${cycleCount} // DEEP WORK`;
            if (PomodoroCore.formatSessionLabel(cycleCount) !== expected) {
                console.error(`formatSessionLabel truncated ${cycleCount}`);
                process.exit(1);
            }
            if (PomodoroCore.getModeSessionLabel('focus', cycleCount) !== expected) {
                console.error(`getModeSessionLabel truncated ${cycleCount}`);
                process.exit(2);
            }
            if (PomodoroCore.parseCycleCount(cycleCount) !== cycleCount) {
                console.error(`parseCycleCount truncated ${cycleCount}`);
                process.exit(3);
            }
        }

        console.log('SUCCESS');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)


if __name__ == '__main__':
    unittest.main()
