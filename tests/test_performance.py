import unittest
import subprocess
import json

class TestEscapeHtmlPerformance(unittest.TestCase):
    def test_escape_html_fast_path_and_equality(self):
        js_code = """
        const { PomodoroCore } = require('./test-runner.js');

        // Check if fast-path is implemented (function source does not use 5 chained .replace calls)
        const fnStr = PomodoroCore.escapeHtml.toString();
        const chainedCount = (fnStr.match(/\\.replace/g) || []).length;
        if (chainedCount > 1) {
            console.error('FAIL: escapeHtml still uses ' + chainedCount + ' chained .replace passes instead of optimized single pass');
            process.exit(2);
        }

        const cases = [
            ['Clean text without specials', 'Clean text without specials'],
            ['<script>alert("xss")</script>', '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;'],
            ["Tom & 'Jerry'", "Tom &amp; &#039;Jerry&#039;"],
            ['Multiple & < > " \\' special chars', 'Multiple &amp; &lt; &gt; &quot; &#039; special chars'],
            ['', ''],
            [null, ''],
            [undefined, ''],
            [12345, '']
        ];

        for (const [input, expected] of cases) {
            const actual = PomodoroCore.escapeHtml(input);
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
            text=True
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

if __name__ == "__main__":
    unittest.main()
