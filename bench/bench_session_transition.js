const { PomodoroCore } = require('../core.js');

// Independent baseline implementations (not reusing PomodoroCore)
function baselineParseCycleCount(cycleCount) {
  if (typeof cycleCount === 'number') {
    if (cycleCount >= 1 && Number.isFinite(cycleCount)) {
      return cycleCount | 0;
    }
    return 1;
  }
  const parsed = parseInt(cycleCount, 10);
  return (!isNaN(parsed) && parsed >= 1) ? parsed : 1;
}

function baselineGetNextMode(currentMode, cycleCount) {
  if (currentMode === 'focus') {
    const validCycle = parseInt(cycleCount, 10);
    return (!isNaN(validCycle) && validCycle > 0 && validCycle % 4 === 0) ? 'longBreak' : 'shortBreak';
  }
  return 'focus';
}

// Baseline implementation prior to fast-path and lookup table optimization
const baseline = {
  calculateCompletedSession(modeOrParams, cycleCount, focusDuration, totalFocusMinsToday, currentStreak, todayStr) {
    let mode = modeOrParams;
    let cycle = cycleCount;
    let duration = focusDuration;
    let totalMins = totalFocusMinsToday;
    let streak = currentStreak;
    let today = todayStr;

    if (modeOrParams && typeof modeOrParams === 'object') {
      mode = modeOrParams.currentMode || modeOrParams.mode;
      cycle = modeOrParams.cycleCount;
      duration = modeOrParams.focusDuration;
      totalMins = modeOrParams.totalFocusMinsToday;
      streak = modeOrParams.currentStreak;
      today = modeOrParams.todayStr || modeOrParams.today;
    }

    const safeCycle = baselineParseCycleCount(cycle);
    const safeMode = (typeof mode === 'string') ? mode : 'focus';

    if (safeMode === 'focus') {
      const nextMode = baselineGetNextMode('focus', safeCycle);
      const nextCycleCount = safeCycle + 1;

      const safeDuration = (typeof duration === 'number' && Number.isFinite(duration) && duration > 0)
        ? duration
        : (parseInt(duration, 10) > 0 ? parseInt(duration, 10) : 1500);
      const addedFocusMins = Math.max(0, Math.round(safeDuration / 60));

      const parsedTotal = parseInt(totalMins, 10);
      const safeTotalMins = (!isNaN(parsedTotal) && parsedTotal >= 0) ? parsedTotal : 0;
      const nextTotalFocusMins = safeTotalMins + addedFocusMins;

      const parsedStreak = parseInt(streak, 10);
      const safeStreak = (!isNaN(parsedStreak) && parsedStreak >= 1) ? parsedStreak : 1;

      const safeToday = (typeof today === 'string' && today.trim().length > 0)
        ? today.trim()
        : PomodoroCore.getLocalDateString();

      const toastMessage = nextMode === 'longBreak' ? 'LONG BREAK STARTED' : 'SHORT BREAK STARTED';

      return {
        nextMode,
        nextCycleCount,
        addedFocusMins,
        nextTotalFocusMins,
        toastMessage,
        storage: {
          cp_focus_mins_today: String(nextTotalFocusMins),
          cp_last_date: safeToday,
          cp_streak: String(safeStreak),
          cp_cycle: String(nextCycleCount)
        }
      };
    }

    const parsedTotal = parseInt(totalMins, 10);
    const safeTotalMins = (!isNaN(parsedTotal) && parsedTotal >= 0) ? parsedTotal : 0;

    return {
      nextMode: 'focus',
      nextCycleCount: safeCycle,
      addedFocusMins: 0,
      nextTotalFocusMins: safeTotalMins,
      toastMessage: 'FOCUS SESSION STARTED',
      storage: {}
    };
  }
};

// 1. Strict Equality Verification across exhaustive cases
let checkedCombinations = 0;
for (const m of ['focus', 'shortBreak', 'other', null]) {
  for (const c of [1, 4, 8, 100, 105, 0, -1, '4', 'bad', NaN]) {
    for (const d of [1500, 1800, 0, -10, NaN, '1500']) {
      for (const tot of [0, 25, 100, -5, NaN, '50']) {
        for (const strk of [1, 2, 5, -1, NaN, '3']) {
          for (const t of ['2026-11-09', '  2026-11-09  ', '', null]) {
            const b = baseline.calculateCompletedSession(m, c, d, tot, strk, t);
            const o = PomodoroCore.calculateCompletedSession(m, c, d, tot, strk, t);
            if (JSON.stringify(b) !== JSON.stringify(o)) {
              throw new Error(`mismatch positional for ${JSON.stringify({ m, c, d, tot, strk, t })}`);
            }
            checkedCombinations++;

            const bObj = baseline.calculateCompletedSession({ currentMode: m, cycleCount: c, focusDuration: d, totalFocusMinsToday: tot, currentStreak: strk, todayStr: t });
            const oObj = PomodoroCore.calculateCompletedSession({ currentMode: m, cycleCount: c, focusDuration: d, totalFocusMinsToday: tot, currentStreak: strk, todayStr: t });
            if (JSON.stringify(bObj) !== JSON.stringify(oObj)) {
              throw new Error(`mismatch obj for ${JSON.stringify({ m, c, d, tot, strk, t })}`);
            }
            checkedCombinations++;
          }
        }
      }
    }
  }
}
console.log(`✓ Strict equality verified across ${checkedCombinations} matrix cases.`);

// 2. Microbenchmarks
const iters = 4000000;

// Warmup
for (let i = 0; i < 50000; i++) {
  baseline.calculateCompletedSession('focus', (i % 100) + 1, 1500, (i % 100) * 25, 2, '2026-11-09');
  baseline.calculateCompletedSession('shortBreak', (i % 100) + 1, 1500, (i % 100) * 25, 2, '2026-11-09');
  PomodoroCore.calculateCompletedSession('focus', (i % 100) + 1, 1500, (i % 100) * 25, 2, '2026-11-09');
  PomodoroCore.calculateCompletedSession('shortBreak', (i % 100) + 1, 1500, (i % 100) * 25, 2, '2026-11-09');
}

// Workload 1: Alternating Positional Transitions (focus -> break -> focus across cycles 1..100)
const t0 = performance.now();
for (let i = 0; i < iters; i++) {
  const mode = (i & 1) === 0 ? 'focus' : 'shortBreak';
  baseline.calculateCompletedSession(mode, (i % 100) + 1, 1500, (i % 100) * 25, 2, '2026-11-09');
}
const tBasePos = performance.now() - t0;

const t1 = performance.now();
for (let i = 0; i < iters; i++) {
  const mode = (i & 1) === 0 ? 'focus' : 'shortBreak';
  PomodoroCore.calculateCompletedSession(mode, (i % 100) + 1, 1500, (i % 100) * 25, 2, '2026-11-09');
}
const tOptPos = performance.now() - t1;

// Workload 2: Routine Focus Session Completion with Object Payload
const objFocus = {
  currentMode: 'focus',
  cycleCount: 1,
  focusDuration: 1500,
  totalFocusMinsToday: 0,
  currentStreak: 2,
  todayStr: '2026-11-09'
};

const t2 = performance.now();
for (let i = 0; i < iters; i++) {
  baseline.calculateCompletedSession(objFocus);
}
const tBaseObj = performance.now() - t2;

const t3 = performance.now();
for (let i = 0; i < iters; i++) {
  PomodoroCore.calculateCompletedSession(objFocus);
}
const tOptObj = performance.now() - t3;

console.log(`[Alternating Positional 1..100] Baseline: ${tBasePos.toFixed(2)}ms | Opt: ${tOptPos.toFixed(2)}ms | Speedup: ${(((tBasePos - tOptPos) / tBasePos) * 100).toFixed(1)}%`);
console.log(`[Focus Object Payload]         Baseline: ${tBaseObj.toFixed(2)}ms | Opt: ${tOptObj.toFixed(2)}ms | Speedup: ${(((tBaseObj - tOptObj) / tBaseObj) * 100).toFixed(1)}%`);
