import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestClearMissionAccessibility(unittest.TestCase):
    def test_clear_mission_button_has_type_button_and_initial_aria_label(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        match = re.search(r'<button[^>]*id="clearMissionBtn"[^>]*>', html)
        self.assertIsNotNone(match, "#clearMissionBtn button not found in index.html")

        elem_html = match.group(0)
        self.assertIn('type="button"', elem_html,
                      "#clearMissionBtn missing type='button' attribute")
        self.assertIn('aria-label="ล้างข้อความภารกิจ"', elem_html,
                      "#clearMissionBtn missing initial aria-label")

    def test_clear_mission_button_updates_aria_label_on_click(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # JavaScript click handler updates accessible label
        self.assertIn("clearMissionBtn.setAttribute('aria-label', 'ล้างข้อความภารกิจสำเร็จ')", html,
                      "clearMissionBtn click handler must update aria-label to confirm clearing")
        self.assertIn("clearMissionBtn.setAttribute('aria-label', origLabel)", html,
                      "clearMissionBtn click handler must restore original aria-label after timeout")


if __name__ == "__main__":
    unittest.main()
