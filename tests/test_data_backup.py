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

    def test_restore_replaces_all_supported_keys_so_no_mixed_state_remains(self):
        self.run_node(r"""
        const assert = require('assert');
        const { PomodoroCore } = require('./core.js');
        const store = { cp_streak: '9', cp_focus_mins_today: '50', cp_last_date: '2026-11-11', unrelated_key: 'keep' };
        const storage = {
          getItem(key) { return Object.hasOwn(store, key) ? store[key] : null; },
          setItem(key, value) { store[key] = String(value); },
          removeItem(key) { delete store[key]; }
        };
        // backup ที่ไม่มี cp_streak / cp_focus_mins_today: ค่าเดิมต้องถูกลบ ไม่ปนกับวันที่ใหม่
        const backup = { version: 1, data: { cp_last_date: '2026-11-12' } };
        assert.strictEqual(PomodoroCore.restoreDataBackup(storage, JSON.stringify(backup), Date.now()), true);
        assert.strictEqual(Object.hasOwn(store, 'cp_streak'), false);
        assert.strictEqual(Object.hasOwn(store, 'cp_focus_mins_today'), false);
        assert.strictEqual(store.cp_last_date, '2026-11-12');
        assert.strictEqual(store.unrelated_key, 'keep');
        """)

    def test_restore_rolls_back_when_storage_write_fails(self):
        self.run_node(r"""
        const assert = require('assert');
        const { PomodoroCore } = require('./core.js');
        const store = { cp_theme: 'cyan', cp_streak: '4' };
        let writes = 0;
        const storage = {
          getItem(key) { return Object.hasOwn(store, key) ? store[key] : null; },
          setItem(key, value) {
            writes += 1;
            if (writes === 3) throw new Error('QuotaExceededError');
            store[key] = String(value);
          },
          removeItem(key) { delete store[key]; }
        };
        const before = JSON.stringify(store);
        const backup = { version: 1, data: { cp_theme: 'green', cp_streak: '2', cp_volume: '0.5' } };
        assert.strictEqual(PomodoroCore.restoreDataBackup(storage, JSON.stringify(backup), Date.now()), false);
        assert.strictEqual(JSON.stringify(store), before, 'storage must be restored to the previous values');
        """)

    def test_import_rejects_duplicate_task_ids(self):
        self.run_node(r"""
        const assert = require('assert');
        const { PomodoroCore } = require('./core.js');
        const dup = { version: 1, data: { cp_tasks: JSON.stringify([
          { id: 1, text: 'A', done: false }, { id: '1', text: 'B', done: true }
        ]) } };
        assert.strictEqual(PomodoroCore.validateDataBackup(dup, Date.now()), null);
        const unique = { version: 1, data: { cp_tasks: JSON.stringify([
          { id: 1, text: 'A', done: false }, { id: 2, text: 'B', done: true }
        ]) } };
        assert.notStrictEqual(PomodoroCore.validateDataBackup(unique, Date.now()), null);
        """)

    def test_import_counts_emoji_code_points_for_mission_and_tasks(self):
        self.run_node(r"""
        const assert = require('assert');
        const { PomodoroCore } = require('./core.js');
        const storage = {
          getItem() { return null; },
          setItem() {},
          removeItem() {}
        };
        for (const count of [40, 60, 80]) {
          const emoji = '😀'.repeat(count);
          for (const data of [
            { cp_mission: emoji },
            { cp_tasks: JSON.stringify([{ id: 1, text: emoji, done: false }]) }
          ]) {
            const backup = JSON.stringify({ version: 1, data });
            assert.strictEqual(PomodoroCore.restoreDataBackup(storage, backup), true,
              `${count} emoji should be accepted`);
          }
        }
        for (const data of [
          { cp_mission: '😀'.repeat(81) },
          { cp_tasks: JSON.stringify([{ id: 1, text: '😀'.repeat(81), done: false }]) }
        ]) {
          const backup = JSON.stringify({ version: 1, data });
          assert.strictEqual(PomodoroCore.restoreDataBackup(storage, backup), false,
            '81 emoji should be rejected');
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
