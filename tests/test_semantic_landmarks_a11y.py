import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestSemanticLandmarksAccessibility(unittest.TestCase):
    def test_main_landmark_and_sections_exist(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Main landmark container
        main_match = re.search(r'<main[^>]*class="station-container"[^>]*>', html)
        self.assertIsNotNone(main_match, "<main class='station-container'> landmark not found in index.html")
        self.assertIn("</main>", html, "Closing </main> tag not found in index.html")

        # Semantic sections with aria-labelledby for Ambient Deck and Mission Checklist
        ambient_section = re.search(r'<section[^>]*class="deck-section"[^>]*aria-labelledby="ambientHeading"[^>]*>', html)
        self.assertIsNotNone(ambient_section, "Ambient deck <section aria-labelledby='ambientHeading'> not found")

        mission_section = re.search(r'<section[^>]*class="deck-section"[^>]*aria-labelledby="missionHeading"[^>]*>', html)
        self.assertIsNotNone(mission_section, "Mission deck <section aria-labelledby='missionHeading'> not found")

    def test_heading_hierarchy_h1_and_h2(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Top-level H1 heading
        h1_match = re.search(r'<h1[^>]*class="glitch-title"[^>]*>(.*?)</h1>', html, re.DOTALL)
        self.assertIsNotNone(h1_match, "<h1 class='glitch-title'> heading not found")
        self.assertIn("CYBERPUNK FOCUS", h1_match.group(1), "H1 does not contain 'CYBERPUNK FOCUS'")

        # H2 heading for Ambient Sound Deck
        h2_ambient = re.search(r'<h2[^>]*id="ambientHeading"[^>]*>(.*?)</h2>', html, re.DOTALL)
        self.assertIsNotNone(h2_ambient, "<h2 id='ambientHeading'> not found")
        self.assertIn("NEURAL AMBIENT GENERATOR", h2_ambient.group(1))

        # H2 heading for Mission Objectives & Tasks
        h2_mission = re.search(r'<h2[^>]*id="missionHeading"[^>]*>(.*?)</h2>', html, re.DOTALL)
        self.assertIsNotNone(h2_mission, "<h2 id='missionHeading'> not found")
        self.assertIn("MISSION OBJECTIVES & TASKS", h2_mission.group(1))

    def test_css_resets_heading_margins_to_preserve_hud_layout(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn(".glitch-title {", html)
        self.assertIn("margin: 0;", html, ".glitch-title should reset default H1 margins")
        self.assertIn(".deck-title h2 {", html, ".deck-title h2 rule not found")
        self.assertIn("margin: 0;", html, ".deck-title h2 should reset default H2 margins")


if __name__ == "__main__":
    unittest.main()
