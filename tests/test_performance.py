import unittest
import os
import re

class TestVisualizerPerformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        index_path = os.path.join(base_dir, 'index.html')
        with open(index_path, 'r', encoding='utf-8') as f:
            cls.index_content = f.read()

        runner_path = os.path.join(base_dir, 'test-runner.js')
        with open(runner_path, 'r', encoding='utf-8') as f:
            cls.runner_content = f.read()

    def test_visualizer_render_frame_caches_theme_storage(self):
        """renderFrame must not call localStorage.getItem('cp_theme') inside the animation frame loop."""
        match = re.search(r'function renderFrame\(\)\s*\{(.*?)\n\s*\}\s*renderFrame\(\);', self.index_content, re.DOTALL)
        self.assertIsNotNone(match, "renderFrame function body not found in index.html")
        body = match.group(1)
        self.assertNotIn("localStorage.getItem('cp_theme')", body,
                         "renderFrame performs synchronous localStorage.getItem in hot animation loop")

    def test_visualizer_hoists_fill_style_out_of_bin_loop(self):
        """renderFrame must hoist ctx.fillStyle assignment outside the bufferLength for-loop."""
        match = re.search(r'function renderFrame\(\)\s*\{(.*?)\n\s*\}\s*renderFrame\(\);', self.index_content, re.DOTALL)
        self.assertIsNotNone(match, "renderFrame function body not found in index.html")
        body = match.group(1)
        loop_match = re.search(r'for\s*\([^)]*bufferLength[^)]*\)\s*\{(.*?)\}', body, re.DOTALL)
        self.assertIsNotNone(loop_match, "bufferLength loop not found in renderFrame")
        loop_body = loop_match.group(1)
        self.assertNotIn("ctx.fillStyle", loop_body,
                         "ctx.fillStyle must be hoisted outside the bufferLength loop to avoid redundant canvas mutations")

    def test_theme_variables_contract_preserved(self):
        """PomodoroCore.getThemeVariables must support cyan, pink, yellow, green themes."""
        for theme in ['cyan', 'pink', 'yellow', 'green']:
            self.assertTrue(f"{theme}:" in self.runner_content or f"'{theme}'" in self.runner_content,
                            f"Theme {theme} should be defined in test-runner.js")

if __name__ == '__main__':
    unittest.main()
