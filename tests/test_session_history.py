import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestSessionHistory(unittest.TestCase):
    def test_session_history_helpers_record_validate_and_limit_entries(self):
        js_code = r"""
        const assert = require('assert');
        const { PomodoroCore } = require('./core.js');

        assert.strictEqual(typeof PomodoroCore.recordCompletedSession, 'function');
        assert.strictEqual(typeof PomodoroCore.validateSessionHistory, 'function');
        assert.strictEqual(typeof PomodoroCore.formatSessionHistoryEntry, 'function');

        const focus = PomodoroCore.recordCompletedSession([], 'focus', '2026-11-12T10:30:00.000Z', 1500);
        assert.strictEqual(focus.length, 1);
        assert.deepStrictEqual(focus[0], {
          mode: 'focus',
          completedAt: '2026-11-12T10:30:00.000Z',
          focusDuration: 1500
        });
        const breakHistory = PomodoroCore.recordCompletedSession(focus, 'shortBreak', '2026-11-12T10:35:00.000Z', 1500);
        assert.strictEqual(breakHistory.length, 2);
        assert.strictEqual(breakHistory[0].mode, 'shortBreak');
        assert.strictEqual(Object.prototype.hasOwnProperty.call(breakHistory[0], 'focusDuration'), false);
        assert.match(PomodoroCore.formatSessionHistoryEntry(focus[0]), /^FOCUS · 25 MIN · /);

        assert.deepStrictEqual(PomodoroCore.validateSessionHistory('{broken'), []);
        assert.deepStrictEqual(PomodoroCore.validateSessionHistory(JSON.stringify([
          { mode: 'focus', completedAt: 'not-a-date', focusDuration: 1500 },
          { mode: 'unknown', completedAt: '2026-11-12T10:30:00.000Z' },
          { mode: 'longBreak', completedAt: 'not-a-date', focusDuration: 1500 },
          { mode: 'focus', completedAt: '2026-11-12T10:30:00.000Z', focusDuration: -1 }
        ])), []);

        const many = Array.from({ length: 60 }, (_, index) => ({
          mode: 'focus',
          completedAt: new Date(Date.UTC(2026, 0, 1, 0, index)).toISOString(),
          focusDuration: 1500
        }));
        const bounded = PomodoroCore.validateSessionHistory(many);
        assert.strictEqual(bounded.length, PomodoroCore.SESSION_HISTORY_LIMIT);
        assert.strictEqual(bounded[0].completedAt, many[0].completedAt);
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")

    def test_index_html_displays_persisted_recent_sessions_accessibly(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn('id="sessionHistory"', html)
        self.assertIn('aria-labelledby="sessionHistoryHeading"', html)
        self.assertIn("localStorage.getItem('cp_session_history')", html)
        self.assertIn("localStorage.setItem('cp_session_history'", html)
        self.assertIn("PomodoroCore.recordCompletedSession", html)


if __name__ == "__main__":
    unittest.main()
