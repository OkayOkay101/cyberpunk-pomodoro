import unittest
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestFormatTimePerformance(unittest.TestCase):
    def test_format_time_fast_path_and_equality(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Verify that formatTime does not use slow String.prototype.padStart
        const fnStr = PomodoroCore.formatTime.toString();
        if (/\\.padStart\\s*\\(/.test(fnStr)) {
            console.error('FAIL: formatTime still uses padStart instead of pre-computed lookup');
            process.exit(2);
        }

        const cases = [
            [0, '00:00'],
            [5, '00:05'],
            [9, '00:09'],
            [10, '00:10'],
            [59, '00:59'],
            [60, '01:00'],
            [65, '01:05'],
            [599, '09:59'],
            [600, '10:00'],
            [1499, '24:59'],
            [1500, '25:00'],
            [3599, '59:59'],
            [3600, '60:00'],
            [5999, '99:59'],
            [6000, '100:00'],
            [7205, '120:05'],
            [-1, '-1:-1'],
            [-30, '-1:-30'],
            [-100, '-2:-40'],
            [NaN, '00:00'],
            [Infinity, '00:00'],
            [-Infinity, '00:00'],
            ['abc', '00:00'],
            [null, '00:00'],
            [undefined, '00:00']
        ];

        for (const [input, expected] of cases) {
            const actual = PomodoroCore.formatTime(input);
            if (actual !== expected) {
                console.error('Mismatch: input=' + input + ' expected=' + expected + ' actual=' + actual);
                process.exit(1);
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
