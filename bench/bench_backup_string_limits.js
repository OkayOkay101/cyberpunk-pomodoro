const assert = require('assert');
const { performance } = require('perf_hooks');

const values = [
  'Ship the daily build',
  '😀'.repeat(40),
  'x'.repeat(80),
  '😀'.repeat(81),
  'x'.repeat(81)
];
const workload = Array.from({ length: 10 }, (_, i) => values[i % values.length]).concat(values[0]);
const iterations = 100000;

function baseline(text) {
  return Array.from(text).length <= 80;
}

function optimized(text) {
  return text.length <= 80 || Array.from(text).length <= 80;
}

function run(check) {
  let accepted = 0;
  for (let i = 0; i < iterations; i++) {
    for (const text of workload) accepted += check(text) ? 1 : 0;
  }
  return accepted;
}

assert.deepStrictEqual(workload.map(baseline), workload.map(optimized));
run(baseline);
run(optimized);

function measure(check) {
  const samples = [];
  for (let round = 0; round < 7; round++) {
    const start = performance.now();
    const checksum = run(check);
    samples.push({ ms: performance.now() - start, checksum });
  }
  samples.sort((a, b) => a.ms - b.ms);
  return samples[3];
}

const before = measure(baseline);
const after = measure(optimized);
assert.strictEqual(before.checksum, after.checksum);
console.log(JSON.stringify({
  workload: `${workload.length} mission/task strings × ${iterations} calls × 7 rounds (median)`,
  baselineMs: before.ms,
  optimizedMs: after.ms,
  improvementPercent: Number(((1 - after.ms / before.ms) * 100).toFixed(1)),
  acceptedCount: after.checksum
}));
