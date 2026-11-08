const { PomodoroCore } = require('../core.js');

// Baseline implementations
function baselineClampVolume(vol) {
  const num = parseFloat(vol);
  if (isNaN(num)) return 0.5;
  return Math.max(0, Math.min(1, num));
}

function baselineFormatVolumePercent(vol, isMuted) {
  if (isMuted) return 'MUTED';
  const clamped = baselineClampVolume(vol);
  return `${Math.round(clamped * 100)}%`;
}

function baselineGetVolumeIcon(vol, isMuted) {
  const clamped = baselineClampVolume(vol);
  return (isMuted || clamped === 0) ? '🔇' : '🔊';
}

// 1. Strict Equality Verification across exhaustive cases
const testVolumes = [
  0.0, 0.5, 1.0, 0.25, 0.75, 0.85, 0.01, 0.99,
  1.8, -0.4, -0.0, 2.5, -100,
  NaN, Infinity, -Infinity,
  '0.5', '1.0', '0.0', '0.85', '1.8', '-0.4',
  'invalid', '', '   ', '0.5px', 'abc',
  null, undefined, true, false, [], {}
];

for (const vol of testVolumes) {
  const baseClamp = baselineClampVolume(vol);
  const optClamp = PomodoroCore.clampVolume(vol);
  if (baseClamp !== optClamp) {
    throw new Error(`clampVolume mismatch on ${vol}: expected ${baseClamp}, got ${optClamp}`);
  }

  for (const muted of [true, false, undefined, null, 1, 0]) {
    const baseFmt = baselineFormatVolumePercent(vol, muted);
    const optFmt = PomodoroCore.formatVolumePercent(vol, muted);
    if (baseFmt !== optFmt) {
      throw new Error(`formatVolumePercent mismatch on vol=${vol}, muted=${muted}: expected "${baseFmt}", got "${optFmt}"`);
    }

    const baseIcon = baselineGetVolumeIcon(vol, muted);
    const optIcon = PomodoroCore.getVolumeIcon(vol, muted);
    if (baseIcon !== optIcon) {
      throw new Error(`getVolumeIcon mismatch on vol=${vol}, muted=${muted}: expected "${baseIcon}", got "${optIcon}"`);
    }
  }
}
console.log('✓ Equality verification: baseline and optimized output match exactly.');

// 2. Performance Benchmark
const iters = 2000000;

// Warmup
for (let i = 0; i < 50000; i++) {
  baselineFormatVolumePercent(0.5, false);
  PomodoroCore.formatVolumePercent(0.5, false);
  baselineGetVolumeIcon(0.5, false);
  PomodoroCore.getVolumeIcon(0.5, false);
}

// Workload A: Volume slider interaction (formatVolumePercent + getVolumeIcon on numeric volume values 0.00..1.00)
const sliderValues = Array.from({ length: 101 }, (_, i) => i / 100);

let t0 = performance.now();
for (let i = 0; i < iters; i++) {
  const v = sliderValues[i % 101];
  baselineFormatVolumePercent(v, false);
  baselineGetVolumeIcon(v, false);
}
const baseSlider = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) {
  const v = sliderValues[i % 101];
  PomodoroCore.formatVolumePercent(v, false);
  PomodoroCore.getVolumeIcon(v, false);
}
const optSlider = performance.now() - t0;

// Workload B: Mixed active and muted states
const mixedInputs = [
  { vol: 0.5, muted: false },
  { vol: 0.75, muted: true },
  { vol: 0.0, muted: false },
  { vol: 1.0, muted: false },
  { vol: 0.25, muted: true }
];

t0 = performance.now();
for (let i = 0; i < iters; i++) {
  const item = mixedInputs[i % mixedInputs.length];
  baselineFormatVolumePercent(item.vol, item.muted);
  baselineGetVolumeIcon(item.vol, item.muted);
}
const baseMixed = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) {
  const item = mixedInputs[i % mixedInputs.length];
  PomodoroCore.formatVolumePercent(item.vol, item.muted);
  PomodoroCore.getVolumeIcon(item.vol, item.muted);
}
const optMixed = performance.now() - t0;

// Workload C: clampVolume alone with numeric inputs
t0 = performance.now();
for (let i = 0; i < iters; i++) {
  baselineClampVolume(sliderValues[i % 101]);
}
const baseClamp = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) {
  PomodoroCore.clampVolume(sliderValues[i % 101]);
}
const optClamp = performance.now() - t0;

console.log(`\n=== Benchmark Results (Workload: ${iters.toLocaleString()} iterations each) ===`);
console.log('[Workload A: Volume slider interaction (formatVolumePercent + getVolumeIcon)]');
console.log(`  Baseline:   ${baseSlider.toFixed(2)} ms (${(baseSlider / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized:  ${optSlider.toFixed(2)} ms (${(optSlider / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:    ${((baseSlider - optSlider) / baseSlider * 100).toFixed(1)}% faster (${(baseSlider / optSlider).toFixed(2)}x)`);

console.log('\n[Workload B: Mixed active and muted states]');
console.log(`  Baseline:   ${baseMixed.toFixed(2)} ms (${(baseMixed / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized:  ${optMixed.toFixed(2)} ms (${(optMixed / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:    ${((baseMixed - optMixed) / baseMixed * 100).toFixed(1)}% faster (${(baseMixed / optMixed).toFixed(2)}x)`);

console.log('\n[Workload C: clampVolume alone (numeric inputs)]');
console.log(`  Baseline:   ${baseClamp.toFixed(2)} ms (${(baseClamp / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized:  ${optClamp.toFixed(2)} ms (${(optClamp / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:    ${((baseClamp - optClamp) / baseClamp * 100).toFixed(1)}% faster (${(baseClamp / optClamp).toFixed(2)}x)`);
