/**
 * Cyberpunk Pomodoro — Shared Core Logic
 * Used by both the production HUD (index.html) and the test suite.
 */
(function (global, factory) {
  const api = factory();
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  } else {
    global.PomodoroCore = api.PomodoroCore;
  }
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  const THEMES = {
    cyan: { border: '#1f294d', primary: '#00f0ff', accent: '#ff0055' },
    pink: { border: '#4d1f3d', primary: '#ff007f', accent: '#00f0ff' },
    yellow: { border: '#4d431f', primary: '#ffe600', accent: '#00f0ff' },
    green: { border: '#1f4d2f', primary: '#00ff66', accent: '#ffe600' }
  };
  const VALID_THEMES = Object.keys(THEMES);
  const LABELS = {
    cyan: 'Cyan Matrix',
    pink: 'Neon Pink / Outrun',
    yellow: 'Night City Yellow',
    green: 'Emerald Hacker'
  };
  const VALID_LABELS = Object.keys(LABELS);
  const DANGEROUS_KEYS = new Set(['__proto__', 'constructor', 'prototype']);
  const PAD_TWO = Array.from({ length: 100 }, (_, i) => (i < 10 ? '0' + i : String(i)));
  const PERCENT_LOOKUP = Array.from({ length: 101 }, (_, i) => i + '%');
  const STREAK_BADGES = Array.from({ length: 101 }, (_, i) => (
    i <= 1 ? '⚡ STREAK: 1 DAY' : '⚡ STREAK: ' + i + ' DAYS'
  ));
  const FOCUS_BADGES = Array.from({ length: 1441 }, (_, i) => '🎯 ' + i + ' MINS TODAY');
  const TAB_LABELS = {
    focus: 'FOCUS',
    shortBreak: 'SHORT',
    longBreak: 'LONG'
  };
  const MODE_SESSION_LABELS = Object.assign(Object.create(null), {
    shortBreak: 'RECHARGE // SHORT BREAK',
    longBreak: 'REST // LONG BREAK'
  });
  const MODE_STROKES = Object.assign(Object.create(null), {
    shortBreak: 'var(--green)',
    longBreak: 'var(--pink)'
  });
  const TIMER_STATUS_RUNNING = Object.freeze({ buttonText: 'PAUSE', statusText: 'SYSTEM // RUNNING' });
  const TIMER_STATUS_PAUSED = Object.freeze({ buttonText: 'RESUME', statusText: 'SYSTEM // PAUSED' });
  const TIMER_STATUS_READY = Object.freeze({ buttonText: 'START', statusText: 'ONLINE // READY' });
  const MS_PER_DAY = 86400000;
  const KEY_ACTIONS = Object.freeze(Object.assign(Object.create(null), {
    r: 'resetTimer',
    R: 'resetTimer',
    s: 'skipMode',
    S: 'skipMode',
    m: 'toggleMute',
    M: 'toggleMute',
    f: 'toggleFullscreen',
    F: 'toggleFullscreen'
  }));
  const PomodoroCore = {
  formatTime(seconds) {
    if (isNaN(seconds) || seconds < 0 || !isFinite(seconds)) return '00:00';
    const totalSecs = Math.floor(seconds);
    const mins = Math.floor(totalSecs / 60);
    const secs = totalSecs % 60;
    const mStr = mins < 100 ? PAD_TWO[mins] : String(mins);
    return mStr + ':' + PAD_TWO[secs];
  },

  calculateProgressOffset(timeLeft, duration, circumference) {
    if (!duration || duration <= 0 || isNaN(duration) || !isFinite(duration)) return 0;
    if (isNaN(circumference) || circumference <= 0 || !isFinite(circumference)) return 0;
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
    const num = typeof vol === 'number' ? vol : parseFloat(vol);
    if (isNaN(num)) return 0.5;
    return num < 0 ? 0 : (num > 1 ? 1 : num);
  },

  calculateStreak(lastDateStr, todayStr, currentStreak) {
    const validStreak = (typeof currentStreak === 'number' && !isNaN(currentStreak) && currentStreak >= 1)
      ? Math.floor(currentStreak)
      : 1;
    if (!lastDateStr || typeof lastDateStr !== 'string') return 1;
    if (lastDateStr === todayStr) return validStreak;
    const todayTime = typeof todayStr === 'string' ? Date.parse(todayStr) : new Date(todayStr).getTime();
    const diffTime = todayTime - Date.parse(lastDateStr);
    if (isNaN(diffTime)) return 1;
    const diffDays = Math.round(diffTime / MS_PER_DAY);
    if (diffDays === 1) return validStreak + 1;
    if (diffDays > 1) return 1;
    return validStreak;
  },

  formatSessionLabel(cycleCount) {
    const parsed = parseInt(cycleCount, 10);
    const validCycle = (!isNaN(parsed) && parsed >= 1) ? parsed : 1;
    const cycleStr = validCycle < 100 ? PAD_TWO[validCycle] : String(validCycle);
    return `SESSION ${cycleStr} // DEEP WORK`;
  },

  sanitizeMission(text) {
    if (!text || typeof text !== 'string') return '';
    return text.trim().slice(0, 80);
  },

  escapeHtml(text) {
    if (!text || typeof text !== 'string') return '';
    if (!/[&<>"']/.test(text)) return text;
    return text.replace(/[&<>"']/g, ch => (
      ch === '&' ? '&amp;' :
      ch === '<' ? '&lt;' :
      ch === '>' ? '&gt;' :
      ch === '"' ? '&quot;' : '&#039;'
    ));
  },

  validateCustomDuration(val, min, max, defaultVal) {
    const num = parseInt(val, 10);
    if (isNaN(num) || num < min || num > max) return defaultVal;
    return num;
  },

  resolveDurations(inputs) {
    const raw = (inputs && typeof inputs === 'object' && !Array.isArray(inputs)) ? inputs : {};
    const f = PomodoroCore.validateCustomDuration(raw.focus, 1, 90, 25);
    const s = PomodoroCore.validateCustomDuration(raw.shortBreak, 1, 30, 5);
    const l = PomodoroCore.validateCustomDuration(raw.longBreak, 1, 60, 15);
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
  },

  getThemeVariables(themeName) {
    const safeTheme = (typeof themeName === 'string' && VALID_THEMES.includes(themeName)) ? themeName : 'cyan';
    return THEMES[safeTheme];
  },

  getThemeLabel(themeName) {
    const safeTheme = (typeof themeName === 'string' && VALID_LABELS.includes(themeName)) ? themeName : 'cyan';
    return LABELS[safeTheme];
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
      let hasDangerous = false;
      for (const key of Object.keys(parsed)) {
        if (DANGEROUS_KEYS.has(key)) {
          hasDangerous = true;
          break;
        }
      }
      if (!hasDangerous) {
        return { ...defaults, ...parsed };
      }
      const result = { ...defaults };
      for (const key of Object.keys(parsed)) {
        if (!DANGEROUS_KEYS.has(key)) {
          result[key] = parsed[key];
        }
      }
      return result;
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
    if (typeof currentStreak === 'number') {
      if (currentStreak <= 1) return STREAK_BADGES[1];
      if (currentStreak <= 100) {
        const intVal = currentStreak | 0;
        if (intVal === currentStreak) return STREAK_BADGES[intVal];
      }
    }
    const parsed = parseInt(currentStreak, 10);
    const valid = (!isNaN(parsed) && parsed >= 1) ? parsed : 1;
    return valid <= 100 ? STREAK_BADGES[valid] : '⚡ STREAK: ' + valid + ' DAYS';
  },

  formatFocusTimeBadge(minutes) {
    if (typeof minutes === 'number') {
      if (minutes <= 0) return FOCUS_BADGES[0];
      if (minutes <= 1440) {
        const intVal = minutes | 0;
        if (intVal === minutes) return FOCUS_BADGES[intVal];
      }
    }
    const parsed = parseInt(minutes, 10);
    const valid = (!isNaN(parsed) && parsed >= 0) ? parsed : 0;
    return valid <= 1440 ? FOCUS_BADGES[valid] : '🎯 ' + valid + ' MINS TODAY';
  },

  calculateRemainingSeconds(targetEndTimeMs, nowMs) {
    const target = Number(targetEndTimeMs);
    const now = Number(nowMs);
    if (isNaN(target) || isNaN(now) || !isFinite(target) || !isFinite(now) || target <= now) return 0;
    return Math.max(0, Math.round((target - now) / 1000));
  },

  formatDocumentTitle(timeStr, isRunning) {
    const safeTime = (typeof timeStr === 'string' && timeStr.trim().length > 0) ? timeStr.trim() : '00:00';
    const statePrefix = isRunning ? '' : '[PAUSED] ';
    return `${statePrefix}(${safeTime}) CYBERPUNK FOCUS`;
  },

  formatTabLabel(mode, durationSeconds) {
    const label = TAB_LABELS[mode] || 'FOCUS';
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
    return {
      isMuted: nextMuted,
      targetVol,
      savedVol: nextSavedVol,
      storage: {
        muted: String(nextMuted),
        volume: String(nextSavedVol)
      }
    };
  },

  formatVolumePercent(vol, isMuted) {
    if (isMuted) return 'MUTED';
    const clamped = PomodoroCore.clampVolume(vol);
    const pct = Math.round(clamped * 100);
    return pct >= 0 && pct <= 100 ? PERCENT_LOOKUP[pct] : pct + '%';
  },

  getVolumeIcon(vol, isMuted) {
    if (isMuted) return '🔇';
    return PomodoroCore.clampVolume(vol) === 0 ? '🔇' : '🔊';
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
    const result = tasks.slice();
    for (let i = 0; i < result.length; i++) {
      const task = result[i];
      if (task && task.id === taskId) {
        result[i] = { ...task, done: Boolean(isDone) };
      }
    }
    return result;
  },

  renderTaskList(tasks) {
    const emptyState = '<div class="task-empty" role="status">ยังไม่มีภารกิจ — พิมพ์ด้านบนแล้วกด Enter เพื่อเพิ่ม</div>';
    if (!Array.isArray(tasks) || tasks.length === 0) {
      return emptyState;
    }
    let html = '';
    for (let i = 0; i < tasks.length; i++) {
      const task = tasks[i];
      if (!task || typeof task.text !== 'string') continue;
      const safeText = PomodoroCore.escapeHtml(task.text);
      const doneClass = task.done ? 'done' : '';
      const checked = task.done ? 'checked' : '';
      const safeId = PomodoroCore.escapeHtml(String(task.id));
      html += `
        <div class="task-item ${doneClass}" data-id="${safeId}">
          <input type="checkbox" ${checked} aria-label="${safeText}">
          <span>${safeText}</span>
        </div>
      `;
    }
    return html || emptyState;
  },

  getLocalDateString(date) {
    let d;
    if (date === undefined) {
      d = new Date();
    } else if (date instanceof Date) {
      d = isNaN(date.getTime()) ? new Date() : date;
    } else {
      d = new Date(date);
      if (isNaN(d.getTime())) d = new Date();
    }
    return `${d.getFullYear()}-${PAD_TWO[d.getMonth() + 1]}-${PAD_TWO[d.getDate()]}`;
  },

  resolveKeyboardAction(params) {
    if (!params || typeof params !== 'object') return null;
    const { key, code, targetTagName, isModalOpen, ctrlKey, metaKey, altKey } = params;

    if (isModalOpen) {
      return key === 'Escape' ? 'closeModal' : null;
    }

    if (ctrlKey || metaKey || altKey) {
      return null;
    }

    if (typeof targetTagName === 'string') {
      if (targetTagName === 'INPUT' || targetTagName === 'TEXTAREA' ||
          targetTagName === 'input' || targetTagName === 'textarea') {
        return null;
      }
      const len = targetTagName.length;
      if ((len === 5 && targetTagName.toUpperCase() === 'INPUT') ||
          (len === 8 && targetTagName.toUpperCase() === 'TEXTAREA')) {
        return null;
      }
    }

    if (code === 'Space') return 'toggleTimer';
    return KEY_ACTIONS[key] || null;
  },

  getModeSessionLabel(mode, cycleCount) {
    if (typeof mode === 'string' && MODE_SESSION_LABELS[mode]) {
      return MODE_SESSION_LABELS[mode];
    }
    return PomodoroCore.formatSessionLabel(cycleCount);
  },

  getModeStroke(mode) {
    if (typeof mode === 'string' && MODE_STROKES[mode]) {
      return MODE_STROKES[mode];
    }
    return 'var(--accent)';
  },

  getNextTabIndex(currentIndex, totalTabs, key) {
    const total = parseInt(totalTabs, 10);
    const curr = parseInt(currentIndex, 10);
    if (isNaN(total) || total <= 0 || isNaN(curr) || curr < 0 || curr >= total) return -1;
    if (key === 'ArrowRight' || key === 'ArrowDown') return (curr + 1) % total;
    if (key === 'ArrowLeft' || key === 'ArrowUp') return (curr - 1 + total) % total;
    if (key === 'Home') return 0;
    if (key === 'End') return total - 1;
    return -1;
  },

  getTimerStatus(isRunningOrParams, timeLeft, duration) {
    let running = false;
    let time = timeLeft;
    let dur = duration;

    if (isRunningOrParams && typeof isRunningOrParams === 'object') {
      running = Boolean(isRunningOrParams.isRunning);
      time = isRunningOrParams.timeLeft;
      dur = isRunningOrParams.duration;
    } else {
      running = Boolean(isRunningOrParams);
    }

    if (running) {
      return TIMER_STATUS_RUNNING;
    }

    const safeTime = Number(time);
    const safeDur = Number(dur);

    if (!isNaN(safeTime) && !isNaN(safeDur) && safeDur > 0 && safeTime > 0 && safeTime < safeDur) {
      return TIMER_STATUS_PAUSED;
    }

    return TIMER_STATUS_READY;
  }
  };

  return { PomodoroCore };
});