import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestTaskCheckboxAccessibility(unittest.TestCase):
    def test_rendered_checkbox_name_explains_task_action_and_preserves_state(self):
        script = """const assert = require('node:assert/strict');
const { PomodoroCore } = require('./core.js');
const html = PomodoroCore.renderTaskList([
  { id: 1, text: 'Review & ship', done: false }, { id: 2, text: 'Deploy', done: true }
]);
assert.match(html, /aria-label="ทำเครื่องหมายภารกิจว่าเสร็จ: Review &amp; ship"/);
assert.match(html, /<input type="checkbox" checked aria-label="ทำเครื่องหมายภารกิจว่าเสร็จ: Deploy"/);"""
        proc = subprocess.run(["node", "-e", script], cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)


if __name__ == "__main__":
    unittest.main()
