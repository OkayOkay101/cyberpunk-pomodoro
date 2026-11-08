const { PomodoroCore } = require('./core.js');

// Baseline implementations
function baselineValidateCustomDuration(val, min, max, defaultVal) {
  const num = parseInt(val, 10);
  if (isNaN(num) || num < min || num > max) return defaultVal;
  return num;
}

function baselineResolveDurations(inputs) {
  const raw = (inputs && typeof inputs === 'object' && !Array.isArray(inputs)) ? inputs : {};
  const f = baselineValidateCustomDuration(raw.focus, 1, 90, 25);
  const s = baselineValidateCustomDuration(raw.shortBreak, 1, 30, 5);
  const l = baselineValidateCustomDuration(raw.longBreak, 1, 60, 15);
  return {
    focus: f * 60,
    shortBreak: s * 60,
    longBreak: l * 60,
    minutes: { focus: f, shortBreak: s, longBreak: l },
    storage: {
      cp_cfg_focus: String(f),
      cp_cfg_short: String(s),
      cp_cfg_long: String(l)
    }
  };
}

// Module-level lookup table for numbers 0..100
const NUM_STRINGS = Array.from({ length: 101 }, (_, i) => String(i));

function optValidateCustomDuration(val, min, max, defaultVal) {
  if (val === undefined || val === null) return defaultVal;
  const num = parseInt(val, 10);
  if (isNaN(num) || num < min || num > max) return defaultVal;
  return num;
}

function optResolveDurations(inputs) {
  if (!inputs || typeof inputs !== 'object' || Array.isArray(inputs)) {
    return {
      focus: 1500,
      shortBreak: 300,
      longBreak: 900,
      minutes: { focus: 25, shortBreak: 5, longBreak: 15 },
      storage: {
        cp_cfg_focus: '25',
        cp_cfg_short: '5',
        cp_cfg_long: '15'
      }
    };
  }
  const f = optValidateCustomDuration(inputs.focus, 1, 90, 25);
  const s = optValidateCustomDuration(inputs.shortBreak, 1, 30, 5);
  const l = optValidateCustomDuration(inputs.longBreak, 1, 60, 15);
  return {
    focus: f * 60,
    shortBreak: s * 60,
    longBreak: l * 60,
    minutes: { focus: f, shortBreak: s, longBreak: l },
    storage: {
      cp_cfg_focus: NUM_STRINGS[f],
      cp_cfg_short: NUM_STRINGS[s],
      cp_cfg_long: NUM_STRINGS[l]
    }
  };
}

// 1. Strict Equality Verification across varied inputs
const samples = [
  undefined,
  null,
  {},
  [],
  [1, 2, 3],
  'string-input',
  12345,
  { focus: 25, shortBreak: 5, longBreak: 15 },
  { focus: '25', shortBreak: '5', longBreak: '15' },
  { focus: 50, shortBreak: 10, longBreak: 25 },
  { focus: '50', shortBreak: '10', longBreak: '25' },
  { focus: 1, shortBreak: 1, longBreak: 1 },
  { focus: 90, shortBreak: 30, longBreak: 60 },
  { focus: 120, shortBreak: 0, longBreak: -5 },
  { focus: -10, shortBreak: 50, longBreak: 100 },
  { focus: NaN, shortBreak: Infinity, longBreak: -Infinity },
  { focus: 'abc', shortBreak: null, longBreak: undefined },
  { focus: '45min', shortBreak: '8min', longBreak: '20min' },
  { focus: 25.9, shortBreak: 5.2, longBreak: 15.8 },
  { otherKey: 99 }
];

for (const s of samples) {
  const base = baselineResolveDurations(s);
  const opt = optResolveDurations(s);
  if (JSON.stringify(base) !== JSON.stringify(opt)) {
    throw new Error(`Output mismatch on ${JSON.stringify(s)}: base=${JSON.stringify(base)}, opt=${JSON.stringify(opt)}`);
  }
}
console.log('✓ Equality verification: baseline and optResolveDurations match 100% across all test cases.');

// 2. Performance Benchmark
const iters = 2000000;

// Warmup
for (let i = 0; i < 50000; i++) {
  baselineResolveDurations();
  optResolveDurations();
}

// Workload A: Default no-args (typical app initialization)
let t0 = performance.now();
for (let i = 0; i < iters; i++) baselineResolveDurations();
const baseNoArgs = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) optResolveDurations();
const optNoArgs = performance.now() - t0;

// Workload B: String durations from localStorage (cp_cfg_focus, etc.)
const storageObj = { focus: '25', shortBreak: '5', longBreak: '15' };
t0 = performance.now();
for (let i = 0; i < iters; i++) baselineResolveDurations(storageObj);
const baseStorage = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) optResolveDurations(storageObj);
const optStorage = performance.now() - t0;

// Workload C: Custom numeric durations
const customNumObj = { focus: 50, shortBreak: 10, longBreak: 25 };
t0 = performance.now();
for (let i = 0; i < iters; i++) baselineResolveDurations(customNumObj);
const baseCustom = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) optResolveDurations(customNumObj);
const optCustom = performance.now() - t0;

// Workload D: Mixed inputs (defaults, strings, numbers, invalid)
const mixedWorkload = [
  undefined,
  { focus: '25', shortBreak: '5', longBreak: '15' },
  { focus: 50, shortBreak: 10, longBreak: 20 },
  { focus: '45', shortBreak: '8', longBreak: '20' },
  {},
  { focus: 120, shortBreak: 0, longBreak: -5 }
];
t0 = performance.now();
for (let i = 0; i < iters; i++) baselineResolveDurations(mixedWorkload[i % mixedWorkload.length]);
const baseMixed = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) optResolveDurations(mixedWorkload[i % mixedWorkload.length]);
const optMixed = performance.now() - t0;

console.log(`\n=== Benchmark Results (Workload: ${iters.toLocaleString()} iterations each) ===`);
console.log(`[Workload A: Default no-args]`);
console.log(`  Baseline:  ${baseNoArgs.toFixed(2)} ms (${(baseNoArgs / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized: ${optNoArgs.toFixed(2)} ms (${(optNoArgs / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:   ${((baseNoArgs - optNoArgs) / baseNoArgs * 100).toFixed(1)}% faster (${(baseNoArgs / optNoArgs).toFixed(2)}x)`);

console.log(`\n[Workload B: String durations from localStorage]`);
console.log(`  Baseline:  ${baseStorage.toFixed(2)} ms (${(baseStorage / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized: ${optStorage.toFixed(2)} ms (${(optStorage / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:   ${((baseStorage - optStorage) / baseStorage * 100).toFixed(1)}% faster (${(baseStorage / optStorage).toFixed(2)}x)`);

console.log(`\n[Workload C: Custom numeric durations]`);
console.log(`  Baseline:  ${baseCustom.toFixed(2)} ms (${(baseCustom / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized: ${optCustom.toFixed(2)} ms (${(optCustom / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:   ${((baseCustom - optCustom) / baseCustom * 100).toFixed(1)}% faster (${(baseCustom / optCustom).toFixed(2)}x)`);

console.log(`\n[Workload D: Mixed inputs (defaults, strings, numbers, invalid)]`);
console.log(`  Baseline:  ${baseMixed.toFixed(2)} ms (${(baseMixed / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized: ${optMixed.toFixed(2)} ms (${(optMixed / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:   ${((baseMixed - optMixed) / baseMixed * 100).toFixed(1)}% faster (${(baseMixed / optMixed).toFixed(2)}x)`);
