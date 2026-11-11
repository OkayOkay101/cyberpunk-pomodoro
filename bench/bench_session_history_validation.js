const assert = require('assert');
const { performance } = require('perf_hooks');
const { PomodoroCore } = require('../core.js');

function baselineValidateSessionHistory(history) {
  let entries = history;
  if (typeof entries === 'string') {
    try {
      entries = JSON.parse(entries);
    } catch (e) {
      return [];
    }
  }
  if (!Array.isArray(entries)) return [];

  const valid = [];
  for (let i = 0; i < entries.length; i++) {
    const entry = entries[i];
    if (!entry || typeof entry !== 'object' || Array.isArray(entry)) continue;
    if (entry.mode !== 'focus' && entry.mode !== 'shortBreak' && entry.mode !== 'longBreak') continue;
    if (typeof entry.completedAt !== 'string' || !Number.isFinite(Date.parse(entry.completedAt))) continue;

    if (entry.mode === 'focus') {
      if (typeof entry.focusDuration !== 'number' || !Number.isFinite(entry.focusDuration) || entry.focusDuration <= 0) continue;
      valid.push({ mode: 'focus', completedAt: entry.completedAt, focusDuration: entry.focusDuration });
    } else {
      valid.push({ mode: entry.mode, completedAt: entry.completedAt });
    }
  }
  return valid.slice(0, PomodoroCore.SESSION_HISTORY_LIMIT);
}

const history = Array.from({ length: 10000 }, (_, index) => ({
  mode: 'focus',
  completedAt: '2026-11-12T10:30:00.000Z',
  focusDuration: 1500 + (index % 60)
}));
const baseline = baselineValidateSessionHistory(history);
assert.deepStrictEqual(PomodoroCore.validateSessionHistory(history), baseline);

function earlyStopValidateSessionHistory(entries) {
  const valid = [];
  for (let i = 0; i < entries.length; i++) {
    const entry = entries[i];
    if (!entry || typeof entry !== 'object' || Array.isArray(entry)) continue;
    if (entry.mode !== 'focus' && entry.mode !== 'shortBreak' && entry.mode !== 'longBreak') continue;
    if (typeof entry.completedAt !== 'string' || !Number.isFinite(Date.parse(entry.completedAt))) continue;

    if (entry.mode === 'focus') {
      if (typeof entry.focusDuration !== 'number' || !Number.isFinite(entry.focusDuration) || entry.focusDuration <= 0) continue;
      valid.push({ mode: 'focus', completedAt: entry.completedAt, focusDuration: entry.focusDuration });
    } else {
      valid.push({ mode: entry.mode, completedAt: entry.completedAt });
    }
    if (valid.length >= PomodoroCore.SESSION_HISTORY_LIMIT) break;
  }
  return valid;
}

function measure(fn) {
  const rounds = [];
  for (let round = 0; round < 5; round++) {
    const start = performance.now();
    for (let i = 0; i < 200; i++) fn(history);
    rounds.push(performance.now() - start);
  }
  rounds.sort((a, b) => a - b);
  return rounds[2];
}

measure(baselineValidateSessionHistory);
measure(earlyStopValidateSessionHistory);
console.log(JSON.stringify({
  workload: `${history.length} valid entries (only 20 returned) × 200 calls × 5 rounds (median)`,
  baselineMs: measure(baselineValidateSessionHistory),
  earlyStopMs: measure(earlyStopValidateSessionHistory)
}));
