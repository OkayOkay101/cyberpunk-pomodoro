import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestThemeVariablesImmutability(unittest.TestCase):
    def test_mutating_returned_theme_does_not_change_later_results(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');
        const original = PomodoroCore.getThemeVariables('cyan');

        original.primary = '#000000';
        original.border = '#000000';
        original.accent = '#000000';

        const later = PomodoroCore.getThemeVariables('cyan');
        if (later.primary !== '#00f0ff' || later.border !== '#1f294d' || later.accent !== '#ff0055') {
            console.error('FAIL: Mutating returned theme variables changed the shared palette');
            process.exit(1);
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


if __name__ == "__main__":
    unittest.main()
