const assert = require('assert');
const { performance } = require('perf_hooks');
const { PomodoroCore } = require('../core.js');

function baselineSanitizeMission(text) {
  if (!text || typeof text !== 'string') return '';
  return Array.from(text.trim()).slice(0, 80).join('');
}

const inputs = [
  '  Finish the sprint retrospective  ',
  'Review pull requests',
  '  café 雨 🌃  ',
  'A'.repeat(79) + '😀B'
];
const expected = inputs.map(baselineSanitizeMission);
for (let i = 0; i < inputs.length; i++) {
  assert.strictEqual(PomodoroCore.sanitizeMission(inputs[i]), expected[i]);
}

function measure(fn) {
  const rounds = [];
  let checksum = 0;
  for (let round = 0; round < 5; round++) {
    const start = performance.now();
    for (let i = 0; i < 250000; i++) {
      checksum += fn(inputs[i % inputs.length]).length;
    }
    rounds.push(performance.now() - start);
  }
  rounds.sort((a, b) => a - b);
  return { medianMs: rounds[2], checksum };
}

const baseline = measure(baselineSanitizeMission);
const current = measure(PomodoroCore.sanitizeMission);
assert.strictEqual(current.checksum, baseline.checksum);
console.log(JSON.stringify({
  workload: `${inputs.length} short/common mission titles × 250,000 calls × 5 rounds (median)`,
  baselineMs: baseline.medianMs,
  currentMs: current.medianMs,
  speedupPercent: (1 - current.medianMs / baseline.medianMs) * 100
}));
