import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestReducedMotionAccessibility(unittest.TestCase):
    def _extract_reduced_motion_block(self, html: str) -> str:
        start_idx = html.find("@media (prefers-reduced-motion: reduce)")
        if start_idx == -1:
            return ""

        open_brace = html.find("{", start_idx)
        if open_brace == -1:
            return ""

        depth = 1
        pos = open_brace + 1
        while pos < len(html) and depth > 0:
            if html[pos] == "{":
                depth += 1
            elif html[pos] == "}":
                depth -= 1
            pos += 1

        return html[open_brace + 1:pos - 1]

    def test_reduced_motion_media_query_exists(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Must include WCAG-compliant prefers-reduced-motion media query
        self.assertIn(
            "@media (prefers-reduced-motion: reduce)",
            html,
            "index.html must include @media (prefers-reduced-motion: reduce) for users with motion sensitivity"
        )

        block_css = self._extract_reduced_motion_block(html)
        self.assertTrue(len(block_css) > 0, "Could not extract prefers-reduced-motion media query block")

        # Pulse animation on .status-dot must be disabled
        self.assertIn(".status-dot", block_css, "Reduced motion block must target .status-dot")
        self.assertTrue(
            re.search(r"animation:\s*none", block_css),
            ".status-dot must set animation: none to prevent infinite pulsing"
        )

    def test_reduced_motion_suppresses_transitions_and_animations(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        block_css = self._extract_reduced_motion_block(html)
        self.assertTrue(len(block_css) > 0, "prefers-reduced-motion media query block not found")

        # Transitions and animation durations must be neutralized
        has_transition_override = "transition-duration" in block_css or "transition: none" in block_css
        self.assertTrue(
            has_transition_override,
            "Reduced motion block must suppress transitions for interactive elements"
        )

        # Ensure scroll behavior or animation duration is also handled
        self.assertIn("animation-duration", block_css)


if __name__ == "__main__":
    unittest.main()
