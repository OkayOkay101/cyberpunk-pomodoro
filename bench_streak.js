const { PomodoroCore } = require('./core.js');

function baselineCalculateStreak(lastDateStr, todayStr, currentStreak) {
  const validStreak = (typeof currentStreak === 'number' && !isNaN(currentStreak) && currentStreak >= 1)
    ? Math.floor(currentStreak)
    : 1;
  if (!lastDateStr || typeof lastDateStr !== 'string') return 1;
  if (lastDateStr === todayStr) return validStreak;
  const lastDate = new Date(lastDateStr);
  const today = new Date(todayStr);
  const diffTime = today - lastDate;
  if (isNaN(diffTime)) return 1;
  const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));
  if (diffDays === 1) return validStreak + 1;
  if (diffDays > 1) return 1;
  return validStreak;
}

// 1. Strict Equality Verification across varied inputs
const samples = [
  ['2026-11-07', '2026-11-08', 1],
  ['2026-11-07', '2026-11-09', 1],
  ['2026-11-08', '2026-11-08', 3],
  ['', '2026-11-08', 1],
  ['2026-11-07', '2026-11-08', NaN],
  ['2026-11-07', '2026-11-08', 0],
  ['2026-11-07', '2026-11-08', -5],
  ['2026-11-09', '2026-11-08', 5],
  ['2026-1-8', '2026-01-08', 3],
  ['2026-03-07', '2026-03-08', 1],
  ['2026-11-01', '2026-11-02', 1],
  [null, '2026-11-08', 1],
  [undefined, '2026-11-08', 1],
  ['invalid-date', '2026-11-08', 1],
  ['2026-11-08', 'invalid-date', 1],
  ['2026-11-08', null, 5],
  ['2026-11-08', undefined, 5],
  ['2026-11-08', 12345, 5],
  ['2026-12-31', '2027-01-01', 10],
  ['2024-02-28', '2024-02-29', 1],
  ['2024-02-29', '2024-03-01', 2]
];

for (const [last, today, cur] of samples) {
  const base = baselineCalculateStreak(last, today, cur);
  const opt = PomodoroCore.calculateStreak(last, today, cur);
  if (base !== opt) {
    throw new Error(`Output mismatch on [${last}, ${today}, ${cur}]: baseline="${base}", optimized="${opt}"`);
  }
}
console.log('✓ Equality verification: baseline and optimized output match exactly across all test cases.');

// 2. Performance Benchmark
const iters = 500000;

// Warmup
for (let i = 0; i < 20000; i++) {
  baselineCalculateStreak('2026-11-07', '2026-11-08', 5);
  PomodoroCore.calculateStreak('2026-11-07', '2026-11-08', 5);
}

// Workload A: Consecutive days (the common active streak update case)
let t0 = performance.now();
for (let i = 0; i < iters; i++) baselineCalculateStreak('2026-11-07', '2026-11-08', 5);
const baseConsecutive = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) PomodoroCore.calculateStreak('2026-11-07', '2026-11-08', 5);
const optConsecutive = performance.now() - t0;

// Workload B: Mixed days (consecutive, gap, same day, invalid)
t0 = performance.now();
for (let i = 0; i < iters; i++) {
  const sample = samples[i % samples.length];
  baselineCalculateStreak(sample[0], sample[1], sample[2]);
}
const baseMixed = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) {
  const sample = samples[i % samples.length];
  PomodoroCore.calculateStreak(sample[0], sample[1], sample[2]);
}
const optMixed = performance.now() - t0;

console.log(`\n=== Benchmark Results (Workload: ${iters.toLocaleString()} iterations each) ===`);
console.log(`[Workload A: Consecutive days streak calculation]`);
console.log(`  Baseline:  ${baseConsecutive.toFixed(2)} ms (${(baseConsecutive / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized: ${optConsecutive.toFixed(2)} ms (${(optConsecutive / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:   ${((baseConsecutive - optConsecutive) / baseConsecutive * 100).toFixed(1)}% faster (${(baseConsecutive / optConsecutive).toFixed(2)}x)`);

console.log(`\n[Workload B: Mixed streak workload]`);
console.log(`  Baseline:  ${baseMixed.toFixed(2)} ms (${(baseMixed / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized: ${optMixed.toFixed(2)} ms (${(optMixed / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:   ${((baseMixed - optMixed) / baseMixed * 100).toFixed(1)}% faster (${(baseMixed / optMixed).toFixed(2)}x)`);
