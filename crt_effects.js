/**
 * Cyberpunk CRT Scanline & Glitch Effect Controller
 * Pure logic and configuration for retro cyberpunk visual overlays.
 */

const CRT_CONFIGS = Object.freeze({
  defaultScanlineOpacity: 0.25,
  defaultGlitchRate: 0.15,
  activeClass: 'crt-scanlines-active',
  overlayId: 'crtOverlay'
});

function getCrtEffectConfig(enabled) {
  const isEnabled = enabled === true || enabled === 'true' || enabled === 1;
  return Object.freeze({
    enabled: isEnabled,
    scanlineOpacity: isEnabled ? CRT_CONFIGS.defaultScanlineOpacity : 0.0,
    glitchRate: isEnabled ? CRT_CONFIGS.defaultGlitchRate : 0.0,
    className: isEnabled ? CRT_CONFIGS.activeClass : '',
    overlayId: CRT_CONFIGS.overlayId
  });
}

function parseCrtStorageState(storedValue) {
  if (storedValue === null || storedValue === undefined) {
    return false;
  }
  if (typeof storedValue === 'boolean') {
    return storedValue;
  }
  if (typeof storedValue === 'string') {
    const trimmed = storedValue.trim().toLowerCase();
    return trimmed === 'true' || trimmed === '1' || trimmed === 'yes' || trimmed === 'on';
  }
  if (typeof storedValue === 'number') {
    return storedValue === 1;
  }
  return false;
}

function generateCrtOverlayHtml() {
  return '<div id="crtOverlay" class="crt-overlay" aria-hidden="true"></div>';
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    CRT_CONFIGS,
    getCrtEffectConfig,
    parseCrtStorageState,
    generateCrtOverlayHtml
  };
}
