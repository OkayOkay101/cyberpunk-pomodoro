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

    def test_delegated_listener_benchmark_preserves_behavior_and_is_faster(self):
        proc = subprocess.run(
            ["node", "bench/bench_task_checkbox_delegation.js"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        results = json.loads(proc.stdout)
        self.assertTrue(results["outputEquality"])
        self.assertEqual(results["delegatedListenerAttachments"], 1)
        self.assertGreaterEqual(results["improvementPercent"], 20)


if __name__ == "__main__":
    unittest.main()
