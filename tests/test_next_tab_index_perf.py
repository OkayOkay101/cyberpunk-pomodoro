import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestNextTabIndexPerformance(unittest.TestCase):
    """
    Performance and behavioral verification for PomodoroCore.getNextTabIndex.
    Verifies elimination of redundant parseInt string coercion and sequential string
    comparisons via early navigation key check and numeric fast-path.
    """

    def _run_node_script(self, script: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["node", "-e", script],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )

    def test_next_tab_index_fast_path_and_switch(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const fnStr = PomodoroCore.getNextTabIndex.toString();
        // Function must not unconditionally call parseInt at entry
        if (/^\\s*getNextTabIndex\\s*\\([^)]*\\)\\s*\\{\\s*const\\s+total\\s*=\\s*parseInt/.test(fnStr)) {
            console.error('FAIL: getNextTabIndex unconditionally calls parseInt without numeric fast-path');
            process.exit(2);
        }
        if (!/switch\\s*\\(key\\)/.test(fnStr)) {
            console.error('FAIL: getNextTabIndex does not use switch(key) dispatch');
            process.exit(3);
        }

        console.log('SUCCESS');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_next_tab_index_standard_navigation(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // ArrowRight & ArrowDown cycle forward with wrapping
        if (PomodoroCore.getNextTabIndex(0, 3, 'ArrowRight') !== 1) process.exit(1);
        if (PomodoroCore.getNextTabIndex(1, 3, 'ArrowRight') !== 2) process.exit(2);
        if (PomodoroCore.getNextTabIndex(2, 3, 'ArrowRight') !== 0) process.exit(3);
        if (PomodoroCore.getNextTabIndex(0, 3, 'ArrowDown') !== 1) process.exit(4);
        if (PomodoroCore.getNextTabIndex(2, 3, 'ArrowDown') !== 0) process.exit(5);

        // ArrowLeft & ArrowUp cycle backward with wrapping
        if (PomodoroCore.getNextTabIndex(0, 3, 'ArrowLeft') !== 2) process.exit(6);
        if (PomodoroCore.getNextTabIndex(2, 3, 'ArrowLeft') !== 1) process.exit(7);
        if (PomodoroCore.getNextTabIndex(1, 3, 'ArrowLeft') !== 0) process.exit(8);
        if (PomodoroCore.getNextTabIndex(0, 3, 'ArrowUp') !== 2) process.exit(9);
        if (PomodoroCore.getNextTabIndex(2, 3, 'ArrowUp') !== 1) process.exit(10);

        // Home jumps to first tab (0), End jumps to last tab (total - 1)
        if (PomodoroCore.getNextTabIndex(1, 3, 'Home') !== 0) process.exit(11);
        if (PomodoroCore.getNextTabIndex(2, 3, 'Home') !== 0) process.exit(12);
        if (PomodoroCore.getNextTabIndex(0, 3, 'End') !== 2) process.exit(13);
        if (PomodoroCore.getNextTabIndex(1, 3, 'End') !== 2) process.exit(14);

        // Unhandled keys return -1
        if (PomodoroCore.getNextTabIndex(0, 3, 'Tab') !== -1) process.exit(15);
        if (PomodoroCore.getNextTabIndex(0, 3, 'Enter') !== -1) process.exit(16);
        if (PomodoroCore.getNextTabIndex(0, 3, 'Space') !== -1) process.exit(17);
        if (PomodoroCore.getNextTabIndex(0, 3, 'Escape') !== -1) process.exit(18);

        // Boundary fallbacks
        if (PomodoroCore.getNextTabIndex(-1, 3, 'ArrowRight') !== -1) process.exit(19);
        if (PomodoroCore.getNextTabIndex(3, 3, 'ArrowRight') !== -1) process.exit(20);
        if (PomodoroCore.getNextTabIndex(0, 0, 'ArrowRight') !== -1) process.exit(21);
        if (PomodoroCore.getNextTabIndex(null, 3, 'ArrowRight') !== -1) process.exit(22);

        console.log('SUCCESS');
        """
        proc = self._run_node_script(js_code)
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_next_tab_index_exhaustive_baseline_equality(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        function baselineGetNextTabIndex(currentIndex, totalTabs, key) {
            const total = parseInt(totalTabs, 10);
            const curr = parseInt(currentIndex, 10);
            if (isNaN(total) || total <= 0 || isNaN(curr) || curr < 0 || curr >= total) return -1;
            if (key === 'ArrowRight' || key === 'ArrowDown') return (curr + 1) % total;
            if (key === 'ArrowLeft' || key === 'ArrowUp') return (curr - 1 + total) % total;
            if (key === 'Home') return 0;
            if (key === 'End') return total - 1;
            return -1;
        }

        const testKeys = [
            'ArrowRight', 'ArrowDown', 'ArrowLeft', 'ArrowUp', 'Home', 'End',
            'Tab', 'Enter', 'Space', 'Escape', 'ArrowRight ', 'arrowright',
            '', '   ', null, undefined, NaN, Infinity, -Infinity, 0, 1, {}, [], true, false
        ];

        const testIndices = [
            0, 1, 2, 3, -1, -5, 10,
            0.0, 0.5, 1.2, 2.9, -0.5, -1.2,
            '0', '1', '2', '3', '-1', ' 1 ', '002', '1.5', '-0.5',
            'abc', '', null, undefined, NaN, Infinity, -Infinity, {}, [], true, false
        ];

        const testTotals = [
            0, 1, 2, 3, 5, 10, -1, -3,
            1.0, 2.5, 3.9, -1.5, -0.5,
            '1', '2', '3', '0', '-1', ' 3 ', '003', '3.5',
            'abc', '', null, undefined, NaN, Infinity, -Infinity, {}, [], true, false
        ];

        for (const k of testKeys) {
            for (const c of testIndices) {
                for (const t of testTotals) {
                    const base = baselineGetNextTabIndex(c, t, k);
                    const opt = PomodoroCore.getNextTabIndex(c, t, k);
                    if (base !== opt) {
                        console.error(`Mismatch for currentIndex=${JSON.stringify(c)}, totalTabs=${JSON.stringify(t)}, key=${JSON.stringify(k)}: expected ${base}, got ${opt}`);
                        process.exit(1);
                    }
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
