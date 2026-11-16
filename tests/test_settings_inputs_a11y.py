import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestSettingsInputAccessibility(unittest.TestCase):
    def test_settings_duration_inputs_have_accessible_labels(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        inputs = ['cfgFocusMin', 'cfgShortMin', 'cfgLongMin', 'cfgDailyFocusGoal']

        for input_id in inputs:
            match = re.search(rf'<input[^>]*id="{input_id}"[^>]*>', html)
            self.assertIsNotNone(match, f"Settings input #{input_id} not found in index.html")
            self.assertRegex(html, rf'<label for="{input_id}">[^<]+</label>',
                             f"Settings input #{input_id} needs a clickable visible label")
            self.assertNotIn('aria-label="', match.group(0),
                             f"Settings input #{input_id} should use its visible label as its accessible name")


if __name__ == "__main__":
    unittest.main()
