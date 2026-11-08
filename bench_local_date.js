const { PomodoroCore } = require('./core.js');

const PAD_TWO = Array.from({ length: 100 }, (_, i) => (i < 10 ? '0' + i : String(i)));

// Baseline implementation
function baselineGetLocalDateString(date = new Date()) {
  const d = new Date(date);
  if (isNaN(d.getTime())) {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

// 1. Strict Equality Verification
const samples = [
  undefined,
  new Date(),
  new Date('2026-11-08T12:00:00'),
  new Date('2026-01-05T01:02:03'),
  new Date('invalid'),
  null,
  0,
  1700000000000,
  '2026-11-08T15:30:00',
  'invalid string'
];

for (const s of samples) {
  const base = baselineGetLocalDateString(s);
  const opt = PomodoroCore.getLocalDateString(s);
  if (base !== opt) {
    throw new Error(`Output mismatch on "${s}": baseline="${base}", optimized="${opt}"`);
  }
}
console.log('✓ Equality verification: baseline and optimized output match exactly.');

// 2. Performance Benchmark
const iters = 1000000;

// Warmup
for (let i = 0; i < 50000; i++) {
  baselineGetLocalDateString();
  PomodoroCore.getLocalDateString();
}

// Workload A: Default no-args (typical timer/clock tick)
let t0 = performance.now();
for (let i = 0; i < iters; i++) baselineGetLocalDateString();
const baseNoArgs = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) PomodoroCore.getLocalDateString();
const optNoArgs = performance.now() - t0;

// Workload B: Existing Date object passed
const dateObj = new Date('2026-11-08T12:00:00');
t0 = performance.now();
for (let i = 0; i < iters; i++) baselineGetLocalDateString(dateObj);
const baseDateObj = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) PomodoroCore.getLocalDateString(dateObj);
const optDateObj = performance.now() - t0;

// Workload C: Mixed inputs
const mixed = [undefined, dateObj, '2026-11-08', null];
t0 = performance.now();
for (let i = 0; i < iters; i++) baselineGetLocalDateString(mixed[i % mixed.length]);
const baseMixed = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) PomodoroCore.getLocalDateString(mixed[i % mixed.length]);
const optMixed = performance.now() - t0;

console.log(`\n=== Benchmark Results (Workload: ${iters.toLocaleString()} iterations each) ===`);
console.log(`[Workload A: Default no-args]`);
console.log(`  Baseline:  ${baseNoArgs.toFixed(2)} ms (${(baseNoArgs / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized: ${optNoArgs.toFixed(2)} ms (${(optNoArgs / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:   ${((baseNoArgs - optNoArgs) / baseNoArgs * 100).toFixed(1)}% faster (${(baseNoArgs / optNoArgs).toFixed(2)}x)`);

console.log(`\n[Workload B: Existing Date object]`);
console.log(`  Baseline:  ${baseDateObj.toFixed(2)} ms (${(baseDateObj / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized: ${optDateObj.toFixed(2)} ms (${(optDateObj / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:   ${((baseDateObj - optDateObj) / baseDateObj * 100).toFixed(1)}% faster (${(baseDateObj / optDateObj).toFixed(2)}x)`);

console.log(`\n[Workload C: Mixed inputs]`);
console.log(`  Baseline:  ${baseMixed.toFixed(2)} ms (${(baseMixed / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized: ${optMixed.toFixed(2)} ms (${(optMixed / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:   ${((baseMixed - optMixed) / baseMixed * 100).toFixed(1)}% faster (${(baseMixed / optMixed).toFixed(2)}x)`);
