import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestSessionCycleAccessibility(unittest.TestCase):
    def test_session_label_has_status_role_and_aria_live(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        match = re.search(r'<div[^>]*id="sessionLabel"[^>]*>', html)
        self.assertIsNotNone(match, "#sessionLabel element not found in index.html")

        elem_html = match.group(0)
        self.assertIn('role="status"', elem_html,
                      "#sessionLabel missing role='status'")
        self.assertIn('aria-live="polite"', elem_html,
                      "#sessionLabel missing aria-live='polite'")
        self.assertIn('aria-atomic="true"', elem_html,
                      "#sessionLabel missing aria-atomic='true'")

    def test_reset_cycle_button_updates_aria_label_on_click(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Initial markup check
        match = re.search(r'<button[^>]*id="resetCycleBtn"[^>]*>', html)
        self.assertIsNotNone(match, "#resetCycleBtn button not found in index.html")

        elem_html = match.group(0)
        self.assertIn('aria-label="รีเซ็ตรอบกลับเป็น 01"', elem_html,
                      "#resetCycleBtn missing initial aria-label")

        # JavaScript click handler updates accessible label
        self.assertIn("resetCycleBtn.setAttribute('aria-label', 'รีเซ็ตรอบเป็น 01 สำเร็จ')", html,
                      "resetCycleBtn click handler must update aria-label to confirm reset")
        self.assertIn("resetCycleBtn.setAttribute('aria-label', origLabel)", html,
                      "resetCycleBtn click handler must restore original aria-label after timeout")


if __name__ == "__main__":
    unittest.main()
