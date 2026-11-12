const { performance } = require('perf_hooks');

const taskCount = 100;
const rendersPerRound = 10000;
let listenerAttachments = 0;

function createEnvironment() {
  const taskItems = Array.from({ length: taskCount }, () => ({ done: false }));
  const checklist = {
    handler: null,
    innerHTML: '',
    querySelectorAll() { return taskItems.map((task) => ({
      task,
      addEventListener(type, handler) {
        if (type === 'change') {
          this.handler = handler;
          listenerAttachments++;
        }
      }
    })); },
    addEventListener(type, handler) {
      if (type === 'change') {
        this.handler = handler;
        listenerAttachments++;
      }
    }
  };
  return { taskItems, checklist };
}

const baseline = createEnvironment();
const delegated = createEnvironment();

function renderWithPerItemListeners() {
  baseline.checklist.innerHTML = '<div class="task-item">task list</div>';
  baseline.checklist.querySelectorAll('input[type="checkbox"]').forEach((box) => {
    box.addEventListener('change', (event) => {
      box.task.done = Boolean(event.target.checked);
    });
  });
}

function renderWithDelegation() {
  delegated.checklist.innerHTML = '<div class="task-item">task list</div>';
}

const delegatedHandler = (event) => {
  if (!event.target.matches('input[type="checkbox"]')) return;
  const task = event.target.closest('.task-item').task;
  if (task) task.done = Boolean(event.target.checked);
};
delegated.checklist.addEventListener('change', delegatedHandler);

const baselineTarget = { checked: true };
const delegatedTarget = {
  checked: true,
  matches: (selector) => selector === 'input[type="checkbox"]',
  closest: (selector) => selector === '.task-item' ? { task: delegated.taskItems[0] } : null
};
const baselineCheckbox = baseline.checklist.querySelectorAll('input[type="checkbox"]')[0];
baselineCheckbox.addEventListener('change', (event) => {
  baseline.taskItems[0].done = Boolean(event.target.checked);
});
baselineCheckbox.handler({ target: baselineTarget });
delegated.checklist.handler({ target: delegatedTarget });
if (JSON.stringify(baseline.taskItems) !== JSON.stringify(delegated.taskItems)) throw new Error('delegated checkbox behavior mismatch');

function measure(render) {
  const start = performance.now();
  for (let i = 0; i < rendersPerRound; i++) render();
  return performance.now() - start;
}

for (let i = 0; i < 2; i++) {
  measure(renderWithPerItemListeners);
  measure(renderWithDelegation);
}

const baselineRounds = [];
const delegatedRounds = [];
listenerAttachments = 0;
for (let i = 0; i < 7; i++) {
  baselineRounds.push(measure(renderWithPerItemListeners));
  delegatedRounds.push(measure(renderWithDelegation));
}
const median = (values) => values.sort((a, b) => a - b)[Math.floor(values.length / 2)];
const baselineMs = median(baselineRounds);
const delegatedMs = median(delegatedRounds);
console.log(JSON.stringify({
  workload: `${taskCount} checkboxes × ${rendersPerRound} renders × 7 measured rounds`,
  baselineMs: Number(baselineMs.toFixed(2)),
  delegatedMs: Number(delegatedMs.toFixed(2)),
  improvementPercent: Number(((baselineMs - delegatedMs) / baselineMs * 100).toFixed(1)),
  baselineListenerAttachments: listenerAttachments,
  delegatedListenerAttachments: 1,
  outputEquality: JSON.stringify(baseline.taskItems) === JSON.stringify(delegated.taskItems)
}));
