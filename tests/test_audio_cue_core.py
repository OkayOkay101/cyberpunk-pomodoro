import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestAudioCueCore(unittest.TestCase):
    def _run_node(self, js_code: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )

    def test_get_audio_cue_config_focus_end(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (typeof PomodoroCore.getAudioCueConfig !== 'function') {
            console.error('FAIL: PomodoroCore.getAudioCueConfig is not a function');
            process.exit(1);
        }

        const config = PomodoroCore.getAudioCueConfig('focus_end');
        if (!config) process.exit(2);
        if (config.waveType !== 'sine') process.exit(3);
        if (config.type !== 'exponential_ramp') process.exit(4);
        if (config.startFreq !== 880) process.exit(5);
        if (config.endFreq !== 1760) process.exit(6);
        if (config.initialGain !== 0.2) process.exit(7);
        if (config.targetGain !== 0.01) process.exit(8);
        if (config.duration !== 0.35) process.exit(9);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_get_audio_cue_config_break_end(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (typeof PomodoroCore.getAudioCueConfig !== 'function') {
            console.error('FAIL: PomodoroCore.getAudioCueConfig is not a function');
            process.exit(1);
        }

        const config = PomodoroCore.getAudioCueConfig('break_end');
        if (!config) process.exit(2);
        if (config.waveType !== 'sine') process.exit(3);
        if (config.type !== 'step_ramp') process.exit(4);
        if (config.startFreq !== 587.33) process.exit(5);
        if (config.stepFreq !== 880) process.exit(6);
        if (config.stepTime !== 0.15) process.exit(7);
        if (config.initialGain !== 0.25) process.exit(8);
        if (config.targetGain !== 0.01) process.exit(9);
        if (config.duration !== 0.35) process.exit(10);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_get_audio_cue_config_fallbacks_and_edge_cases(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const fallbackCases = [
            null,
            undefined,
            '',
            '   ',
            'unknown_cue',
            123,
            true,
            false,
            {},
            []
        ];

        for (const input of fallbackCases) {
            const config = PomodoroCore.getAudioCueConfig(input);
            if (!config) {
                console.error('FAIL: null/empty result for', input);
                process.exit(1);
            }
            if (config.type !== 'exponential_ramp' || config.startFreq !== 880 || config.endFreq !== 1760) {
                console.error('FAIL: fallback mismatch for', input, config);
                process.exit(2);
            }
        }

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_get_audio_cue_config_prototype_pollution_guard(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const dangerousKeys = ['__proto__', 'constructor', 'prototype', 'toString', 'valueOf'];
        for (const key of dangerousKeys) {
            const config = PomodoroCore.getAudioCueConfig(key);
            if (!config || config.type !== 'exponential_ramp') {
                console.error('FAIL: prototype pollution vector not handled safely:', key);
                process.exit(1);
            }
        }

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_get_audio_cue_config_immutability(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const focusConfig = PomodoroCore.getAudioCueConfig('focus_end');
        if (!Object.isFrozen(focusConfig)) {
            console.error('FAIL: focus_end audio cue config must be frozen');
            process.exit(1);
        }

        const breakConfig = PomodoroCore.getAudioCueConfig('break_end');
        if (!Object.isFrozen(breakConfig)) {
            console.error('FAIL: break_end audio cue config must be frozen');
            process.exit(2);
        }

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_index_html_wires_get_audio_cue_config(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn(
            "PomodoroCore.getAudioCueConfig",
            html,
            "index.html must decouple audio synthesis parameters using PomodoroCore.getAudioCueConfig"
        )

    def test_play_beep_synthesis_integration(self):
        js_code = """
        const fs = require('fs');
        const { PomodoroCore } = require('./core.js');
        const html = fs.readFileSync('index.html', 'utf8');

        const playBeepMatch = html.match(/async function playBeep\\([\\s\\S]*?\\)\\s*\\{[\\s\\S]*?\\n    \\}/);
        if (!playBeepMatch) {
            console.error('FAIL: could not extract playBeep from index.html');
            process.exit(1);
        }

        const freqCalls = [];
        const gainCalls = [];
        let oscStarted = false;
        let oscStoppedAt = null;

        const mockOsc = {
            type: '',
            frequency: {
                setValueAtTime: (val, time) => { freqCalls.push({ method: 'set', val, time }); },
                exponentialRampToValueAtTime: (val, time) => { freqCalls.push({ method: 'expRamp', val, time }); }
            },
            connect: () => {},
            start: () => { oscStarted = true; },
            stop: (time) => { oscStoppedAt = time; }
        };

        const mockGain = {
            gain: {
                setValueAtTime: (val, time) => { gainCalls.push({ method: 'set', val, time }); },
                linearRampToValueAtTime: (val, time) => { gainCalls.push({ method: 'linRamp', val, time }); }
            },
            connect: () => {}
        };

        const audioCtx = {
            currentTime: 10.0,
            createOscillator: () => mockOsc,
            createGain: () => mockGain,
            destination: {}
        };
        const masterCompressor = null;
        async function ensureAudio() {}

        eval(playBeepMatch[0]);

        playBeep('focus_end').then(() => {
            if (!oscStarted) process.exit(2);
            if (oscStoppedAt !== 10.35) process.exit(3);
            if (mockOsc.type !== 'sine') process.exit(4);
            if (freqCalls.length !== 2 || freqCalls[0].val !== 880 || freqCalls[1].val !== 1760) process.exit(5);
            if (gainCalls.length !== 2 || gainCalls[0].val !== 0.2 || gainCalls[1].val !== 0.01) process.exit(6);
            console.log('SUCCESS');
        }).catch(err => {
            console.error('FAIL: playBeep threw error: ' + err.message);
            process.exit(7);
        });
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)


if __name__ == "__main__":
    unittest.main()
