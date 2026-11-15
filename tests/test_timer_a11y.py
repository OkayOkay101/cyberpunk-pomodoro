import re
import unittest
from pathlib import Path


class TestTimerAccessibility(unittest.TestCase):
    def test_timer_has_a_clear_accessible_name(self):
        html = (Path(__file__).resolve().parent.parent / "index.html").read_text(encoding="utf-8")
        timer = re.search(r'<[^>]*id="timeDisplay"[^>]*>', html)
        self.assertIsNotNone(timer)
        self.assertIn('role="timer"', timer.group(0))
        self.assertRegex(timer.group(0), r'aria-label="[^"]+"')


if __name__ == "__main__":
    unittest.main()
