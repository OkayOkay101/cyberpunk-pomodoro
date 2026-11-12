import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestVisualizerAccessibility(unittest.TestCase):
    def test_audio_visualizer_has_graphic_role_and_name(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
        match = re.search(r'<canvas[^>]*id="audioVisualizer"[^>]*>', html)

        self.assertIsNotNone(match, "Audio visualizer canvas not found")
        self.assertIn('role="img"', match.group(0))
        self.assertIn('aria-label="เส้นคลื่นเสียง"', match.group(0))


if __name__ == "__main__":
    unittest.main()
