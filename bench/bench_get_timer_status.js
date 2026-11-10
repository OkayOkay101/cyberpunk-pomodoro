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

// Map a status result to a small integer code so checksums are numeric and
// do not depend on string concatenation of objects.
function statusCode(status) {
  switch (status.buttonText) {
    case 'PAUSE': return 1;
    case 'RESUME': return 2;
    case 'START': return 3;
    default: throw new Error(`unexpected buttonText: ${status.buttonText}`);
  }
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

// Object-parameter form must also match baseline.
for (const isRunning of testRunning) {
  for (const t of testTargets) {
    for (const d of testDurations) {
      const params = { isRunning, timeLeft: t, duration: d };
      const b = baselineGetTimerStatus(params);
      const c = PomodoroCore.getTimerStatus(params);
      if (JSON.stringify(b) !== JSON.stringify(c)) {
        throw new Error(`object-form mismatch for ${JSON.stringify(params)}: expected ${JSON.stringify(b)}, got ${JSON.stringify(c)}`);
      }
    }
  }
}
console.log('✓ Object-parameter form matches baseline.');

// Randomized fuzz check across 100,000 cases
console.log('--- Fuzz Verification ---');
for (let i = 0; i < 100000; i++) {
  const t = Math.random() < 0.3 ? baseNow + Math.floor(Math.random() * 3000000) - 1500000 : (Math.random() < 0.6 ? String(baseNow + 10000) : (Math.random() < 0.8 ? NaN : Infinity));
  const d = Math.random() < 0.5 ? 1500 : (Math.random() < 0.8 ? '1500' : (Math.random() < 0.8 ? NaN : Infinity));
  const r = Math.random() < 0.5 ? true : false;
  const b = baselineGetTimerStatus(r, t, d);
  const c = PomodoroCore.getTimerStatus(r, t, d);
  if (JSON.stringify(b) !== JSON.stringify(c)) {
    throw new Error(`fuzz mismatch for running=${r}, target=${t}, duration=${d}`);
  }
}
console.log('✓ 100,000 fuzz cases passed.');

// 2. Performance benchmarks (checksums are numeric status codes)
console.log('\n--- Benchmark Results (1,000,000 iterations each) ---');
const iters = 1000000;

function runWorkload(label, fn) {
  // Warmup
  let warm = 0;
  for (let i = 0; i < 10000; i++) warm += statusCode(fn(i));

  const t0 = performance.now();
  let sum = 0;
  for (let i = 0; i < iters; i++) sum += statusCode(fn(i));
  return { label, ms: performance.now() - t0, sum };
}

function compare(name, baseFn, optFn) {
  const base = runWorkload(`${name} baseline`, baseFn);
  const opt = runWorkload(`${name} optimized`, optFn);
  if (base.sum !== opt.sum) {
    throw new Error(`Checksum mismatch in ${name}: baseline=${base.sum}, optimized=${opt.sum}`);
  }
  const speedup = ((base.ms - opt.ms) / base.ms) * 100;
  console.log(`${name}: Baseline ${base.ms.toFixed(2)}ms | Optimized ${opt.ms.toFixed(2)}ms | Speedup: ${speedup.toFixed(1)}% (checksum ${base.sum})`);
}

// Workload 1: native numbers, times spread across 1..duration so both PAUSED and READY branches run.
const numDur = 1500;
compare(
  'Workload 1 (native numbers, mixed PAUSED/READY)',
  (i) => baselineGetTimerStatus(false, (i % numDur) + 1, numDur),
  (i) => PomodoroCore.getTimerStatus(false, (i % numDur) + 1, numDur),
);

// Workload 2: string inputs (fallback path), mixed types.
const mixedTargets = [String(baseNow + 25000), String(900), '0', '25000'];
const mixedDurations = ['1500', '300', '0', 'invalid'];
compare(
  'Workload 2 (string inputs)',
  (i) => baselineGetTimerStatus(false, mixedTargets[i % 4], mixedDurations[i % 4]),
  (i) => PomodoroCore.getTimerStatus(false, mixedTargets[i % 4], mixedDurations[i % 4]),
);

// Workload 3: object-parameter form (true object input), mixed running/paused/ready.
compare(
  'Workload 3 (object inputs)',
  (i) => baselineGetTimerStatus({ isRunning: i % 3 === 0, timeLeft: (i % numDur) + 1, duration: numDur }),
  (i) => PomodoroCore.getTimerStatus({ isRunning: i % 3 === 0, timeLeft: (i % numDur) + 1, duration: numDur }),
);
