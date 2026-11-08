import unittest
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestGetLocalDateStringPerformance(unittest.TestCase):
    def test_get_local_date_string_fast_path_and_equality(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Verify that getLocalDateString does not use slow String.prototype.padStart
        const fnStr = PomodoroCore.getLocalDateString.toString();
        if (/\\.padStart\\s*\\(/.test(fnStr)) {
            console.error('FAIL: getLocalDateString still uses padStart instead of pre-computed PAD_TWO lookup');
            process.exit(2);
        }

        function baselineGetLocalDateString(date = new Date()) {
            const d = new Date(date);
            if (isNaN(d.getTime())) {
                const now = new Date();
                const year = now.getFullYear();
                const month = String(now.getMonth() + 1).padStart(2, '0');
                const day = String(now.getDate()).padStart(2, '0');
                return `${year}-${month}-${day}`;
            }
            const year = d.getFullYear();
            const month = String(d.getMonth() + 1).padStart(2, '0');
            const day = String(d.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        }

        const cases = [
            undefined,
            new Date('2026-11-08T12:00:00'),
            new Date('2026-01-05T01:02:03'),
            new Date('2024-02-29T23:59:59'),
            new Date('1999-12-31T00:00:00'),
            new Date('invalid'),
            null,
            0,
            1700000000000,
            '2026-11-08T15:30:00',
            'invalid date input'
        ];

        for (const input of cases) {
            const actual = PomodoroCore.getLocalDateString(input);
            const expected = baselineGetLocalDateString(input);
            if (actual !== expected) {
                console.error('Mismatch: input=' + input + ' expected=' + expected + ' actual=' + actual);
                process.exit(1);
            }
        }

        // Also test no-arguments call
        const actualNoArgs = PomodoroCore.getLocalDateString();
        const expectedNoArgs = baselineGetLocalDateString();
        if (actualNoArgs !== expectedNoArgs) {
            console.error('Mismatch on no-args: expected=' + expectedNoArgs + ' actual=' + actualNoArgs);
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
