import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestAmbientSoundAccessibility(unittest.TestCase):
    def test_sound_grid_has_accessible_group_role_and_label(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        pattern = r'<div[^>]*class="sound-grid"[^>]*>'
        match = re.search(pattern, html)
        self.assertIsNotNone(match, ".sound-grid container not found in index.html")

        grid_html = match.group(0)
        self.assertIn('role="group"', grid_html, ".sound-grid missing role='group'")
        self.assertIn('aria-label="เสียงสังเคราะห์บรรยากาศ"', grid_html,
                      ".sound-grid missing aria-label='เสียงสังเคราะห์บรรยากาศ'")

    def test_sound_buttons_have_aligned_aria_labels_matching_visible_text(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Map data-sound key to (expected_visible_text, expected_aria_label)
        expected_buttons = [
            ('rain', 'Cyber Rain', 'เปิด/ปิดเสียง Cyber Rain'),
            ('engine', 'Deep Space Hum', 'เปิด/ปิดเสียง Deep Space Hum'),
            ('binaural', '40Hz Focus Wave', 'เปิด/ปิดเสียง 40Hz Focus Wave'),
            ('fan', 'Server Fan', 'เปิด/ปิดเสียง Server Fan'),
            ('storm', 'Cyber Storm', 'เปิด/ปิดเสียง Cyber Storm'),
        ]

        for sound_key, visible_text, expected_label in expected_buttons:
            pattern = rf'<button[^>]*data-sound="{sound_key}"[^>]*>'
            match = re.search(pattern, html)
            self.assertIsNotNone(match, f"Sound button for {sound_key} not found")

            btn_html = match.group(0)
            self.assertIn(f'aria-label="{expected_label}"', btn_html,
                          f"Sound button {sound_key} missing aria-label='{expected_label}'")
            self.assertIn('aria-pressed="false"', btn_html,
                          f"Sound button {sound_key} missing initial aria-pressed='false'")

            # Verify visible label also exists directly inside the button
            btn_block_pattern = rf'<button[^>]*data-sound="{sound_key}"[^>]*>[\s\S]*?</button>'
            block_match = re.search(btn_block_pattern, html)
            self.assertIsNotNone(block_match, f"Full button block for {sound_key} not found")
            self.assertIn(f'<b>{visible_text}</b>', block_match.group(0),
                          f"Button {sound_key} visible text does not match <b>{visible_text}</b>")

    def test_javascript_updates_sound_aria_pressed_on_toggle(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Verify toggleSound updates aria-pressed to false when stopping
        self.assertIn("btn.setAttribute('aria-pressed', 'false')", html,
                      "toggleSound does not reset aria-pressed to 'false' on stop")
        # Verify toggleSound updates aria-pressed to true when starting
        self.assertIn("btn.setAttribute('aria-pressed', 'true')", html,
                      "toggleSound does not set aria-pressed to 'true' on start")


if __name__ == "__main__":
    unittest.main()
