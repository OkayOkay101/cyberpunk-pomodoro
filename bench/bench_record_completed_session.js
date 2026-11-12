const { performance } = require('perf_hooks');
const { PomodoroCore } = require('../core.js');

const completedAt = '2026-11-12T10:30:00.000Z';
const history = Array.from({ length: PomodoroCore.SESSION_HISTORY_LIMIT }, (_, index) => ({
  mode: index % 3 === 0 ? 'focus' : (index % 3 === 1 ? 'shortBreak' : 'longBreak'),
  completedAt: new Date(Date.UTC(2026, 0, 1, 0, index)).toISOString(),
  ...(index % 3 === 0 ? { focusDuration: 1500 + index } : {})
}));

function optimizedRecordCompletedSession(existingHistory, mode, timestamp, focusDuration) {
  const entries = PomodoroCore.validateSessionHistory(existingHistory);
  if (mode !== 'focus' && mode !== 'shortBreak' && mode !== 'longBreak') return entries;
  if (typeof timestamp !== 'string' || !Number.isFinite(Date.parse(timestamp))) return entries;
  if (mode === 'focus' && (typeof focusDuration !== 'number' || !Number.isFinite(focusDuration) || focusDuration <= 0)) return entries;

  const entry = { mode, completedAt: timestamp };
  if (mode === 'focus') entry.focusDuration = focusDuration;
  entries.length = Math.min(entries.length, PomodoroCore.SESSION_HISTORY_LIMIT - 1);
  entries.unshift(entry);
  return entries;
}

function baselineRecordCompletedSession(existingHistory, mode, timestamp, focusDuration) {
  const entries = PomodoroCore.validateSessionHistory(existingHistory);
  if (mode !== 'focus' && mode !== 'shortBreak' && mode !== 'longBreak') return entries;
  const entry = { mode, completedAt: timestamp };
  if (mode === 'focus') entry.focusDuration = focusDuration;
  return PomodoroCore.validateSessionHistory([entry, ...entries]);
}

function run(fn, iterations) {
  let checksum = 0;
  const start = performance.now();
  for (let i = 0; i < iterations; i++) {
    const result = fn(history, 'focus', completedAt, 1500);
    checksum += result.length + result[0].focusDuration + result[result.length - 1].mode.length;
  }
  return { elapsed: performance.now() - start, checksum };
}

const iterations = 100000;
const rounds = 7;
const baselineTimes = [];
const optimizedTimes = [];
for (let round = 0; round < rounds; round++) {
  const baseline = run(baselineRecordCompletedSession, iterations);
  const optimized = run(optimizedRecordCompletedSession, iterations);
  if (baseline.checksum !== optimized.checksum) throw new Error('Benchmark outputs differ');
  baselineTimes.push(baseline.elapsed);
  optimizedTimes.push(optimized.elapsed);
}

function median(values) {
  return values.sort((a, b) => a - b)[Math.floor(values.length / 2)];
}

const beforeMs = median(baselineTimes);
const afterMs = median(optimizedTimes);
console.log(JSON.stringify({
  workload: `${iterations} records/round, ${history.length} valid history entries, median of ${rounds} rounds`,
  beforeMs: Number(beforeMs.toFixed(2)),
  afterMs: Number(afterMs.toFixed(2)),
  improvementPercent: Number(((beforeMs - afterMs) / beforeMs * 100).toFixed(1))
}));
