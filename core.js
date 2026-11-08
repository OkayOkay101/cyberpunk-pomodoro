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
      const dangerousKeys = ['__proto__', 'constructor', 'prototype'];
      const sanitized = {};
      for (const key of Object.keys(parsed)) {
        if (!dangerousKeys.includes(key)) {
          sanitized[key] = parsed[key];
        }
      }
      return { ...defaults, ...sanitized };
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
    const label = labels[mode] || 'FOCUS';
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

  getLocalDateString(date = new Date()) {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
  };

  return { PomodoroCore };
});
