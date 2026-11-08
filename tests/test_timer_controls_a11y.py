import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestTimerControlsAccessibility(unittest.TestCase):
    def test_timer_buttons_have_accessible_initial_labels(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        toggle_match = re.search(r'<button[^>]*id="toggleBtn"[^>]*>', html)
        self.assertIsNotNone(toggle_match, "Toggle button #toggleBtn not found")
        self.assertIn('aria-label="เริ่มจับเวลา"', toggle_match.group(0),
                      "Toggle button #toggleBtn missing initial aria-label='เริ่มจับเวลา'")

        reset_match = re.search(r'<button[^>]*id="resetBtn"[^>]*>', html)
        self.assertIsNotNone(reset_match, "Reset button #resetBtn not found")
        self.assertIn('aria-label="รีเซ็ตเวลา"', reset_match.group(0),
                      "Reset button #resetBtn missing aria-label='รีเซ็ตเวลา'")

    def test_javascript_updates_toggle_btn_aria_label_dynamically(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn("PomodoroCore.getTimerToggleAriaLabel", html,
                      "JavaScript does not use getTimerToggleAriaLabel to synchronize toggleBtn aria-label")

    def test_javascript_updates_reset_btn_aria_label_on_confirm(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn("PomodoroCore.getResetButtonAriaLabel", html,
                      "JavaScript does not use getResetButtonAriaLabel to update resetBtn confirmation aria-label")

    def test_core_timer_aria_label_helpers(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (typeof PomodoroCore.getTimerToggleAriaLabel !== 'function') {
            console.error('FAIL: getTimerToggleAriaLabel is not defined');
            process.exit(1);
        }
        if (PomodoroCore.getTimerToggleAriaLabel('START') !== 'เริ่มจับเวลา') {
            console.error('FAIL: START should return เริ่มจับเวลา');
            process.exit(2);
        }
        if (PomodoroCore.getTimerToggleAriaLabel('PAUSE') !== 'หยุดชั่วคราว') {
            console.error('FAIL: PAUSE should return หยุดชั่วคราว');
            process.exit(3);
        }
        if (PomodoroCore.getTimerToggleAriaLabel('RESUME') !== 'จับเวลาต่อ') {
            console.error('FAIL: RESUME should return จับเวลาต่อ');
            process.exit(4);
        }
        if (PomodoroCore.getTimerToggleAriaLabel(null) !== 'เริ่มจับเวลา') {
            console.error('FAIL: null should fallback to เริ่มจับเวลา');
            process.exit(5);
        }

        if (typeof PomodoroCore.getResetButtonAriaLabel !== 'function') {
            console.error('FAIL: getResetButtonAriaLabel is not defined');
            process.exit(6);
        }
        if (PomodoroCore.getResetButtonAriaLabel(true) !== 'ยืนยันการรีเซ็ตเวลา') {
            console.error('FAIL: true should return ยืนยันการรีเซ็ตเวลา');
            process.exit(7);
        }
        if (PomodoroCore.getResetButtonAriaLabel(false) !== 'รีเซ็ตเวลา') {
            console.error('FAIL: false should return รีเซ็ตเวลา');
            process.exit(8);
        }
        console.log('SUCCESS');
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
