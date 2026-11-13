import json
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class TestTaskCheckboxDelegation(unittest.TestCase):
    def test_production_task_rendering_delegates_checkbox_changes(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
        start = html.index("function renderTasks()")
        end = html.index("    renderTasks();", start)
        task_rendering = html[start:end]
        task_list_render = task_rendering[:task_rendering.index("taskChecklist.addEventListener('change'")]

        self.assertNotIn("querySelectorAll('input[type=\"checkbox\"]')", task_list_render)
        self.assertIn("taskChecklist.addEventListener('change'", task_rendering)
        self.assertIn("e.target.matches('input[type=\"checkbox\"]')", task_rendering)
        self.assertIn("PomodoroCore.toggleTaskItem(tasks, id, e.target.checked)", task_rendering)


if __name__ == "__main__":
    unittest.main()
