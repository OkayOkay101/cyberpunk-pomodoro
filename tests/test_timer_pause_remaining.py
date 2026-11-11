import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestTimerPauseRemaining(unittest.TestCase):
    def test_pause_recalculates_remaining_time_before_clearing_interval(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
        match = re.search(r"if \(isRunning\) \{(?P<pause>.*?)\n        \} else \{", html, re.DOTALL)

        self.assertIsNotNone(match, "toggleTimer pause branch not found")
        pause_branch = match.group("pause")
        recalculate = "timeLeft = PomodoroCore.calculateRemainingSeconds(targetEndTime, Date.now());"

        self.assertIn(recalculate, pause_branch)
        self.assertLess(
            pause_branch.index(recalculate),
            pause_branch.index("clearInterval(timerId);"),
            "remaining time must be captured before stopping the timer interval",
        )


if __name__ == "__main__":
    unittest.main()
