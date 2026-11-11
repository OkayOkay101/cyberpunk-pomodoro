import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestTimerStatePersistence(unittest.TestCase):
    def test_page_restores_running_timer_and_persists_lifecycle_changes(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn("PomodoroCore.parseTimerState(localStorage.getItem('cp_timer_state'), Date.now())", html)
        self.assertIn("if (isRunning) startTimerInterval();", html)
        self.assertIn("targetEndTime: isRunning ? targetEndTime : null", html)
        self.assertIn("persistTimerState();", html)
        self.assertIn("localStorage.removeItem('cp_timer_state');", html)


if __name__ == "__main__":
    unittest.main()
