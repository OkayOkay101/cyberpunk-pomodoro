import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestNetrunnerLeveling(unittest.TestCase):
    def _run_node(self, js_code: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )

    def test_calculate_netrunner_exp(self):
        js_code = """
        const { calculateNetrunnerExp } = require('./netrunner_leveling.js');

        // 4 sessions (25 each = 100) + 100 mins (100) = 200
        const exp = calculateNetrunnerExp(4, 100);
        if (exp !== 200) {
            console.error('FAIL: expected 200, got', exp);
            process.exit(1);
        }

        // Falsy and invalid inputs must fallback safely to 0
        if (calculateNetrunnerExp(null, undefined) !== 0) process.exit(2);
        if (calculateNetrunnerExp(-5, -100) !== 0) process.exit(3);
        if (calculateNetrunnerExp(NaN, Infinity) !== 0) process.exit(4);
        if (calculateNetrunnerExp(2.9, 10.8) !== 60) process.exit(5);
        if (calculateNetrunnerExp('2', '10') !== 0) process.exit(6);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_rank_progression_across_all_levels(self):
        js_code = """
        const { getNetrunnerRank } = require('./netrunner_leveling.js');

        const testCases = [
            { exp: 0, expectedLvl: 1, expectedTitle: 'Script Kiddie', expectedProgress: 0 },
            { exp: 99, expectedLvl: 1, expectedTitle: 'Script Kiddie', expectedProgress: 99 },
            { exp: 100, expectedLvl: 2, expectedTitle: 'Wirehead', expectedProgress: 0 },
            { exp: 299, expectedLvl: 2, expectedTitle: 'Wirehead', expectedProgress: 99 },
            { exp: 300, expectedLvl: 3, expectedTitle: 'Cyber Jockey', expectedProgress: 0 },
            { exp: 599, expectedLvl: 3, expectedTitle: 'Cyber Jockey', expectedProgress: 99 },
            { exp: 600, expectedLvl: 4, expectedTitle: 'Netrunner', expectedProgress: 0 },
            { exp: 999, expectedLvl: 4, expectedTitle: 'Netrunner', expectedProgress: 99 },
            { exp: 1000, expectedLvl: 5, expectedTitle: 'Subnet Phantom', expectedProgress: 0 },
            { exp: 1499, expectedLvl: 5, expectedTitle: 'Subnet Phantom', expectedProgress: 99 },
            { exp: 1500, expectedLvl: 6, expectedTitle: 'Street Legend', expectedProgress: 100 },
            { exp: 5000, expectedLvl: 6, expectedTitle: 'Street Legend', expectedProgress: 100 }
        ];

        for (const tc of testCases) {
            const rank = getNetrunnerRank(tc.exp);
            if (rank.level !== tc.expectedLvl || rank.title !== tc.expectedTitle || rank.progressPercent !== tc.expectedProgress) {
                console.error('FAIL on exp', tc.exp, 'expected', tc, 'got', rank);
                process.exit(1);
            }
            if (!Object.isFrozen(rank)) {
                console.error('FAIL: rank must be frozen');
                process.exit(2);
            }
        }

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_format_netrunner_status(self):
        js_code = """
        const { formatNetrunnerStatus } = require('./netrunner_leveling.js');

        const s1 = formatNetrunnerStatus(0);
        if (s1 !== 'LVL 01 // SCRIPT KIDDIE [0%]') {
            console.error('FAIL s1:', s1);
            process.exit(1);
        }

        const s4 = formatNetrunnerStatus(700);
        // Netrunner level 4: 600-999. Range = 400. Gained = 100. Progress = 25%
        if (s4 !== 'LVL 04 // NETRUNNER [25%]') {
            console.error('FAIL s4:', s4);
            process.exit(2);
        }

        const s6 = formatNetrunnerStatus(2000);
        if (s6 !== 'LVL 06 // STREET LEGEND [100%]') {
            console.error('FAIL s6:', s6);
            process.exit(3);
        }

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_parse_stored_exp_fallbacks(self):
        js_code = """
        const { parseStoredExp } = require('./netrunner_leveling.js');

        if (parseStoredExp('450') !== 450) process.exit(1);
        if (parseStoredExp(120) !== 120) process.exit(2);
        if (parseStoredExp('  300  ') !== 300) process.exit(3);
        if (parseStoredExp('0007') !== 7) process.exit(4);

        if (parseStoredExp(null) !== 0) process.exit(5);
        if (parseStoredExp(undefined) !== 0) process.exit(6);
        if (parseStoredExp('') !== 0) process.exit(7);
        if (parseStoredExp('invalid') !== 0) process.exit(8);
        if (parseStoredExp('450xp') !== 0) process.exit(9);
        if (parseStoredExp('1.5') !== 0) process.exit(10);
        if (parseStoredExp('1e2') !== 0) process.exit(11);
        if (parseStoredExp('   ') !== 0) process.exit(12);
        if (parseStoredExp('-50') !== 0) process.exit(13);
        if (parseStoredExp(-50) !== 0) process.exit(14);
        if (parseStoredExp(NaN) !== 0) process.exit(15);
        if (parseStoredExp(Infinity) !== 0) process.exit(16);
        if (parseStoredExp({ exp: 450 }) !== 0) process.exit(17);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
