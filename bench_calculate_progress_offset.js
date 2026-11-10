const { PomodoroCore } = require('./core.js');

// Baseline implementation: pre-optimization logic (no numeric fast-path,
// unconditional isNaN/isFinite checks and Math.max/Math.min calls).
function baselineCalculateProgressOffset(timeLeft, duration, circumference) {
  if (!duration || duration <= 0 || isNaN(duration) || !isFinite(duration)) return 0;
  if (isNaN(circumference) || circumference <= 0 || !isFinite(circumference)) return 0;
  const safeTime = isNaN(timeLeft) ? 0 : timeLeft;
  const clamped = Math.max(0, Math.min(safeTime, duration));
  return circumference - (clamped / duration) * circumference;
}

// 1. Strict Equality Verification across exhaustive cases
const C = 691.15;
const testCases = [
  [1500, 1500, C], [0, 1500, C], [750, 1500, C], [300, 1500, C], [1499, 1500, C],
  [1, 1500, C], [1500, 1, C], [100, 100, C],
  [0, 0, C], [100, 0, C], [100, -5, C],
  [100, 100, 0], [100, 100, -1],
  [NaN, 1500, C], [1500, NaN, C], [NaN, NaN, C],
  [Infinity, 1500, C], [1500, Infinity, C], [-Infinity, 1500, C],
  [100, 1500, Infinity], [100, 1500, -Infinity],
  [100, '1500', C], ['750', 1500, C], ['invalid', 1500, C],
  [100, null, C], [100, undefined, C], [null, 1500, C],
  [100, 1500, null], [100, 1500, undefined], [100, 1500, 'invalid']
];

for (const [t, d, c] of testCases) {
  const base = baselineCalculateProgressOffset(t, d, c);
  const opt = PomodoroCore.calculateProgressOffset(t, d, c);
  if (base !== opt) {
    throw new Error(`MISMATCH t=${JSON.stringify(t)} d=${JSON.stringify(d)} c=${JSON.stringify(c)}: base=${base}, opt=${opt}`);
  }
}
console.log('✓ Equality verification: baseline and optimized output match exactly.');

// 2. Performance Benchmark
const iters = 3000000;

// Warmup
for (let i = 0; i < 50000; i++) {
  baselineCalculateProgressOffset(750, 1500, C);
  PomodoroCore.calculateProgressOffset(750, 1500, C);
}

// Workload A: Active countdown tick (typical 0 < timeLeft < duration, all numeric)
const ticks = Array.from({ length: 1501 }, (_, i) => i);

let t0 = performance.now();
for (let i = 0; i < iters; i++) {
  baselineCalculateProgressOffset(ticks[i % 1501], 1500, C);
}
const baseActive = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) {
  PomodoroCore.calculateProgressOffset(ticks[i % 1501], 1500, C);
}
const optActive = performance.now() - t0;

// Workload B: Boundary and expired ticks (timeLeft >= duration or <= 0)
const boundaryTicks = [0, 1, 750, 1500, 1501, 3000, -100];

t0 = performance.now();
for (let i = 0; i < iters; i++) {
  const v = boundaryTicks[i % boundaryTicks.length];
  baselineCalculateProgressOffset(v, 1500, C);
}
const baseBoundary = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) {
  const v = boundaryTicks[i % boundaryTicks.length];
  PomodoroCore.calculateProgressOffset(v, 1500, C);
}
const optBoundary = performance.now() - t0;

// Workload C: Mixed invalid / non-numeric inputs
const mixedInputs = [
  [NaN, 1500, C], [1500, NaN, C], [NaN, NaN, C],
  [Infinity, 1500, C], [100, 1500, Infinity],
  ['invalid', 1500, C], [100, null, C], [100, 1500, undefined]
];

t0 = performance.now();
for (let i = 0; i < iters; i++) {
  const [t, d, c] = mixedInputs[i % mixedInputs.length];
  baselineCalculateProgressOffset(t, d, c);
}
const baseMixed = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) {
  const [t, d, c] = mixedInputs[i % mixedInputs.length];
  PomodoroCore.calculateProgressOffset(t, d, c);
}
const optMixed = performance.now() - t0;

function pct(a, b) { return ((a - b) / a * 100).toFixed(1); }
function x(a, b) { return (a / b).toFixed(2); }

console.log(`\n=== Benchmark Results (Workload: ${iters.toLocaleString()} iterations each) ===`);
console.log('[Workload A: Active countdown tick (0 < timeLeft < duration, numeric)]');
console.log(`  Baseline:  ${baseActive.toFixed(2)} ms (${(baseActive / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized: ${optActive.toFixed(2)} ms (${(optActive / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:   ${pct(baseActive, optActive)}% faster (${x(baseActive, optActive)}x)`);

console.log('\n[Workload B: Boundary / expired ticks]');
console.log(`  Baseline:  ${baseBoundary.toFixed(2)} ms (${(baseBoundary / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized: ${optBoundary.toFixed(2)} ms (${(optBoundary / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:   ${pct(baseBoundary, optBoundary)}% faster (${x(baseBoundary, optBoundary)}x)`);

console.log('\n[Workload C: Mixed invalid / non-numeric inputs]');
console.log(`  Baseline:  ${baseMixed.toFixed(2)} ms (${(baseMixed / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized: ${optMixed.toFixed(2)} ms (${(optMixed / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:   ${pct(baseMixed, optMixed)}% faster (${x(baseMixed, optMixed)}x)`);
