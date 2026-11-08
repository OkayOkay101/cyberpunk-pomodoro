const { PomodoroCore } = require('./core.js');

function baselineFormatDocumentTitle(timeStr, isRunning) {
  const safeTime = (typeof timeStr === 'string' && timeStr.trim().length > 0) ? timeStr.trim() : '00:00';
  const statePrefix = isRunning ? '' : '[PAUSED] ';
  return `${statePrefix}(${safeTime}) CYBERPUNK FOCUS`;
}

const samples = [
  ['25:00', true],
  ['24:59', true],
  ['00:00', false],
  ['05:00', true],
  ['  10:00  ', true],
  ['', false],
  [null, true],
  ['   ', false],
  ['120:05', true],
  ['invalid', false],
  [undefined, true]
];

// 1. Strict Equality Verification
for (const [timeStr, isRunning] of samples) {
  const base = baselineFormatDocumentTitle(timeStr, isRunning);
  const opt = PomodoroCore.formatDocumentTitle(timeStr, isRunning);
  if (base !== opt) {
    throw new Error(`Output mismatch on "${timeStr}", isRunning=${isRunning}: baseline="${base}", optimized="${opt}"`);
  }
}
console.log('✓ Equality verification: baseline and optimized output match exactly.');

// 2. Performance Benchmark
const iters = 2000000;
const times = ['25:00', '24:59', '15:00', '05:00', '00:00', '120:05'];

// Warmup
for (let i = 0; i < 50000; i++) {
  baselineFormatDocumentTitle('25:00', true);
  PomodoroCore.formatDocumentTitle('25:00', true);
}

// Workload A: Running timer across time strings (active timer ticks)
let t0 = performance.now();
for (let i = 0; i < iters; i++) baselineFormatDocumentTitle(times[i % times.length], true);
const baseRunning = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) PomodoroCore.formatDocumentTitle(times[i % times.length], true);
const optRunning = performance.now() - t0;

// Workload B: Mixed states (running, paused, edge cases)
t0 = performance.now();
for (let i = 0; i < iters; i++) {
  const [t, r] = samples[i % samples.length];
  baselineFormatDocumentTitle(t, r);
}
const baseMixed = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) {
  const [t, r] = samples[i % samples.length];
  PomodoroCore.formatDocumentTitle(t, r);
}
const optMixed = performance.now() - t0;

console.log('\n=== Benchmark Results (Workload: 2,000,000 iterations each) ===');
console.log(`[Workload A: Active timer ticking]`);
console.log(`  Baseline:   ${baseRunning.toFixed(2)} ms (${(baseRunning / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized:  ${optRunning.toFixed(2)} ms (${(optRunning / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:    ${((baseRunning - optRunning) / baseRunning * 100).toFixed(1)}% faster (${(baseRunning / optRunning).toFixed(2)}x)`);

console.log(`\n[Workload B: Mixed states & edge cases]`);
console.log(`  Baseline:   ${baseMixed.toFixed(2)} ms (${(baseMixed / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized:  ${optMixed.toFixed(2)} ms (${(optMixed / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:    ${((baseMixed - optMixed) / baseMixed * 100).toFixed(1)}% faster (${(baseMixed / optMixed).toFixed(2)}x)`);
