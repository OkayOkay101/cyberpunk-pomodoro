import unittest
import subprocess


class TestToggleTaskItemPerformance(unittest.TestCase):
    def test_toggle_task_item_single_pass_and_equality(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        function baselineToggleTaskItem(tasks, taskId, isDone) {
            if (!Array.isArray(tasks)) return [];
            return tasks.map(task => {
                if (task && task.id === taskId) {
                    return { ...task, done: Boolean(isDone) };
                }
                return task;
            });
        }

        const fnStr = PomodoroCore.toggleTaskItem.toString();
        if (/\\.map\\s*\\(/.test(fnStr)) {
            console.error('FAIL: toggleTaskItem still uses Array.map callback allocation');
            process.exit(2);
        }

        const baseTasks = [
            { id: 1, text: 'Task 1', done: false },
            { id: 2, text: 'Task 2', done: true },
            { id: 3, text: 'Task 3', done: false }
        ];

        const cases = [
            [null, 1, true],
            [undefined, 1, true],
            [[], 1, true],
            [baseTasks, 2, false],
            [baseTasks, 99, true],
            [[null, undefined, { id: 5, text: 'ok', done: false }], 5, true],
            [[{ id: 7, text: 'dup', done: false }, { id: 7, text: 'dup2', done: true }], 7, false],
            [Array.from({ length: 500 }, (_, i) => ({ id: i, text: 'Task ' + i, done: i % 2 === 0 })), 499, true]
        ];

        for (const [tasks, taskId, isDone] of cases) {
            const expected = baselineToggleTaskItem(tasks, taskId, isDone);
            const actual = PomodoroCore.toggleTaskItem(tasks, taskId, isDone);
            if (JSON.stringify(actual) !== JSON.stringify(expected)) {
                console.error('Mismatch for taskId=' + taskId + ' with ' + (tasks ? tasks.length : tasks) + ' tasks');
                process.exit(1);
            }
        }
        console.log('SUCCESS');
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
