const assert = require('assert');
const { performance } = require('perf_hooks');
const leveling = require('../netrunner_leveling.js');
const { getNetrunnerRank, RANKS } = leveling;

function baselineGetNetrunnerRank(exp) {
  const safeExp = (typeof exp === 'number' && Number.isFinite(exp) && exp > 0)
    ? Math.floor(exp)
    : 0;
  let currentRank = RANKS[0];
  for (let i = RANKS.length - 1; i >= 0; i--) {
    if (safeExp >= RANKS[i].minExp) {
      currentRank = RANKS[i];
      break;
    }
  }
  const nextLevelExp = currentRank.maxExp === Infinity ? null : currentRank.maxExp + 1;
  let progressPercent = 100;
  if (nextLevelExp !== null) {
    const range = nextLevelExp - currentRank.minExp;
    const gained = safeExp - currentRank.minExp;
    progressPercent = Math.min(100, Math.max(0, Math.floor((gained / range) * 100)));
  }
  return Object.freeze({
    level: currentRank.level,
    title: currentRank.title,
    badge: currentRank.badge,
    currentExp: safeExp,
    minExp: currentRank.minExp,
    maxExp: currentRank.maxExp,
    nextLevelExp,
    progressPercent
  });
}

const cases = Array.from({ length: 10001 }, (_, exp) => exp).concat([
  -1, NaN, Infinity, -Infinity, 0.9, 99.9, 100.9, 299.9, 599.9, 999.9,
  1499.9, Number.MAX_SAFE_INTEGER
]);
for (const exp of cases) {
  assert.deepStrictEqual(getNetrunnerRank(exp), baselineGetNetrunnerRank(exp));
}

const inputs = Array.from({ length: 256 }, (_, i) => (i * 7919) % 1500);
const iterations = 1000000;
function measure(fn) {
  let checksum = 0;
  const start = performance.now();
  for (let i = 0; i < iterations; i++) checksum += fn(inputs[i & 255]).progressPercent;
  return { ms: performance.now() - start, checksum };
}
function median(values) {
  values.sort((a, b) => a - b);
  return values[values.length >> 1];
}

measure(baselineGetNetrunnerRank);
measure(getNetrunnerRank);
const baselineMs = median(Array.from({ length: 7 }, () => measure(baselineGetNetrunnerRank).ms));
const optimizedMs = median(Array.from({ length: 7 }, () => measure(getNetrunnerRank).ms));
console.log(JSON.stringify({
  workload: `${inputs.length} mixed EXP values × ${iterations} calls per round (median of 7 rounds)`,
  equalityCases: cases.length,
  baselineMs,
  optimizedMs,
  speedupPercent: ((baselineMs - optimizedMs) / baselineMs * 100).toFixed(1)
}));
