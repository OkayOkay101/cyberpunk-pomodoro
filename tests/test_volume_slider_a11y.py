import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestVolumeSliderAccessibility(unittest.TestCase):
    def test_volume_slider_has_aria_valuetext(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        pattern = r'<input[^>]*id="volumeSlider"[^>]*>'
        match = re.search(pattern, html)
        self.assertIsNotNone(match, "Volume slider #volumeSlider not found")

        slider_html = match.group(0)
        self.assertIn('aria-label="ระดับเสียงบรรยากาศ"', slider_html,
                      "Volume slider missing aria-label")
        self.assertIn('aria-valuetext="', slider_html,
                      "Volume slider missing initial aria-valuetext")

    def test_javascript_updates_aria_valuetext(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Check that updateVolumeDisplay sets aria-valuetext on volumeSlider
        self.assertIn("volumeSlider.setAttribute('aria-valuetext', displayText)", html,
                      "updateVolumeDisplay does not set aria-valuetext on volumeSlider")

    def test_format_volume_percent_for_valuetext(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Test normal volume levels
        if (PomodoroCore.formatVolumePercent(0.5, false) !== '50%') {
            console.error('FAIL: 0.5 should be 50%');
            process.exit(1);
        }
        if (PomodoroCore.formatVolumePercent(0.0, false) !== '0%') {
            console.error('FAIL: 0.0 should be 0%');
            process.exit(2);
        }
        if (PomodoroCore.formatVolumePercent(1.0, false) !== '100%') {
            console.error('FAIL: 1.0 should be 100%');
            process.exit(3);
        }
        if (PomodoroCore.formatVolumePercent(0.75, false) !== '75%') {
            console.error('FAIL: 0.75 should be 75%');
            process.exit(4);
        }

        // Test muted state
        if (PomodoroCore.formatVolumePercent(0.5, true) !== 'MUTED') {
            console.error('FAIL: muted should return MUTED');
            process.exit(5);
        }
        if (PomodoroCore.formatVolumePercent(0.0, true) !== 'MUTED') {
            console.error('FAIL: muted with 0 volume should return MUTED');
            process.exit(6);
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