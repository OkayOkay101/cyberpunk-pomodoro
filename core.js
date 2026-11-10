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
  const SESSION_LABELS = Array.from({ length: 101 }, (_, i) => (
    i <= 0 ? 'SESSION 01 // DEEP WORK' : 'SESSION ' + (i < 100 ? PAD_TWO[i] : String(i)) + ' // DEEP WORK'
  ));
  const MODE_STROKES = Object.assign(Object.create(null), {
    shortBreak: 'var(--green)',
    longBreak: 'var(--pink)'
  });
  const MODE_TOAST_MESSAGES = Object.freeze(Object.assign(Object.create(null), {
    focus: 'FOCUS MODE',
    shortBreak: 'SHORT BREAK',
    longBreak: 'LONG BREAK'
  }));
  const TIMER_STATUS_RUNNING = Object.freeze({ buttonText: 'PAUSE', statusText: 'SYSTEM // RUNNING' });
  const TIMER_STATUS_PAUSED = Object.freeze({ buttonText: 'RESUME', statusText: 'SYSTEM // PAUSED' });
  const TIMER_STATUS_READY = Object.freeze({ buttonText: 'START', statusText: 'ONLINE // READY' });
  const BREAK_NOTIFICATION = Object.freeze({
    title: 'BREAK FINISHED // BACK TO MATRIX',
    body: 'หมดเวลาพักแล้ว พร้อมกลับมาลุยภารกิจต่อหรือยัง?',
    soundType: 'break_end'
  });
  const FOCUS_NOTIFICATIONS = Array.from({ length: 101 }, (_, i) => Object.freeze({
    title: 'FOCUS COMPLETE // CYBERPUNK POMODORO',
    body: 'จบ Session ' + i + ' เรียบร้อยแล้ว ได้เวลาพักผ่อน!',
    soundType: 'focus_end'
  }));
  const FOCUS_SKIP_LOOKUP = Array.from({ length: 101 }, (_, i) => {
    const isLong = (i > 0 && i % 4 === 0);
    return Object.freeze({
      nextMode: isLong ? 'longBreak' : 'shortBreak',
      toastMessage: isLong ? 'LONG BREAK' : 'SHORT BREAK',
      cycleCount: i
    });
  });
  const BREAK_SKIP_LOOKUP = Array.from({ length: 101 }, (_, i) => Object.freeze({
    nextMode: 'focus',
    toastMessage: 'FOCUS MODE',
    cycleCount: i
  }));
  const NUM_STRINGS = Array.from({ length: 1500 }, (_, i) => String(i));
  const FOCUS_SESSION_LOOKUP = Array.from({ length: 101 }, (_, i) => {
    const isLong = (i > 0 && i % 4 === 0);
    const nextCycle = i + 1;
    return Object.freeze({
      nextMode: isLong ? 'longBreak' : 'shortBreak',
      toastMessage: isLong ? 'LONG BREAK STARTED' : 'SHORT BREAK STARTED',
      nextCycleCount: nextCycle,
      cycleStr: String(nextCycle)
    });
  });
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
  const AUDIO_CUE_CONFIGS = Object.freeze(Object.assign(Object.create(null), {
    focus_end: Object.freeze({
      waveType: 'sine',
      duration: 0.35,
      type: 'exponential_ramp',
      startFreq: 880,
      endFreq: 1760,
      initialGain: 0.2,
      targetGain: 0.01
    }),
    break_end: Object.freeze({
      waveType: 'sine',
      duration: 0.35,
      type: 'step_ramp',
      startFreq: 587.33,
      stepFreq: 880,
      stepTime: 0.15,
      initialGain: 0.25,
      targetGain: 0.01
    })
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
    if (typeof timeLeft === 'number' && typeof duration === 'number' && typeof circumference === 'number') {
      if (duration <= 0 || !Number.isFinite(duration)) return 0;
      if (circumference <= 0 || !Number.isFinite(circumference)) return 0;
      const t = timeLeft !== timeLeft ? 0 : timeLeft;
      const clamped = t < 0 ? 0 : (t > duration ? duration : t);
      return circumference - (clamped / duration) * circumference;
    }
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
    if (typeof cycleCount === 'number') {
      if (cycleCount >= 1 && cycleCount <= 100 && (cycleCount | 0) === cycleCount) {
        return SESSION_LABELS[cycleCount];
      }
      if (cycleCount >= 1 && Number.isFinite(cycleCount)) {
        const intVal = cycleCount | 0;
        return intVal <= 100 ? SESSION_LABELS[intVal] : 'SESSION ' + intVal + ' // DEEP WORK';
      }
      return SESSION_LABELS[1];
    }
    const parsed = parseInt(cycleCount, 10);
    const validCycle = (!isNaN(parsed) && parsed >= 1) ? parsed : 1;
    return validCycle <= 100 ? SESSION_LABELS[validCycle] : 'SESSION ' + validCycle + ' // DEEP WORK';
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
    if (typeof val !== 'string' && typeof val !== 'number') return defaultVal;
    if (typeof val === 'number') {
      if (!Number.isFinite(val) || val !== Math.floor(val)) return defaultVal;
      return val >= min && val <= max ? val : defaultVal;
    }
    const trimmed = val.trim();
    if (trimmed === '') return defaultVal;
    if (!/^[+-]?\d+$/.test(trimmed)) return defaultVal;
    const num = parseInt(trimmed, 10);
    return num >= min && num <= max ? num : defaultVal;
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
    if (typeof targetEndTimeMs === 'number' && typeof nowMs === 'number') {
      const diff = targetEndTimeMs - nowMs;
      if (diff <= 0 || !Number.isFinite(diff)) return 0;
      return Math.round(diff / 1000);
    }
    const target = Number(targetEndTimeMs);
    const now = Number(nowMs);
    const diff = target - now;
    if (diff <= 0 || !Number.isFinite(diff)) return 0;
    return Math.round(diff / 1000);
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
    let validId;
    if (typeof id === 'number' && Number.isFinite(id)) {
      validId = id;
    } else if (typeof id === 'string' && id.trim() !== '') {
      const parsed = Number(id);
      validId = Number.isFinite(parsed) ? parsed : Date.now();
    } else {
      validId = Date.now();
    }
    return {
      id: validId,
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
    if (typeof mode === 'string') {
      if (mode === 'focus') {
        if (typeof cycleCount === 'number' && cycleCount >= 1 && cycleCount <= 100 && (cycleCount | 0) === cycleCount) {
          return SESSION_LABELS[cycleCount];
        }
      } else {
        const label = MODE_SESSION_LABELS[mode];
        if (label !== undefined) return label;
      }
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
    switch (key) {
      case 'ArrowRight':
      case 'ArrowDown':
      case 'ArrowLeft':
      case 'ArrowUp':
      case 'Home':
      case 'End':
        break;
      default:
        return -1;
    }

    let total;
    if (typeof totalTabs === 'number') {
      if (!isFinite(totalTabs)) return -1;
      total = totalTabs | 0;
      if (total <= 0) return -1;
    } else {
      total = parseInt(totalTabs, 10);
      if (isNaN(total) || total <= 0) return -1;
    }

    let curr;
    if (typeof currentIndex === 'number') {
      if (!isFinite(currentIndex)) return -1;
      curr = currentIndex | 0;
      if (curr < 0 || curr >= total) return -1;
    } else {
      curr = parseInt(currentIndex, 10);
      if (isNaN(curr) || curr < 0 || curr >= total) return -1;
    }

    if (key === 'ArrowRight' || key === 'ArrowDown') return (curr + 1) % total;
    if (key === 'ArrowLeft' || key === 'ArrowUp') return (curr - 1 + total) % total;
    if (key === 'Home') return 0;
    return total - 1;
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

    if (typeof time === 'number' && typeof dur === 'number') {
      if (time !== time || dur !== dur) return TIMER_STATUS_READY;
      if (time > 0 && time < dur) return TIMER_STATUS_PAUSED;
      return TIMER_STATUS_READY;
    }

    const safeTime = Number(time);
    const safeDur = Number(dur);

    if (safeTime === safeTime && safeDur === safeDur && safeTime > 0 && safeTime < safeDur) {
      return TIMER_STATUS_PAUSED;
    }

    return TIMER_STATUS_READY;
  },

  parseCycleCount(cycleCount) {
    if (typeof cycleCount === 'number') {
      if (cycleCount >= 1 && Number.isFinite(cycleCount)) {
        return cycleCount | 0;
      }
      return 1;
    }
    const parsed = parseInt(cycleCount, 10);
    return (!isNaN(parsed) && parsed >= 1) ? parsed : 1;
  },

  getSessionNotification(modeOrParams, cycleCount) {
    let mode = modeOrParams;
    let cycle = cycleCount;

    if (modeOrParams && typeof modeOrParams === 'object') {
      mode = modeOrParams.mode;
      cycle = modeOrParams.cycleCount;
    }

    if (mode === 'focus') {
      const validCycle = PomodoroCore.parseCycleCount(cycle);
      if (validCycle <= 100) {
        return FOCUS_NOTIFICATIONS[validCycle];
      }
      return {
        title: 'FOCUS COMPLETE // CYBERPUNK POMODORO',
        body: `จบ Session ${validCycle} เรียบร้อยแล้ว ได้เวลาพักผ่อน!`,
        soundType: 'focus_end'
      };
    }

    return BREAK_NOTIFICATION;
  },

  calculateCompletedSession(modeOrParams, cycleCount, focusDuration, totalFocusMinsToday, currentStreak, todayStr) {
    let mode;
    let cycle;
    let duration;
    let totalMins;
    let streak;
    let today;

    if (typeof modeOrParams === 'string') {
      mode = modeOrParams;
      cycle = cycleCount;
      duration = focusDuration;
      totalMins = totalFocusMinsToday;
      streak = currentStreak;
      today = todayStr;
    } else if (modeOrParams && typeof modeOrParams === 'object') {
      mode = modeOrParams.currentMode || modeOrParams.mode;
      cycle = modeOrParams.cycleCount;
      duration = modeOrParams.focusDuration;
      totalMins = modeOrParams.totalFocusMinsToday;
      streak = modeOrParams.currentStreak;
      today = modeOrParams.todayStr || modeOrParams.today;
    } else {
      mode = modeOrParams;
      cycle = cycleCount;
      duration = focusDuration;
      totalMins = totalFocusMinsToday;
      streak = currentStreak;
      today = todayStr;
    }

    let safeCycle;
    if (typeof cycle === 'number') {
      safeCycle = (cycle >= 1 && Number.isFinite(cycle)) ? (cycle | 0) : 1;
    } else {
      const parsedCycle = parseInt(cycle, 10);
      safeCycle = (!isNaN(parsedCycle) && parsedCycle >= 1) ? parsedCycle : 1;
    }

    const safeMode = (typeof mode === 'string') ? mode : 'focus';

    if (safeMode === 'focus') {
      let nextMode;
      let toastMessage;
      let nextCycleCount;
      let cycleStr;

      if (safeCycle <= 100) {
        const lookup = FOCUS_SESSION_LOOKUP[safeCycle];
        nextMode = lookup.nextMode;
        toastMessage = lookup.toastMessage;
        nextCycleCount = lookup.nextCycleCount;
        cycleStr = lookup.cycleStr;
      } else {
        const isLong = (safeCycle % 4 === 0);
        nextMode = isLong ? 'longBreak' : 'shortBreak';
        toastMessage = isLong ? 'LONG BREAK STARTED' : 'SHORT BREAK STARTED';
        nextCycleCount = safeCycle + 1;
        cycleStr = nextCycleCount < 1500 ? NUM_STRINGS[nextCycleCount] : String(nextCycleCount);
      }

      let addedFocusMins;
      if (typeof duration === 'number') {
        addedFocusMins = (Number.isFinite(duration) && duration > 0) ? Math.round(duration / 60) : 25;
      } else {
        const parsedDur = parseInt(duration, 10);
        addedFocusMins = (parsedDur > 0) ? Math.round(parsedDur / 60) : 25;
      }

      let safeTotalMins;
      if (typeof totalMins === 'number') {
        safeTotalMins = (totalMins >= 0 && Number.isFinite(totalMins)) ? (totalMins | 0) : 0;
      } else {
        const parsedTotal = parseInt(totalMins, 10);
        safeTotalMins = (!isNaN(parsedTotal) && parsedTotal >= 0) ? parsedTotal : 0;
      }
      const nextTotalFocusMins = safeTotalMins + addedFocusMins;

      let safeStreak;
      if (typeof streak === 'number') {
        safeStreak = (streak >= 1 && Number.isFinite(streak)) ? (streak | 0) : 1;
      } else {
        const parsedStreak = parseInt(streak, 10);
        safeStreak = (!isNaN(parsedStreak) && parsedStreak >= 1) ? parsedStreak : 1;
      }

      let safeToday;
      if (typeof today === 'string' && today.length > 0) {
        const start = today.charCodeAt(0);
        const end = today.charCodeAt(today.length - 1);
        safeToday = (start > 32 && end > 32) ? today : today.trim();
        if (safeToday.length === 0) safeToday = PomodoroCore.getLocalDateString();
      } else {
        safeToday = PomodoroCore.getLocalDateString();
      }

      return {
        nextMode,
        nextCycleCount,
        addedFocusMins,
        nextTotalFocusMins,
        toastMessage,
        storage: {
          cp_focus_mins_today: nextTotalFocusMins < 1500 ? NUM_STRINGS[nextTotalFocusMins] : String(nextTotalFocusMins),
          cp_last_date: safeToday,
          cp_streak: safeStreak < 1500 ? NUM_STRINGS[safeStreak] : String(safeStreak),
          cp_cycle: cycleStr
        }
      };
    }

    let safeTotalMins;
    if (typeof totalMins === 'number') {
      safeTotalMins = (totalMins >= 0 && Number.isFinite(totalMins)) ? (totalMins | 0) : 0;
    } else {
      const parsedTotal = parseInt(totalMins, 10);
      safeTotalMins = (!isNaN(parsedTotal) && parsedTotal >= 0) ? parsedTotal : 0;
    }

    return {
      nextMode: 'focus',
      nextCycleCount: safeCycle,
      addedFocusMins: 0,
      nextTotalFocusMins: safeTotalMins,
      toastMessage: 'FOCUS SESSION STARTED',
      storage: {}
    };
  },

  getModeToastMessage(mode) {
    if (typeof mode === 'string' && MODE_TOAST_MESSAGES[mode]) {
      return MODE_TOAST_MESSAGES[mode];
    }
    return 'FOCUS MODE';
  },

  calculateSkipTransition(modeOrParams, cycleCount) {
    if (typeof modeOrParams === 'string' && typeof cycleCount === 'number') {
      if (cycleCount >= 1 && cycleCount <= 100 && (cycleCount | 0) === cycleCount) {
        if (modeOrParams === 'focus') {
          return FOCUS_SKIP_LOOKUP[cycleCount];
        }
        return BREAK_SKIP_LOOKUP[cycleCount];
      }
    }

    let mode = modeOrParams;
    let cycle = cycleCount;

    if (modeOrParams && typeof modeOrParams === 'object') {
      mode = modeOrParams.currentMode || modeOrParams.mode;
      cycle = modeOrParams.cycleCount;
    }

    const safeCycle = PomodoroCore.parseCycleCount(cycle);

    if (mode === 'focus') {
      if (safeCycle <= 100) {
        return FOCUS_SKIP_LOOKUP[safeCycle];
      }
      const isLong = (safeCycle % 4 === 0);
      return {
        nextMode: isLong ? 'longBreak' : 'shortBreak',
        toastMessage: isLong ? 'LONG BREAK' : 'SHORT BREAK',
        cycleCount: safeCycle
      };
    }

    if (safeCycle <= 100) {
      return BREAK_SKIP_LOOKUP[safeCycle];
    }

    return {
      nextMode: 'focus',
      toastMessage: 'FOCUS MODE',
      cycleCount: safeCycle
    };
  },

  getAudioCueConfig(soundType) {
    if (typeof soundType === 'string' && AUDIO_CUE_CONFIGS[soundType]) {
      return AUDIO_CUE_CONFIGS[soundType];
    }
    return AUDIO_CUE_CONFIGS.focus_end;
  }
  };

  return { PomodoroCore };
});