const { PomodoroCore } = require('./core.js');

// Baseline: uses String.padStart (like old formatTime)
function baselineFormatSessionLabel(cycleCount) {
  const parsed = parseInt(cycleCount, 10);
  const validCycle = (!isNaN(parsed) && parsed >= 1) ? parsed : 1;
  return `SESSION ${String(validCycle).padStart(2, '0')} // DEEP WORK`;
}

// 1. Strict Equality Verification
const samples = [
  1, 2, 9, 10, 11, 25, 99, 100, 999,
  '5', '09', 'abc', NaN, 0, -5, null, undefined
];

for (const s of samples) {
  const base = baselineFormatSessionLabel(s);
  const opt = PomodoroCore.formatSessionLabel(s);
  if (base !== opt) {
    throw new Error(`Output mismatch on "${s}": baseline="${base}", optimized="${opt}"`);
  }
}
console.log('✓ Equality verification: baseline and optimized output match exactly.');

// 2. Performance Benchmark
const iters = 3000000;

// Warmup
for (let i = 0; i < 50000; i++) {
  baselineFormatSessionLabel(25);
  PomodoroCore.formatSessionLabel(25);
}

// Workload A: Typical cycles 1-99 (2-digit padStart range)
let t0 = performance.now();
for (let i = 0; i < iters; i++) baselineFormatSessionLabel((i % 99) + 1);
const baseTypical = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) PomodoroCore.formatSessionLabel((i % 99) + 1);
const optTypical = performance.now() - t0;

// Workload B: Mixed including 3+ digit cycles
const mixedCycles = [1, 5, 9, 10, 25, 99, 100, 150, 999];
t0 = performance.now();
for (let i = 0; i < iters; i++) baselineFormatSessionLabel(mixedCycles[i % mixedCycles.length]);
const baseMixed = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) PomodoroCore.formatSessionLabel(mixedCycles[i % mixedCycles.length]);
const optMixed = performance.now() - t0;

console.log('\n=== Benchmark Results (Workload: 3,000,000 iterations each) ===');
console.log(`[Workload A: Typical cycles 1-99]`);
console.log(`  Baseline (padStart):  ${baseTypical.toFixed(2)} ms (${(baseTypical / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized (PAD_TWO):  ${optTypical.toFixed(2)} ms (${(optTypical / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:              ${((baseTypical - optTypical) / baseTypical * 100).toFixed(1)}% faster (${(baseTypical / optTypical).toFixed(2)}x)`);

console.log(`\n[Workload B: Mixed cycles (1-999)]`);
console.log(`  Baseline (padStart):  ${baseMixed.toFixed(2)} ms (${(baseMixed / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized (PAD_TWO):  ${optMixed.toFixed(2)} ms (${(optMixed / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:              ${((baseMixed - optMixed) / baseMixed * 100).toFixed(1)}% faster (${(baseMixed / optMixed).toFixed(2)}x)`);