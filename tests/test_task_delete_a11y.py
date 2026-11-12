import unittest
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class TestTaskDeleteAccessibility(unittest.TestCase):
    def test_each_rendered_task_has_accessibly_named_remove_button(self):
        proc = subprocess.run(
            ["node", "-e", """
            const { PomodoroCore } = require('./core.js');
            const html = PomodoroCore.renderTaskList([{ id: 4, text: 'Review & ship', done: false }]);
            if (!html.includes('<button type=\"button\" class=\"task-remove\"')) process.exit(1);
            if (!html.includes('aria-label=\"ลบภารกิจ: Review &amp; ship\"')) process.exit(2);
            console.log('SUCCESS');
            """],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_remove_button_uses_delegated_handler_and_persists_removal(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
        start = html.index("function renderTasks()")
        end = html.index("    let savedMission", start)
        task_rendering = html[start:end]
        self.assertIn("taskChecklist.addEventListener('click'", task_rendering)
        self.assertIn("e.target.closest('.task-remove')", task_rendering)
        self.assertIn("PomodoroCore.removeTaskItem(tasks, task.id)", task_rendering)
        self.assertIn("localStorage.setItem('cp_tasks', JSON.stringify(tasks))", task_rendering)
        self.assertIn("renderTasks();", task_rendering)


if __name__ == "__main__":
    unittest.main()
