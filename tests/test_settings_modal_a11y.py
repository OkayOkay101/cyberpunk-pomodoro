import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestSettingsModalAccessibility(unittest.TestCase):
    def test_settings_modal_dialog_semantics_and_title(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Modal box must have role="dialog", aria-modal="true", and aria-labelledby
        match = re.search(r'<div[^>]*class="modal-box"[^>]*>', html)
        self.assertIsNotNone(match, ".modal-box container not found in index.html")

        box_html = match.group(0)
        self.assertIn('role="dialog"', box_html, ".modal-box missing role='dialog'")
        self.assertIn('aria-modal="true"', box_html, ".modal-box missing aria-modal='true'")
        self.assertIn('aria-labelledby="settingsModalTitle"', box_html,
                      ".modal-box missing aria-labelledby='settingsModalTitle'")

        # Modal title must be a semantic h2 heading matching aria-labelledby
        title_match = re.search(r'<h2[^>]*id="settingsModalTitle"[^>]*>(.*?)</h2>', html, re.DOTALL)
        self.assertIsNotNone(title_match, "<h2 id='settingsModalTitle'> not found in index.html")
        self.assertIn("SYSTEM CONFIGURATION", title_match.group(1),
                      "Modal heading does not contain 'SYSTEM CONFIGURATION'")

    def test_settings_modal_action_buttons_have_accessible_labels(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Cancel button
        cancel_match = re.search(r'<button[^>]*id="closeSettingsBtn"[^>]*>', html)
        self.assertIsNotNone(cancel_match, "#closeSettingsBtn not found in index.html")
        self.assertIn('aria-label="ยกเลิกการตั้งค่า"', cancel_match.group(0),
                      "#closeSettingsBtn missing aria-label='ยกเลิกการตั้งค่า'")

        # Save button
        save_match = re.search(r'<button[^>]*id="saveSettingsBtn"[^>]*>', html)
        self.assertIsNotNone(save_match, "#saveSettingsBtn not found in index.html")
        self.assertIn('aria-label="บันทึกการตั้งค่า"', save_match.group(0),
                      "#saveSettingsBtn missing aria-label='บันทึกการตั้งค่า'")


if __name__ == "__main__":
    unittest.main()
