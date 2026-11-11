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

    def test_settings_modal_focus_management_on_open(self):
        """Test that modal stores previous focus and moves focus to first focusable element on open."""
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Should store the trigger button reference before opening
        self.assertIn('lastFocusedElement', html,
                      "Missing lastFocusedElement variable to store previous focus")
        self.assertIn('settingsBtn', html,
                      "settingsBtn reference not found")

        # Should focus first focusable element in modal (cfgFocusMin input)
        self.assertIn('cfgFocusMin.focus()', html,
                      "Missing focus() call on first focusable element (cfgFocusMin) when modal opens")

    def test_settings_modal_focus_trap_tab_navigation(self):
        """Test that Tab key traps focus inside the modal."""
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Should have keydown handler for focus trap
        self.assertIn('keydown', html.lower(),
                      "Missing keydown event listener for focus trap")
        self.assertIn('Tab', html,
                      "Missing Tab key handling for focus trap")

        # Should handle Shift+Tab for reverse navigation
        self.assertIn('shiftKey', html,
                      "Missing shiftKey check for reverse Tab navigation")

    def test_settings_modal_focus_restore_on_close(self):
        """Test that focus returns to settings button when modal closes."""
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Should restore focus to settingsBtn when closing
        self.assertIn('lastFocusedElement.focus()', html,
                      "Missing focus restoration to lastFocusedElement on close")
        self.assertIn('settingsBtn', html,
                      "settingsBtn reference not found for focus restoration")

    def test_settings_modal_save_button_saves_settings_before_close(self):
        """Test that saveSettingsBtn saves duration values and theme before closing modal."""
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Save button handler should read values from cfgFocusMin, cfgShortMin, cfgLongMin
        self.assertIn('cfgFocusMin.value', html,
                      "Save handler missing reading cfgFocusMin value")
        self.assertIn('cfgShortMin.value', html,
                      "Save handler missing reading cfgShortMin value")
        self.assertIn('cfgLongMin.value', html,
                      "Save handler missing reading cfgLongMin value")

        # Should update configDurations via resolveDurations
        self.assertIn('resolveDurations', html,
                      "Save handler missing resolveDurations call")

        # Should persist to localStorage
        self.assertIn('localStorage.setItem', html,
                      "Save handler missing localStorage persistence")

        # Should refresh tab labels after saving
        self.assertIn('refreshTabLabels', html,
                      "Save handler missing refreshTabLabels call")

        # Should call closeSettingsModal after saving
        self.assertIn('closeSettingsModal()', html,
                      "Save handler missing closeSettingsModal call")


if __name__ == "__main__":
    unittest.main()
