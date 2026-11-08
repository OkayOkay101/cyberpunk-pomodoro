import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestSkipToContentAccessibility(unittest.TestCase):
    def test_skip_link_markup_and_main_target(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Skip link must exist before main content
        skip_link_pattern = r'<a[^>]*class="[^"]*skip-link[^"]*"[^>]*>(.*?)</a>'
        match = re.search(skip_link_pattern, html, re.DOTALL)
        self.assertIsNotNone(match, "Skip link <a class='skip-link'> not found in index.html")
        self.assertIn('href="#mainContent"', match.group(0), "Skip link must have href='#mainContent'")

        # Skip link text must be descriptive in Thai
        self.assertIn("ข้ามไปยังเนื้อหาหลัก", match.group(1),
                      "Skip link must contain accessible Thai text 'ข้ามไปยังเนื้อหาหลัก'")

        # Skip link must appear before <main
        body_idx = html.find("<body>")
        skip_idx = html.find('class="skip-link"')
        main_idx = html.find("<main")
        self.assertTrue(body_idx < skip_idx < main_idx,
                        "Skip link must appear at the beginning of <body> before <main>")

        # <main> must have id="mainContent" and tabindex="-1" to receive focus
        main_match = re.search(r'<main[^>]*id="mainContent"[^>]*>', html)
        self.assertIsNotNone(main_match, "<main> landmark must have id='mainContent'")
        self.assertIn('tabindex="-1"', main_match.group(0),
                      "<main> landmark must have tabindex='-1' for programmatic keyboard focus")

    def test_skip_link_css_positioning_and_focus_state(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # CSS rule for .skip-link (visually hidden offscreen until focused)
        self.assertIn(".skip-link {", html, ".skip-link CSS rule not found")
        self.assertIn("position: absolute;", html, ".skip-link must use absolute positioning")

        # CSS rule for .skip-link:focus (visible when receiving keyboard focus)
        self.assertIn(".skip-link:focus", html, ".skip-link:focus CSS rule not found")


if __name__ == "__main__":
    unittest.main()
