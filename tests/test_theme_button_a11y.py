import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestThemeButtonAccessibility(unittest.TestCase):
    def test_theme_buttons_have_data_label_and_aria_attributes(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Check all four theme buttons have data-label attribute
        themes = [
            ('cyan', 'Cyan Matrix'),
            ('pink', 'Neon Pink'),
            ('yellow', 'Night City Yellow'),
            ('green', 'Emerald Hacker'),
        ]

        for theme_key, expected_label in themes:
            # Find the button for this theme
            pattern = rf'<button[^>]*data-theme="{theme_key}"[^>]*>'
            match = re.search(pattern, html)
            self.assertIsNotNone(match, f"Theme button for {theme_key} not found")

            button_html = match.group(0)

            # Check data-label attribute
            self.assertIn(f'data-label="{expected_label}"', button_html,
                          f"Theme button {theme_key} missing data-label='{expected_label}'")

            # Check aria-label attribute
            self.assertIn('aria-label="', button_html,
                          f"Theme button {theme_key} missing aria-label")

            # Check aria-pressed attribute
            self.assertIn('aria-pressed="', button_html,
                          f"Theme button {theme_key} missing aria-pressed")

        # Check CSS has hover/focus label display rule (using ::before for tooltip)
        self.assertIn('.theme-btn:hover::before', html)
        self.assertIn('.theme-btn:focus-visible::before', html)
        self.assertIn('content: attr(data-label)', html)


if __name__ == "__main__":
    unittest.main()