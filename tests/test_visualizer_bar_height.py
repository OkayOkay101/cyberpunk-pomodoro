import json
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class TestVisualizerBarHeightLookup(unittest.TestCase):
    def test_visualizer_precomputes_bar_heights_for_byte_frequency_values(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
        visualizer_start = html.index("function startVisualizer()")
        visualizer_end = html.index("// Tick Sound Engine", visualizer_start)
        visualizer = html[visualizer_start:visualizer_end]
        self.assertIn("const barHeights = new Float64Array(256);", visualizer)
        self.assertIn("barHeights[value] = (value / 255) * canvas.height;", visualizer)
        self.assertIn("const barHeight = barHeights[dataArray[i]];", visualizer)
        self.assertNotIn("(dataArray[i] / 255) * canvas.height", visualizer)


if __name__ == "__main__":
    unittest.main()
