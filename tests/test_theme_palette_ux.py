import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestThemePaletteUX(unittest.TestCase):
    def setUp(self):
        self.html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

    def test_theme_button_has_relative_positioning_and_safe_tooltip(self):
        """Theme swatches must have position: relative to properly anchor tooltips."""
        # Find .theme-btn CSS block
        match = re.search(r'\.theme-btn\s*\{([^}]+)\}', self.html)
        self.assertIsNotNone(match, ".theme-btn CSS rule not found in index.html")
        theme_btn_css = match.group(1)
        self.assertIn(
            "position: relative",
            theme_btn_css,
            ".theme-btn must specify 'position: relative;' to anchor ::before tooltips"
        )

        # Check tooltip pointer-events: none to avoid hover flickering
        match_tooltip = re.search(r'\.theme-btn:hover::before[^{]*\{([^}]+)\}', self.html)
        self.assertIsNotNone(match_tooltip, ".theme-btn:hover::before rule not found")
        tooltip_css = match_tooltip.group(1)
        self.assertIn(
            "pointer-events: none",
            tooltip_css,
            ".theme-btn tooltip must specify 'pointer-events: none;' to prevent cursor flicker"
        )

    def test_apply_theme_synchronizes_data_theme_attribute(self):
        """applyTheme must set data-theme on documentElement for CSS theming and assistive tools."""
        self.assertIn(
            "document.documentElement.setAttribute('data-theme', theme)",
            self.html,
            "applyTheme must sync active theme name to documentElement data-theme attribute"
        )

    def test_dynamic_theme_ambient_glow_palettes(self):
        """Each HUD neon theme must have distinct ambient glow colors matching its personality."""
        # Root variable definition
        self.assertIn("--theme-glow:", self.html, ":root should declare --theme-glow variable")

        # Check all 4 cyberpunk personality themes have dynamic glow rules
        themes = ['cyan', 'pink', 'yellow', 'green']
        for theme in themes:
            pattern = rf'\[data-theme=["\']?{theme}["\']?\]\s*\{{[^}}]*--theme-glow:'
            self.assertTrue(
                re.search(pattern, self.html),
                f"CSS rule for [data-theme='{theme}'] must define --theme-glow"
            )

        # Body background and modal box should use var(--theme-glow) instead of hardcoded cyan
        self.assertIn(
            "var(--theme-glow)",
            self.html,
            "Ambient background or modal box should consume var(--theme-glow)"
        )


if __name__ == "__main__":
    unittest.main()
