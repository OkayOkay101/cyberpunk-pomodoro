import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestDynamicContentAriaLive(unittest.TestCase):
    def test_timer_updates_do_not_interrupt_screen_reader_users(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        timer_match = re.search(r'<div[^>]*id="timeDisplay"[^>]*>', html)
        self.assertIsNotNone(timer_match, "#timeDisplay not found")
        self.assertIn('role="timer"', timer_match.group(0))
        self.assertIn('aria-live="off"', timer_match.group(0),
                      "Per-second timer updates should not be announced continuously")

    def test_stats_badges_have_aria_live(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        streak_match = re.search(r'<span[^>]*id="streakBadge"[^>]*>', html)
        self.assertIsNotNone(streak_match, "#streakBadge not found")
        self.assertIn('aria-live="polite"', streak_match.group(0),
                      "#streakBadge missing aria-live='polite'")
        self.assertIn('aria-atomic="true"', streak_match.group(0),
                      "#streakBadge missing aria-atomic='true'")

        focus_match = re.search(r'<span[^>]*id="focusTimeBadge"[^>]*>', html)
        self.assertIsNotNone(focus_match, "#focusTimeBadge not found")
        self.assertIn('aria-live="polite"', focus_match.group(0),
                      "#focusTimeBadge missing aria-live='polite'")
        self.assertIn('aria-atomic="true"', focus_match.group(0),
                      "#focusTimeBadge missing aria-atomic='true'")

    def test_volume_percent_has_aria_live(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        vol_match = re.search(r'<span[^>]*id="volumePercent"[^>]*>', html)
        self.assertIsNotNone(vol_match, "#volumePercent not found")
        self.assertIn('aria-live="polite"', vol_match.group(0),
                      "#volumePercent missing aria-live='polite'")
        self.assertIn('aria-atomic="true"', vol_match.group(0),
                      "#volumePercent missing aria-atomic='true'")


if __name__ == "__main__":
    unittest.main()
