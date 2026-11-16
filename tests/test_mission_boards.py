import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class TestMissionBoards(unittest.TestCase):
    def run_node(self, js_code):
        proc = subprocess.run(
            ["node", "-e", js_code], capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")

    def test_board_crud_switching_and_independent_tasks(self):
        self.run_node(r"""
        const assert = require('assert');
        const { PomodoroCore } = require('./core.js');
        const initial = PomodoroCore.loadMissionBoards(null, '[{"id":1,"text":"Legacy task","done":true}]');
        assert.deepStrictEqual(initial, {
          selectedBoardId: 'default',
          boards: [{ id: 'default', name: 'Main Board', tasks: [{ id: 1, text: 'Legacy task', done: true }] }]
        });
        const study = PomodoroCore.createMissionBoard(initial, '  Study  ', 'study');
        assert.strictEqual(study.boards.length, 2);
        assert.strictEqual(study.selectedBoardId, 'study');
        assert.strictEqual(study.boards[1].name, 'Study');
        const studyTasks = PomodoroCore.updateMissionBoardTasks(study, 'study', [
          { id: 2, text: 'Read chapter', done: false }
        ]);
        const switched = PomodoroCore.selectMissionBoard(studyTasks, 'default');
        assert.strictEqual(switched.boards[0].tasks[0].done, true);
        assert.deepStrictEqual(switched.boards[1].tasks, [{ id: 2, text: 'Read chapter', done: false }]);
        const renamed = PomodoroCore.renameMissionBoard(switched, 'study', '  Exam prep ');
        assert.strictEqual(renamed.boards[1].name, 'Exam prep');
        const deleted = PomodoroCore.deleteMissionBoard(renamed, 'default');
        assert.strictEqual(deleted.boards.length, 1);
        assert.strictEqual(deleted.selectedBoardId, 'study');
        assert.strictEqual(PomodoroCore.deleteMissionBoard(deleted, 'study'), null);
        """)

    def test_board_loading_validates_names_ids_and_task_lists(self):
        self.run_node(r"""
        const assert = require('assert');
        const { PomodoroCore } = require('./core.js');
        const valid = { selectedBoardId: 'a', boards: [{ id: 'a', name: 'Work', tasks: [] }] };
        assert.deepStrictEqual(PomodoroCore.validateMissionBoards(valid), valid);
        assert.strictEqual(PomodoroCore.validateMissionBoards({ selectedBoardId: 'missing', boards: valid.boards }), null);
        assert.strictEqual(PomodoroCore.validateMissionBoards({ selectedBoardId: 'a', boards: [
          { id: 'a', name: 'Work', tasks: [] }, { id: 'a', name: 'Duplicate', tasks: [] }
        ] }), null);
        assert.strictEqual(PomodoroCore.validateMissionBoards({ selectedBoardId: 'a', boards: [
          { id: 'a', name: '   ', tasks: [] }
        ] }), null);
        assert.strictEqual(PomodoroCore.validateMissionBoards({ selectedBoardId: 'a', boards: [
          { id: 'a', name: 'Work', tasks: [{ id: 1, text: 'Bad task', done: 'yes' }] }
        ] }), null);
        const fallback = PomodoroCore.loadMissionBoards('{bad json', 'invalid');
        assert.strictEqual(fallback.selectedBoardId, 'default');
        assert.strictEqual(fallback.boards[0].name, 'Main Board');
        assert.deepStrictEqual(fallback.boards[0].tasks, []);
        """)

    def test_board_controls_and_selected_board_persist_in_page(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
        for control_id in ["missionBoardSelect", "missionBoardName", "createMissionBoardBtn",
                           "renameMissionBoardBtn", "deleteMissionBoardBtn"]:
            self.assertIn(f'id="{control_id}"', html)
        self.assertIn("cp_mission_boards", html)
        self.assertIn("PomodoroCore.selectMissionBoard", html)


if __name__ == "__main__":
    unittest.main()
