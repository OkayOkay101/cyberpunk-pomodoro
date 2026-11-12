import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class TestHotkeyHintLocalization(unittest.TestCase):
    def test_hotkey_actions_use_thai_labels(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
        match = re.search(r'<div class="hotkey-hint">(.*?)</div>', html, re.DOTALL)
        self.assertIsNotNone(match, "hotkey guidance should render on the page")
        for label in ("เริ่ม/หยุด", "รีเซ็ต", "ข้าม", "ปิดเสียง", "เต็มจอ"):
            self.assertIn(label, match.group(1))


if __name__ == "__main__":
    unittest.main()
