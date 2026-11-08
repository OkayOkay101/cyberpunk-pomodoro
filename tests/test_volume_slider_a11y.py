import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestVolumeSliderAccessibility(unittest.TestCase):
    def test_volume_slider_has_initial_aria_valuetext(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        pattern = r'<input[^>]*id="volumeSlider"[^>]*>'
        match = re.search(pattern, html)
        self.assertIsNotNone(match, "Volume slider #volumeSlider not found")

        slider_html = match.group(0)
        self.assertIn('aria-valuetext="50%"', slider_html,
                      "Volume slider #volumeSlider missing initial aria-valuetext='50%'")
        self.assertIn('aria-label="ระดับเสียงบรรยากาศ"', slider_html,
                      "Volume slider #volumeSlider missing aria-label")

    def test_javascript_updates_volume_slider_aria_valuetext(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Check that updateVolumeDisplay updates aria-valuetext for volumeSlider
        self.assertIn(
            "volumeSlider.setAttribute('aria-valuetext'",
            html,
            "JavaScript does not update aria-valuetext for volumeSlider in updateVolumeDisplay"
        )

    def test_volume_slider_aria_valuetext_values(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (PomodoroCore.formatVolumePercent(0.5, false) !== '50%') {
            console.error('FAIL: formatVolumePercent(0.5, false) should return 50%');
            process.exit(1);
        }
        if (PomodoroCore.formatVolumePercent(0.85, false) !== '85%') {
            console.error('FAIL: formatVolumePercent(0.85, false) should return 85%');
            process.exit(2);
        }
        if (PomodoroCore.formatVolumePercent(0.5, true) !== 'MUTED') {
            console.error('FAIL: formatVolumePercent when isMuted=true should return MUTED');
            process.exit(3);
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
