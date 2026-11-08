import unittest
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestPrototypePollutionDefense(unittest.TestCase):
    def test_deserialize_config_blocks_proto_pollution(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Test that __proto__, constructor, prototype are not used for pollution
        const vectors = ['__proto__', 'constructor', 'prototype'];
        
        for (const vector of vectors) {
            const maliciousJson = '{"' + vector + '": {"polluted": true}}';
            const result = PomodoroCore.deserializeConfig(maliciousJson, { safe: 'value' });
            
            // The dangerous key should not be present as own property in result
            if (Object.prototype.hasOwnProperty.call(result, vector)) {
                console.error('FAIL: deserializeConfig allows dangerous key: ' + vector);
                process.exit(1);
            }
            
            // Prototype should not be polluted
            if ('polluted' in {}) {
                console.error('FAIL: Prototype was polluted via ' + vector);
                process.exit(2);
            }
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

    def test_get_theme_variables_rejects_proto_keys(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const vectors = ['__proto__', 'constructor', 'prototype'];
        
        for (const vector of vectors) {
            const result = PomodoroCore.getThemeVariables(vector);
            
            // Should return a valid theme object (cyan default), not Object.prototype or Function
            if (!result || typeof result !== 'object' || Array.isArray(result)) {
                console.error('FAIL: getThemeVariables(' + vector + ') returned non-object: ' + result);
                process.exit(1);
            }
            
            // Should have valid theme properties
            if (typeof result.primary !== 'string' || typeof result.border !== 'string' || typeof result.accent !== 'string') {
                console.error('FAIL: getThemeVariables(' + vector + ') returned invalid theme: ' + JSON.stringify(result));
                process.exit(2);
            }
            
            // Should be the cyan theme (default fallback)
            if (result.primary !== '#00f0ff' || result.border !== '#1f294d' || result.accent !== '#ff0055') {
                console.error('FAIL: getThemeVariables(' + vector + ') did not return cyan default');
                process.exit(3);
            }
        }
        
        // Valid themes should still work
        const cyan = PomodoroCore.getThemeVariables('cyan');
        if (cyan.primary !== '#00f0ff') {
            console.error('FAIL: valid theme cyan broken');
            process.exit(4);
        }
        
        const pink = PomodoroCore.getThemeVariables('pink');
        if (pink.primary !== '#ff007f') {
            console.error('FAIL: valid theme pink broken');
            process.exit(5);
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

    def test_get_theme_label_rejects_proto_keys(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const vectors = ['__proto__', 'constructor', 'prototype'];
        
        for (const vector of vectors) {
            const result = PomodoroCore.getThemeLabel(vector);
            
            // Should return a valid string label (cyan default)
            if (typeof result !== 'string' || result.length === 0) {
                console.error('FAIL: getThemeLabel(' + vector + ') returned invalid label: ' + result);
                process.exit(1);
            }
            
            // Should be the cyan label (default fallback)
            if (result !== 'Cyan Matrix') {
                console.error('FAIL: getThemeLabel(' + vector + ') did not return cyan default, got: ' + result);
                process.exit(2);
            }
        }
        
        // Valid themes should still work
        if (PomodoroCore.getThemeLabel('cyan') !== 'Cyan Matrix') {
            console.error('FAIL: valid theme label cyan broken');
            process.exit(3);
        }
        if (PomodoroCore.getThemeLabel('pink') !== 'Neon Pink / Outrun') {
            console.error('FAIL: valid theme label pink broken');
            process.exit(4);
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

    def test_format_tab_label_rejects_proto_and_builtins(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const protoVectors = [
            '__proto__', 'constructor', 'prototype',
            'toString', 'valueOf', 'hasOwnProperty', 'isPrototypeOf'
        ];

        for (const vector of protoVectors) {
            const label = PomodoroCore.formatTabLabel(vector, 1500);
            if (label !== 'FOCUS (25M)') {
                console.error(`FAIL: formatTabLabel('${vector}', 1500) leaked prototype/builtin: "${label}"`);
                process.exit(1);
            }
        }

        // Standard modes still format correctly
        if (PomodoroCore.formatTabLabel('focus', 1500) !== 'FOCUS (25M)') process.exit(2);
        if (PomodoroCore.formatTabLabel('shortBreak', 300) !== 'SHORT (5M)') process.exit(3);
        if (PomodoroCore.formatTabLabel('longBreak', 900) !== 'LONG (15M)') process.exit(4);

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

    def test_format_tab_label_handles_null_prototype_and_non_string(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Object.create(null) must not crash with TypeError: Cannot convert object to primitive value
        try {
            const label = PomodoroCore.formatTabLabel(Object.create(null), 1500);
            if (label !== 'FOCUS (25M)') {
                console.error('FAIL: formatTabLabel(Object.create(null)) returned ' + label);
                process.exit(1);
            }
        } catch (e) {
            console.error('FAIL: formatTabLabel(Object.create(null)) threw ' + e.message);
            process.exit(2);
        }

        // Symbol and function inputs must fall back safely
        if (PomodoroCore.formatTabLabel(() => {}, 1500) !== 'FOCUS (25M)') process.exit(3);

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

    def test_resolve_keyboard_action_handles_null_prototype_and_proto_keys(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Null-prototype object as key must not crash with TypeError
        try {
            const action = PomodoroCore.resolveKeyboardAction({ key: Object.create(null) });
            if (action !== null) {
                console.error('FAIL: resolveKeyboardAction with null-prototype key should be null, got ' + action);
                process.exit(1);
            }
        } catch (e) {
            console.error('FAIL: resolveKeyboardAction threw on null-prototype key: ' + e.message);
            process.exit(2);
        }

        // Prototype names should return null, not throw or leak
        const protoKeys = ['toString', 'valueOf', '__proto__', 'constructor'];
        for (const k of protoKeys) {
            const action = PomodoroCore.resolveKeyboardAction({ key: k });
            if (action !== null) {
                console.error(`FAIL: resolveKeyboardAction with key '${k}' should return null, got ${action}`);
                process.exit(3);
            }
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