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

    def test_visualizer_bar_height_lookup_preserves_output_and_improves_frame_work(self):
        proc = subprocess.run(
            ["node", "bench/bench_visualizer_bar_height.js"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        results = json.loads(proc.stdout)
        self.assertTrue(results["outputEquality"])
        self.assertGreaterEqual(results["improvementPercent"], 20)


if __name__ == "__main__":
    unittest.main()
