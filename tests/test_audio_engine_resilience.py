import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestAudioEngineResilience(unittest.TestCase):
    def setUp(self):
        self.html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

    def test_ensure_audio_handles_missing_audio_context_class(self):
        """
        Verify that ensureAudio() does not throw or reject when AudioContextClass
        is undefined (e.g. environments without Web Audio API support).
        """
        js_code = """
        const fs = require('fs');
        const html = fs.readFileSync('index.html', 'utf8');

        const ensureAudioMatch = html.match(/async function ensureAudio\\(\\)\\s*\\{[\\s\\S]*?\\n    \\}/);
        if (!ensureAudioMatch) {
            console.error('FAIL: could not extract ensureAudio');
            process.exit(1);
        }

        let AudioContextClass = undefined;
        let audioCtx = null;
        let audioInitLock = false;
        let masterCompressor = null;
        let analyser = null;
        let masterGain = null;
        let isMuted = false;
        let savedVol = 0.5;
        function startVisualizer() {}

        eval(ensureAudioMatch[0]);

        ensureAudio().then(() => {
            if (audioCtx !== null) {
                console.error('FAIL: audioCtx should remain null');
                process.exit(2);
            }
            console.log('SUCCESS');
        }).catch(err => {
            console.error('FAIL: ensureAudio threw error: ' + err.message);
            process.exit(3);
        });
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_ensure_audio_handles_constructor_error(self):
        """
        Verify that ensureAudio() catches initialization errors when AudioContextClass
        constructor throws (e.g. NotAllowedError or device allocation failure).
        """
        js_code = """
        const fs = require('fs');
        const html = fs.readFileSync('index.html', 'utf8');

        const ensureAudioMatch = html.match(/async function ensureAudio\\(\\)\\s*\\{[\\s\\S]*?\\n    \\}/);
        if (!ensureAudioMatch) {
            console.error('FAIL: could not extract ensureAudio');
            process.exit(1);
        }

        let AudioContextClass = function() {
            throw new Error('NotAllowedError: The AudioContext was not allowed to start');
        };
        let audioCtx = null;
        let audioInitLock = false;
        let masterCompressor = null;
        let analyser = null;
        let masterGain = null;
        let isMuted = false;
        let savedVol = 0.5;
        function startVisualizer() {}

        eval(ensureAudioMatch[0]);

        ensureAudio().then(() => {
            if (audioInitLock !== false) {
                console.error('FAIL: audioInitLock must be released');
                process.exit(2);
            }
            if (audioCtx !== null) {
                console.error('FAIL: audioCtx should be null on failure');
                process.exit(3);
            }
            console.log('SUCCESS');
        }).catch(err => {
            console.error('FAIL: ensureAudio threw unhandled rejection: ' + err.message);
            process.exit(4);
        });
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_ensure_audio_guards_audio_ctx_state_check(self):
        """
        Verify that audioCtx.state is guarded with a null-check so accessing
        .state when audioCtx is null does not throw a TypeError.
        """
        self.assertIn(
            "if (audioCtx && audioCtx.state === 'suspended')",
            self.html,
            "ensureAudio must guard audioCtx.state check with 'audioCtx &&'"
        )

    def test_toggle_sound_stops_active_node_immediately(self):
        """
        Verify that toggleSound() checks activeNodes before awaiting audio init,
        stopping active ambient sounds immediately and setting aria-pressed='false'.
        """
        js_code = """
        const fs = require('fs');
        const html = fs.readFileSync('index.html', 'utf8');

        const toggleSoundMatch = html.match(/async function toggleSound\\(type, btn\\)\\s*\\{[\\s\\S]*?\\n    \\}/);
        if (!toggleSoundMatch) {
            console.error('FAIL: could not extract toggleSound');
            process.exit(1);
        }

        let stopped = false;
        let activeNodes = {
            rain: {
                stop: () => { stopped = true; }
            }
        };
        let audioCtx = null;
        let AudioContextClass = undefined;
        let audioInitLock = false;
        async function ensureAudio() {
            throw new Error('ensureAudio should not be called when stopping sound');
        }

        const btn = {
            classList: {
                remove: (cls) => { btn._removed = cls; },
                add: (cls) => { btn._added = cls; }
            },
            setAttribute: (attr, val) => { btn[attr] = val; }
        };

        eval(toggleSoundMatch[0]);

        toggleSound('rain', btn).then(() => {
            if (!stopped) {
                console.error('FAIL: active node was not stopped');
                process.exit(2);
            }
            if (activeNodes.rain !== null) {
                console.error('FAIL: activeNodes.rain was not cleared');
                process.exit(3);
            }
            if (btn['aria-pressed'] !== 'false') {
                console.error('FAIL: aria-pressed not set to false');
                process.exit(4);
            }
            console.log('SUCCESS');
        }).catch(err => {
            console.error('FAIL: toggleSound threw when stopping: ' + err.message);
            process.exit(5);
        });
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_toggle_sound_guards_against_null_audio_context(self):
        """
        Verify that toggleSound() bails out cleanly when audioCtx is unavailable,
        ensuring the button returns to non-playing state without throwing.
        """
        js_code = """
        const fs = require('fs');
        const html = fs.readFileSync('index.html', 'utf8');

        const toggleSoundMatch = html.match(/async function toggleSound\\(type, btn\\)\\s*\\{[\\s\\S]*?\\n    \\}/);
        if (!toggleSoundMatch) {
            console.error('FAIL: could not extract toggleSound');
            process.exit(1);
        }

        let activeNodes = { storm: null };
        let audioCtx = null;
        let AudioContextClass = undefined;
        async function ensureAudio() {
            // resolves safely with null audioCtx
        }

        const btn = {
            classList: {
                remove: (cls) => { btn._playing = false; },
                add: (cls) => { btn._playing = true; }
            },
            setAttribute: (attr, val) => { btn[attr] = val; }
        };

        eval(toggleSoundMatch[0]);

        toggleSound('storm', btn).then(() => {
            if (btn['aria-pressed'] !== 'false') {
                console.error('FAIL: aria-pressed should be false when audioCtx is unavailable');
                process.exit(2);
            }
            if (activeNodes.storm !== null) {
                console.error('FAIL: activeNodes.storm should remain null');
                process.exit(3);
            }
            console.log('SUCCESS');
        }).catch(err => {
            console.error('FAIL: toggleSound threw: ' + err.message);
            process.exit(4);
        });
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_html_source_integrity_and_guards(self):
        """
        Verify that index.html includes safe guards for AudioContextClass existence
        and volume control audioCtx null-checks.
        """
        self.assertIn(
            "if (!audioCtx && AudioContextClass)",
            self.html,
            "index.html must check AudioContextClass before attempting instantiation"
        )
        self.assertIn(
            "if (masterGain && audioCtx)",
            self.html,
            "index.html must guard audioCtx access when updating masterGain"
        )


if __name__ == "__main__":
    unittest.main()
