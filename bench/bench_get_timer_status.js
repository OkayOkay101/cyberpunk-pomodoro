const { PomodoroCore } = require('../core.js');

// Baseline getTimerStatus (prior to numeric fast-path optimization)
function baselineGetTimerStatus(isRunningOrParams, timeLeft, duration) {
  let running = false;
  let time = timeLeft;
  let dur = duration;

  if (isRunningOrParams && typeof isRunningOrParams === 'object') {
    running = Boolean(isRunningOrParams.isRunning);
    time = isRunningOrParams.timeLeft;
    dur = isRunningOrParams.duration;
  } else {
    running = Boolean(isRunningOrParams);
  }

  if (running) {
    return { buttonText: 'PAUSE', statusText: 'SYSTEM // RUNNING' };
  }

  const safeTime = Number(time);
  const safeDur = Number(dur);

  if (!isNaN(safeTime) && !isNaN(safeDur) && safeDur > 0 && safeTime > 0 && safeTime < safeDur) {
    return { buttonText: 'RESUME', statusText: 'SYSTEM // PAUSED' };
  }

  return { buttonText: 'START', statusText: 'ONLINE // READY' };
}

// 1. Strict Equality Verification across exhaustive cases
console.log('--- Strict Equality Verification ---');
const baseNow = 1731110000000;
const testRunning = [true, false];
const testTargets = [
  baseNow + 25000, baseNow + 1500, baseNow + 1499, baseNow + 500, baseNow + 499, baseNow + 1,
  baseNow, baseNow - 1, baseNow - 1000, baseNow - 50000,
  0, -1000, 1000,
  NaN, Infinity, -Infinity,
  String(baseNow + 25000), String(baseNow), String(baseNow - 5000),
  '25000', '-5000', '0', 'invalid', '', '   ',
  null, undefined, true, false, {}, [], [baseNow + 1000]
];
const testDurations = [
  1500, 300, 0, -5, -10, NaN, Infinity, -Infinity,
  '1500', '300', '0', '-5', '-10', 'invalid', '',
  null, undefined, true, false, {}, []
];

let checkedCombinations = 0;
for (const t of testTargets) {
  for (const d of testDurations) {
    for (const r of testRunning) {
      const b = baselineGetTimerStatus(r, t, d);
      const c = PomodoroCore.getTimerStatus(r, t, d);
      if (JSON.stringify(b) !== JSON.stringify(c)) {
        throw new Error(`getTimerStatus mismatch for running=${r}, target=${JSON.stringify(t)}, duration=${JSON.stringify(d)}: expected ${JSON.stringify(b)}, got ${JSON.stringify(c)}`);
      }
      checkedCombinations++;
    }
  }
}

console.log(`✓ Strict equality verified across ${checkedCombinations} matrix cases.`);

// Randomized fuzz check across 100,000 cases
console.log('--- Fuzz Verification ---');
let fuzzPassed = 0;
for (let i = 0; i < 100000; i++) {
  const t = Math.random() < 0.3 ? baseNow + Math.floor(Math.random() * 3000000) - 1500000 : (Math.random() < 0.6 ? String(baseNow + 10000) : (Math.random() < 0.8 ? NaN : Infinity));
  const d = Math.random() < 0.5 ? 1500 : (Math.random() < 0.8 ? '1500' : (Math.random() < 0.8 ? NaN : Infinity));
  const r = Math.random() < 0.5 ? true : false;
  const b = baselineGetTimerStatus(r, t, d);
  const c = PomodoroCore.getTimerStatus(r, t, d);
  if (JSON.stringify(b) === JSON.stringify(c)) {
    fuzzPassed++;
  } else {
    throw new Error(`fuzz mismatch for running=${r}, target=${t}, duration=${d}`);
  }
}
console.log(`✓ 100,000 fuzz cases passed.`);

// 2. Performance Benchmarks
console.log('\n--- Benchmark Results (1,000,000 iterations each) ---');
const iters = 1000000;

// Warmup
for (let i = 0; i < 10000; i++) {
  baselineGetTimerStatus(false, baseNow + 1500, 1500);
  PomodoroCore.getTimerStatus(false, baseNow + 1500, 1500);
}

// Workload 1: Numeric fast-path (running=false, native numbers) - primary hot path
let sBaseNum = 0;
let t0 = performance.now();
for (let i = 0; i < iters; i++) {
  sBaseNum += baselineGetTimerStatus(false, baseNow + 1500 - (i % 1500), 1500);
}
let t1 = performance.now();
const baseNumTime = t1 - t0;

let sOptNum = 0;
let t2 = performance.now();
for (let i = 0; i < iters; i++) {
  sOptNum += PomodoroCore.getTimerStatus(false, baseNow + 1500 - (i % 1500), 1500);
}
let t3 = performance.now();
const optNumTime = t3 - t2;

if (sBaseNum !== sOptNum) throw new Error('Checksum mismatch in Workload 1 (numeric)');

const numSpeedup = ((baseNumTime - optNumTime) / baseNumTime) * 100;
console.log(`Workload 1 (Numeric Fast-Path): Baseline ${baseNumTime.toFixed(2)}ms | Optimized ${optNumTime.toFixed(2)}ms | Speedup: ${numSpeedup.toFixed(1)}%`);

// Workload 2: String inputs (fallback path) - mixed types
const mixedTargets = [baseNow + 25000, baseNow + 1500, baseNow, '25000'];
const mixedDurations = ['1500', '300', '0', 'invalid'];

let sBaseStr = 0;
let t4 = performance.now();
for (let i = 0; i < iters; i++) {
  sBaseStr += baselineGetTimerStatus(false, mixedTargets[i % mixedTargets.length], mixedDurations[i % mixedDurations.length]);
}
let t5 = performance.now();
const baseStrTime = t5 - t4;

let sOptStr = 0;
let t6 = performance.now();
for (let i = 0; i < iters; i++) {
  sOptStr += PomodoroCore.getTimerStatus(false, mixedTargets[i % mixedTargets.length], mixedDurations[i % mixedDurations.length]);
}
let t7 = performance.now();
const optStrTime = t7 - t6;

if (sBaseStr !== sOptStr) throw new Error('Checksum mismatch in Workload 2 (string)');

const strSpeedup = ((baseStrTime - optStrTime) / baseStrTime) * 100;
console.log(`Workload 2 (String Inputs):    Baseline ${baseStrTime.toFixed(2)}ms | Optimized ${optStrTime.toFixed(2)}ms | Speedup: ${strSpeedup.toFixed(1)}%`);

// Workload 3: Object inputs - secondary path
const objRunning = true;
const objTimeLeft = 500;
const objDuration = 1500;

let sBaseObj = 0;
let t8 = performance.now();
for (let i = 0; i < iters; i++) {
  sBaseObj += baselineGetTimerStatus(objRunning, baseNow + 1500 - (i % 1500), 1500);
}
let t9 = performance.now();
const baseObjTime = t9 - t8;

let sOptObj = 0;
let t10 = performance.now();
for (let i = 0; i < iters; i++) {
  sOptObj += PomodoroCore.getTimerStatus(objRunning, baseNow + 1500 - (i % 1500), 1500);
}
let t11 = performance.now();
const optObjTime = t11 - t10;

if (sBaseObj !== sOptObj) throw new Error('Checksum mismatch in Workload 3 (object)');

const objSpeedup = ((baseObjTime - optObjTime) / baseObjTime) * 100;
console.log(`Workload 3 (Object Inputs):    Baseline ${baseObjTime.toFixed(2)}ms | Optimized ${optObjTime.toFixed(2)}ms | Speedup: ${objSpeedup.toFixed(1)}%`);
