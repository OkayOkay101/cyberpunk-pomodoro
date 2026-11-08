import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestSystemStatusAccessibility(unittest.TestCase):
    def test_status_dot_has_aria_hidden(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        match = re.search(r'<span[^>]*class="status-dot"[^>]*>', html)
        self.assertIsNotNone(match, ".status-dot element not found in index.html")

        elem_html = match.group(0)
        self.assertIn('aria-hidden="true"', elem_html,
                      ".status-dot missing aria-hidden='true' for decorative visual element")

    def test_system_status_has_status_role_and_atomic_aria_live(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        status_match = re.search(r'<span[^>]*id="systemStatus"[^>]*>', html)
        self.assertIsNotNone(status_match, "#systemStatus element not found in index.html")

        status_html = status_match.group(0)
        self.assertIn('role="status"', status_html,
                      "#systemStatus missing role='status'")
        self.assertIn('aria-live="polite"', status_html,
                      "#systemStatus missing aria-live='polite'")
        self.assertIn('aria-atomic="true"', status_html,
                      "#systemStatus missing aria-atomic='true'")


if __name__ == "__main__":
    unittest.main()
