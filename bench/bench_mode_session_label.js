const { PomodoroCore } = require('../core.js');

// Baseline implementation prior to fast-path and SESSION_LABELS lookup table
const BASE_BREAK_LABELS = {
  shortBreak: 'RECHARGE // SHORT BREAK',
  longBreak: 'REST // LONG BREAK'
};

function baselineGetModeSessionLabel(mode, cycleCount) {
  if (typeof mode === 'string' && BASE_BREAK_LABELS[mode]) {
    return BASE_BREAK_LABELS[mode];
  }
  const parsed = parseInt(cycleCount, 10);
  const valid = (!isNaN(parsed) && parsed >= 1) ? parsed : 1;
  const cycleStr = valid < 100 ? (valid < 10 ? '0' + valid : String(valid)) : String(valid);
  return `SESSION ${cycleStr} // DEEP WORK`;
}

// 1. Strict Equality Verification across exhaustive matrix
const testModes = [
  'focus', 'shortBreak', 'longBreak',
  'unknown', 'custom', '', '   ',
  null, undefined, true, false, 123, {}, []
];

const testCycles = [
  1, 2, 3, 4, 8, 9, 10, 25, 50, 99, 100, 101, 250, 999,
  0, -1, -5, -100,
  1.2, 4.8, 99.9, 100.5,
  '1', '04', '9', '10', '25', '99', '100', '101', '500',
  '0', '-1', '-5', '4.8', 'invalid', '', '   ',
  null, undefined, true, false, NaN, Infinity, -Infinity,
  {}, [], [1], [100]
];

let checkedCombinations = 0;
for (const m of testModes) {
  for (const c of testCycles) {
    const base = baselineGetModeSessionLabel(m, c);
    const current = PomodoroCore.getModeSessionLabel(m, c);
    if (base !== current) {
      throw new Error(`getModeSessionLabel mismatch for mode=${JSON.stringify(m)}, cycle=${JSON.stringify(c)}: expected "${base}", got "${current}"`);
    }
    checkedCombinations++;
  }
}

// Randomized fuzz check across 50,000 cases
const sampleModes = ['focus', 'shortBreak', 'longBreak', 'other', null, undefined];
for (let i = 0; i < 50000; i++) {
  const m = sampleModes[Math.floor(Math.random() * sampleModes.length)];
  let c;
  const randType = Math.random();
  if (randType < 0.6) {
    c = Math.floor(Math.random() * 120);
  } else if (randType < 0.8) {
    c = String(Math.floor(Math.random() * 120));
  } else {
    c = [null, undefined, NaN, Infinity, -5, 3.7, 'invalid'][Math.floor(Math.random() * 7)];
  }
  const base = baselineGetModeSessionLabel(m, c);
  const current = PomodoroCore.getModeSessionLabel(m, c);
  if (base !== current) {
    throw new Error(`fuzz mismatch for mode=${m}, cycle=${c}: expected "${base}", got "${current}"`);
  }
}

console.log(`✓ Strict equality verified across ${checkedCombinations} matrix cases and 50,000 fuzz cases.`);

// 2. Performance Benchmarks
const iters = 4000000;

// Warmup
for (let i = 0; i < 50000; i++) {
  baselineGetModeSessionLabel('focus', (i % 100) + 1);
  PomodoroCore.getModeSessionLabel('focus', (i % 100) + 1);
}

// Workload 1: Focus mode session labels (standard routine numeric cycles 1..100)
let t0 = performance.now();
let accBase1 = 0;
for (let i = 0; i < iters; i++) {
  accBase1 += baselineGetModeSessionLabel('focus', (i % 100) + 1).length;
}
const baseFocusTime = performance.now() - t0;

t0 = performance.now();
let accOpt1 = 0;
for (let i = 0; i < iters; i++) {
  accOpt1 += PomodoroCore.getModeSessionLabel('focus', (i % 100) + 1).length;
}
const optFocusTime = performance.now() - t0;

if (accBase1 !== accOpt1) throw new Error('Workload 1 accumulator mismatch');

// Workload 2: Mixed mode transitions (focus, shortBreak, longBreak)
const modes = ['focus', 'shortBreak', 'longBreak'];
t0 = performance.now();
let accBase2 = 0;
for (let i = 0; i < iters; i++) {
  accBase2 += baselineGetModeSessionLabel(modes[i % 3], (i % 100) + 1).length;
}
const baseMixedTime = performance.now() - t0;

t0 = performance.now();
let accOpt2 = 0;
for (let i = 0; i < iters; i++) {
  accOpt2 += PomodoroCore.getModeSessionLabel(modes[i % 3], (i % 100) + 1).length;
}
const optMixedTime = performance.now() - t0;

if (accBase2 !== accOpt2) throw new Error('Workload 2 accumulator mismatch');

// Workload 3: Mixed types (numeric, string, boundary, fallback)
const mixedInputs = [
  ['focus', 1], ['focus', 4], ['focus', 25], ['focus', 99], ['focus', 100], ['focus', 101],
  ['shortBreak', 1], ['longBreak', 4],
  ['focus', '5'], ['focus', '08'], ['unknown', 2], [null, 3], ['focus', 0], ['focus', -2]
];
t0 = performance.now();
let accBase3 = 0;
for (let i = 0; i < iters; i++) {
  const [m, c] = mixedInputs[i % mixedInputs.length];
  accBase3 += baselineGetModeSessionLabel(m, c).length;
}
const baseBoundaryTime = performance.now() - t0;

t0 = performance.now();
let accOpt3 = 0;
for (let i = 0; i < iters; i++) {
  const [m, c] = mixedInputs[i % mixedInputs.length];
  accOpt3 += PomodoroCore.getModeSessionLabel(m, c).length;
}
const optBoundaryTime = performance.now() - t0;

if (accBase3 !== accOpt3) throw new Error('Workload 3 accumulator mismatch');

console.log(`\n=== Benchmark Results (${iters.toLocaleString()} iterations each) ===`);
console.log(`[Workload 1: Focus mode cycles 1..100]`);
console.log(`  Baseline:   ${baseFocusTime.toFixed(2)} ms (${(baseFocusTime / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized:  ${optFocusTime.toFixed(2)} ms (${(optFocusTime / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:    ${((baseFocusTime - optFocusTime) / baseFocusTime * 100).toFixed(1)}% faster (${(baseFocusTime / optFocusTime).toFixed(2)}x)`);

console.log(`\n[Workload 2: Mixed mode transitions (focus, shortBreak, longBreak)]`);
console.log(`  Baseline:   ${baseMixedTime.toFixed(2)} ms (${(baseMixedTime / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized:  ${optMixedTime.toFixed(2)} ms (${(optMixedTime / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:    ${((baseMixedTime - optMixedTime) / baseMixedTime * 100).toFixed(1)}% faster (${(baseMixedTime / optMixedTime).toFixed(2)}x)`);

console.log(`\n[Workload 3: Mixed types & boundaries]`);
console.log(`  Baseline:   ${baseBoundaryTime.toFixed(2)} ms (${(baseBoundaryTime / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized:  ${optBoundaryTime.toFixed(2)} ms (${(optBoundaryTime / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:    ${((baseBoundaryTime - optBoundaryTime) / baseBoundaryTime * 100).toFixed(1)}% faster (${(baseBoundaryTime / optBoundaryTime).toFixed(2)}x)`);
