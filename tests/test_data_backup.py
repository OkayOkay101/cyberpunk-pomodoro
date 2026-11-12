import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestDataBackup(unittest.TestCase):
    def run_node(self, js_code):
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")

    def test_export_contains_versioned_supported_preferences_tasks_timer_and_history(self):
        self.run_node(r"""
        const assert = require('assert');
        const { PomodoroCore } = require('./core.js');
        const values = {
          cp_cfg_focus: '40', cp_cfg_short: '7', cp_cfg_long: '20', cp_theme: 'pink',
          cp_volume: '0.7', cp_muted: 'false', cp_tick: 'true', cp_autostart: 'false',
          cp_tasks: JSON.stringify([{ id: 7, text: 'Ship feature', done: true }]),
          cp_mission: 'Ship feature', cp_cycle: '3',
          cp_timer_state: JSON.stringify({ mode: 'focus', duration: 2400, timeLeft: 1200,
            isRunning: false, targetEndTime: null, cycleCount: 3 }),
          cp_session_history: JSON.stringify([{ mode: 'focus', completedAt: '2026-11-12T10:30:00.000Z', focusDuration: 2400 }])
        };
        const backup = PomodoroCore.createDataBackup({ getItem: key => values[key] ?? null });
        assert.strictEqual(backup.version, PomodoroCore.DATA_BACKUP_VERSION);
        assert.strictEqual(backup.data.cp_cfg_focus, '40');
        assert.strictEqual(backup.data.cp_theme, 'pink');
        assert.deepStrictEqual(JSON.parse(backup.data.cp_tasks), JSON.parse(values.cp_tasks));
        assert.deepStrictEqual(JSON.parse(backup.data.cp_timer_state), JSON.parse(values.cp_timer_state));
        assert.deepStrictEqual(JSON.parse(backup.data.cp_session_history), JSON.parse(values.cp_session_history));
        assert.strictEqual(Object.hasOwn(backup.data, 'unrelated_key'), false);
        """)

    def test_valid_import_restores_data_and_rejected_imports_leave_storage_unchanged(self):
        self.run_node(r"""
        const assert = require('assert');
        const { PomodoroCore } = require('./core.js');
        const initial = { cp_theme: 'cyan', cp_cfg_focus: '25', unrelated_key: 'keep' };
        const storage = {
          getItem(key) { return Object.hasOwn(initial, key) ? initial[key] : null; },
          setItem(key, value) { initial[key] = String(value); },
          removeItem(key) { delete initial[key]; }
        };
        const valid = { version: 1, data: { cp_theme: 'green', cp_cfg_focus: '45', cp_tasks: '[]' } };
        assert.strictEqual(PomodoroCore.restoreDataBackup(storage, JSON.stringify(valid), Date.now()), true);
        assert.strictEqual(initial.cp_theme, 'green');
        assert.strictEqual(initial.cp_cfg_focus, '45');
        assert.strictEqual(initial.cp_tasks, '[]');
        assert.strictEqual(Object.hasOwn(initial, 'cp_cfg_short'), false);
        assert.strictEqual(initial.unrelated_key, 'keep');

        for (const invalid of [
          '{bad json',
          JSON.stringify({ version: 99, data: valid.data }),
          JSON.stringify({ version: 1, data: { cp_theme: 'ultraviolet' } }),
          JSON.stringify({ version: 1, data: { cp_tasks: '{"bad":true}' } }),
          JSON.stringify({ version: 1, data: { cp_cfg_focus: '999' } }),
          JSON.stringify({ version: 1, data: { cp_not_supported: 'value' } })
        ]) {
          const before = JSON.stringify(initial);
          assert.strictEqual(PomodoroCore.restoreDataBackup(storage, invalid, Date.now()), false);
          assert.strictEqual(JSON.stringify(initial), before);
        }
        """)

    def test_settings_modal_exposes_export_and_import_controls(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn('id="exportDataBtn"', html)
        self.assertIn('id="importDataInput"', html)
        self.assertIn("PomodoroCore.createDataBackup(localStorage)", html)
        self.assertIn("PomodoroCore.restoreDataBackup(localStorage", html)


if __name__ == "__main__":
    unittest.main()
