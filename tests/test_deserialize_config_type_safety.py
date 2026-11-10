import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestDeserializeConfigTypeSafety(unittest.TestCase):
    """Type-safety tests for PomodoroCore.deserializeConfig."""

    def _run_node(self, js_code: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )

    def test_deserialize_config_array_payload_with_object_defaults_returns_defaults(self):
        """An array JSON payload is incompatible with object defaults; must fall back to defaults."""
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (typeof PomodoroCore.deserializeConfig !== 'function') {
            console.error('FAIL: deserializeConfig is not a function');
            process.exit(1);
        }

        // Object defaults + array payload is a type mismatch -> must return defaults, not a bare array.
        const result = PomodoroCore.deserializeConfig('[1,2,3]', { focusTime: 1500, breakTime: 300 });
        if (Array.isArray(result)) {
            console.error('FAIL: returned array instead of object defaults:', result);
            process.exit(2);
        }
        if (typeof result !== 'object' || result === null) {
            console.error('FAIL: result is not an object');
            process.exit(3);
        }
        if (result.focusTime !== 1500 || result.breakTime !== 300) {
            console.error('FAIL: defaults not preserved:', result);
            process.exit(4);
        }

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_deserialize_config_array_defaults_preserves_array_type(self):
        """Array defaults with an array payload must still preserve the array type (no regression)."""
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const arrResult = PomodoroCore.deserializeConfig('[{"id":1,"text":"Task"}]', []);
        if (!Array.isArray(arrResult) || arrResult.length !== 1) {
            console.error('FAIL: array defaults should preserve array type:', arrResult);
            process.exit(1);
        }
        if (arrResult[0].text !== 'Task') {
            console.error('FAIL: array payload not preserved:', arrResult);
            process.exit(2);
        }

        // Object defaults with object payload must still merge correctly.
        const objResult = PomodoroCore.deserializeConfig('{"theme":"pink"}', { theme: 'cyan', focusTime: 1500 });
        if (objResult.theme !== 'pink' || objResult.focusTime !== 1500) {
            console.error('FAIL: object merge broken:', objResult);
            process.exit(3);
        }

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
