import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestMuteButtonAccessibility(unittest.TestCase):
    def test_mute_button_has_aria_pressed_attribute(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        pattern = r'<button[^>]*id="muteBtn"[^>]*>'
        match = re.search(pattern, html)
        self.assertIsNotNone(match, "Mute button #muteBtn not found")

        button_html = match.group(0)
        self.assertIn('aria-pressed="false"', button_html,
                      "Mute button #muteBtn missing initial aria-pressed='false'")
        self.assertIn('aria-label="เปิดหรือปิดเสียง"', button_html,
                      "Mute button #muteBtn missing aria-label")

    def test_javascript_updates_mute_aria_pressed(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Check that updateVolumeDisplay updates aria-pressed for muteBtn
        self.assertIn("muteBtn.setAttribute('aria-pressed', String(isMuted))", html,
                      "JavaScript does not update aria-pressed for muteBtn in updateVolumeDisplay")

    def test_format_volume_percent_displays_muted_state(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (PomodoroCore.formatVolumePercent(0.5, true) !== 'MUTED') {
            console.error('FAIL: formatVolumePercent must return MUTED when isMuted is true');
            process.exit(1);
        }
        if (PomodoroCore.formatVolumePercent(0.5, false) !== '50%') {
            console.error('FAIL: formatVolumePercent must return 50% when isMuted is false');
            process.exit(2);
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
