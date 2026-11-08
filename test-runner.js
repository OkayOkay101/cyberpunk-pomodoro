/**
 * Cyberpunk Pomodoro — Standalone Unit Test Suite
 * Zero-dependency pure JavaScript unit tests
 */

// Core Logic Functions (shared module, production code lives in core.js)
const PomodoroCore = (typeof module !== 'undefined' && module.exports)
  ? require('./core.js').PomodoroCore
  : (typeof globalThis !== 'undefined' ? globalThis.PomodoroCore : window.PomodoroCore);


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
    assertEqual(PomodoroCore.calculateProgressOffset(1500, Infinity, C), 0, 'Infinity duration yields 0');
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
    assertEqual(PomodoroCore.formatStreakBadge('5'), '⚡ STREAK: 5 DAYS');
    assertEqual(PomodoroCore.formatStreakBadge('1'), '⚡ STREAK: 1 DAY');
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
    assertEqual(PomodoroCore.calculateRemainingSeconds(Infinity, now), 0, 'Infinity target yields 0');
    assertEqual(PomodoroCore.calculateRemainingSeconds(now + 10000, -Infinity), 0, '-Infinity now yields 0');
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
    assertEqual(PomodoroCore.formatVolumePercent(0.5, true), 'MUTED');
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

  // 27. Optimized HTML Sanitizer Fast-Path and Equality
  test('escapeHtml() preserves exact character mappings with optimized fast-path', () => {
    assertEqual(PomodoroCore.escapeHtml('Clean cyberpunk mission title'), 'Clean cyberpunk mission title');
    assertEqual(PomodoroCore.escapeHtml('<script>alert("xss")</script>'), '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;');
    assertEqual(PomodoroCore.escapeHtml("Tom & 'Jerry'"), 'Tom &amp; &#039;Jerry&#039;');
    assertEqual(PomodoroCore.escapeHtml('A & B < C > D "E" \'F\''), 'A &amp; B &lt; C &gt; D &quot;E&quot; &#039;F&#039;');
    assertEqual(PomodoroCore.escapeHtml(''), '');
    assertEqual(PomodoroCore.escapeHtml(null), '');
    assertEqual(PomodoroCore.escapeHtml(undefined), '');
    assertEqual(PomodoroCore.escapeHtml(42), '');
  });

  // 28. Mute State Persistence (Bug Fix)
  test('calculateMuteToggle() returns storage values that preserve restored volume', () => {
    const unmuteFromZero = PomodoroCore.calculateMuteToggle(true, 0);
    assertEqual(unmuteFromZero.storage.muted, 'false', 'Unmute must persist muted=false');
    assertEqual(unmuteFromZero.storage.volume, '0.5', 'Restored volume must persist as 0.5');

    const muteFromActive = PomodoroCore.calculateMuteToggle(false, 0.7);
    assertEqual(muteFromActive.storage.muted, 'true', 'Mute must persist muted=true');
    assertEqual(muteFromActive.storage.volume, '0.7', 'Muting must keep the last active volume');

    const unmuteFromSaved = PomodoroCore.calculateMuteToggle(true, 0.7);
    assertEqual(unmuteFromSaved.storage.volume, '0.7', 'Unmute must restore the saved volume');

    const invalidVol = PomodoroCore.calculateMuteToggle(true, 'invalid');
    assertEqual(invalidVol.storage.volume, '0.5', 'Invalid saved volume must persist the 0.5 default');
  });

  // 29. Human-readable Theme Palette Labels
  test('getThemeLabel() returns descriptive palette names with a safe cyan fallback', () => {
    assertEqual(PomodoroCore.getThemeLabel('cyan'), 'Cyan Matrix');
    assertEqual(PomodoroCore.getThemeLabel('pink'), 'Neon Pink / Outrun');
    assertEqual(PomodoroCore.getThemeLabel('yellow'), 'Night City Yellow');
    assertEqual(PomodoroCore.getThemeLabel('green'), 'Emerald Hacker');
    assertEqual(PomodoroCore.getThemeLabel('unknown'), 'Cyan Matrix', 'Unknown theme falls back to cyan');
    assertEqual(PomodoroCore.getThemeLabel(), 'Cyan Matrix', 'Missing theme falls back to cyan');
  });

  // 30. Task List Fallback for Unrenderable Entries
  test('renderTaskList() falls back to the empty state when no task is renderable', () => {
    const emptyState = PomodoroCore.renderTaskList([]);
    assertEqual(
      PomodoroCore.renderTaskList([null, undefined, { id: 9 }, { id: 10, text: 42 }, 'not-a-task']),
      emptyState,
      'List with no renderable tasks should reuse the empty state'
    );
    const mixed = PomodoroCore.renderTaskList([null, { id: 11 }, { id: 12, text: 'Valid <x>', done: false }]);
    assertEqual(mixed.includes('task-empty'), false, 'Mixed list should not show the empty state');
    assertEqual(mixed.includes('Valid &lt;x&gt;'), true, 'Valid task text should stay escaped');
  });

  // 32. Local Date String Generation (Timezone Bug Fix)
  test('getLocalDateString() returns local date in YYYY-MM-DD format', () => {
    const dateStr = PomodoroCore.getLocalDateString();
    assertEqual(typeof dateStr, 'string');
    assertEqual(dateStr.length, 10);
    assertEqual(dateStr.charAt(4), '-');
    assertEqual(dateStr.charAt(7), '-');
    const year = parseInt(dateStr.substring(0, 4), 10);
    const month = parseInt(dateStr.substring(5, 7), 10);
    const day = parseInt(dateStr.substring(8, 10), 10);
    assertEqual(!isNaN(year) && year >= 2020 && year <= 2100, true);
    assertEqual(!isNaN(month) && month >= 1 && month <= 12, true);
    assertEqual(!isNaN(day) && day >= 1 && day <= 31, true);

    const now = new Date();
    assertEqual(year, now.getFullYear());
    assertEqual(month, now.getMonth() + 1);
    assertEqual(day, now.getDate());

    const testDate = new Date('2026-01-15T12:00:00');
    const customStr = PomodoroCore.getLocalDateString(testDate);
    assertEqual(customStr, '2026-01-15');
  });

  // 33. Keyboard Shortcut Action Resolver
  test('resolveKeyboardAction() maps shortcut keys and respects modal and input focus states', () => {
    assertEqual(PomodoroCore.resolveKeyboardAction({ code: 'Space', key: ' ', targetTagName: 'BODY', isModalOpen: false }), 'toggleTimer');
    assertEqual(PomodoroCore.resolveKeyboardAction({ code: 'KeyR', key: 'r', targetTagName: 'BODY', isModalOpen: false }), 'resetTimer');
    assertEqual(PomodoroCore.resolveKeyboardAction({ code: 'KeyS', key: 's', targetTagName: 'BODY', isModalOpen: false }), 'skipMode');
    assertEqual(PomodoroCore.resolveKeyboardAction({ code: 'KeyM', key: 'm', targetTagName: 'BODY', isModalOpen: false }), 'toggleMute');
    assertEqual(PomodoroCore.resolveKeyboardAction({ code: 'KeyF', key: 'f', targetTagName: 'BODY', isModalOpen: false }), 'toggleFullscreen');
    assertEqual(PomodoroCore.resolveKeyboardAction({ code: 'Space', key: ' ', targetTagName: 'INPUT', isModalOpen: false }), null);
    assertEqual(PomodoroCore.resolveKeyboardAction({ key: 'Escape', isModalOpen: true }), 'closeModal');
    assertEqual(PomodoroCore.resolveKeyboardAction({ code: 'Space', key: ' ', isModalOpen: true }), null);
    assertEqual(PomodoroCore.resolveKeyboardAction(null), null);
  });

  // 34. Duration Config Resolver & Sanitization
  test('resolveDurations() enforces bounds and returns seconds, minutes, and storage representations', () => {
    const def = PomodoroCore.resolveDurations();
    assertEqual(def.focus, 1500);
    assertEqual(def.shortBreak, 300);
    assertEqual(def.longBreak, 900);
    assertEqual(def.minutes.focus, 25);
    assertEqual(def.minutes.shortBreak, 5);
    assertEqual(def.minutes.longBreak, 15);
    assertEqual(def.storage.cp_cfg_focus, '25');

    const custom = PomodoroCore.resolveDurations({ focus: '50', shortBreak: 10, longBreak: '20' });
    assertEqual(custom.focus, 3000);
    assertEqual(custom.shortBreak, 600);
    assertEqual(custom.longBreak, 1200);
    assertEqual(custom.minutes.focus, 50);

    const bounded = PomodoroCore.resolveDurations({ focus: 150, shortBreak: -5, longBreak: 0 });
    assertEqual(bounded.minutes.focus, 25);
    assertEqual(bounded.minutes.shortBreak, 5);
    assertEqual(bounded.minutes.longBreak, 15);
  });

  // 35. Keyboard Shortcut Modifier Key Protection (Bug Fix)
  test('resolveKeyboardAction() ignores shortcuts when modifier keys (ctrl, meta, alt) are pressed', () => {
    assertEqual(PomodoroCore.resolveKeyboardAction({ code: 'KeyR', key: 'r', targetTagName: 'BODY', isModalOpen: false, ctrlKey: true }), null, 'Ctrl+R must not trigger reset');
    assertEqual(PomodoroCore.resolveKeyboardAction({ code: 'KeyS', key: 's', targetTagName: 'BODY', isModalOpen: false, ctrlKey: true }), null, 'Ctrl+S must not trigger skip');
    assertEqual(PomodoroCore.resolveKeyboardAction({ code: 'KeyF', key: 'f', targetTagName: 'BODY', isModalOpen: false, ctrlKey: true }), null, 'Ctrl+F must not trigger fullscreen');
    assertEqual(PomodoroCore.resolveKeyboardAction({ code: 'KeyR', key: 'r', targetTagName: 'BODY', isModalOpen: false, metaKey: true }), null, 'Cmd+R must not trigger reset');
    assertEqual(PomodoroCore.resolveKeyboardAction({ code: 'KeyF', key: 'f', targetTagName: 'BODY', isModalOpen: false, metaKey: true }), null, 'Cmd+F must not trigger fullscreen');
    assertEqual(PomodoroCore.resolveKeyboardAction({ code: 'Space', key: ' ', targetTagName: 'BODY', isModalOpen: false, altKey: true }), null, 'Alt+Space must not trigger timer');
    assertEqual(PomodoroCore.resolveKeyboardAction({ key: 'Escape', isModalOpen: true, ctrlKey: false }), 'closeModal', 'Escape in modal still closes modal');
  });

  // 32. Mode Tabs Keyboard Navigation
  test('getNextTabIndex() handles arrow key and home/end navigation with wrapping', () => {
    assertEqual(PomodoroCore.getNextTabIndex(0, 3, 'ArrowRight'), 1);
    assertEqual(PomodoroCore.getNextTabIndex(2, 3, 'ArrowRight'), 0);
    assertEqual(PomodoroCore.getNextTabIndex(0, 3, 'ArrowLeft'), 2);
    assertEqual(PomodoroCore.getNextTabIndex(1, 3, 'Home'), 0);
    assertEqual(PomodoroCore.getNextTabIndex(1, 3, 'End'), 2);
    assertEqual(PomodoroCore.getNextTabIndex(0, 3, 'Space'), -1);
  });

  // 36. Mode Session Labels Formatter
  test('getModeSessionLabel() resolves session labels for each mode with fallback', () => {
    assertEqual(PomodoroCore.getModeSessionLabel('focus', 1), 'SESSION 01 // DEEP WORK');
    assertEqual(PomodoroCore.getModeSessionLabel('focus', 4), 'SESSION 04 // DEEP WORK');
    assertEqual(PomodoroCore.getModeSessionLabel('shortBreak', 1), 'RECHARGE // SHORT BREAK');
    assertEqual(PomodoroCore.getModeSessionLabel('longBreak', 4), 'REST // LONG BREAK');
    assertEqual(PomodoroCore.getModeSessionLabel('unknown', 1), 'SESSION 01 // DEEP WORK');
    assertEqual(PomodoroCore.getModeSessionLabel(null, 2), 'SESSION 02 // DEEP WORK');
  });

  // 37. Mode Stroke Color Resolver
  test('getModeStroke() maps modes to theme CSS stroke variables with fallback', () => {
    assertEqual(PomodoroCore.getModeStroke('focus'), 'var(--accent)');
    assertEqual(PomodoroCore.getModeStroke('shortBreak'), 'var(--green)');
    assertEqual(PomodoroCore.getModeStroke('longBreak'), 'var(--pink)');
    assertEqual(PomodoroCore.getModeStroke('unknown'), 'var(--accent)');
    assertEqual(PomodoroCore.getModeStroke(null), 'var(--accent)');
  });

  // 38. Timer Control Status & HUD State Resolver
  test('getTimerStatus() resolves button label and system status across states', () => {
    const run = PomodoroCore.getTimerStatus(true, 500, 1500);
    assertEqual(run.buttonText, 'PAUSE');
    assertEqual(run.statusText, 'SYSTEM // RUNNING');

    const paused = PomodoroCore.getTimerStatus(false, 500, 1500);
    assertEqual(paused.buttonText, 'RESUME');
    assertEqual(paused.statusText, 'SYSTEM // PAUSED');

    const ready = PomodoroCore.getTimerStatus(false, 1500, 1500);
    assertEqual(ready.buttonText, 'START');
    assertEqual(ready.statusText, 'ONLINE // READY');

    const completed = PomodoroCore.getTimerStatus(false, 0, 1500);
    assertEqual(completed.buttonText, 'START');
    assertEqual(completed.statusText, 'ONLINE // READY');

    const objRun = PomodoroCore.getTimerStatus({ isRunning: true, timeLeft: 100, duration: 1500 });
    assertEqual(objRun.buttonText, 'PAUSE');
    assertEqual(objRun.statusText, 'SYSTEM // RUNNING');

    const fallback = PomodoroCore.getTimerStatus(null);
    assertEqual(fallback.buttonText, 'START');
    assertEqual(fallback.statusText, 'ONLINE // READY');

    assertEqual(PomodoroCore.getTimerStatus(true, 100, 1500), PomodoroCore.getTimerStatus(true, 200, 1500));
  });

  // 31. Theme Selector UI Wiring (Node only; the browser suite renders the real markup)
  if (typeof require === 'function') {
    const fs = require('fs');
    const path = require('path');
    const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
    test('theme selector shows the active palette name and pressed state', () => {
      assertEqual(html.includes('id="activeThemeName"'), true, 'Active palette name element is missing');
      assertEqual(html.includes('aria-pressed="true"'), true, 'Active option is not exposed as pressed');
      assertEqual(html.includes('PomodoroCore.getThemeLabel(theme)'), true, 'Palette name is not kept in sync');
    });
  }

  return { passed, failed, total: passed + failed, results };
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { PomodoroCore, runUnitTests };
  const res = runUnitTests();
  console.log(`Unit Tests Completed: ${res.passed}/${res.total} passed, ${res.failed} failed.`);
  if (res.failed > 0) process.exit(1);
}