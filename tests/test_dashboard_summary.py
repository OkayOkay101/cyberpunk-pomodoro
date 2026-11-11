import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestDashboardSummary(unittest.TestCase):
    def test_summary_reports_success_and_failure_results_accurately(self):
        js_code = r"""
        const assert = require('assert');
        const fs = require('fs');
        const vm = require('vm');
        const html = fs.readFileSync('test.html', 'utf8');
        const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
        assert(scripts.length > 0, 'dashboard inline script should exist');
        const dashboardScript = scripts[scripts.length - 1][1];

        function getSummary(result) {
          const elements = { summary: {}, testList: {} };
          let onReady;
          const context = {
            document: {
              addEventListener(event, callback) {
                assert.strictEqual(event, 'DOMContentLoaded');
                onReady = callback;
              },
              getElementById(id) { return elements[id]; }
            },
            runUnitTests() { return result; }
          };
          vm.runInNewContext(dashboardScript, context);
          onReady();
          return elements.summary.textContent;
        }

        const failedSummary = getSummary({
          passed: 2, failed: 1, total: 3,
          results: [{ name: 'pass', passed: true }, { name: 'fail', passed: false }]
        });
        assert.match(failedSummary, /FAIL/i, `expected failure status, got: ${failedSummary}`);
        assert.match(failedSummary, /1/, `expected failure count, got: ${failedSummary}`);
        assert.doesNotMatch(failedSummary, /100% SUCCESS/);

        const passedSummary = getSummary({
          passed: 3, failed: 0, total: 3,
          results: [{ name: 'pass', passed: true }]
        });
        assert.match(passedSummary, /100% SUCCESS/);
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")


if __name__ == "__main__":
    unittest.main()
