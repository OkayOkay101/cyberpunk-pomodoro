/**
 * Cyberpunk Pomodoro — Standalone Unit Test Suite
 * Zero-dependency pure JavaScript unit tests
 */

// Core Logic Functions
const PomodoroCore = {
  formatTime(seconds) {
    if (isNaN(seconds) || seconds < 0) return '00:00';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  },

  calculateProgressOffset(timeLeft, duration, circumference) {
    if (!duration || duration <= 0) return 0;
    const clamped = Math.max(0, Math.min(timeLeft, duration));
    return circumference - (clamped / duration) * circumference;
  },

  getNextMode(currentMode, cycleCount) {
    if (currentMode === 'focus') {
      return (cycleCount % 4 === 0) ? 'longBreak' : 'shortBreak';
    }
    return 'focus';
  },

  clampVolume(vol) {
    const num = parseFloat(vol);
    if (isNaN(num)) return 0.5;
    return Math.max(0, Math.min(1, num));
  },

  calculateStreak(lastDateStr, todayStr, currentStreak) {
    if (!lastDateStr) return 1;
    if (lastDateStr === todayStr) return currentStreak;
    const lastDate = new Date(lastDateStr);
    const today = new Date(todayStr);
    const diffTime = today - lastDate;
    const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));
    if (diffDays === 1) return currentStreak + 1;
    if (diffDays > 1) return 1;
    return currentStreak;
  },

  formatSessionLabel(cycleCount) {
    const validCycle = Math.max(1, parseInt(cycleCount || '1', 10));
    return `SESSION ${String(validCycle).padStart(2, '0')} // DEEP WORK`;
  },

  sanitizeMission(text) {
    if (!text || typeof text !== 'string') return '';
    return text.trim().slice(0, 80);
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
    return themes[themeName] || themes.cyan;
  },

  serializeConfig(config) {
    return JSON.stringify(config);
  },

  deserializeConfig(jsonStr, defaults) {
    try {
      if (!jsonStr) return defaults;
      const parsed = JSON.parse(jsonStr);
      return { ...defaults, ...parsed };
    } catch (e) {
      return defaults;
    }
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

  // 11. Modal Dialog & Accessibility Attributes Specification
  test('modal dialog and interactive buttons enforce WCAG a11y specifications', () => {
    if (typeof require !== 'undefined') {
      const fs = require('fs');
      const html = fs.readFileSync('index.html', 'utf8');
      assertEqual(html.includes('role="dialog"'), true, 'Modal box must have role="dialog"');
      assertEqual(html.includes('aria-modal="true"'), true, 'Modal box must have aria-modal="true"');
      assertEqual(html.includes('id="settingsModalTitle"'), true, 'Modal title must have id="settingsModalTitle"');
      assertEqual(html.includes('aria-labelledby="settingsModalTitle"'), true, 'Modal box must reference title via aria-labelledby');
      assertEqual(html.includes('id="fullscreenBtn" title="โหมดเต็มจอ" aria-label="โหมดเต็มจอ"'), true, 'Fullscreen button must provide explicit aria-label');
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
