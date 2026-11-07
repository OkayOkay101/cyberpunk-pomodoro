/**
 * Cyberpunk Pomodoro — Standalone Unit Test Suite
 * Zero-dependency pure JavaScript unit tests
 */

// Core Logic Functions
const PomodoroCore = {
  formatTime(seconds) {
    if (isNaN(seconds) || seconds < 0 || !isFinite(seconds)) return '00:00';
    const totalSecs = Math.floor(seconds);
    const mins = Math.floor(totalSecs / 60);
    const secs = totalSecs % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  },

  calculateProgressOffset(timeLeft, duration, circumference) {
    if (!duration || duration <= 0 || isNaN(duration)) return 0;
    if (isNaN(circumference) || circumference <= 0) return 0;
    const safeTime = isNaN(timeLeft) ? 0 : timeLeft;
    const clamped = Math.max(0, Math.min(safeTime, duration));
    return circumference - (clamped / duration) * circumference;
  },

  getNextMode(currentMode, cycleCount) {
    if (currentMode === 'focus') {
      const validCycle = parseInt(cycleCount, 10);
      return (!isNaN(validCycle) && validCycle > 0 && validCycle % 4 === 0) ? 'longBreak' : 'shortBreak';
    }
    return 'focus';
  },

  clampVolume(vol) {
    const num = parseFloat(vol);
    if (isNaN(num)) return 0.5;
    return Math.max(0, Math.min(1, num));
  },

  calculateStreak(lastDateStr, todayStr, currentStreak) {
    const validStreak = (typeof currentStreak === 'number' && !isNaN(currentStreak) && currentStreak >= 1)
      ? Math.floor(currentStreak)
      : 1;
    if (!lastDateStr || typeof lastDateStr !== 'string') return 1;
    if (lastDateStr === todayStr) return validStreak;
    const lastDate = new Date(lastDateStr);
    const today = new Date(todayStr);
    const diffTime = today - lastDate;
    if (isNaN(diffTime)) return 1;
    const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));
    if (diffDays === 1) return validStreak + 1;
    if (diffDays > 1) return 1;
    return validStreak;
  },

  formatSessionLabel(cycleCount) {
    const parsed = parseInt(cycleCount, 10);
    const validCycle = (!isNaN(parsed) && parsed >= 1) ? parsed : 1;
    return `SESSION ${String(validCycle).padStart(2, '0')} // DEEP WORK`;
  },

  sanitizeMission(text) {
    if (!text || typeof text !== 'string') return '';
    return text.trim().slice(0, 80);
  },

  escapeHtml(text) {
    if (!text || typeof text !== 'string') return '';
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  },

  validateCustomDuration(val, min, max, defaultVal) {
    const num = parseInt(val, 10);
    if (isNaN(num) || num < min || num > max) return defaultVal;
    return num;
  },

  getThemeVariables(themeName) {
    const themes = {
      cyan: { border: '#1f294d', primary: '#00f0ff', accent: '#ff0055' },
      pink: { border: '#4d1f3d', primary: '#ff007f', accent: '#00f0ff' },
      yellow: { border: '#4d431f', primary: '#ffe600', accent: '#00f0ff' },
      green: { border: '#1f4d2f', primary: '#00ff66', accent: '#ffe600' }
    };
    if (themeName && Object.prototype.hasOwnProperty.call(themes, themeName)) {
      return themes[themeName];
    }
    return themes.cyan;
  },

  serializeConfig(config) {
    return JSON.stringify(config);
  },

  deserializeConfig(jsonStr, defaults) {
    try {
      if (!jsonStr) return defaults;
      const parsed = JSON.parse(jsonStr);
      if (parsed === null || typeof parsed !== 'object') return defaults;
      if (Array.isArray(defaults)) {
        return Array.isArray(parsed) ? parsed : defaults;
      }
      if (Array.isArray(parsed)) {
        return parsed;
      }
      return { ...defaults, ...parsed };
    } catch (e) {
      return defaults;
    }
  },

  calculateDailyFocusMins(lastDateStr, todayStr, storedMins) {
    if (!lastDateStr || lastDateStr !== todayStr) return 0;
    const parsed = parseInt(storedMins, 10);
    return (!isNaN(parsed) && parsed > 0) ? parsed : 0;
  },

  formatStreakBadge(currentStreak) {
    const valid = (typeof currentStreak === 'number' && !isNaN(currentStreak) && currentStreak >= 1)
      ? Math.floor(currentStreak)
      : 1;
    return `⚡ STREAK: ${valid} DAY${valid > 1 ? 'S' : ''}`;
  },

  formatFocusTimeBadge(minutes) {
    const parsed = parseInt(minutes, 10);
    const valid = (!isNaN(parsed) && parsed >= 0) ? parsed : 0;
    return `🎯 ${valid} MINS TODAY`;
  },

  calculateRemainingSeconds(targetEndTimeMs, nowMs) {
    const target = Number(targetEndTimeMs);
    const now = Number(nowMs);
    if (isNaN(target) || isNaN(now) || target <= now) return 0;
    return Math.max(0, Math.round((target - now) / 1000));
  },

  formatDocumentTitle(timeStr, isRunning) {
    const safeTime = (typeof timeStr === 'string' && timeStr.trim().length > 0) ? timeStr.trim() : '00:00';
    const statePrefix = isRunning ? '' : '[PAUSED] ';
    return `${statePrefix}(${safeTime}) CYBERPUNK FOCUS`;
  },

  formatTabLabel(mode, durationSeconds) {
    const labels = {
      focus: 'FOCUS',
      shortBreak: 'SHORT',
      longBreak: 'LONG'
    };
    const label = (mode && Object.prototype.hasOwnProperty.call(labels, mode))
      ? labels[mode]
      : 'FOCUS';
    const num = Number(durationSeconds);
    const mins = (!isNaN(num) && num > 0) ? Math.round(num / 60) : 0;
    return `${label} (${mins}M)`;
  },

  calculateMuteToggle(isMuted, savedVol) {
    const nextMuted = !isMuted;
    const validVol = PomodoroCore.clampVolume(savedVol);
    let targetVol = 0;
    let nextSavedVol = validVol;
    if (!nextMuted) {
      nextSavedVol = validVol > 0 ? validVol : 0.5;
      targetVol = nextSavedVol;
    }
    return { isMuted: nextMuted, targetVol, savedVol: nextSavedVol };
  },

  formatVolumePercent(vol, isMuted) {
    if (isMuted) return '0%';
    const clamped = PomodoroCore.clampVolume(vol);
    return `${Math.round(clamped * 100)}%`;
  },

  getVolumeIcon(vol, isMuted) {
    const clamped = PomodoroCore.clampVolume(vol);
    return (isMuted || clamped === 0) ? '🔇' : '🔊';
  },

  createTaskItem(text, id) {
    const sanitized = PomodoroCore.sanitizeMission(text);
    if (!sanitized) return null;
    return {
      id: (typeof id === 'number' && !isNaN(id)) ? id : Date.now(),
      text: sanitized,
      done: false
    };
  },

  toggleTaskItem(tasks, taskId, isDone) {
    if (!Array.isArray(tasks)) return [];
    return tasks.map(task => {
      if (task && task.id === taskId) {
        return { ...task, done: Boolean(isDone) };
      }
      return task;
    });
  }
};

// Test Runner Engine
function runUnitTests() {
  const results = [];
  let passed = 0;
  let failed = 0;

  function test(description, testFn) {
    try {
      testFn();
      passed++;
      results.push({ name: description, passed: true });
    } catch (err) {
      failed++;
      results.push({ name: description, passed: false, error: err.message });
    }
  }

  function assertEqual(actual, expected, message) {
    if (actual !== expected) {
      throw new Error(`${message || 'Assertion failed'}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
    }
  }

  // 1. Time formatting
  test('formatTime() formats standard and zero seconds correctly', () => {
    assertEqual(PomodoroCore.formatTime(1500), '25:00', '1500s should be 25:00');
    assertEqual(PomodoroCore.formatTime(65), '01:05', '65s should be 01:05');
    assertEqual(PomodoroCore.formatTime(0), '00:00', '0s should be 00:00');
    assertEqual(PomodoroCore.formatTime(-5), '00:00', 'Negative should be 00:00');
  });

  // 2. Progress Offset Calculation
  test('calculateProgressOffset() calculates SVG dashoffset correctly', () => {
    const C = 691.15;
    assertEqual(PomodoroCore.calculateProgressOffset(1500, 1500, C), 0, 'Full time should have offset 0');
    assertEqual(PomodoroCore.calculateProgressOffset(0, 1500, C), C, 'Zero time should have offset C');
    const half = Math.round(PomodoroCore.calculateProgressOffset(750, 1500, C));
    assertEqual(half, Math.round(C / 2), 'Half time should have offset C/2');
  });

  // 3. Cycle and Long Break Transition
  test('getNextMode() triggers long break every 4th cycle', () => {
    assertEqual(PomodoroCore.getNextMode('focus', 1), 'shortBreak', 'Cycle 1 focus -> shortBreak');
    assertEqual(PomodoroCore.getNextMode('focus', 3), 'shortBreak', 'Cycle 3 focus -> shortBreak');
    assertEqual(PomodoroCore.getNextMode('focus', 4), 'longBreak', 'Cycle 4 focus -> longBreak');
    assertEqual(PomodoroCore.getNextMode('focus', 8), 'longBreak', 'Cycle 8 focus -> longBreak');
    assertEqual(PomodoroCore.getNextMode('shortBreak', 4), 'focus', 'Break -> focus');
    assertEqual(PomodoroCore.getNextMode('longBreak', 4), 'focus', 'LongBreak -> focus');
  });

  // 4. Volume Clamping
  test('clampVolume() bounds volume strictly between 0.0 and 1.0', () => {
    assertEqual(PomodoroCore.clampVolume(0.5), 0.5, '0.5 remains 0.5');
    assertEqual(PomodoroCore.clampVolume(1.8), 1.0, '>1 clamps to 1.0');
    assertEqual(PomodoroCore.clampVolume(-0.4), 0.0, '<0 clamps to 0.0');
    assertEqual(PomodoroCore.clampVolume('invalid'), 0.5, 'Invalid defaults to 0.5');
  });

  // 5. Streak Calculator
  test('calculateStreak() handles daily consecutive streaks correctly', () => {
    assertEqual(PomodoroCore.calculateStreak(null, '2026-11-03', 0), 1, 'First day streak is 1');
    assertEqual(PomodoroCore.calculateStreak('2026-11-03', '2026-11-03', 3), 3, 'Same day maintains streak');
    assertEqual(PomodoroCore.calculateStreak('2026-11-02', '2026-11-03', 3), 4, 'Consecutive day increments streak');
    assertEqual(PomodoroCore.calculateStreak('2026-10-30', '2026-11-03', 5), 1, 'Broken streak resets to 1');
  });

  // 6. Session Label Formatter
  test('formatSessionLabel() formats session title cleanly with padding', () => {
    assertEqual(PomodoroCore.formatSessionLabel(1), 'SESSION 01 // DEEP WORK');
    assertEqual(PomodoroCore.formatSessionLabel(9), 'SESSION 09 // DEEP WORK');
    assertEqual(PomodoroCore.formatSessionLabel(10), 'SESSION 10 // DEEP WORK');
    assertEqual(PomodoroCore.formatSessionLabel(100), 'SESSION 100 // DEEP WORK');
  });

  // 7. Mission Sanitizer
  test('sanitizeMission() trims whitespace and limits length to 80 chars', () => {
    const raw = '   Cyberpunk Deep Focus Mission   ';
    assertEqual(PomodoroCore.sanitizeMission(raw), 'Cyberpunk Deep Focus Mission');
    const longText = 'A'.repeat(120);
    assertEqual(PomodoroCore.sanitizeMission(longText).length, 80);
    assertEqual(PomodoroCore.sanitizeMission(null), '');
  });

  // 8. Custom Duration Validation
  test('validateCustomDuration() enforces minimum and maximum boundaries', () => {
    assertEqual(PomodoroCore.validateCustomDuration(25, 1, 90, 25), 25, 'Valid 25');
    assertEqual(PomodoroCore.validateCustomDuration(0, 1, 90, 25), 25, 'Below min defaults');
    assertEqual(PomodoroCore.validateCustomDuration(120, 1, 90, 25), 25, 'Above max defaults');
    assertEqual(PomodoroCore.validateCustomDuration('abc', 1, 90, 25), 25, 'NaN defaults');
  });

  // 9. Theme Palette Resolver
  test('getThemeVariables() returns valid neon palettes for all themes', () => {
    const cyan = PomodoroCore.getThemeVariables('cyan');
    assertEqual(cyan.primary, '#00f0ff');
    const pink = PomodoroCore.getThemeVariables('pink');
    assertEqual(pink.primary, '#ff007f');
    const fallback = PomodoroCore.getThemeVariables('unknown_theme');
    assertEqual(fallback.primary, '#00f0ff');
  });

  // 10. Storage Config Serialization
  test('serializeConfig and deserializeConfig handle roundtrips safely', () => {
    const defaults = { focusTime: 1500, breakTime: 300, theme: 'cyan' };
    const saved = { focusTime: 1800, breakTime: 300, theme: 'pink' };
    const json = PomodoroCore.serializeConfig(saved);
    const restored = PomodoroCore.deserializeConfig(json, defaults);
    assertEqual(restored.focusTime, 1800);
    assertEqual(restored.theme, 'pink');
    const corrupt = PomodoroCore.deserializeConfig('invalid-json{{{', defaults);
    assertEqual(corrupt.focusTime, 1500);
  });

  // 11. Array Deserialization Safety (Bug Fix)
  test('deserializeConfig() preserves Array type when deserializing array data', () => {
    const defaultTasks = [
      { id: 1, text: 'Task 1', done: true },
      { id: 2, text: 'Task 2', done: false }
    ];
    const savedTasks = [
      { id: 10, text: 'Injected Task', done: false }
    ];
    const json = JSON.stringify(savedTasks);
    const restored = PomodoroCore.deserializeConfig(json, defaultTasks);
    assertEqual(Array.isArray(restored), true, 'Restored tasks must be an Array instance');
    assertEqual(restored.length, 1, 'Restored array should have length 1');
    assertEqual(restored[0].text, 'Injected Task', 'Restored task text should match');
  });

  // 12. Deserialization Fallback for Malformed / Primitive JSON
  test('deserializeConfig() rejects primitive or non-object JSON payloads', () => {
    const defaults = { focusTime: 1500 };
    assertEqual(PomodoroCore.deserializeConfig('null', defaults).focusTime, 1500, 'null JSON should fallback to defaults');
    assertEqual(PomodoroCore.deserializeConfig('12345', defaults).focusTime, 1500, 'number JSON should fallback to defaults');
    assertEqual(PomodoroCore.deserializeConfig('"some string"', defaults).focusTime, 1500, 'string JSON should fallback to defaults');
  });

  // 13. Session Label NaN & Boundary Protection
  test('formatSessionLabel() handles non-numeric strings and invalid cycle numbers safely', () => {
    assertEqual(PomodoroCore.formatSessionLabel('abc'), 'SESSION 01 // DEEP WORK');
    assertEqual(PomodoroCore.formatSessionLabel(NaN), 'SESSION 01 // DEEP WORK');
    assertEqual(PomodoroCore.formatSessionLabel(0), 'SESSION 01 // DEEP WORK');
    assertEqual(PomodoroCore.formatSessionLabel(-5), 'SESSION 01 // DEEP WORK');
    assertEqual(PomodoroCore.formatSessionLabel(null), 'SESSION 01 // DEEP WORK');
  });

  // 14. Time Formatting with Fractional and Non-finite Numbers
  test('formatTime() handles fractional seconds and non-finite numbers safely', () => {
    assertEqual(PomodoroCore.formatTime(65.8), '01:05', '65.8s should truncate to 01:05');
    assertEqual(PomodoroCore.formatTime(0.9), '00:00', '0.9s should truncate to 00:00');
    assertEqual(PomodoroCore.formatTime(Infinity), '00:00', 'Infinity should fallback to 00:00');
    assertEqual(PomodoroCore.formatTime(-Infinity), '00:00', '-Infinity should fallback to 00:00');
  });

  // 15. Cycle Count Boundary Protection in getNextMode
  test('getNextMode() guards against zero and negative cycle counts', () => {
    assertEqual(PomodoroCore.getNextMode('focus', 0), 'shortBreak', 'Cycle 0 should not trigger longBreak');
    assertEqual(PomodoroCore.getNextMode('focus', -4), 'shortBreak', 'Negative cycle should not trigger longBreak');
    assertEqual(PomodoroCore.getNextMode('focus', 'invalid'), 'shortBreak', 'Invalid cycle should not trigger longBreak');
  });

  // 16. Streak Calculation Error Handling
  test('calculateStreak() handles invalid date strings and non-numeric streak gracefully', () => {
    assertEqual(PomodoroCore.calculateStreak('invalid-date', '2026-11-03', 5), 1, 'Corrupted last date resets to 1');
    assertEqual(PomodoroCore.calculateStreak('2026-11-03', '2026-11-03', null), 1, 'Null current streak defaults to 1');
    assertEqual(PomodoroCore.calculateStreak('2026-11-03', '2026-11-03', 'abc'), 1, 'Non-numeric streak defaults to 1');
  });

  // 17. Progress Offset Robustness
  test('calculateProgressOffset() handles NaN timeLeft and invalid circumference safely', () => {
    const C = 691.15;
    assertEqual(PomodoroCore.calculateProgressOffset(NaN, 1500, C), C, 'NaN timeLeft should yield full circumference');
    assertEqual(PomodoroCore.calculateProgressOffset(1500, 0, C), 0, 'Zero duration yields 0');
    assertEqual(PomodoroCore.calculateProgressOffset(1500, -10, C), 0, 'Negative duration yields 0');
    assertEqual(PomodoroCore.calculateProgressOffset(1500, 1500, 0), 0, 'Zero circumference yields 0');
  });

  // 18. HTML Sanitization Helper
  test('escapeHtml() escapes special HTML characters to prevent XSS injection', () => {
    assertEqual(PomodoroCore.escapeHtml('<script>alert("xss")</script>'), '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;');
    assertEqual(PomodoroCore.escapeHtml("Tom & 'Jerry'"), 'Tom &amp; &#039;Jerry&#039;');
    assertEqual(PomodoroCore.escapeHtml(null), '');
    assertEqual(PomodoroCore.escapeHtml(undefined), '');
  });

  // 19. Daily Focus Minutes Reset (Bug Fix)
  test('calculateDailyFocusMins() resets to 0 on date change or missing date', () => {
    assertEqual(PomodoroCore.calculateDailyFocusMins('2026-11-02', '2026-11-03', 100), 0, 'New day should reset focus minutes to 0');
    assertEqual(PomodoroCore.calculateDailyFocusMins(null, '2026-11-03', 50), 0, 'Null lastDate should reset to 0');
    assertEqual(PomodoroCore.calculateDailyFocusMins('2026-11-03', '2026-11-03', 75), 75, 'Same day maintains stored focus minutes');
    assertEqual(PomodoroCore.calculateDailyFocusMins('2026-11-03', '2026-11-03', '50'), 50, 'Numeric string parses correctly');
    assertEqual(PomodoroCore.calculateDailyFocusMins('2026-11-03', '2026-11-03', -10), 0, 'Negative minutes fallback to 0');
    assertEqual(PomodoroCore.calculateDailyFocusMins('2026-11-03', '2026-11-03', 'invalid'), 0, 'Invalid string fallback to 0');
  });

  // 20. HUD Stats Badge Formatters
  test('formatStreakBadge() and formatFocusTimeBadge() format stats HUD correctly', () => {
    assertEqual(PomodoroCore.formatStreakBadge(1), '⚡ STREAK: 1 DAY');
    assertEqual(PomodoroCore.formatStreakBadge(5), '⚡ STREAK: 5 DAYS');
    assertEqual(PomodoroCore.formatStreakBadge(0), '⚡ STREAK: 1 DAY');
    assertEqual(PomodoroCore.formatStreakBadge(null), '⚡ STREAK: 1 DAY');
    assertEqual(PomodoroCore.formatStreakBadge('abc'), '⚡ STREAK: 1 DAY');

    assertEqual(PomodoroCore.formatFocusTimeBadge(0), '🎯 0 MINS TODAY');
    assertEqual(PomodoroCore.formatFocusTimeBadge(50), '🎯 50 MINS TODAY');
    assertEqual(PomodoroCore.formatFocusTimeBadge('75'), '🎯 75 MINS TODAY');
    assertEqual(PomodoroCore.formatFocusTimeBadge(-20), '🎯 0 MINS TODAY');
    assertEqual(PomodoroCore.formatFocusTimeBadge(null), '🎯 0 MINS TODAY');
  });

  // 21. Countdown Remaining Seconds Calculation
  test('calculateRemainingSeconds() calculates remaining seconds accurately', () => {
    const now = 1700000000000;
    assertEqual(PomodoroCore.calculateRemainingSeconds(now + 25000, now), 25, '25s future');
    assertEqual(PomodoroCore.calculateRemainingSeconds(now + 1500, now), 2, 'Rounds 1.5s to 2s');
    assertEqual(PomodoroCore.calculateRemainingSeconds(now, now), 0, 'Current time yields 0');
    assertEqual(PomodoroCore.calculateRemainingSeconds(now - 5000, now), 0, 'Past time clamps to 0');
    assertEqual(PomodoroCore.calculateRemainingSeconds(NaN, now), 0, 'NaN target yields 0');
    assertEqual(PomodoroCore.calculateRemainingSeconds(now + 10000, 'invalid'), 0, 'Invalid now yields 0');
  });

  // 22. Document Title Formatting
  test('formatDocumentTitle() reflects paused vs running state and time display', () => {
    assertEqual(PomodoroCore.formatDocumentTitle('25:00', true), '(25:00) CYBERPUNK FOCUS');
    assertEqual(PomodoroCore.formatDocumentTitle('25:00', false), '[PAUSED] (25:00) CYBERPUNK FOCUS');
    assertEqual(PomodoroCore.formatDocumentTitle('', false), '[PAUSED] (00:00) CYBERPUNK FOCUS');
    assertEqual(PomodoroCore.formatDocumentTitle(null, true), '(00:00) CYBERPUNK FOCUS');
  });

  // 23. Mode Tab Label Formatter
  test('formatTabLabel() formats mode labels with converted minute values', () => {
    assertEqual(PomodoroCore.formatTabLabel('focus', 1500), 'FOCUS (25M)');
    assertEqual(PomodoroCore.formatTabLabel('shortBreak', 300), 'SHORT (5M)');
    assertEqual(PomodoroCore.formatTabLabel('longBreak', 900), 'LONG (15M)');
    assertEqual(PomodoroCore.formatTabLabel('focus', 0), 'FOCUS (0M)');
    assertEqual(PomodoroCore.formatTabLabel('unknown', 1500), 'FOCUS (25M)');
  });

  // 24. Mute Toggle State Calculation
  test('calculateMuteToggle() toggles mute state and handles zero volume safely', () => {
    const muteFromActive = PomodoroCore.calculateMuteToggle(false, 0.7);
    assertEqual(muteFromActive.isMuted, true);
    assertEqual(muteFromActive.targetVol, 0);
    assertEqual(muteFromActive.savedVol, 0.7);

    const unmuteToSaved = PomodoroCore.calculateMuteToggle(true, 0.7);
    assertEqual(unmuteToSaved.isMuted, false);
    assertEqual(unmuteToSaved.targetVol, 0.7);
    assertEqual(unmuteToSaved.savedVol, 0.7);

    const unmuteFromZero = PomodoroCore.calculateMuteToggle(true, 0);
    assertEqual(unmuteFromZero.isMuted, false);
    assertEqual(unmuteFromZero.targetVol, 0.5);
    assertEqual(unmuteFromZero.savedVol, 0.5);
  });

  // 25. Volume Display Percentage and Icon Resolver
  test('formatVolumePercent() and getVolumeIcon() format audio controls accurately', () => {
    assertEqual(PomodoroCore.formatVolumePercent(0.5, false), '50%');
    assertEqual(PomodoroCore.formatVolumePercent(0.85, false), '85%');
    assertEqual(PomodoroCore.formatVolumePercent(0.5, true), '0%');
    assertEqual(PomodoroCore.formatVolumePercent(0, false), '0%');

    assertEqual(PomodoroCore.getVolumeIcon(0.5, false), '🔊');
    assertEqual(PomodoroCore.getVolumeIcon(0.5, true), '🔇');
    assertEqual(PomodoroCore.getVolumeIcon(0, false), '🔇');
  });

  // 26. Task Management Pure Functions
  test('createTaskItem() and toggleTaskItem() manage task models safely', () => {
    const item = PomodoroCore.createTaskItem('   Write unit tests   ', 101);
    assertEqual(item.id, 101);
    assertEqual(item.text, 'Write unit tests');
    assertEqual(item.done, false);

    const empty = PomodoroCore.createTaskItem('   ');
    assertEqual(empty, null);

    const tasks = [
      { id: 1, text: 'Task 1', done: false },
      { id: 2, text: 'Task 2', done: false }
    ];
    const toggled = PomodoroCore.toggleTaskItem(tasks, 1, true);
    assertEqual(toggled[0].done, true);
    assertEqual(toggled[1].done, false);
    assertEqual(tasks[0].done, false, 'Should not mutate original array');
  });

  // 27. Prototype Pollution & Inherited Property Lookup Hardening
  test('getThemeVariables() and formatTabLabel() guard against prototype property lookups', () => {
    const prototypeKeys = ['toString', 'valueOf', 'constructor', '__proto__', 'hasOwnProperty'];
    for (const key of prototypeKeys) {
      const theme = PomodoroCore.getThemeVariables(key);
      assertEqual(theme.primary, '#00f0ff', `Theme key "${key}" must fallback to cyan primary`);
      assertEqual(theme.border, '#1f294d', `Theme key "${key}" must fallback to cyan border`);
      assertEqual(theme.accent, '#ff0055', `Theme key "${key}" must fallback to cyan accent`);

      const tabLabel = PomodoroCore.formatTabLabel(key, 1500);
      assertEqual(tabLabel, 'FOCUS (25M)', `Tab mode "${key}" must fallback to default FOCUS`);
    }
  });

  return { passed, failed, total: passed + failed, results };
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { PomodoroCore, runUnitTests };
  const res = runUnitTests();
  console.log(`Unit Tests Completed: ${res.passed}/${res.total} passed, ${res.failed} failed.`);
  if (res.failed > 0) process.exit(1);
}
