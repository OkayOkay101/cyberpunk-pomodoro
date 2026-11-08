import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestSettingsModalAccessibility(unittest.TestCase):
    def test_settings_modal_dialog_semantics_and_attributes(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        modal_match = re.search(r'<div[^>]*id="settingsModal"[^>]*>', html)
        self.assertIsNotNone(modal_match, "#settingsModal overlay not found in index.html")

        modal_html = modal_match.group(0)
        self.assertIn('role="dialog"', modal_html, "#settingsModal missing role='dialog'")
        self.assertIn('aria-modal="true"', modal_html, "#settingsModal missing aria-modal='true'")
        self.assertIn('aria-labelledby="modalTitle"', modal_html, "#settingsModal missing aria-labelledby='modalTitle'")
        self.assertIn('aria-hidden="true"', modal_html, "#settingsModal missing initial aria-hidden='true'")

        title_match = re.search(r'<h2[^>]*id="modalTitle"[^>]*class="modal-title"[^>]*>(.*?)</h2>', html, re.DOTALL)
        if not title_match:
            title_match = re.search(r'<h2[^>]*class="modal-title"[^>]*id="modalTitle"[^>]*>(.*?)</h2>', html, re.DOTALL)
        self.assertIsNotNone(title_match, "Modal title heading <h2 id='modalTitle' class='modal-title'> not found")
        self.assertIn("SYSTEM CONFIGURATION", title_match.group(1))

    def test_settings_inputs_have_associated_labels(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        inputs = [
            ("cfgFocusMin", "Focus Duration"),
            ("cfgShortMin", "Short Break"),
            ("cfgLongMin", "Long Break"),
        ]

        for input_id, label_text in inputs:
            pattern = rf'<label[^>]*for="{input_id}"[^>]*>(.*?)</label>'
            match = re.search(pattern, html, re.DOTALL)
            self.assertIsNotNone(match, f"Missing <label for='{input_id}'> in settings modal")
            self.assertIn(label_text, match.group(1), f"Label for {input_id} should mention '{label_text}'")

    def test_settings_modal_javascript_wiring_and_focus_management(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Verify open/close updates aria-hidden
        self.assertIn("settingsModal.setAttribute('aria-hidden', 'false')", html,
                      "Opening settings modal must set aria-hidden to 'false'")
        self.assertIn("settingsModal.setAttribute('aria-hidden', 'true')", html,
                      "Closing settings modal must set aria-hidden to 'true'")

        # Verify focus management
        self.assertIn("cfgFocusMin.focus()", html,
                      "Opening settings modal must move focus to first input cfgFocusMin")
        self.assertIn("settingsBtn.focus()", html,
                      "Closing settings modal must restore focus to settingsBtn")

        # Verify backdrop click dismiss
        self.assertIn("e.target === settingsModal", html,
                      "Clicking modal backdrop overlay must dismiss settings modal")

    def test_css_resets_modal_heading_margins(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn(".modal-title {", html, ".modal-title CSS rule not found")
        # Check that top margin is reset (e.g. margin: 0 or margin-top: 0)
        title_css_match = re.search(r'\.modal-title\s*\{([^}]+)\}', html)
        self.assertIsNotNone(title_css_match, "Could not extract .modal-title CSS block")
        css_block = title_css_match.group(1)
        self.assertTrue(
            "margin: 0" in css_block or "margin-top: 0" in css_block,
            ".modal-title should reset default h2 top margin to preserve HUD layout"
        )


if __name__ == "__main__":
    unittest.main()
