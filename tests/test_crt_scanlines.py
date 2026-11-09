import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestCrtScanlines(unittest.TestCase):
    def _run_node(self, js_code: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )

    def test_crt_effect_config_enabled(self):
        js_code = """
        const { getCrtEffectConfig, CRT_CONFIGS } = require('./crt_effects.js');

        const config = getCrtEffectConfig(true);
        if (!config.enabled) process.exit(1);
        if (config.scanlineOpacity !== CRT_CONFIGS.defaultScanlineOpacity) process.exit(2);
        if (config.className !== 'crt-scanlines-active') process.exit(3);
        if (config.overlayId !== 'crtOverlay') process.exit(4);
        if (!Object.isFrozen(config)) process.exit(5);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_crt_effect_config_disabled_and_fallbacks(self):
        js_code = """
        const { getCrtEffectConfig } = require('./crt_effects.js');

        const falsyCases = [false, 'false', '0', 0, null, undefined, '', 'off', {}, []];
        for (const input of falsyCases) {
            const config = getCrtEffectConfig(input);
            if (config.enabled) {
                console.error('FAIL: should be disabled for', input);
                process.exit(1);
            }
            if (config.scanlineOpacity !== 0.0) process.exit(2);
            if (config.className !== '') process.exit(3);
        }

        const truthyCases = [true, 'true', 1];
        for (const input of truthyCases) {
            const config = getCrtEffectConfig(input);
            if (!config.enabled) {
                console.error('FAIL: should be enabled for', input);
                process.exit(4);
            }
        }

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_parse_crt_storage_state(self):
        js_code = """
        const { parseCrtStorageState } = require('./crt_effects.js');

        if (parseCrtStorageState('true') !== true) process.exit(1);
        if (parseCrtStorageState('1') !== true) process.exit(2);
        if (parseCrtStorageState('yes') !== true) process.exit(3);
        if (parseCrtStorageState('on') !== true) process.exit(4);
        if (parseCrtStorageState(true) !== true) process.exit(5);
        if (parseCrtStorageState(1) !== true) process.exit(6);

        if (parseCrtStorageState('false') !== false) process.exit(7);
        if (parseCrtStorageState('0') !== false) process.exit(8);
        if (parseCrtStorageState(null) !== false) process.exit(9);
        if (parseCrtStorageState(undefined) !== false) process.exit(10);
        if (parseCrtStorageState('invalid') !== false) process.exit(11);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_generate_crt_overlay_html(self):
        js_code = """
        const { generateCrtOverlayHtml } = require('./crt_effects.js');

        const html = generateCrtOverlayHtml();
        if (!html.includes('id="crtOverlay"')) process.exit(1);
        if (!html.includes('class="crt-overlay"')) process.exit(2);
        if (!html.includes('aria-hidden="true"')) process.exit(3);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
