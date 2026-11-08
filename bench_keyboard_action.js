const { PomodoroCore } = require('./core.js');

// Baseline: original implementation before optimization
function baselineResolveKeyboardAction(params) {
  if (!params || typeof params !== 'object') return null;
  const { key, code, targetTagName, isModalOpen } = params;

  if (isModalOpen) {
    if (key === 'Escape') return 'closeModal';
    return null;
  }

  const tag = (typeof targetTagName === 'string') ? targetTagName.toUpperCase() : '';
  if (tag === 'INPUT' || tag === 'TEXTAREA') {
    return null;
  }

  if (code === 'Space') return 'toggleTimer';
  if (key === 'r' || key === 'R') return 'resetTimer';
  if (key === 's' || key === 'S') return 'skipMode';
  if (key === 'm' || key === 'M') return 'toggleMute';
  if (key === 'f' || key === 'F') return 'toggleFullscreen';

  return null;
}

// 1. Strict Equality Verification across exhaustive cases
const testCases = [
  { key: ' ', code: 'Space', targetTagName: 'BODY', isModalOpen: false },
  { key: 'r', code: 'KeyR', targetTagName: 'BODY', isModalOpen: false },
  { key: 'R', code: 'KeyR', targetTagName: 'BUTTON', isModalOpen: false },
  { key: 's', code: 'KeyS', targetTagName: 'DIV', isModalOpen: false },
  { key: 'S', code: 'KeyS', targetTagName: 'MAIN', isModalOpen: false },
  { key: 'm', code: 'KeyM', targetTagName: 'SECTION', isModalOpen: false },
  { key: 'M', code: 'KeyM', targetTagName: 'HEADER', isModalOpen: false },
  { key: 'f', code: 'KeyF', targetTagName: 'NAV', isModalOpen: false },
  { key: 'F', code: 'KeyF', targetTagName: 'FOOTER', isModalOpen: false },
  { key: 'a', code: 'KeyA', targetTagName: 'BODY', isModalOpen: false },
  { key: 'Tab', code: 'Tab', targetTagName: 'BUTTON', isModalOpen: false },
  { key: 'ArrowRight', code: 'ArrowRight', targetTagName: 'BUTTON', isModalOpen: false },
  { key: 'ArrowLeft', code: 'ArrowLeft', targetTagName: 'BUTTON', isModalOpen: false },
  { key: 'ArrowDown', code: 'ArrowDown', targetTagName: 'BUTTON', isModalOpen: false },
  { key: 'ArrowUp', code: 'ArrowUp', targetTagName: 'BUTTON', isModalOpen: false },
  { key: 'Home', code: 'Home', targetTagName: 'BUTTON', isModalOpen: false },
  { key: 'End', code: 'End', targetTagName: 'BUTTON', isModalOpen: false },
  { key: 'Enter', code: 'Enter', targetTagName: 'BUTTON', isModalOpen: false },
  { key: 'r', code: 'KeyR', targetTagName: 'INPUT', isModalOpen: false },
  { key: 'r', code: 'KeyR', targetTagName: 'input', isModalOpen: false },
  { key: 'r', code: 'KeyR', targetTagName: 'Input', isModalOpen: false },
  { key: ' ', code: 'Space', targetTagName: 'TEXTAREA', isModalOpen: false },
  { key: ' ', code: 'Space', targetTagName: 'textarea', isModalOpen: false },
  { key: ' ', code: 'Space', targetTagName: 'TextArea', isModalOpen: false },
  { key: 'Escape', code: 'Escape', targetTagName: 'BODY', isModalOpen: true },
  { key: 'Escape', code: 'Escape', targetTagName: 'INPUT', isModalOpen: true },
  { key: ' ', code: 'Space', targetTagName: 'BODY', isModalOpen: true },
  { key: 'r', code: 'KeyR', targetTagName: 'BODY', isModalOpen: true },
  { key: 'Escape', code: 'Escape', targetTagName: 'BODY', isModalOpen: false },
  { key: 'toString', code: 'KeyT', targetTagName: 'BODY', isModalOpen: false },
  { key: 'valueOf', code: 'KeyV', targetTagName: 'BODY', isModalOpen: false },
  { key: 'constructor', code: 'KeyC', targetTagName: 'BODY', isModalOpen: false },
  { key: '__proto__', code: 'KeyP', targetTagName: 'BODY', isModalOpen: false },
  { key: 'r', code: 'KeyR', targetTagName: null, isModalOpen: false },
  { key: 'r', code: 'KeyR', targetTagName: undefined, isModalOpen: false },
  { key: 'r', code: 'KeyR', targetTagName: 123, isModalOpen: false },
  null,
  undefined,
  'invalid',
  {},
  { isModalOpen: true },
  { code: 'Space' }
];

for (const c of testCases) {
  const base = baselineResolveKeyboardAction(c);
  const opt = PomodoroCore.resolveKeyboardAction(c);
  if (base !== opt) {
    throw new Error(`Output mismatch on ${JSON.stringify(c)}: baseline="${base}", optimized="${opt}"`);
  }
}
console.log('✓ Equality verification: baseline and optimized output match exactly across all test cases.');

// 2. Performance Benchmark
const iters = 1000000;

// Warmup
for (let i = 0; i < 50000; i++) {
  baselineResolveKeyboardAction(testCases[0]);
  PomodoroCore.resolveKeyboardAction(testCases[0]);
}

// Workload A: Common UI Keypresses (hotkeys and navigation outside input elements)
const commonWorkload = [
  { key: ' ', code: 'Space', targetTagName: 'BODY', isModalOpen: false },
  { key: 'r', code: 'KeyR', targetTagName: 'BODY', isModalOpen: false },
  { key: 's', code: 'KeyS', targetTagName: 'BODY', isModalOpen: false },
  { key: 'm', code: 'KeyM', targetTagName: 'BODY', isModalOpen: false },
  { key: 'f', code: 'KeyF', targetTagName: 'BODY', isModalOpen: false },
  { key: 'Tab', code: 'Tab', targetTagName: 'BUTTON', isModalOpen: false },
  { key: 'ArrowRight', code: 'ArrowRight', targetTagName: 'BUTTON', isModalOpen: false },
  { key: 'ArrowLeft', code: 'ArrowLeft', targetTagName: 'BUTTON', isModalOpen: false },
  { key: 'Enter', code: 'Enter', targetTagName: 'BUTTON', isModalOpen: false },
  { key: 'a', code: 'KeyA', targetTagName: 'INPUT', isModalOpen: false }
];

let t0 = performance.now();
for (let i = 0; i < iters; i++) {
  for (let j = 0; j < commonWorkload.length; j++) {
    baselineResolveKeyboardAction(commonWorkload[j]);
  }
}
const baseCommon = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) {
  for (let j = 0; j < commonWorkload.length; j++) {
    PomodoroCore.resolveKeyboardAction(commonWorkload[j]);
  }
}
const optCommon = performance.now() - t0;

// Workload B: Mixed Workload (exhaustive cases including modal, inputs, edge cases)
t0 = performance.now();
for (let i = 0; i < iters / 2; i++) {
  for (let j = 0; j < testCases.length; j++) {
    baselineResolveKeyboardAction(testCases[j]);
  }
}
const baseMixed = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters / 2; i++) {
  for (let j = 0; j < testCases.length; j++) {
    PomodoroCore.resolveKeyboardAction(testCases[j]);
  }
}
const optMixed = performance.now() - t0;

const totalCommonCalls = iters * commonWorkload.length;
const totalMixedCalls = (iters / 2) * testCases.length;

console.log('\n=== Benchmark Results ===');
console.log(`[Workload A: Common UI Keypresses (${totalCommonCalls.toLocaleString()} calls)]`);
console.log(`  Baseline (toUpperCase + sequential branches): ${baseCommon.toFixed(2)} ms (${(baseCommon / totalCommonCalls * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized (Fast-path tag + KEY_ACTIONS map):   ${optCommon.toFixed(2)} ms (${(optCommon / totalCommonCalls * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:                                      ${((baseCommon - optCommon) / baseCommon * 100).toFixed(1)}% faster (${(baseCommon / optCommon).toFixed(2)}x)`);

console.log(`\n[Workload B: Mixed Exhaustive Cases (${totalMixedCalls.toLocaleString()} calls)]`);
console.log(`  Baseline (toUpperCase + sequential branches): ${baseMixed.toFixed(2)} ms (${(baseMixed / totalMixedCalls * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized (Fast-path tag + KEY_ACTIONS map):   ${optMixed.toFixed(2)} ms (${(optMixed / totalMixedCalls * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:                                      ${((baseMixed - optMixed) / baseMixed * 100).toFixed(1)}% faster (${(baseMixed / optMixed).toFixed(2)}x)`);
