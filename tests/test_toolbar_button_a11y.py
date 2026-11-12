import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestToolbarButtonAccessibility(unittest.TestCase):
    def test_toolbar_buttons_have_aria_attributes(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Check all toolbar buttons have aria-label
        buttons = [
            ('tickToggleBtn', 'เปิด/ปิดเสียงเดินของเวลา (Tick)'),
            ('autoStartBtn', 'สลับโหมดเริ่มรอบถัดไปอัตโนมัติ'),
            ('settingsBtn', 'การตั้งค่า'),
            ('fullscreenBtn', 'โหมดเต็มจอ'),
        ]

        for btn_id, expected_label in buttons:
            pattern = rf'<button[^>]*id="{btn_id}"[^>]*>'
            match = re.search(pattern, html)
            self.assertIsNotNone(match, f"Toolbar button {btn_id} not found")

            button_html = match.group(0)

            # Check aria-label attribute
            self.assertIn(f'aria-label="{expected_label}"', button_html,
                          f"Toolbar button {btn_id} missing aria-label='{expected_label}'")

        # Check TESTS link has aria-label
        tests_pattern = r'<a[^>]*href="test\.html"[^>]*>'
        tests_match = re.search(tests_pattern, html)
        self.assertIsNotNone(tests_match, "TESTS link not found")
        self.assertIn('aria-label="เปิดดูผล Unit Tests"', tests_match.group(0),
                      "TESTS link missing aria-label")

    def test_toggle_buttons_have_aria_pressed(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Toggle buttons should have aria-pressed attribute
        toggle_buttons = ['tickToggleBtn', 'autoStartBtn']

        for btn_id in toggle_buttons:
            pattern = rf'<button[^>]*id="{btn_id}"[^>]*>'
            match = re.search(pattern, html)
            self.assertIsNotNone(match, f"Toggle button {btn_id} not found")

            button_html = match.group(0)
            self.assertIn('aria-pressed="', button_html,
                          f"Toggle button {btn_id} missing aria-pressed attribute")

    def test_fullscreen_button_has_visible_text_label(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
        match = re.search(r'<button[^>]*id="fullscreenBtn"[^>]*>(.*?)</button>', html)

        self.assertIsNotNone(match, "Fullscreen button not found")
        self.assertIn("FULL", match.group(1), "Fullscreen button needs a visible label")
        self.assertIn("EXIT FULL", html, "Fullscreen button needs an exit label while fullscreen is active")
        self.assertIn("fullscreenchange", html, "Fullscreen button label must follow fullscreen state")
        self.assertIn("fullscreenBtn.title = label", html,
                      "Fullscreen button tooltip must follow fullscreen state")

    def test_fullscreen_button_exposes_pressed_state(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
        match = re.search(r'<button[^>]*id="fullscreenBtn"[^>]*>', html)

        self.assertIsNotNone(match, "Fullscreen button not found")
        self.assertIn("fullscreenBtn.setAttribute('aria-pressed', String(isFullscreen))", html)
        self.assertIn("updateFullscreenButton();", html)

    def test_javascript_updates_aria_pressed_on_toggle(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Check that JavaScript updates aria-pressed for tickToggleBtn
        self.assertIn("tickToggleBtn.setAttribute('aria-pressed', String(isTickEnabled))", html,
                      "JavaScript does not update aria-pressed for tickToggleBtn on init")
        # Check click handler updates aria-pressed
        tick_handler_section = html[html.find("tickToggleBtn.addEventListener('click'"):html.find("tickToggleBtn.addEventListener('click'") + 500]
        self.assertIn("tickToggleBtn.setAttribute('aria-pressed', String(isTickEnabled))", tick_handler_section,
                      "JavaScript does not update aria-pressed for tickToggleBtn on click")

        # Check that JavaScript updates aria-pressed for autoStartBtn
        self.assertIn("autoStartBtn.setAttribute('aria-pressed', String(isAutoStart))", html,
                      "JavaScript does not update aria-pressed for autoStartBtn on init")
        auto_handler_section = html[html.find("autoStartBtn.addEventListener('click'"):html.find("autoStartBtn.addEventListener('click'") + 500]
        self.assertIn("autoStartBtn.setAttribute('aria-pressed', String(isAutoStart))", auto_handler_section,
                      "JavaScript does not update aria-pressed for autoStartBtn on click")


if __name__ == "__main__":
    unittest.main()
