import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestModeTabsAccessibility(unittest.TestCase):
    def test_mode_tabs_have_initial_roving_tabindex(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Focus tab is initially active and must have tabindex="0"
        focus_match = re.search(r'<button[^>]*id="tabFocus"[^>]*>', html)
        self.assertIsNotNone(focus_match, "#tabFocus button not found")
        self.assertIn('tabindex="0"', focus_match.group(0),
                      "#tabFocus must have initial tabindex='0'")

        # Inactive tabs must have tabindex="-1" to prevent extra Tab stops
        for tab_id in ['tabShort', 'tabLong']:
            match = re.search(rf'<button[^>]*id="{tab_id}"[^>]*>', html)
            self.assertIsNotNone(match, f"#{tab_id} button not found")
            self.assertIn('tabindex="-1"', match.group(0),
                          f"#{tab_id} must have initial tabindex='-1'")

    def test_mode_tab_accessible_names_include_current_duration(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
        refresh = html[html.index("function refreshTabLabels()"):
                       html.index("function updateTimerStatusUI()")]

        self.assertIn("tab.setAttribute('aria-label', `${label} ${configDurations[mode]} นาที`)", refresh)
        for label in ['โฟกัส', 'พักสั้น', 'พักยาว']:
            self.assertIn(f"'{label}'", refresh)

    def test_setmode_updates_tabindex_for_roving_focus(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Check setMode updates tabindex alongside aria-selected
        self.assertIn("t.setAttribute('tabindex', isActive ? '0' : '-1')", html,
                      "setMode must update tabindex for roving focus")

    def test_mode_tabs_have_keyboard_arrow_navigation(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Check keydown listener on mode-tabs container
        self.assertIn("PomodoroCore.getNextTabIndex", html,
                      "mode-tabs container must use PomodoroCore.getNextTabIndex for keyboard navigation")

    def test_get_next_tab_index_logic(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (typeof PomodoroCore.getNextTabIndex !== 'function') {
            console.error('FAIL: getNextTabIndex function is missing');
            process.exit(1);
        }

        // Forward cycling (ArrowRight / ArrowDown)
        if (PomodoroCore.getNextTabIndex(0, 3, 'ArrowRight') !== 1) process.exit(2);
        if (PomodoroCore.getNextTabIndex(1, 3, 'ArrowDown') !== 2) process.exit(3);
        if (PomodoroCore.getNextTabIndex(2, 3, 'ArrowRight') !== 0) process.exit(4); // wrapping

        // Backward cycling (ArrowLeft / ArrowUp)
        if (PomodoroCore.getNextTabIndex(0, 3, 'ArrowLeft') !== 2) process.exit(5); // wrapping
        if (PomodoroCore.getNextTabIndex(2, 3, 'ArrowUp') !== 1) process.exit(6);
        if (PomodoroCore.getNextTabIndex(1, 3, 'ArrowLeft') !== 0) process.exit(7);

        // Boundary navigation (Home / End)
        if (PomodoroCore.getNextTabIndex(1, 3, 'Home') !== 0) process.exit(8);
        if (PomodoroCore.getNextTabIndex(1, 3, 'End') !== 2) process.exit(9);

        // Unrelated keys return -1
        if (PomodoroCore.getNextTabIndex(0, 3, 'Space') !== -1) process.exit(10);
        if (PomodoroCore.getNextTabIndex(0, 3, 'Enter') !== -1) process.exit(11);
        if (PomodoroCore.getNextTabIndex(0, 3, 'Tab') !== -1) process.exit(12);

        // Edge cases and invalid inputs
        if (PomodoroCore.getNextTabIndex(-1, 3, 'ArrowRight') !== -1) process.exit(13);
        if (PomodoroCore.getNextTabIndex(3, 3, 'ArrowRight') !== -1) process.exit(14);
        if (PomodoroCore.getNextTabIndex(0, 0, 'ArrowRight') !== -1) process.exit(15);
        if (PomodoroCore.getNextTabIndex(null, 3, 'ArrowRight') !== -1) process.exit(16);

        console.log('SUCCESS');
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
