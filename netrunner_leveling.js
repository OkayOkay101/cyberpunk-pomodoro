/**
 * Netrunner EXP & Leveling System
 * Pure functions and configuration for Cyberpunk Pomodoro gamification.
 */

const RANKS = Object.freeze([
  Object.freeze({ level: 1, title: 'Script Kiddie', minExp: 0, maxExp: 99, badge: '👾' }),
  Object.freeze({ level: 2, title: 'Wirehead', minExp: 100, maxExp: 299, badge: '⚡' }),
  Object.freeze({ level: 3, title: 'Cyber Jockey', minExp: 300, maxExp: 599, badge: '🕹️' }),
  Object.freeze({ level: 4, title: 'Netrunner', minExp: 600, maxExp: 999, badge: '💻' }),
  Object.freeze({ level: 5, title: 'Subnet Phantom', minExp: 1000, maxExp: 1499, badge: '👁️' }),
  Object.freeze({ level: 6, title: 'Street Legend', minExp: 1500, maxExp: Infinity, badge: '👑' })
]);

const EXP_PER_COMPLETED_SESSION = 25;
const EXP_PER_FOCUS_MINUTE = 1;

function calculateNetrunnerExp(completedCycles, totalFocusMins) {
  const safeCycles = (typeof completedCycles === 'number' && Number.isFinite(completedCycles) && completedCycles > 0)
    ? Math.floor(completedCycles)
    : 0;
  const safeMins = (typeof totalFocusMins === 'number' && Number.isFinite(totalFocusMins) && totalFocusMins > 0)
    ? Math.floor(totalFocusMins)
    : 0;

  return (safeCycles * EXP_PER_COMPLETED_SESSION) + (safeMins * EXP_PER_FOCUS_MINUTE);
}

function getNetrunnerRank(exp) {
  const safeExp = (typeof exp === 'number' && Number.isFinite(exp) && exp > 0)
    ? Math.floor(exp)
    : 0;

  let currentRank = RANKS[0];
  for (let i = RANKS.length - 1; i >= 0; i--) {
    if (safeExp >= RANKS[i].minExp) {
      currentRank = RANKS[i];
      break;
    }
  }

  let nextLevelExp = null;
  let progressPercent = 100;

  if (currentRank.maxExp !== Infinity) {
    nextLevelExp = currentRank.maxExp + 1;
    const range = nextLevelExp - currentRank.minExp;
    const gained = safeExp - currentRank.minExp;
    progressPercent = Math.min(100, Math.max(0, Math.floor((gained / range) * 100)));
  }

  return Object.freeze({
    level: currentRank.level,
    title: currentRank.title,
    badge: currentRank.badge,
    currentExp: safeExp,
    minExp: currentRank.minExp,
    maxExp: currentRank.maxExp,
    nextLevelExp: nextLevelExp,
    progressPercent: progressPercent
  });
}

function formatNetrunnerStatus(exp) {
  const rank = getNetrunnerRank(exp);
  const lvlStr = rank.level < 10 ? '0' + rank.level : String(rank.level);
  return `LVL ${lvlStr} // ${rank.title.toUpperCase()} [${rank.progressPercent}%]`;
}

function parseStoredExp(storedValue) {
  if (storedValue === null || storedValue === undefined) {
    return 0;
  }
  if (typeof storedValue === 'number') {
    return (Number.isFinite(storedValue) && storedValue > 0) ? Math.floor(storedValue) : 0;
  }
  if (typeof storedValue === 'string') {
    const parsed = parseInt(storedValue.trim(), 10);
    return (!isNaN(parsed) && parsed > 0) ? parsed : 0;
  }
  return 0;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    RANKS,
    EXP_PER_COMPLETED_SESSION,
    EXP_PER_FOCUS_MINUTE,
    calculateNetrunnerExp,
    getNetrunnerRank,
    formatNetrunnerStatus,
    parseStoredExp
  };
}
