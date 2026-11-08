const { PomodoroCore } = require('../core.js');

// Baseline implementation prior to fast-path and pre-computed lookup tables
const baseline = {
  calculateSkipTransition(modeOrParams, cycleCount) {
    let mode = modeOrParams;
    let cycle = cycleCount;

    if (modeOrParams && typeof modeOrParams === 'object') {
      mode = modeOrParams.currentMode || modeOrParams.mode;
      cycle = modeOrParams.cycleCount;
    }

    const safeCycle = PomodoroCore.parseCycleCount(cycle);

    if (mode === 'focus') {
      const nextMode = PomodoroCore.getNextMode('focus', safeCycle);
      const toastMessage = PomodoroCore.getModeToastMessage(nextMode);
      return {
        nextMode,
        toastMessage,
        cycleCount: safeCycle
      };
    }

    return {
      nextMode: 'focus',
      toastMessage: 'FOCUS MODE',
      cycleCount: safeCycle
    };
  }
};

// 1. Strict Equality Verification across exhaustive cases
const testModes = [
  'focus', 'shortBreak', 'longBreak', 'unknown',
  '', '   ', null, undefined, NaN, Infinity, -Infinity, 0, 1, {}, [], true, false
];

const testCycles = [
  1, 2, 3, 4, 7, 8, 10, 50, 100, 101, 250,
  0, -1, -4, -10,
  0.5, 1.2, 3.9, 4.5, 99.9, 100.1, -0.5,
  '1', '4', '08', '100', '101', '0', '-5', '2.5', '99.9',
  '1 session', '4sessions', '004', ' 10 ',
  null, undefined, NaN, Infinity, -Infinity,
  '', '   ', 'corrupted', {}, [], [4], true, false
];

let checkedCombinations = 0;
for (const m of testModes) {
  for (const c of testCycles) {
    const base = baseline.calculateSkipTransition(m, c);
    const opt = PomodoroCore.calculateSkipTransition(m, c);
    if (base.nextMode !== opt.nextMode || base.toastMessage !== opt.toastMessage || base.cycleCount !== opt.cycleCount) {
      throw new Error(`mismatch for mode=${JSON.stringify(m)}, cycle=${JSON.stringify(c)}: expected ${JSON.stringify(base)}, got ${JSON.stringify(opt)}`);
    }
    checkedCombinations++;
  }
}

// Verify object parameter equality
for (const m of ['focus', 'shortBreak', 'longBreak', 'invalid', null, undefined]) {
  for (const c of [1, 2, 4, 8, 100, 105, 0, -1, '4', 'corrupt', NaN]) {
    const base1 = baseline.calculateSkipTransition({ currentMode: m, cycleCount: c });
    const opt1 = PomodoroCore.calculateSkipTransition({ currentMode: m, cycleCount: c });
    if (base1.nextMode !== opt1.nextMode || base1.toastMessage !== opt1.toastMessage || base1.cycleCount !== opt1.cycleCount) {
      throw new Error(`mismatch for currentMode=${JSON.stringify(m)}, cycle=${JSON.stringify(c)}`);
    }

    const base2 = baseline.calculateSkipTransition({ mode: m, cycleCount: c });
    const opt2 = PomodoroCore.calculateSkipTransition({ mode: m, cycleCount: c });
    if (base2.nextMode !== opt2.nextMode || base2.toastMessage !== opt2.toastMessage || base2.cycleCount !== opt2.cycleCount) {
      throw new Error(`mismatch for mode=${JSON.stringify(m)}, cycle=${JSON.stringify(c)}`);
    }
    checkedCombinations += 2;
  }
}

console.log(`✓ Strict equality verified across ${checkedCombinations} matrix cases.`);

// 2. Performance Benchmarks
const iters = 5000000;

// Warmup
for (let i = 0; i < 50000; i++) {
  baseline.calculateSkipTransition('focus', 1);
  baseline.calculateSkipTransition('focus', 4);
  baseline.calculateSkipTransition('shortBreak', 2);
  PomodoroCore.calculateSkipTransition('focus', 1);
  PomodoroCore.calculateSkipTransition('focus', 4);
  PomodoroCore.calculateSkipTransition('shortBreak', 2);
}

// Workload 1: Routine Positional Skips (cycling focus and break across cycles 1..100)
let sBasePos = 0;
let t0 = performance.now();
for (let i = 0; i < iters; i++) {
  const cycle = (i % 100) + 1;
  const mode = (i & 1) === 0 ? 'focus' : 'shortBreak';
  const res = baseline.calculateSkipTransition(mode, cycle);
  sBasePos += res.nextMode.length + res.toastMessage.length + res.cycleCount;
}
let t1 = performance.now();
const basePosTime = t1 - t0;

let sOptPos = 0;
let t2 = performance.now();
for (let i = 0; i < iters; i++) {
  const cycle = (i % 100) + 1;
  const mode = (i & 1) === 0 ? 'focus' : 'shortBreak';
  const res = PomodoroCore.calculateSkipTransition(mode, cycle);
  sOptPos += res.nextMode.length + res.toastMessage.length + res.cycleCount;
}
let t3 = performance.now();
const optPosTime = t3 - t2;

if (sBasePos !== sOptPos) throw new Error('Checksum mismatch in Workload 1');

// Workload 2: Focus Mode Skips (simulating skips at session boundaries including cycle 4 long breaks)
let sBaseFocus = 0;
let t4 = performance.now();
for (let i = 0; i < iters; i++) {
  const cycle = (i % 100) + 1;
  const res = baseline.calculateSkipTransition('focus', cycle);
  sBaseFocus += res.nextMode.length + res.toastMessage.length + res.cycleCount;
}
let t5 = performance.now();
const baseFocusTime = t5 - t4;

let sOptFocus = 0;
let t6 = performance.now();
for (let i = 0; i < iters; i++) {
  const cycle = (i % 100) + 1;
  const res = PomodoroCore.calculateSkipTransition('focus', cycle);
  sOptFocus += res.nextMode.length + res.toastMessage.length + res.cycleCount;
}
let t7 = performance.now();
const optFocusTime = t7 - t6;

if (sBaseFocus !== sOptFocus) throw new Error('Checksum mismatch in Workload 2');

// Workload 3: Object-parameter Invocations ({ currentMode, cycleCount })
const objCases = [
  { currentMode: 'focus', cycleCount: 1 },
  { currentMode: 'focus', cycleCount: 4 },
  { currentMode: 'shortBreak', cycleCount: 2 },
  { currentMode: 'longBreak', cycleCount: 8 }
];

let sBaseObj = 0;
let t8 = performance.now();
for (let i = 0; i < iters; i++) {
  const res = baseline.calculateSkipTransition(objCases[i & 3]);
  sBaseObj += res.nextMode.length + res.toastMessage.length + res.cycleCount;
}
let t9 = performance.now();
const baseObjTime = t9 - t8;

let sOptObj = 0;
let t10 = performance.now();
for (let i = 0; i < iters; i++) {
  const res = PomodoroCore.calculateSkipTransition(objCases[i & 3]);
  sOptObj += res.nextMode.length + res.toastMessage.length + res.cycleCount;
}
let t11 = performance.now();
const optObjTime = t11 - t10;

if (sBaseObj !== sOptObj) throw new Error('Checksum mismatch in Workload 3');

const posSpeedup = ((basePosTime - optPosTime) / basePosTime) * 100;
const focusSpeedup = ((baseFocusTime - optFocusTime) / baseFocusTime) * 100;
const objSpeedup = ((baseObjTime - optObjTime) / baseObjTime) * 100;

console.log('\n--- Benchmark Results (5,000,000 iterations each) ---');
console.log(`Workload 1 (Routine Positional Skips): Baseline ${basePosTime.toFixed(2)}ms | Optimized ${optPosTime.toFixed(2)}ms | Speedup: ${posSpeedup.toFixed(1)}%`);
console.log(`Workload 2 (Focus Mode Skips):        Baseline ${baseFocusTime.toFixed(2)}ms | Optimized ${optFocusTime.toFixed(2)}ms | Speedup: ${focusSpeedup.toFixed(1)}%`);
console.log(`Workload 3 (Object-param Skips):       Baseline ${baseObjTime.toFixed(2)}ms | Optimized ${optObjTime.toFixed(2)}ms | Speedup: ${objSpeedup.toFixed(1)}%`);
