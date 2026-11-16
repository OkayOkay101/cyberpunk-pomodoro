import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestWeeklyFocusReport(unittest.TestCase):
    def run_node(self, js_code):
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")

    def test_summary_covers_local_monday_to_sunday_and_counts_focus_only(self):
        self.run_node(r"""
        const assert = require('assert');
        process.env.TZ = 'America/Los_Angeles';
        const { PomodoroCore } = require('./core.js');
        assert.strictEqual(typeof PomodoroCore.getWeeklyFocusSummary, 'function');
        const history = [
          { mode: 'focus', completedAt: '2026-11-16T06:30:00.000Z', focusDuration: 1500 },
          { mode: 'shortBreak', completedAt: '2026-11-15T12:00:00', focusDuration: 9999 },
          { mode: 'focus', completedAt: '2026-11-09T12:00:00', focusDuration: 3600 },
          { mode: 'focus', completedAt: '2026-11-08T23:59:00', focusDuration: 6000 },
          { mode: 'longBreak', completedAt: '2026-11-11T12:00:00' }
        ];
        const summary = PomodoroCore.getWeeklyFocusSummary(history, new Date(2026, 10, 15, 12));
        assert.strictEqual(summary.startDate, '2026-11-09');
        assert.strictEqual(summary.endDate, '2026-11-15');
        assert.deepStrictEqual(summary.days.map(day => day.date), [
          '2026-11-09', '2026-11-10', '2026-11-11', '2026-11-12',
          '2026-11-13', '2026-11-14', '2026-11-15'
        ]);
        assert.strictEqual(summary.days[0].focusMins, 60);
        assert.strictEqual(summary.days[6].focusMins, 25);
        assert.strictEqual(summary.days[6].dayLabel, new Date(2026, 10, 15).toLocaleDateString(undefined, { weekday: 'short' }));
        assert.strictEqual(summary.days.reduce((total, day) => total + day.focusMins, 0), 85);
        """)

    def test_empty_summary_and_retained_history_cover_report_period(self):
        self.run_node(r"""
        const assert = require('assert');
        const { PomodoroCore } = require('./core.js');
        const summary = PomodoroCore.getWeeklyFocusSummary([], new Date(2026, 10, 15, 12));
        assert.strictEqual(summary.days.length, 7);
        assert.strictEqual(summary.days.every(day => day.focusMins === 0), true);
        assert.ok(PomodoroCore.SESSION_HISTORY_LIMIT >= 500);
        const history = Array.from({ length: 500 }, (_, index) => ({
          mode: 'focus', completedAt: new Date(2026, 10, 9, 0, index).toISOString(), focusDuration: 60
        }));
        assert.strictEqual(PomodoroCore.validateSessionHistory(history).length, 500);
        const values = { cp_session_history: JSON.stringify(history) };
        const backup = PomodoroCore.createDataBackup({ getItem: key => values[key] ?? null });
        const validated = PomodoroCore.validateDataBackup(backup);
        assert.strictEqual(JSON.parse(validated.data.cp_session_history).length, 500);
        const restored = {};
        assert.strictEqual(PomodoroCore.restoreDataBackup({
          getItem: key => restored[key] ?? null,
          setItem: (key, value) => { restored[key] = value; },
          removeItem: key => { delete restored[key]; }
        }, backup), true);
        assert.strictEqual(JSON.parse(restored.cp_session_history).length, 500);
        """)

    def test_index_renders_accessible_theme_aware_weekly_report(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="weeklyFocusReport"', html)
        self.assertIn('aria-labelledby="weeklyFocusHeading"', html)
        self.assertIn('role="group"', html)
        self.assertIn("PomodoroCore.getWeeklyFocusSummary", html)
        self.assertIn("weekly-focus-empty", html)
        self.assertIn("var(--accent)", html)
        self.assertIn("${day.focusMins} MIN", html)
        self.assertIn("${day.dayLabel}", html)
        self.assertIn("${summary.totalFocusMins}", html)


if __name__ == "__main__":
    unittest.main()
