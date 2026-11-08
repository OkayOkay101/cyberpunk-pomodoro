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
        </div>
      `;
  }).join('');
}

function makeTasks(n) {
  const tasks = [];
  for (let i = 0; i < n; i++) {
    tasks.push({
      id: i,
      text: i % 7 === 0 ? 'Task <' + i + '> & "x"' : 'Task ' + i,
      done: i % 3 === 0
    });
  }
  return tasks;
}

function bench(fn, iters) {
  for (let i = 0; i < Math.min(iters, 50); i++) fn();
  const t0 = performance.now();
  for (let i = 0; i < iters; i++) fn();
  return performance.now() - t0;
}

for (const size of [100, 2000]) {
  const tasks = makeTasks(size);
  const expected = baselineRenderTaskList(tasks);
  const actual = PomodoroCore.renderTaskList(tasks);
  if (expected !== actual) throw new Error('Output mismatch at ' + size + ' tasks');

  const iters = size === 100 ? 20000 : 1000;
  const base = bench(() => baselineRenderTaskList(tasks), iters);
  const opt = bench(() => PomodoroCore.renderTaskList(tasks), iters);

  console.log(`\n[renderTaskList — ${size} tasks, ${iters.toLocaleString()} iterations]`);
  console.log(`  Baseline (map/join): ${base.toFixed(2)} ms (${(base / iters * 1000).toFixed(2)} us/op)`);
  console.log(`  Optimized (loop):    ${opt.toFixed(2)} ms (${(opt / iters * 1000).toFixed(2)} us/op)`);
  console.log(`  Speedup:             ${((base - opt) / base * 100).toFixed(1)}% faster (${(base / opt).toFixed(2)}x)`);
}
