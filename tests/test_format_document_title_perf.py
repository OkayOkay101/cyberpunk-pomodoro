import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestFormatDocumentTitlePerformance(unittest.TestCase):
    def test_format_document_title_fast_path_and_equality(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Verify that formatDocumentTitle does not call .trim() repeatedly
        const fnStr = PomodoroCore.formatDocumentTitle.toString();
        const trimCalls = (fnStr.match(/\\.trim\\s*\\(/g) || []).length;
        if (trimCalls > 1) {
            console.error('FAIL: formatDocumentTitle calls .trim() ' + trimCalls + ' times instead of using fast-path or single trim');
            process.exit(2);
        }

        // Verify that fast-path edge character checking is implemented
        if (!/charCodeAt/.test(fnStr)) {
            console.error('FAIL: formatDocumentTitle missing fast-path character code check');
            process.exit(3);
        }

        function baselineFormatDocumentTitle(timeStr, isRunning) {
            const safeTime = (typeof timeStr === 'string' && timeStr.trim().length > 0) ? timeStr.trim() : '00:00';
            const statePrefix = isRunning ? '' : '[PAUSED] ';
            return `${statePrefix}(${safeTime}) CYBERPUNK FOCUS`;
        }

        const cases = [
            ['25:00', true],
            ['24:59', true],
            ['00:00', false],
            ['0:00', true],
            ['120:05', false],
            ['  10:00  ', true],
            ['   ', true],
            ['   ', false],
            ['', true],
            ['', false],
            [null, true],
            [null, false],
            [undefined, true],
            [undefined, false],
            [12345, true],
            [true, false],
            [false, true],
            ['\\u00A0', true],
            ['\\u00A025:00\\u00A0', false],
            ['\\t05:00\\n', true],
            ['Custom Mission', true],
            ['Custom Mission', false]
        ];

        for (const [timeStr, isRunning] of cases) {
            const actual = PomodoroCore.formatDocumentTitle(timeStr, isRunning);
            const expected = baselineFormatDocumentTitle(timeStr, isRunning);
            if (actual !== expected) {
                console.error('Mismatch: input=' + JSON.stringify(timeStr) + ' isRunning=' + isRunning +
                              ' expected=' + JSON.stringify(expected) + ' actual=' + JSON.stringify(actual));
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
