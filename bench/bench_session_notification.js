const { PomodoroCore } = require('../core.js');

// Baseline implementations prior to fast-path and lookup table optimization
const BASE_BREAK_NOTIFICATION = Object.freeze({
  title: 'BREAK FINISHED // BACK TO MATRIX',
  body: 'หมดเวลาพักแล้ว พร้อมกลับมาลุยภารกิจต่อหรือยัง?',
  soundType: 'break_end'
});

const baseline = {
  parseCycleCount(cycleCount) {
    const parsed = parseInt(cycleCount, 10);
    return (!isNaN(parsed) && parsed >= 1) ? parsed : 1;
  },
  getSessionNotification(modeOrParams, cycleCount) {
    let mode = modeOrParams;
    let cycle = cycleCount;

    if (modeOrParams && typeof modeOrParams === 'object') {
      mode = modeOrParams.mode;
      cycle = modeOrParams.cycleCount;
    }

    if (mode === 'focus') {
      const validCycle = baseline.parseCycleCount(cycle);
      return {
        title: 'FOCUS COMPLETE // CYBERPUNK POMODORO',
        body: `จบ Session ${validCycle} เรียบร้อยแล้ว ได้เวลาพักผ่อน!`,
        soundType: 'focus_end'
      };
    }

    return BASE_BREAK_NOTIFICATION;
  }
};

// 1. Strict Equality Verification across exhaustive cases
const testModes = [
  'focus', 'shortBreak', 'longBreak', 'unknown',
  '', '   ', null, undefined, NaN, Infinity, -Infinity, 0, 1, {}, [], true, false
];

const testCycles = [
  1, 2, 3, 4, 10, 50, 100, 101, 250,
  0, -1, -10,
  0.5, 1.2, 3.9, 4.5, 99.9, 100.1, -0.5,
  '1', '4', '08', '100', '101', '0', '-5', '2.5', '99.9',
  '1 session', '4sessions', '004', ' 10 ',
  null, undefined, NaN, Infinity, -Infinity,
  '', '   ', 'corrupted', {}, [], [4], true, false
];

for (const m of testModes) {
  for (const c of testCycles) {
    const base = baseline.getSessionNotification(m, c);
    const opt = PomodoroCore.getSessionNotification(m, c);
    if (base.title !== opt.title || base.body !== opt.body || base.soundType !== opt.soundType) {
      throw new Error(`mismatch for mode=${JSON.stringify(m)}, cycle=${JSON.stringify(c)}: expected ${JSON.stringify(base)}, got ${JSON.stringify(opt)}`);
    }

    const baseParse = baseline.parseCycleCount(c);
    const optParse = PomodoroCore.parseCycleCount(c);
    if (baseParse !== optParse) {
      throw new Error(`parseCycleCount mismatch for ${JSON.stringify(c)}: expected ${baseParse}, got ${optParse}`);
    }
  }
}

// Verify object parameter equality
for (const m of ['focus', 'shortBreak', 'longBreak', 'unknown', null]) {
  for (const c of [1, 2, 4, 10, 100, 101, '5', 'corrupted', null]) {
    const base = baseline.getSessionNotification({ mode: m, cycleCount: c });
    const opt = PomodoroCore.getSessionNotification({ mode: m, cycleCount: c });
    if (base.title !== opt.title || base.body !== opt.body || base.soundType !== opt.soundType) {
      throw new Error(`mismatch for object arg {mode: ${m}, cycleCount: ${c}}`);
    }
  }
}

console.log('✓ Strict equality verified across all combinations and object parameters.');

// 2. Performance Benchmark
const iters = 2000000;

// Warmup
for (let i = 0; i < 50000; i++) {
  baseline.getSessionNotification('focus', 4);
  PomodoroCore.getSessionNotification('focus', 4);
}

// Workload 1: Focus Notification with Numeric Cycles (1..8)
let sBaseFocus = 0;
let t0 = performance.now();
for (let i = 0; i < iters; i++) {
  const notif = baseline.getSessionNotification('focus', (i % 8) + 1);
  sBaseFocus += notif.title.length + notif.body.length;
}
let t1 = performance.now();
const baseFocus = t1 - t0;

let sOptFocus = 0;
t0 = performance.now();
for (let i = 0; i < iters; i++) {
  const notif = PomodoroCore.getSessionNotification('focus', (i % 8) + 1);
  sOptFocus += notif.title.length + notif.body.length;
}
t1 = performance.now();
const optFocus = t1 - t0;

if (sBaseFocus !== sOptFocus) throw new Error('Workload 1 checksum mismatch');

// Workload 2: Routine Pomodoro Cycle (Unrolled 8-stage focus & breaks)
let sBaseCycle = 0;
t0 = performance.now();
for (let i = 0; i < iters / 8; i++) {
  let n = baseline.getSessionNotification('focus', 1); sBaseCycle += n.title.length + n.body.length;
  n = baseline.getSessionNotification('shortBreak', 1); sBaseCycle += n.title.length + n.body.length;
  n = baseline.getSessionNotification('focus', 2); sBaseCycle += n.title.length + n.body.length;
  n = baseline.getSessionNotification('shortBreak', 2); sBaseCycle += n.title.length + n.body.length;
  n = baseline.getSessionNotification('focus', 3); sBaseCycle += n.title.length + n.body.length;
  n = baseline.getSessionNotification('shortBreak', 3); sBaseCycle += n.title.length + n.body.length;
  n = baseline.getSessionNotification('focus', 4); sBaseCycle += n.title.length + n.body.length;
  n = baseline.getSessionNotification('longBreak', 4); sBaseCycle += n.title.length + n.body.length;
}
t1 = performance.now();
const baseCycle = t1 - t0;

let sOptCycle = 0;
t0 = performance.now();
for (let i = 0; i < iters / 8; i++) {
  let n = PomodoroCore.getSessionNotification('focus', 1); sOptCycle += n.title.length + n.body.length;
  n = PomodoroCore.getSessionNotification('shortBreak', 1); sOptCycle += n.title.length + n.body.length;
  n = PomodoroCore.getSessionNotification('focus', 2); sOptCycle += n.title.length + n.body.length;
  n = PomodoroCore.getSessionNotification('shortBreak', 2); sOptCycle += n.title.length + n.body.length;
  n = PomodoroCore.getSessionNotification('focus', 3); sOptCycle += n.title.length + n.body.length;
  n = PomodoroCore.getSessionNotification('shortBreak', 3); sOptCycle += n.title.length + n.body.length;
  n = PomodoroCore.getSessionNotification('focus', 4); sOptCycle += n.title.length + n.body.length;
  n = PomodoroCore.getSessionNotification('longBreak', 4); sOptCycle += n.title.length + n.body.length;
}
t1 = performance.now();
const optCycle = t1 - t0;

if (sBaseCycle !== sOptCycle) throw new Error('Workload 2 checksum mismatch');

// Workload 3: parseCycleCount standalone
let sBaseParse = 0;
t0 = performance.now();
for (let i = 0; i < iters; i++) {
  sBaseParse += baseline.parseCycleCount((i % 8) + 1);
}
t1 = performance.now();
const baseParse = t1 - t0;

let sOptParse = 0;
t0 = performance.now();
for (let i = 0; i < iters; i++) {
  sOptParse += PomodoroCore.parseCycleCount((i % 8) + 1);
}
t1 = performance.now();
const optParse = t1 - t0;

if (sBaseParse !== sOptParse) throw new Error('Workload 3 checksum mismatch');

console.log(`\nBenchmark Results (${iters.toLocaleString()} iterations):`);
console.log(`--------------------------------------------------`);
console.log(`1. getSessionNotification (Focus Sessions):`);
console.log(`   Baseline:  ${baseFocus.toFixed(2)} ms`);
console.log(`   Optimized: ${optFocus.toFixed(2)} ms`);
console.log(`   Speedup:   ${((baseFocus - optFocus) / baseFocus * 100).toFixed(1)}% faster`);

console.log(`\n2. Routine Pomodoro Cycle (Focus & Breaks):`);
console.log(`   Baseline:  ${baseCycle.toFixed(2)} ms`);
console.log(`   Optimized: ${optCycle.toFixed(2)} ms`);
console.log(`   Speedup:   ${((baseCycle - optCycle) / baseCycle * 100).toFixed(1)}% faster`);

console.log(`\n3. parseCycleCount (Standalone):`);
console.log(`   Baseline:  ${baseParse.toFixed(2)} ms`);
console.log(`   Optimized: ${optParse.toFixed(2)} ms`);
console.log(`   Speedup:   ${((baseParse - optParse) / baseParse * 100).toFixed(1)}% faster`);
