const { PomodoroCore } = require('../core.js');

// Baseline implementation (prior to early key check, switch dispatch, and numeric fast-path)
function baselineGetNextTabIndex(currentIndex, totalTabs, key) {
  const total = parseInt(totalTabs, 10);
  const curr = parseInt(currentIndex, 10);
  if (isNaN(total) || total <= 0 || isNaN(curr) || curr < 0 || curr >= total) return -1;
  if (key === 'ArrowRight' || key === 'ArrowDown') return (curr + 1) % total;
  if (key === 'ArrowLeft' || key === 'ArrowUp') return (curr - 1 + total) % total;
  if (key === 'Home') return 0;
  if (key === 'End') return total - 1;
  return -1;
}

// 1. Strict Equality Verification across exhaustive cases
const testKeys = [
  'ArrowRight', 'ArrowDown', 'ArrowLeft', 'ArrowUp', 'Home', 'End',
  'Tab', 'Enter', 'Space', 'Escape', 'ArrowRight ', 'arrowright',
  '', '   ', null, undefined, NaN, Infinity, -Infinity, 0, 1, {}, [], true, false
];

const testIndices = [
  0, 1, 2, 3, -1, -5, 10,
  0.0, 0.5, 1.2, 2.9, -0.5, -1.2,
  '0', '1', '2', '3', '-1', ' 1 ', '002', '1.5', '-0.5',
  'abc', '', null, undefined, NaN, Infinity, -Infinity, {}, [], true, false
];

const testTotals = [
  0, 1, 2, 3, 5, 10, -1, -3,
  1.0, 2.5, 3.9, -1.5, -0.5,
  '1', '2', '3', '0', '-1', ' 3 ', '003', '3.5',
  'abc', '', null, undefined, NaN, Infinity, -Infinity, {}, [], true, false
];

let checkedComparisons = 0;
for (const k of testKeys) {
  for (const c of testIndices) {
    for (const t of testTotals) {
      const base = baselineGetNextTabIndex(c, t, k);
      const opt = PomodoroCore.getNextTabIndex(c, t, k);
      checkedComparisons++;
      if (base !== opt) {
        throw new Error(`mismatch for currentIndex=${JSON.stringify(c)}, totalTabs=${JSON.stringify(t)}, key=${JSON.stringify(k)}: expected ${base}, got ${opt}`);
      }
    }
  }
}
console.log(`✓ Strict equality verified across ${checkedComparisons} test cases.`);

// 2. Performance Benchmark
const iters = 5000000;

// Warmup
for (let i = 0; i < 50000; i++) {
  baselineGetNextTabIndex(1, 3, 'ArrowRight');
  PomodoroCore.getNextTabIndex(1, 3, 'ArrowRight');
}

// Workload 1: Sequential Arrow Navigation (ArrowRight / ArrowLeft)
let baseChecksum1 = 0;
let t0 = performance.now();
for (let i = 0; i < iters; i++) {
  baseChecksum1 += baselineGetNextTabIndex(i % 3, 3, (i & 1) === 0 ? 'ArrowRight' : 'ArrowLeft');
}
let t1 = performance.now();
const baseArrows = t1 - t0;

let optChecksum1 = 0;
t0 = performance.now();
for (let i = 0; i < iters; i++) {
  optChecksum1 += PomodoroCore.getNextTabIndex(i % 3, 3, (i & 1) === 0 ? 'ArrowRight' : 'ArrowLeft');
}
t1 = performance.now();
const optArrows = t1 - t0;
if (baseChecksum1 !== optChecksum1) throw new Error(`Checksum mismatch Workload 1: baseline=${baseChecksum1}, opt=${optChecksum1}`);

// Workload 2: ArrowRight (Frequent next-tab cycling)
let baseChecksum2 = 0;
t0 = performance.now();
for (let i = 0; i < iters; i++) {
  baseChecksum2 += baselineGetNextTabIndex(i % 3, 3, 'ArrowRight');
}
t1 = performance.now();
const baseRight = t1 - t0;

let optChecksum2 = 0;
t0 = performance.now();
for (let i = 0; i < iters; i++) {
  optChecksum2 += PomodoroCore.getNextTabIndex(i % 3, 3, 'ArrowRight');
}
t1 = performance.now();
const optRight = t1 - t0;
if (baseChecksum2 !== optChecksum2) throw new Error(`Checksum mismatch Workload 2: baseline=${baseChecksum2}, opt=${optChecksum2}`);

// Workload 3: Home / End (Direct jump to boundary tabs)
let baseChecksum3 = 0;
t0 = performance.now();
for (let i = 0; i < iters; i++) {
  baseChecksum3 += baselineGetNextTabIndex(i % 3, 3, (i & 1) === 0 ? 'Home' : 'End');
}
t1 = performance.now();
const baseBoundary = t1 - t0;

let optChecksum3 = 0;
t0 = performance.now();
for (let i = 0; i < iters; i++) {
  optChecksum3 += PomodoroCore.getNextTabIndex(i % 3, 3, (i & 1) === 0 ? 'Home' : 'End');
}
t1 = performance.now();
const optBoundary = t1 - t0;
if (baseChecksum3 !== optChecksum3) throw new Error(`Checksum mismatch Workload 3: baseline=${baseChecksum3}, opt=${optChecksum3}`);

// Workload 4: Unhandled UI Key Events (e.g. Tab traversal bypass)
let baseChecksum4 = 0;
t0 = performance.now();
for (let i = 0; i < iters; i++) {
  baseChecksum4 += baselineGetNextTabIndex(i % 3, 3, 'Tab');
}
t1 = performance.now();
const baseUnhandled = t1 - t0;

let optChecksum4 = 0;
t0 = performance.now();
for (let i = 0; i < iters; i++) {
  optChecksum4 += PomodoroCore.getNextTabIndex(i % 3, 3, 'Tab');
}
t1 = performance.now();
const optUnhandled = t1 - t0;
if (baseChecksum4 !== optChecksum4) throw new Error(`Checksum mismatch Workload 4: baseline=${baseChecksum4}, opt=${optChecksum4}`);

console.log('\n--- Benchmark Results (5,000,000 iterations) ---');
console.log(`Workload 1 (Arrow Nav):     Baseline: ${baseArrows.toFixed(2)}ms | Opt: ${optArrows.toFixed(2)}ms | Speedup: ${(((baseArrows - optArrows) / baseArrows) * 100).toFixed(1)}%`);
console.log(`Workload 2 (ArrowRight):    Baseline: ${baseRight.toFixed(2)}ms | Opt: ${optRight.toFixed(2)}ms | Speedup: ${(((baseRight - optRight) / baseRight) * 100).toFixed(1)}%`);
console.log(`Workload 3 (Home/End):      Baseline: ${baseBoundary.toFixed(2)}ms | Opt: ${optBoundary.toFixed(2)}ms | Speedup: ${(((baseBoundary - optBoundary) / baseBoundary) * 100).toFixed(1)}%`);
console.log(`Workload 4 (Unhandled Tab): Baseline: ${baseUnhandled.toFixed(2)}ms | Opt: ${optUnhandled.toFixed(2)}ms | Speedup: ${(((baseUnhandled - optUnhandled) / baseUnhandled) * 100).toFixed(1)}%`);
