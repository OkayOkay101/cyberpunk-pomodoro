import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestSettingsInputAccessibility(unittest.TestCase):
    def test_settings_duration_inputs_have_accessible_labels(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        inputs = [
            ('cfgFocusMin', 'ระยะเวลาโฟกัส (นาที)'),
            ('cfgShortMin', 'ระยะเวลาพักสั้น (นาที)'),
            ('cfgLongMin', 'ระยะเวลาพักยาว (นาที)'),
        ]

        for input_id, expected_label in inputs:
            match = re.search(rf'<input[^>]*id="{input_id}"[^>]*>', html)
            self.assertIsNotNone(match, f"Settings input #{input_id} not found in index.html")
            self.assertIn(f'aria-label="{expected_label}"', match.group(0),
                          f"Settings input #{input_id} missing aria-label='{expected_label}'")


if __name__ == "__main__":
    unittest.main()
