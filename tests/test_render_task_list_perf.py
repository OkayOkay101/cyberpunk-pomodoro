import unittest
import subprocess
from pathlib import Path


class TestRenderTaskListPerformance(unittest.TestCase):
    def test_render_task_list_single_pass_and_equality(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        function escapeHtml(text) {
            if (!text || typeof text !== 'string') return '';
            if (!/[&<>"']/.test(text)) return text;
            return text.replace(/[&<>"']/g, ch => (
                ch === '&' ? '&amp;' :
                ch === '<' ? '&lt;' :
                ch === '>' ? '&gt;' :
                ch === '"' ? '&quot;' : '&#039;'
            ));
        }

        function baselineRenderTaskList(tasks) {
            if (!Array.isArray(tasks) || tasks.length === 0) {
                return '<div class="task-empty" role="status">ยังไม่มีภารกิจ — พิมพ์ด้านบนแล้วกด Enter เพื่อเพิ่ม</div>';
            }
            return tasks.map(task => {
                if (!task || typeof task.text !== 'string') return '';
                const safeText = escapeHtml(task.text);
                return `
        <div class="task-item ${task.done ? 'done' : ''}" data-id="${escapeHtml(String(task.id))}">
          <input type="checkbox" ${task.done ? 'checked' : ''} aria-label="${safeText}">
          <span>${safeText}</span>
          <button type="button" class="task-remove" aria-label="ลบภารกิจ: ${safeText}">×</button>
        </div>
      `;
            }).join('');
        }

        const fnStr = PomodoroCore.renderTaskList.toString();
        if (/\\.map\\s*\\(/.test(fnStr) || /\\.join\\s*\\(/.test(fnStr)) {
            console.error('FAIL: renderTaskList still builds intermediate map/join arrays');
            process.exit(2);
        }

        const cases = [
            [],
            null,
            undefined,
            [null, { id: 1 }, { id: 2, text: 'ok' }],
            [{ id: 7, text: 'A & B <script>', done: false }],
            [{ id: 8, text: 'Finished task', done: true }],
            [
                { id: 1, text: 'Task 1', done: false },
                { id: 2, text: 'Task 2', done: true },
                { id: 3, text: 'Tom & "Jerry" <x>', done: false }
            ],
            Array.from({ length: 500 }, (_, i) => ({
                id: i,
                text: i % 7 === 0 ? 'Task <' + i + '> & "x"' : 'Task ' + i,
                done: i % 3 === 0
            }))
        ];

        for (const tasks of cases) {
            const expected = baselineRenderTaskList(tasks);
            const actual = PomodoroCore.renderTaskList(tasks);
            if (actual !== expected) {
                console.error('Mismatch for case with ' + (tasks ? tasks.length : tasks) + ' tasks');
                process.exit(1);
            }
        }
        console.log('SUCCESS');
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=Path(__file__).resolve().parents[1]
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
