import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestModeTransitionToast(unittest.TestCase):
    def test_mode_toast_element_exists_in_html(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Check for mode toast element with correct attributes
        pattern = r'<div[^>]*id="modeToast"[^>]*>'
        match = re.search(pattern, html)
        self.assertIsNotNone(match, "Mode toast element #modeToast not found")

        toast_html = match.group(0)
        self.assertIn('role="status"', toast_html, "Mode toast missing role='status'")
        self.assertIn('aria-live="polite"', toast_html, "Mode toast missing aria-live='polite'")
        self.assertIn('aria-atomic="true"', toast_html, "Mode toast missing aria-atomic='true'")

    def test_mode_toast_css_styles_exist(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Check for toast CSS styles
        self.assertIn('.mode-toast {', html, "Mode toast CSS class not found")
        self.assertIn('.mode-toast.show {', html, "Mode toast show state CSS not found")
        self.assertIn('opacity: 0', html, "Mode toast initial opacity not found")
        self.assertIn('opacity: 1', html, "Mode toast show opacity not found")

    def test_mode_toast_wraps_within_narrow_viewports(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
        toast_style = html.split('.mode-toast {', 1)[1].split('}', 1)[0]
        self.assertIn('max-width: calc(100vw - 32px);', toast_style)
        self.assertIn('white-space: normal;', toast_style)

    def test_show_mode_toast_function_exists(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Check for showModeToast function
        self.assertIn('function showModeToast(', html, "showModeToast function not found")
        self.assertIn('modeToast', html, "showModeToast references modeToast element")
        self.assertIn('classList.add(\'show\')', html, "showModeToast adds show class")
        self.assertIn('classList.remove(\'show\')', html, "showModeToast removes show class")
        self.assertIn('setTimeout', html, "showModeToast uses setTimeout for auto-hide")

    def test_setmode_accepts_toast_message_parameter(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Check setMode signature includes toastMessage parameter
        pattern = r'function setMode\(mode, duration, toastMessage\)'
        match = re.search(pattern, html)
        self.assertIsNotNone(match, "setMode function missing toastMessage parameter")

        # Check that setMode calls showModeToast when toastMessage provided
        self.assertIn('if (toastMessage) {', html, "setMode missing toastMessage conditional")
        self.assertIn('showModeToast(toastMessage)', html, "setMode does not call showModeToast")

    def test_handle_timer_complete_passes_toast_messages(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Check handleTimerComplete passes toast messages for auto transitions
        self.assertIn("'SHORT BREAK STARTED'", html, "handleTimerComplete missing SHORT BREAK toast")
        self.assertIn("'LONG BREAK STARTED'", html, "handleTimerComplete missing LONG BREAK toast")
        self.assertIn("'FOCUS SESSION STARTED'", html, "handleTimerComplete missing FOCUS toast")

    def test_manual_mode_changes_pass_toast_messages(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Check mode tab clicks pass toast messages
        self.assertIn("'FOCUS MODE'", html, "Manual focus mode change missing toast")
        self.assertIn("'SHORT BREAK'", html, "Manual short break change missing toast")
        self.assertIn("'LONG BREAK'", html, "Manual long break change missing toast")

        # Check skip button passes toast messages
        pattern_skip = r"setMode\(next, configDurations\[next\], toastMsg\)"
        self.assertTrue(re.search(pattern_skip, html), "Skip button does not pass toast message")

    def test_reset_does_not_show_toast(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Find handleResetAction and verify it calls setMode without toast message
        reset_section = html[html.find("function handleResetAction"):html.find("function handleResetAction") + 800]
        setmode_call = re.search(r"setMode\(currentMode, currentDuration\)", reset_section)
        self.assertIsNotNone(setmode_call, "handleResetAction should call setMode without toast message")


if __name__ == "__main__":
    unittest.main()
