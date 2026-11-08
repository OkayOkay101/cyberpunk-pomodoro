const { PomodoroCore } = require('./core.js');

function baselineFormatTime(seconds) {
  if (isNaN(seconds) || seconds < 0 || !isFinite(seconds)) return '00:00';
  const totalSecs = Math.floor(seconds);
  const mins = Math.floor(totalSecs / 60);
  const secs = totalSecs % 60;
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

const samples = [
  0,
  5,
  9,
  10,
  59,
  60,
  65,
  1499,
  1500,
  3599,
  3600,
  5999,
  6000,
  7205,
  -1,
  NaN,
  Infinity,
  -Infinity,
  'abc',
  null,
  undefined
];

// 1. Strict Equality Verification
for (const s of samples) {
  const base = baselineFormatTime(s);
  const opt = PomodoroCore.formatTime(s);
  if (base !== opt) {
    throw new Error(`Output mismatch on "${s}": baseline="${base}", optimized="${opt}"`);
  }
}
console.log('✓ Equality verification: baseline and optimized output match exactly.');

// 2. Performance Benchmark
const iters = 1000000;

// Warmup
for (let i = 0; i < 10000; i++) {
  baselineFormatTime(1499);
  PomodoroCore.formatTime(1499);
}

// Workload A: Typical pomodoro duration (25:00 countdown)
let t0 = performance.now();
for (let i = 0; i < iters; i++) baselineFormatTime(1499);
const baseTypical = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) PomodoroCore.formatTime(1499);
const optTypical = performance.now() - t0;

// Workload B: Mixed varied seconds across ranges
const mixedTimes = [0, 5, 59, 65, 300, 900, 1500, 3599, 6005];
t0 = performance.now();
for (let i = 0; i < iters; i++) baselineFormatTime(mixedTimes[i % mixedTimes.length]);
const baseMixed = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) PomodoroCore.formatTime(mixedTimes[i % mixedTimes.length]);
const optMixed = performance.now() - t0;

console.log('\n=== Benchmark Results (Workload: 1,000,000 iterations each) ===');
console.log(`[Workload A: Typical pomodoro timer (1499s)]`);
console.log(`  Baseline (padStart):  ${baseTypical.toFixed(2)} ms (${(baseTypical / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized (PAD_TWO):  ${optTypical.toFixed(2)} ms (${(optTypical / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:              ${((baseTypical - optTypical) / baseTypical * 100).toFixed(1)}% faster (${(baseTypical / optTypical).toFixed(2)}x)`);

console.log(`\n[Workload B: Mixed durations (0s to 6005s)]`);
console.log(`  Baseline (padStart):  ${baseMixed.toFixed(2)} ms (${(baseMixed / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized (PAD_TWO):  ${optMixed.toFixed(2)} ms (${(optMixed / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:              ${((baseMixed - optMixed) / baseMixed * 100).toFixed(1)}% faster (${(baseMixed / optMixed).toFixed(2)}x)`);
