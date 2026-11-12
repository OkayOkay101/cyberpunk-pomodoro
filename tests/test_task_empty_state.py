import unittest
import subprocess
import re
from pathlib import Path


class TestTaskChecklistEmptyState(unittest.TestCase):
    def test_empty_checklist_renders_guidance_message(self):
        root = Path(__file__).resolve().parent.parent
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const empty = PomodoroCore.renderTaskList([]);
        if (!empty.includes('class="task-empty"')) {
            console.error('FAIL: empty task list has no empty-state element');
            process.exit(1);
        }
        if (!empty.includes('role="status"')) {
            console.error('FAIL: empty state is not announced to assistive tech');
            process.exit(2);
        }
        if (!empty.includes('ยังไม่มีภารกิจ')) {
            console.error('FAIL: empty state has no user guidance text');
            process.exit(3);
        }

        const notArray = PomodoroCore.renderTaskList(null);
        if (notArray !== empty) {
            console.error('FAIL: non-array input should render the same empty state');
            process.exit(4);
        }

        const items = PomodoroCore.renderTaskList([
            { id: 7, text: 'A & B <script>', done: false },
            { id: 8, text: 'Finished task', done: true }
        ]);
        if (!items.includes('task-item') || items.includes('task-empty')) {
            console.error('FAIL: non-empty list should render task items only');
            process.exit(5);
        }
        if (!items.includes('A &amp; B &lt;script&gt;')) {
            console.error('FAIL: task text is not HTML-escaped');
            process.exit(6);
        }
        if (!items.includes('task-item done')) {
            console.error('FAIL: completed task is not marked as done');
            process.exit(7);
        }
        console.log('SUCCESS');
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(root)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_unrenderable_entries_fall_back_to_empty_state(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const emptyState = PomodoroCore.renderTaskList([]);
        if (!emptyState.includes('class="task-empty"') || !emptyState.includes('role="status"')) {
            console.error('FAIL: baseline empty state is missing its accessible markup');
            process.exit(1);
        }

        const corrupted = [null, undefined, { id: 9 }, { id: 10, text: 42 }, 'not-a-task'];
        const rendered = PomodoroCore.renderTaskList(corrupted);
        if (rendered !== emptyState) {
            console.error('FAIL: list with no renderable tasks should fall back to the empty state, got ' + JSON.stringify(rendered));
            process.exit(2);
        }

        const mixed = [null, { id: 11 }, { id: 12, text: 'Valid <x>', done: false }];
        const mixedHtml = PomodoroCore.renderTaskList(mixed);
        if (!mixedHtml.includes('task-item') || mixedHtml.includes('task-empty')) {
            console.error('FAIL: mixed list should render only its valid tasks');
            process.exit(3);
        }
        if (!mixedHtml.includes('Valid &lt;x&gt;')) {
            console.error('FAIL: valid task text is not HTML-escaped');
            process.exit(4);
        }
        console.log('SUCCESS');
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).resolve().parent.parent)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_production_page_uses_shared_core_module(self):
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent
        html = (root / "index.html").read_text(encoding="utf-8")
        self.assertIn('<script src="core.js"></script>', html)
        self.assertIn("PomodoroCore.renderTaskList(tasks)", html)
        self.assertNotIn('<script src="test-runner.js"></script>', html)

    def test_long_task_text_wraps_inside_checklist(self):
        root = Path(__file__).resolve().parent.parent
        html = (root / "index.html").read_text(encoding="utf-8")
        self.assertIn(".task-item > span {", html)
        self.assertIn("min-width: 0;", html)
        self.assertIn("overflow-wrap: anywhere;", html)

    def test_mission_input_explains_character_limit(self):
        root = Path(__file__).resolve().parent.parent
        html = (root / "index.html").read_text(encoding="utf-8")
        match = re.search(r'<input[^>]*id="missionInput"[^>]*>', html)
        self.assertIsNotNone(match)
        self.assertIn('maxlength="80"', match.group(0))
        self.assertIn("ไม่เกิน 80 ตัวอักษร", match.group(0))


if __name__ == "__main__":
    unittest.main()
