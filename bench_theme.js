const { PomodoroCore } = require('./core.js');

// Baseline: recreate objects every call (simulating the old buggy implementation)
function baselineGetThemeVariables(themeName) {
  const themes = {
    cyan: { border: '#1f294d', primary: '#00f0ff', accent: '#ff0055' },
    pink: { border: '#4d1f3d', primary: '#ff007f', accent: '#00f0ff' },
    yellow: { border: '#4d431f', primary: '#ffe600', accent: '#00f0ff' },
    green: { border: '#1f4d2f', primary: '#00ff66', accent: '#ffe600' }
  };
  const validThemes = Object.keys(themes);
  const safeTheme = (typeof themeName === 'string' && validThemes.includes(themeName)) ? themeName : 'cyan';
  return themes[safeTheme];
}

function baselineGetThemeLabel(themeName) {
  const labels = {
    cyan: 'Cyan Matrix',
    pink: 'Neon Pink / Outrun',
    yellow: 'Night City Yellow',
    green: 'Emerald Hacker'
  };
  const validLabels = Object.keys(labels);
  const safeTheme = (typeof themeName === 'string' && validLabels.includes(themeName)) ? themeName : 'cyan';
  return labels[safeTheme];
}

// 1. Strict Equality Verification: ensure optimized core.js matches baseline
const themes = ['cyan', 'pink', 'yellow', 'green', 'invalid', null, undefined, 123];
for (const t of themes) {
  const baseVars = baselineGetThemeVariables(t);
  const optVars = PomodoroCore.getThemeVariables(t);
  if (JSON.stringify(baseVars) !== JSON.stringify(optVars)) {
    throw new Error(`getThemeVariables mismatch on "${t}"`);
  }
  const baseLabel = baselineGetThemeLabel(t);
  const optLabel = PomodoroCore.getThemeLabel(t);
  if (baseLabel !== optLabel) {
    throw new Error(`getThemeLabel mismatch on "${t}"`);
  }
}
console.log('✓ Equality verification: core.js output matches baseline exactly.');

// 2. Performance Benchmark
const iters = 500000;

// Warmup
for (let i = 0; i < 10000; i++) {
  baselineGetThemeVariables('cyan');
  PomodoroCore.getThemeVariables('cyan');
  baselineGetThemeLabel('cyan');
  PomodoroCore.getThemeLabel('cyan');
}

// Workload: getThemeVariables
let t0 = performance.now();
for (let i = 0; i < iters; i++) baselineGetThemeVariables(themes[i % themes.length]);
const baseVars = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) PomodoroCore.getThemeVariables(themes[i % themes.length]);
const optVars = performance.now() - t0;

// Workload: getThemeLabel
t0 = performance.now();
for (let i = 0; i < iters; i++) baselineGetThemeLabel(themes[i % themes.length]);
const baseLabel = performance.now() - t0;

t0 = performance.now();
for (let i = 0; i < iters; i++) PomodoroCore.getThemeLabel(themes[i % themes.length]);
const optLabel = performance.now() - t0;

console.log('\n=== Benchmark Results (Workload: 500,000 iterations each) ===');
console.log(`[getThemeVariables]`);
console.log(`  Baseline (recreate): ${baseVars.toFixed(2)} ms (${(baseVars / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized (const):   ${optVars.toFixed(2)} ms (${(optVars / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:             ${((baseVars - optVars) / baseVars * 100).toFixed(1)}% faster (${(baseVars / optVars).toFixed(2)}x)`);

console.log(`\n[getThemeLabel]`);
console.log(`  Baseline (recreate): ${baseLabel.toFixed(2)} ms (${(baseLabel / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Optimized (const):   ${optLabel.toFixed(2)} ms (${(optLabel / iters * 1000).toFixed(4)} us/op)`);
console.log(`  Speedup:             ${((baseLabel - optLabel) / baseLabel * 100).toFixed(1)}% faster (${(baseLabel / optLabel).toFixed(2)}x)`);