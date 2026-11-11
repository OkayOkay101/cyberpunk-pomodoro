const { PomodoroCore } = require('../core.js');

// Baseline implementations (prior to fast-path and lookup table optimization)
function baselineFormatStreakBadge(currentStreak) {
  const parsed = parseInt(currentStreak, 10);
  const valid = (!isNaN(parsed) && parsed >= 1) ? parsed : 1;
  return `⚡ STREAK: ${valid} DAY${valid > 1 ? 'S' : ''}`;
}

function baselineFormatFocusTimeBadge(minutes) {
  const parsed = parseInt(minutes, 10);
  const valid = (!isNaN(parsed) && parsed >= 0) ? parsed : 0;
  return `🎯 ${valid} MINS TODAY`;
}

// 1. Strict Equality Verification across exhaustive cases
const testStreaks = [
  1, 2, 5, 10, 50, 100, 101, 250, 999,
  0, -1, -50,
  0.5, 1.2, 1.9, 2.5, 99.9, 100.1, -0.5,
  '1', '2', '5', '100', '101', '0', '-5', '2.5', '99.9',
  '1 day', '5days', '005', ' 10 ',
  null, undefined, NaN, Infinity, -Infinity,
  '', '   ', 'abc', {}, [], [5], true, false
];

const testFocusTimes = [
  0, 1, 25, 50, 75, 120, 500, 1440, 1441, 3000,
  -1, -20, -500,
  0.2, 0.9, 25.4, 50.8, 1439.9, 1440.1, -0.5,
  '0', '25', '75', '1440', '1500', '-20', '50.5',
  '25 mins', '0025', ' 50 ',
  null, undefined, NaN, Infinity, -Infinity,
  '', '   ', 'abc', {}, [], [25], true, false
];

for (const s of testStreaks) {
  const base = baselineFormatStreakBadge(s);
  const opt = PomodoroCore.formatStreakBadge(s);
  if (base !== opt) {
    throw new Error(`formatStreakBadge mismatch on ${JSON.stringify(s)}: expected "${base}", got "${opt}"`);
  }
}

for (const f of testFocusTimes) {
  const base = baselineFormatFocusTimeBadge(f);
  const opt = PomodoroCore.formatFocusTimeBadge(f);
  if (base !== opt) {
    throw new Error(`formatFocusTimeBadge mismatch on ${JSON.stringify(f)}: expected "${base}", got "${opt}"`);
  }
}

console.log('✓ Strict equality verified across all edge cases.');

// 2. Performance Benchmark
const iters = 3000000;
function badgeChecksum(badge) {
  return badge.length + badge.charCodeAt(0) + badge.charCodeAt(badge.length - 1);
}

// Warmup
for (let i = 0; i < 50000; i++) {
  baselineFormatStreakBadge(5);
  PomodoroCore.formatStreakBadge(5);
  baselineFormatFocusTimeBadge(50);
  PomodoroCore.formatFocusTimeBadge(50);
}

// Workload 1: Routine HUD update (both badges called on stats sync)
let baseHUDChecksum = 0;
let t0 = performance.now();
for (let i = 0; i < iters; i++) {
  baseHUDChecksum += badgeChecksum(baselineFormatStreakBadge((i % 30) + 1));
  baseHUDChecksum += badgeChecksum(baselineFormatFocusTimeBadge((i % 12) * 25));
}
let t1 = performance.now();
const baseHUD = t1 - t0;

let optHUDChecksum = 0;
t0 = performance.now();
for (let i = 0; i < iters; i++) {
  optHUDChecksum += badgeChecksum(PomodoroCore.formatStreakBadge((i % 30) + 1));
  optHUDChecksum += badgeChecksum(PomodoroCore.formatFocusTimeBadge((i % 12) * 25));
}
t1 = performance.now();
const optHUD = t1 - t0;
if (baseHUDChecksum !== optHUDChecksum) throw new Error(`Checksum mismatch Workload 1: baseline=${baseHUDChecksum}, opt=${optHUDChecksum}`);

// Workload 2: formatStreakBadge alone (1..100)
let baseStreakChecksum = 0;
t0 = performance.now();
for (let i = 0; i < iters; i++) {
  baseStreakChecksum += badgeChecksum(baselineFormatStreakBadge((i % 30) + 1));
}
t1 = performance.now();
const baseStreak = t1 - t0;

let optStreakChecksum = 0;
t0 = performance.now();
for (let i = 0; i < iters; i++) {
  optStreakChecksum += badgeChecksum(PomodoroCore.formatStreakBadge((i % 30) + 1));
}
t1 = performance.now();
const optStreak = t1 - t0;
if (baseStreakChecksum !== optStreakChecksum) throw new Error(`Checksum mismatch Workload 2: baseline=${baseStreakChecksum}, opt=${optStreakChecksum}`);

// Workload 3: formatFocusTimeBadge alone (0..300 mins)
let baseFocusChecksum = 0;
t0 = performance.now();
for (let i = 0; i < iters; i++) {
  baseFocusChecksum += badgeChecksum(baselineFormatFocusTimeBadge((i % 12) * 25));
}
t1 = performance.now();
const baseFocus = t1 - t0;

let optFocusChecksum = 0;
t0 = performance.now();
for (let i = 0; i < iters; i++) {
  optFocusChecksum += badgeChecksum(PomodoroCore.formatFocusTimeBadge((i % 12) * 25));
}
t1 = performance.now();
const optFocus = t1 - t0;
if (baseFocusChecksum !== optFocusChecksum) throw new Error(`Checksum mismatch Workload 3: baseline=${baseFocusChecksum}, opt=${optFocusChecksum}`);

// Workload 4: Mixed input workload (strings, out-of-range, null, negative)
const mixedStreak = [1, 5, '5', '1', 0, -2, null, 'abc', 50, 150];
const mixedFocus = [0, 50, '75', -20, null, 120, 1440, 2000];

let baseMixedChecksum = 0;
t0 = performance.now();
for (let i = 0; i < iters; i++) {
  baseMixedChecksum += badgeChecksum(baselineFormatStreakBadge(mixedStreak[i % mixedStreak.length]));
  baseMixedChecksum += badgeChecksum(baselineFormatFocusTimeBadge(mixedFocus[i % mixedFocus.length]));
}
t1 = performance.now();
const baseMixed = t1 - t0;

let optMixedChecksum = 0;
t0 = performance.now();
for (let i = 0; i < iters; i++) {
  optMixedChecksum += badgeChecksum(PomodoroCore.formatStreakBadge(mixedStreak[i % mixedStreak.length]));
  optMixedChecksum += badgeChecksum(PomodoroCore.formatFocusTimeBadge(mixedFocus[i % mixedFocus.length]));
}
t1 = performance.now();
const optMixed = t1 - t0;
if (baseMixedChecksum !== optMixedChecksum) throw new Error(`Checksum mismatch Workload 4: baseline=${baseMixedChecksum}, opt=${optMixedChecksum}`);

console.log('\n--- Benchmark Results (3,000,000 iterations) ---');
console.log(`Workload 1 (HUD sync stats):    Baseline: ${baseHUD.toFixed(2)}ms | Opt: ${optHUD.toFixed(2)}ms | Speedup: ${(((baseHUD - optHUD) / baseHUD) * 100).toFixed(1)}%`);
console.log(`Workload 2 (formatStreakBadge):  Baseline: ${baseStreak.toFixed(2)}ms | Opt: ${optStreak.toFixed(2)}ms | Speedup: ${(((baseStreak - optStreak) / baseStreak) * 100).toFixed(1)}%`);
console.log(`Workload 3 (formatFocusTime):   Baseline: ${baseFocus.toFixed(2)}ms | Opt: ${optFocus.toFixed(2)}ms | Speedup: ${(((baseFocus - optFocus) / baseFocus) * 100).toFixed(1)}%`);
console.log(`Workload 4 (Mixed inputs):      Baseline: ${baseMixed.toFixed(2)}ms | Opt: ${optMixed.toFixed(2)}ms | Speedup: ${(((baseMixed - optMixed) / baseMixed) * 100).toFixed(1)}%`);
