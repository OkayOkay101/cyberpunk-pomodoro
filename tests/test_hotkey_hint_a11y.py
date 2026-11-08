import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestHotkeyHintAccessibility(unittest.TestCase):
    def test_hotkey_hint_has_accessible_role_and_label(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        pattern = r'<div[^>]*class="hotkey-hint"[^>]*>'
        match = re.search(pattern, html)
        self.assertIsNotNone(match, ".hotkey-hint container not found in index.html")

        hint_html = match.group(0)
        self.assertIn('role="note"', hint_html,
                      ".hotkey-hint missing role='note'")
        self.assertIn('aria-label="คีย์ลัดสำหรับควบคุม"', hint_html,
                      ".hotkey-hint missing aria-label='คีย์ลัดสำหรับควบคุม'")

    def test_hotkey_tags_use_semantic_kbd_elements(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        expected_keys = ['Space', 'R', 'S', 'M', 'F']
        for key in expected_keys:
            pattern = rf'<kbd[^>]*class="hotkey-tag"[^>]*>{key}</kbd>'
            match = re.search(pattern, html)
            self.assertIsNotNone(
                match,
                f"Shortcut key '{key}' should use semantic <kbd class=\"hotkey-tag\">"
            )

        # Ensure no legacy span tags remain for hotkey-tag
        legacy_pattern = r'<span[^>]*class="hotkey-tag"[^>]*>'
        legacy_match = re.search(legacy_pattern, html)
        self.assertIsNone(
            legacy_match,
            "Legacy <span class=\"hotkey-tag\"> should be replaced with <kbd>"
        )

    def test_hotkey_tag_css_preserves_typography(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn('.hotkey-tag {', html, ".hotkey-tag CSS rule not found")
        self.assertIn('font-family: inherit;', html,
                      ".hotkey-tag should declare font-family: inherit to preserve typography")


if __name__ == "__main__":
    unittest.main()
