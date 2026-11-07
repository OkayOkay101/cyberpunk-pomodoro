const { PomodoroCore } = require('./test-runner.js');

function baselineEscapeHtml(text) {
  if (!text || typeof text !== 'string') return '';
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

const samples = [
  'Deep work 25 mins session',
  '<script>alert("xss")</script>',
  "Tom & 'Jerry' matrix mission",
  'Normal mission title 12345',
  '',
  null
];

// 1. Strict Equality Verification
for (const s of samples) {
  const base = baselineEscapeHtml(s);
  const opt = PomodoroCore.escapeHtml(s);
  if (base !== opt) {
    throw new Error(`Output mismatch on "${s}": baseline="${base}", optimized="${opt}"`);
  }
}
console.log('✓ Equality verification: baseline and optimized output match exactly.');

// 2. Performance Benchmark
const iters = 200000;

// Warmup
for (let i = 0; i < 10000; i++) {
  baselineEscapeHtml('warmup & <test>' + i);
  PomodoroCore.escapeHtml('warmup & <test>' + i);
}

// Workload A: Clean text without special HTML entities
let t0 = performance.now();
for (let i = 0; i < iters; i++) baselineEscapeHtml('Cyberpunk Focus Deep Work Session ' + i);
const baseClean = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) PomodoroCore.escapeHtml('Cyberpunk Focus Deep Work Session ' + i);
const optClean = performance.now() - t0;

// Workload B: Text with special HTML characters (&, <, >, ", ')
t0 = performance.now();
for (let i = 0; i < iters; i++) baselineEscapeHtml('<b>Cyberpunk & "Mission" <id="' + i + '"></b>');
const baseSpec = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) PomodoroCore.escapeHtml('<b>Cyberpunk & "Mission" <id="' + i + '"></b>');
const optSpec = performance.now() - t0;

console.log('\n=== Benchmark Results (Workload: 200,000 iterations each) ===');
console.log(`[Workload A: Clean text]`);
console.log(`  Baseline:  ${baseClean.toFixed(2)} ms (${(baseClean / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized: ${optClean.toFixed(2)} ms (${(optClean / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:   ${((baseClean - optClean) / baseClean * 100).toFixed(1)}% faster (${(baseClean / optClean).toFixed(2)}x)`);

console.log(`\n[Workload B: Text with HTML characters]`);
console.log(`  Baseline:  ${baseSpec.toFixed(2)} ms (${(baseSpec / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized: ${optSpec.toFixed(2)} ms (${(optSpec / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:   ${((baseSpec - optSpec) / baseSpec * 100).toFixed(1)}% faster (${(baseSpec / optSpec).toFixed(2)}x)`);
