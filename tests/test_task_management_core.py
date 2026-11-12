import json
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestTaskManagementCore(unittest.TestCase):
    """
    Unit tests for PomodoroCore task management and mission sanitizer functions:
    - PomodoroCore.sanitizeMission(text)
    - PomodoroCore.createTaskItem(text, id)
    """

    def _run_node(self, js_code: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )

    def test_sanitize_mission_edge_cases_and_boundaries(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (typeof PomodoroCore.sanitizeMission !== 'function') {
            console.error('FAIL: sanitizeMission is not a function');
            process.exit(1);
        }

        // 1. Whitespace trimming
        if (PomodoroCore.sanitizeMission('   Deep Work Mission   ') !== 'Deep Work Mission') {
            console.error('FAIL: trimming');
            process.exit(2);
        }

        // 2. Exact length boundaries: 79, 80, 81 chars
        const s79 = 'A'.repeat(79);
        const s80 = 'B'.repeat(80);
        const s81 = 'C'.repeat(81);
        const s120 = 'D'.repeat(120);

        if (PomodoroCore.sanitizeMission(s79) !== s79) process.exit(3);
        if (PomodoroCore.sanitizeMission(s80) !== s80) process.exit(4);
        if (PomodoroCore.sanitizeMission(s81) !== 'C'.repeat(80)) process.exit(5);
        if (PomodoroCore.sanitizeMission(s120).length !== 80) process.exit(6);

        // 2. Truncating at the 80-character boundary must not split a Unicode surrogate pair.
        const unicodeBoundary = 'A'.repeat(79) + '😀B';
        if (PomodoroCore.sanitizeMission(unicodeBoundary) !== 'A'.repeat(79) + '😀') process.exit(17);

        // 3. Null, undefined, empty, and whitespace-only
        if (PomodoroCore.sanitizeMission(null) !== '') process.exit(7);
        if (PomodoroCore.sanitizeMission(undefined) !== '') process.exit(8);
        if (PomodoroCore.sanitizeMission('') !== '') process.exit(9);
        if (PomodoroCore.sanitizeMission('   ') !== '') process.exit(10);
        if (PomodoroCore.sanitizeMission('\\t\\r\\n  ') !== '') process.exit(11);

        // 4. Non-string inputs must return empty string
        if (PomodoroCore.sanitizeMission(12345) !== '') process.exit(12);
        if (PomodoroCore.sanitizeMission(true) !== '') process.exit(13);
        if (PomodoroCore.sanitizeMission(false) !== '') process.exit(14);
        if (PomodoroCore.sanitizeMission({ text: 'mission' }) !== '') process.exit(15);
        if (PomodoroCore.sanitizeMission(['mission']) !== '') process.exit(16);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_create_task_item_valid_inputs_and_properties(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (typeof PomodoroCore.createTaskItem !== 'function') {
            console.error('FAIL: createTaskItem is not a function');
            process.exit(1);
        }

        const tBefore = Date.now();

        // 1. Explicit valid numeric ID
        const task1 = PomodoroCore.createTaskItem('   Audit code quality   ', 101);
        if (!task1 || task1.id !== 101 || task1.text !== 'Audit code quality' || task1.done !== false) {
            console.error('FAIL: task1 structure mismatch', task1);
            process.exit(2);
        }

        // 2. ID of 0 is valid numeric ID and must not be overwritten by Date.now()
        const taskZero = PomodoroCore.createTaskItem('Zero Index Task', 0);
        if (!taskZero || taskZero.id !== 0 || taskZero.text !== 'Zero Index Task' || taskZero.done !== false) {
            console.error('FAIL: taskZero id 0 should be preserved', taskZero);
            process.exit(3);
        }

        // 3. Negative numeric ID is valid finite number
        const taskNeg = PomodoroCore.createTaskItem('Negative ID Task', -10);
        if (!taskNeg || taskNeg.id !== -10) {
            console.error('FAIL: taskNeg id -10 should be preserved', taskNeg);
            process.exit(4);
        }

        // 4. Omitted ID generates finite timestamp >= tBefore
        const taskAuto = PomodoroCore.createTaskItem('Auto Generated ID');
        const tAfter = Date.now();
        if (!taskAuto || typeof taskAuto.id !== 'number' || !Number.isFinite(taskAuto.id) || taskAuto.id < tBefore || taskAuto.id > tAfter) {
            console.error('FAIL: taskAuto id should be within [tBefore, tAfter]', taskAuto);
            process.exit(5);
        }

        // 5. String numeric ID from DOM dataset parses to finite number
        const taskStr = PomodoroCore.createTaskItem('DOM Task', '205');
        if (!taskStr || taskStr.id !== 205) {
            console.error('FAIL: numeric string ID "205" should parse to number 205', taskStr);
            process.exit(6);
        }

        const taskStrZero = PomodoroCore.createTaskItem('DOM Zero Task', '0');
        if (!taskStrZero || taskStrZero.id !== 0) {
            console.error('FAIL: numeric string ID "0" should parse to number 0', taskStrZero);
            process.exit(7);
        }

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_create_task_item_invalid_text_returns_null(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const invalidTexts = [
            '',
            '    ',
            '\\t\\n\\r',
            null,
            undefined,
            42,
            true,
            false,
            { task: 'obj' },
            ['array'],
            NaN
        ];

        for (const input of invalidTexts) {
            const result = PomodoroCore.createTaskItem(input, 10);
            if (result !== null) {
                console.error('FAIL: expected null for invalid text input:', input, 'got:', result);
                process.exit(1);
            }
        }

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_create_task_item_non_finite_id_guard_and_json_safety(self):
        """
        Verify that non-finite IDs (Infinity, -Infinity, NaN, 'Infinity') do NOT produce
        unserializable IDs that become null in JSON, permanently breaking task checkboxes.
        """
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const nonFiniteCases = [
            Infinity,
            -Infinity,
            NaN,
            'Infinity',
            '-Infinity',
            'abc',
            '   '
        ];

        for (const badId of nonFiniteCases) {
            const task = PomodoroCore.createTaskItem('Cyberpunk Task', badId);
            if (!task) {
                console.error('FAIL: task should be created for valid text even with badId:', badId);
                process.exit(1);
            }

            // ID must be finite number (never Infinity, -Infinity, or NaN)
            if (typeof task.id !== 'number' || !Number.isFinite(task.id)) {
                console.error('FAIL: non-finite ID assigned to task:', badId, 'got task.id:', task.id);
                process.exit(2);
            }

            // Verify JSON serialization safety: id must NOT serialize to null
            const json = JSON.stringify(task);
            if (json.includes('"id":null')) {
                console.error('FAIL: JSON serialized task has null id:', json);
                process.exit(3);
            }

            const parsed = JSON.parse(json);
            if (typeof parsed.id !== 'number' || !Number.isFinite(parsed.id)) {
                console.error('FAIL: deserialized task id is not a finite number:', parsed);
                process.exit(4);
            }

            // Verify toggleTaskItem works with the deserialized task
            const tasks = [parsed];
            const toggled = PomodoroCore.toggleTaskItem(tasks, parsed.id, true);
            if (!toggled[0].done) {
                console.error('FAIL: toggleTaskItem failed to toggle deserialized task:', toggled);
                process.exit(5);
            }
        }

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_task_lifecycle_create_serialize_toggle_render(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Create tasks
        const t1 = PomodoroCore.createTaskItem('   Task 1 <alpha>   ', 1);
        const t2 = PomodoroCore.createTaskItem('Task 2 & "beta"', 2);
        const initialTasks = [t1, t2];

        // Serialize and deserialize
        const jsonStr = PomodoroCore.serializeConfig(initialTasks);
        const loadedTasks = PomodoroCore.deserializeConfig(jsonStr, []);

        if (loadedTasks.length !== 2) {
            console.error('FAIL: loadedTasks length', loadedTasks);
            process.exit(1);
        }
        if (loadedTasks[0].text !== 'Task 1 <alpha>' || loadedTasks[0].done !== false) {
            console.error('FAIL: loadedTask[0] mismatch', loadedTasks[0]);
            process.exit(2);
        }

        // Toggle task 1 to done
        const toggledTasks = PomodoroCore.toggleTaskItem(loadedTasks, 1, true);
        if (!toggledTasks[0].done || toggledTasks[1].done) {
            console.error('FAIL: toggle mismatch', toggledTasks);
            process.exit(3);
        }

        // Render checklist HTML
        const html = PomodoroCore.renderTaskList(toggledTasks);
        if (!html.includes('class="task-item done"') || !html.includes('data-id="1"')) {
            console.error('FAIL: task 1 rendered html mismatch', html);
            process.exit(4);
        }
        if (!html.includes('Task 1 &lt;alpha&gt;') || !html.includes('Task 2 &amp; &quot;beta&quot;')) {
            console.error('FAIL: html escaping in task list mismatch', html);
            process.exit(5);
        }

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
