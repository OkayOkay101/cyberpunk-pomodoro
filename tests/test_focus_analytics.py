import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestFocusAnalytics(unittest.TestCase):
    def run_node(self, js_code):
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")

    def test_daily_totals_accumulate_and_weekly_summary_uses_local_calendar_days(self):
        self.run_node(r"""
        const assert = require('assert');
        const { PomodoroCore } = require('./core.js');
        assert.strictEqual(typeof PomodoroCore.updateDailyFocusTotals, 'function');
        assert.strictEqual(typeof PomodoroCore.summarizeWeeklyFocus, 'function');

        let totals = PomodoroCore.updateDailyFocusTotals({}, '2026-11-16', 25);
        totals = PomodoroCore.updateDailyFocusTotals(totals, '2026-11-16', 40);
        totals = PomodoroCore.updateDailyFocusTotals(totals, '2026-11-22', 15);
        totals = PomodoroCore.updateDailyFocusTotals(totals, '2026-11-09', 50);
        assert.deepStrictEqual(totals, {
          '2026-11-09': 50, '2026-11-16': 65, '2026-11-22': 15
        });
        const week = PomodoroCore.summarizeWeeklyFocus(totals, '2026-11-17');
        assert.strictEqual(week.totalMinutes, 80);
        assert.deepStrictEqual(week.days.map(day => [day.date, day.minutes]), [
          ['2026-11-16', 65], ['2026-11-17', 0], ['2026-11-18', 0],
          ['2026-11-19', 0], ['2026-11-20', 0], ['2026-11-21', 0],
          ['2026-11-22', 15]
        ]);
        assert.strictEqual(PomodoroCore.summarizeWeeklyFocus(totals, '2026-11-15').totalMinutes, 50);
        """)

    def test_malformed_daily_totals_are_discarded_and_empty_week_is_zeroed(self):
        self.run_node(r"""
        const assert = require('assert');
        const { PomodoroCore } = require('./core.js');
        const malformed = {
          '2026-11-16': 30, '2026-02-30': 20, 'not-a-date': 10,
          '2026-11-17': -1, '2026-11-18': Number.MAX_SAFE_INTEGER + 1
        };
        assert.deepStrictEqual(PomodoroCore.validateDailyFocusTotals(malformed), {
          '2026-11-16': 30
        });
        const week = PomodoroCore.summarizeWeeklyFocus('{broken', '2026-11-17');
        assert.strictEqual(week.totalMinutes, 0);
        assert.deepStrictEqual(week.days.map(day => day.minutes), [0, 0, 0, 0, 0, 0, 0]);
        """)

    def test_weekly_chart_provides_visible_and_accessible_summary(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="weeklyFocusChart"', html)
        self.assertIn('aria-label="Weekly focus analytics"', html)
        self.assertIn('id="weeklyFocusSummary"', html)
        self.assertIn("PomodoroCore.summarizeWeeklyFocus", html)
        self.assertIn("สัปดาห์นี้โฟกัสรวม ${summary.totalMinutes} นาที", html)
        self.assertIn("weeklyFocusChart.setAttribute('aria-label', `Weekly focus analytics:", html)
        self.assertIn("${summary.days.map(day => `${day.date}, ${day.minutes} minutes`).join('; ')}", html)
        self.assertIn("Total ${summary.totalMinutes} minutes.", html)
        self.assertIn("cp_focus_mins_by_date", html)
        self.assertIn("PomodoroCore.updateDailyFocusTotals(focusMinsByDate, completionDate, transition.addedFocusMins)", html)
        self.assertIn("localStorage.setItem('cp_focus_mins_by_date', JSON.stringify(focusMinsByDate))", html)


if __name__ == "__main__":
    unittest.main()
