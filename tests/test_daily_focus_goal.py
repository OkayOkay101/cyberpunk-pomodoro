import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestDailyFocusGoal(unittest.TestCase):
    def run_node(self, js_code):
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")

    def test_goal_validation_and_default(self):
        self.run_node(r"""
        const assert = require('assert');
        const { PomodoroCore } = require('./core.js');
        assert.deepStrictEqual(PomodoroCore.resolveDailyFocusGoal(), {
          minutes: 120, storage: { cp_daily_focus_goal: '120' }
        });
        assert.deepStrictEqual(PomodoroCore.resolveDailyFocusGoal('90'), {
          minutes: 90, storage: { cp_daily_focus_goal: '90' }
        });
        assert.strictEqual(PomodoroCore.resolveDailyFocusGoal(1).minutes, 1);
        assert.strictEqual(PomodoroCore.resolveDailyFocusGoal(1440).minutes, 1440);
        for (const invalid of [0, 1441, 1.5, '1.5', '', 'nope', null]) {
          assert.strictEqual(PomodoroCore.resolveDailyFocusGoal(invalid).minutes, 120);
        }
        """)

    def test_progress_and_completion_boundaries_and_badge_updates(self):
        self.run_node(r"""
        const assert = require('assert');
        const { PomodoroCore } = require('./core.js');
        assert.deepStrictEqual(PomodoroCore.getDailyFocusGoalProgress(0, 120), {
          percent: 0, completed: false
        });
        assert.deepStrictEqual(PomodoroCore.getDailyFocusGoalProgress(60, 120), {
          percent: 50, completed: false
        });
        assert.deepStrictEqual(PomodoroCore.getDailyFocusGoalProgress(119, 120), {
          percent: 99, completed: false
        });
        assert.deepStrictEqual(PomodoroCore.getDailyFocusGoalProgress(120, 120), {
          percent: 100, completed: true
        });
        assert.deepStrictEqual(PomodoroCore.getDailyFocusGoalProgress(135, 120), {
          percent: 100, completed: true
        });
        assert.strictEqual(PomodoroCore.formatFocusTimeBadge(60, 120), '🎯 60 / 120 MINS TODAY · 50%');
        assert.strictEqual(PomodoroCore.formatFocusTimeBadge(61, 120), '🎯 61 / 120 MINS TODAY · 50%');
        assert.strictEqual(PomodoroCore.formatFocusTimeBadge(120, 120), '🎯 120 / 120 MINS TODAY · GOAL COMPLETE');
        """)

    def test_settings_and_hud_are_wired_to_refresh_goal_progress(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="cfgDailyFocusGoal"', html)
        self.assertIn('id="focusTimeBadge"', html)
        self.assertIn("PomodoroCore.resolveDailyFocusGoal", html)
        self.assertIn("PomodoroCore.formatFocusTimeBadge(totalFocusMinsToday, dailyFocusGoal)", html)
        self.assertIn("localStorage.setItem('cp_daily_focus_goal'", html)


if __name__ == "__main__":
    unittest.main()
