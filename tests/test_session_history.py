import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestSessionHistory(unittest.TestCase):
    def test_history_validation_stops_after_limit_and_matches_baseline(self):
        js_code = r"""
        const assert = require('assert');
        const { PomodoroCore } = require('./core.js');

        function baselineValidateSessionHistory(history) {
          let entries = history;
          if (typeof entries === 'string') {
            try {
              entries = JSON.parse(entries);
            } catch (e) {
              return [];
            }
          }
          if (!Array.isArray(entries)) return [];

          const valid = [];
          for (let i = 0; i < entries.length; i++) {
            const entry = entries[i];
            if (!entry || typeof entry !== 'object' || Array.isArray(entry)) continue;
            if (entry.mode !== 'focus' && entry.mode !== 'shortBreak' && entry.mode !== 'longBreak') continue;
            if (typeof entry.completedAt !== 'string' || !Number.isFinite(Date.parse(entry.completedAt))) continue;

            if (entry.mode === 'focus') {
              if (typeof entry.focusDuration !== 'number' || !Number.isFinite(entry.focusDuration) || entry.focusDuration <= 0) continue;
              valid.push({ mode: 'focus', completedAt: entry.completedAt, focusDuration: entry.focusDuration });
            } else {
              valid.push({ mode: entry.mode, completedAt: entry.completedAt });
            }
          }
          return valid.slice(0, PomodoroCore.SESSION_HISTORY_LIMIT);
        }

        const completedAt = '2026-11-12T10:30:00.000Z';
        const cases = [
          [null, [], 'invalid JSON', 'not an array'],
          [
            { mode: 'unknown', completedAt },
            { mode: 'focus', completedAt, focusDuration: 0 },
            { mode: 'shortBreak', completedAt },
            { mode: 'focus', completedAt, focusDuration: 1500 },
            { mode: 'longBreak', completedAt },
            { mode: 'focus', completedAt, focusDuration: Infinity }
          ],
          JSON.stringify([
            { mode: 'focus', completedAt, focusDuration: 1500 },
            { mode: 'shortBreak', completedAt }
          ])
        ];
        for (const history of cases) {
          assert.deepStrictEqual(
            PomodoroCore.validateSessionHistory(history),
            baselineValidateSessionHistory(history)
          );
        }

        const fullHistory = Array.from({ length: 10000 }, (_, index) => ({
          mode: 'focus', completedAt, focusDuration: 1500 + index
        }));
        let indexedReads = 0;
        const trackedHistory = new Proxy(fullHistory, {
          get(target, property, receiver) {
            if (/^(0|[1-9]\d*)$/.test(String(property))) indexedReads++;
            return Reflect.get(target, property, receiver);
          }
        });
        const validated = PomodoroCore.validateSessionHistory(trackedHistory);
        assert.strictEqual(validated.length, PomodoroCore.SESSION_HISTORY_LIMIT);
        assert.deepStrictEqual(validated, baselineValidateSessionHistory(fullHistory));
        assert.strictEqual(indexedReads, PomodoroCore.SESSION_HISTORY_LIMIT);
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")

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

    def test_empty_history_guides_users_and_announces_status(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn("emptyItem.className = 'session-history-empty'", html)
        self.assertIn("emptyItem.setAttribute('role', 'status')", html)
        self.assertIn("Complete a focus session to see it here.", html)
        self.assertIn(".session-history-list .session-history-empty", html)


if __name__ == "__main__":
    unittest.main()
