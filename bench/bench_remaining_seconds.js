const { PomodoroCore } = require('../core.js');

// Baseline implementation prior to numeric fast-path optimization
function baselineCalculateRemainingSeconds(targetEndTimeMs, nowMs) {
  const target = Number(targetEndTimeMs);
  const now = Number(nowMs);
  if (isNaN(target) || isNaN(now) || !isFinite(target) || !isFinite(now) || target <= now) return 0;
  return Math.max(0, Math.ceil((target - now) / 1000));
}

// 1. Strict Equality Verification across exhaustive cases
const baseNow = 1731110000000;
const testTargets = [
  baseNow + 25000, baseNow + 1500, baseNow + 1499, baseNow + 500, baseNow + 499, baseNow + 1,
  baseNow, baseNow - 1, baseNow - 1000, baseNow - 50000,
  0, -1000, 1000,
  NaN, Infinity, -Infinity,
  String(baseNow + 25000), String(baseNow), String(baseNow - 5000),
  '25000', '-5000', '0', 'invalid', '', '   ',
  null, undefined, true, false, {}, [], [baseNow + 1000]
];

const testNows = [
  baseNow, baseNow + 1000, baseNow - 1000,
  0, -1000, 1000,
  NaN, Infinity, -Infinity,
  String(baseNow), String(baseNow - 5000),
  'invalid', '', '   ',
  null, undefined, true, false, {}, []
];

let checkedCombinations = 0;
for (const t of testTargets) {
  for (const n of testNows) {
    const base = baselineCalculateRemainingSeconds(t, n);
    const current = PomodoroCore.calculateRemainingSeconds(t, n);
    if (base !== current) {
      throw new Error(`calculateRemainingSeconds mismatch for target=${JSON.stringify(t)}, now=${JSON.stringify(n)}: expected ${base}, got ${current}`);
    }
    checkedCombinations++;
  }
}

// Randomized fuzz check across 50,000 cases
for (let i = 0; i < 50000; i++) {
  const t = Math.random() < 0.3
    ? baseNow + Math.floor(Math.random() * 3000000) - 1500000
    : (Math.random() < 0.6 ? String(baseNow + 10000) : (Math.random() < 0.8 ? NaN : Infinity));
  const n = Math.random() < 0.5 ? baseNow : (Math.random() < 0.8 ? baseNow + 5000 : 'invalid');
  const base = baselineCalculateRemainingSeconds(t, n);
  const current = PomodoroCore.calculateRemainingSeconds(t, n);
  if (base !== current) {
    throw new Error(`fuzz mismatch for t=${t}, n=${n}: expected ${base}, got ${current}`);
  }
}

console.log(`✓ Strict equality verified across ${checkedCombinations} matrix cases and 50,000 fuzz cases.`);

// 2. Performance Benchmarks
const iters = 5000000;

// Warmup
for (let i = 0; i < 50000; i++) {
  baselineCalculateRemainingSeconds(baseNow + 1500000, baseNow);
  PomodoroCore.calculateRemainingSeconds(baseNow + 1500000, baseNow);
}

// Workload 1: Active Countdown Timer (target > now, simulating 25m focus ticking)
let sBaseActive = 0;
let t0 = performance.now();
for (let i = 0; i < iters; i++) {
  sBaseActive += baselineCalculateRemainingSeconds(baseNow + 1500000 - (i % 1500000), baseNow);
}
let t1 = performance.now();
const baseActiveTime = t1 - t0;

let sOptActive = 0;
let t2 = performance.now();
for (let i = 0; i < iters; i++) {
  sOptActive += PomodoroCore.calculateRemainingSeconds(baseNow + 1500000 - (i % 1500000), baseNow);
}
let t3 = performance.now();
const optActiveTime = t3 - t2;

if (sBaseActive !== sOptActive) throw new Error('Checksum mismatch in Workload 1');

// Workload 2: Expired / Boundary Timer (target <= now)
let sBaseExpired = 0;
let t4 = performance.now();
for (let i = 0; i < iters; i++) {
  sBaseExpired += baselineCalculateRemainingSeconds(baseNow - (i % 1000), baseNow);
}
let t5 = performance.now();
const baseExpiredTime = t5 - t4;

let sOptExpired = 0;
let t6 = performance.now();
for (let i = 0; i < iters; i++) {
  sOptExpired += PomodoroCore.calculateRemainingSeconds(baseNow - (i % 1000), baseNow);
}
let t7 = performance.now();
const optExpiredTime = t7 - t6;

if (sBaseExpired !== sOptExpired) throw new Error('Checksum mismatch in Workload 2');

// Workload 3: Mixed Workload (active, expired, string, and boundary timestamps)
const mixedTargets = [
  baseNow + 25000, baseNow + 1500, baseNow - 5000, baseNow,
  String(baseNow + 10000), NaN, Infinity, 'invalid'
];
const mixedNows = [baseNow, baseNow + 1000, baseNow - 1000, 'invalid'];

let sBaseMixed = 0;
let t8 = performance.now();
for (let i = 0; i < iters; i++) {
  sBaseMixed += baselineCalculateRemainingSeconds(mixedTargets[i % mixedTargets.length], mixedNows[i % mixedNows.length]);
}
let t9 = performance.now();
const baseMixedTime = t9 - t8;

let sOptMixed = 0;
let t10 = performance.now();
for (let i = 0; i < iters; i++) {
  sOptMixed += PomodoroCore.calculateRemainingSeconds(mixedTargets[i % mixedTargets.length], mixedNows[i % mixedNows.length]);
}
let t11 = performance.now();
const optMixedTime = t11 - t10;

if (sBaseMixed !== sOptMixed) throw new Error('Checksum mismatch in Workload 3');

const activeSpeedup = ((baseActiveTime - optActiveTime) / baseActiveTime) * 100;
const expiredSpeedup = ((baseExpiredTime - optExpiredTime) / baseExpiredTime) * 100;
const mixedSpeedup = ((baseMixedTime - optMixedTime) / baseMixedTime) * 100;

console.log('\n--- Benchmark Results (5,000,000 iterations each) ---');
console.log(`Workload 1 (Active Timer):  Baseline ${baseActiveTime.toFixed(2)}ms | Optimized ${optActiveTime.toFixed(2)}ms | Speedup: ${activeSpeedup.toFixed(1)}%`);
console.log(`Workload 2 (Expired Timer): Baseline ${baseExpiredTime.toFixed(2)}ms | Optimized ${optExpiredTime.toFixed(2)}ms | Speedup: ${expiredSpeedup.toFixed(1)}%`);
console.log(`Workload 3 (Mixed Inputs):  Baseline ${baseMixedTime.toFixed(2)}ms | Optimized ${optMixedTime.toFixed(2)}ms | Speedup: ${mixedSpeedup.toFixed(1)}%`);
