import json
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class TestVisualizerPerformance(unittest.TestCase):
    def test_production_visualizer_sets_fill_style_before_bar_loop(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
        start = html.index("function startVisualizer()")
        end = html.index("// Tick Sound Engine", start)
        render_frame = html[start:end]
        loop_start = render_frame.index("for (let i = 0; i < bufferLength; i++)")
        loop_end = render_frame.index("\n        }", loop_start)
        self.assertLess(render_frame.index("ctx.fillStyle = primaryColor;"), loop_start)
        self.assertNotIn("ctx.fillStyle =", render_frame[loop_start:loop_end])


if __name__ == "__main__":
    unittest.main()
