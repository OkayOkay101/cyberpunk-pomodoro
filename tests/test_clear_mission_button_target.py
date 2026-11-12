import re
import unittest
from pathlib import Path


class TestClearMissionButtonTarget(unittest.TestCase):
    def test_clear_button_has_mobile_friendly_hit_area(self):
        html = (Path(__file__).resolve().parent.parent / "index.html").read_text(encoding="utf-8")
        styles = re.search(r"\.clear-mission-btn\s*\{([^}]*)\}", html)
        self.assertIsNotNone(styles)
        self.assertRegex(styles.group(1), r"min-width:\s*44px")
        self.assertRegex(styles.group(1), r"min-height:\s*44px")


if __name__ == "__main__":
    unittest.main()
