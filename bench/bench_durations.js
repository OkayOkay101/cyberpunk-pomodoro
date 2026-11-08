const { PomodoroCore } = require('../core.js');

// Baseline implementations (prior to fast-path and lookup table optimization)
function baselineValidateCustomDuration(val, min, max, defaultVal) {
  const num = parseInt(val, 10);
  if (isNaN(num) || num < min || num > max) return defaultVal;
  return num;
}

function baselineResolveDurations(inputs) {
  const raw = (inputs && typeof inputs === 'object' && !Array.isArray(inputs)) ? inputs : {};
  const f = baselineValidateCustomDuration(raw.focus, 1, 90, 25);
  const s = baselineValidateCustomDuration(raw.shortBreak, 1, 30, 5);
  const l = baselineValidateCustomDuration(raw.longBreak, 1, 60, 15);
  return {
    focus: f * 60,
    shortBreak: s * 60,
    longBreak: l * 60,
    minutes: { focus: f, shortBreak: s, longBreak: l },
    storage: {
      cp_cfg_focus: String(f),
      cp_cfg_short: String(s),
      cp_cfg_long: String(l)
    }
  };
}

// 1. Strict Equality Verification across exhaustive cases
const testInputs = [
  null,
  undefined,
  0,
  1,
  'string',
  [],
  [1, 2, 3],
  {},
  { focus: 25, shortBreak: 5, longBreak: 15 },
  { focus: 1, shortBreak: 1, longBreak: 1 },
  { focus: 90, shortBreak: 30, longBreak: 60 },
  { focus: 50, shortBreak: 10, longBreak: 20 },
  { focus: 0, shortBreak: 0, longBreak: 0 },
  { focus: 91, shortBreak: 31, longBreak: 61 },
  { focus: -10, shortBreak: -5, longBreak: -1 },
  { focus: '1', shortBreak: '1', longBreak: '1' },
  { focus: '25', shortBreak: '5', longBreak: '15' },
  { focus: '90', shortBreak: '30', longBreak: '60' },
  { focus: '50', shortBreak: '10', longBreak: '20' },
  { focus: '0', shortBreak: '0', longBreak: '0' },
  { focus: '91', shortBreak: '31', longBreak: '61' },
  { focus: 'abc', shortBreak: '', longBreak: ' ' },
  { focus: NaN, shortBreak: Infinity, longBreak: -Infinity },
  { focus: 25.4, shortBreak: 5.9, longBreak: 15.1 },
  { focus: '25.4', shortBreak: '5.9', longBreak: '15.1' },
  { focus: true, shortBreak: false, longBreak: {} },
  { focus: 120, shortBreak: -5, longBreak: 0 }
];

for (const input of testInputs) {
  const base = JSON.stringify(baselineResolveDurations(input));
  const opt = JSON.stringify(PomodoroCore.resolveDurations(input));
  if (base !== opt) {
    throw new Error(`resolveDurations mismatch on ${JSON.stringify(input)}:\nbase: ${base}\n opt: ${opt}`);
  }
}

// Check validateCustomDuration directly
const boundsCases = [
  [25, 1, 90, 25],
  [0, 1, 90, 25],
  [120, 1, 90, 25],
  ['abc', 1, 90, 25],
  ['50', 1, 90, 25],
  ['5.2', 1, 30, 5],
  [5.2, 1, 30, 5],
  [NaN, 1, 90, 25],
  [null, 1, 90, 25]
];

for (const [val, min, max, def] of boundsCases) {
  const base = baselineValidateCustomDuration(val, min, max, def);
  const opt = PomodoroCore.validateCustomDuration(val, min, max, def);
  if (base !== opt) {
    throw new Error(`validateCustomDuration mismatch on val=${val}: expected ${base}, got ${opt}`);
  }
}

console.log('✓ Strict equality verified across all edge cases.');

// 2. Performance Benchmark
const iters = 1000000;

const workloads = {
  'typical numbers': [
    { focus: 25, shortBreak: 5, longBreak: 15 },
    { focus: 50, shortBreak: 10, longBreak: 20 },
    { focus: 90, shortBreak: 30, longBreak: 60 }
  ],
  'localStorage strings': [
    { focus: '25', shortBreak: '5', longBreak: '15' },
    { focus: '50', shortBreak: '10', longBreak: '20' },
    { focus: '90', shortBreak: '30', longBreak: '60' }
  ],
  'default/empty/null': [
    {},
    null,
    undefined
  ],
  'mixed realistic': [
    { focus: 25, shortBreak: 5, longBreak: 15 },
    { focus: '50', shortBreak: '10', longBreak: '20' },
    {},
    null,
    { focus: '45', shortBreak: 8, longBreak: '20' },
    { focus: 120, shortBreak: 0, longBreak: -5 }
  ]
};

console.log(`\nRunning benchmark (${iters.toLocaleString()} iterations per workload):`);
for (const [name, cases] of Object.entries(workloads)) {
  for (let i = 0; i < 50000; i++) {
    baselineResolveDurations(cases[i % cases.length]);
    PomodoroCore.resolveDurations(cases[i % cases.length]);
  }

  const t0 = performance.now();
  for (let i = 0; i < iters; i++) {
    baselineResolveDurations(cases[i % cases.length]);
  }
  const baseTime = performance.now() - t0;

  const t1 = performance.now();
  for (let i = 0; i < iters; i++) {
    PomodoroCore.resolveDurations(cases[i % cases.length]);
  }
  const optTime = performance.now() - t1;

  const speedup = ((baseTime - optTime) / baseTime * 100).toFixed(1);
  console.log(`  ${name.padEnd(25)}: base = ${baseTime.toFixed(2)}ms, opt = ${optTime.toFixed(2)}ms -> ${speedup}% faster`);
}
