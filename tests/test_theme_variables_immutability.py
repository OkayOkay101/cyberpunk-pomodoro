import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestThemeVariablesImmutability(unittest.TestCase):
    def test_theme_lookups_match_legacy_outputs_without_array_scans(self):
        js_code = """
        const assert = require('assert');
        const { PomodoroCore } = require('./core.js');
        const variables = {
          cyan: { border: '#1f294d', primary: '#00f0ff', accent: '#ff0055' },
          pink: { border: '#4d1f3d', primary: '#ff007f', accent: '#00f0ff' },
          yellow: { border: '#4d431f', primary: '#ffe600', accent: '#00f0ff' },
          green: { border: '#1f4d2f', primary: '#00ff66', accent: '#ffe600' }
        };
        const labels = {
          cyan: 'Cyan Matrix',
          pink: 'Neon Pink / Outrun',
          yellow: 'Night City Yellow',
          green: 'Emerald Hacker'
        };
        const inputs = ['cyan', 'pink', 'yellow', 'green', 'unknown', '', null, undefined, 1, new String('pink')];
        for (const input of inputs) {
          const safeTheme = typeof input === 'string' && ['cyan', 'pink', 'yellow', 'green'].includes(input) ? input : 'cyan';
          assert.deepStrictEqual(PomodoroCore.getThemeVariables(input), variables[safeTheme]);
          assert.strictEqual(PomodoroCore.getThemeLabel(input), labels[safeTheme]);
        }

        const originalIncludes = Array.prototype.includes;
        let greenVariables;
        let fallbackVariables;
        let pinkLabel;
        let fallbackLabel;
        Array.prototype.includes = () => { throw new Error('theme lookup scanned an array'); };
        try {
          greenVariables = PomodoroCore.getThemeVariables('green');
          fallbackVariables = PomodoroCore.getThemeVariables('invalid');
          pinkLabel = PomodoroCore.getThemeLabel('pink');
          fallbackLabel = PomodoroCore.getThemeLabel('invalid');
        } finally {
          Array.prototype.includes = originalIncludes;
        }
        assert.deepStrictEqual(greenVariables, variables.green);
        assert.deepStrictEqual(fallbackVariables, variables.cyan);
        assert.strictEqual(pinkLabel, labels.pink);
        assert.strictEqual(fallbackLabel, labels.cyan);
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")

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
