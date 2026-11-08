import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestModeVisualsDecoupling(unittest.TestCase):
    def test_get_mode_session_label_standard_modes(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (typeof PomodoroCore.getModeSessionLabel !== 'function') {
            console.error('FAIL: PomodoroCore.getModeSessionLabel is not a function');
            process.exit(1);
        }

        // Focus mode uses formatSessionLabel with padded cycle count
        if (PomodoroCore.getModeSessionLabel('focus', 1) !== 'SESSION 01 // DEEP WORK') process.exit(2);
        if (PomodoroCore.getModeSessionLabel('focus', 4) !== 'SESSION 04 // DEEP WORK') process.exit(3);
        if (PomodoroCore.getModeSessionLabel('focus', 12) !== 'SESSION 12 // DEEP WORK') process.exit(4);
        if (PomodoroCore.getModeSessionLabel('focus', '5') !== 'SESSION 05 // DEEP WORK') process.exit(5);

        // Break modes return dedicated cyberpunk status labels
        if (PomodoroCore.getModeSessionLabel('shortBreak', 1) !== 'RECHARGE // SHORT BREAK') process.exit(6);
        if (PomodoroCore.getModeSessionLabel('shortBreak', 4) !== 'RECHARGE // SHORT BREAK') process.exit(7);
        if (PomodoroCore.getModeSessionLabel('longBreak', 4) !== 'REST // LONG BREAK') process.exit(8);
        if (PomodoroCore.getModeSessionLabel('longBreak', 8) !== 'REST // LONG BREAK') process.exit(9);

        console.log('SUCCESS');
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_get_mode_session_label_invalid_and_fallback(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Unknown or invalid mode must fall back gracefully to focus session label instead of longBreak
        if (PomodoroCore.getModeSessionLabel('unknown', 1) !== 'SESSION 01 // DEEP WORK') process.exit(1);
        if (PomodoroCore.getModeSessionLabel('custom', 3) !== 'SESSION 03 // DEEP WORK') process.exit(2);
        if (PomodoroCore.getModeSessionLabel(null, 1) !== 'SESSION 01 // DEEP WORK') process.exit(3);
        if (PomodoroCore.getModeSessionLabel(undefined, 2) !== 'SESSION 02 // DEEP WORK') process.exit(4);
        if (PomodoroCore.getModeSessionLabel('', 1) !== 'SESSION 01 // DEEP WORK') process.exit(5);
        if (PomodoroCore.getModeSessionLabel('__proto__', 1) !== 'SESSION 01 // DEEP WORK') process.exit(6);

        // Fallback with invalid cycle numbers
        if (PomodoroCore.getModeSessionLabel('focus', NaN) !== 'SESSION 01 // DEEP WORK') process.exit(7);
        if (PomodoroCore.getModeSessionLabel('focus', 0) !== 'SESSION 01 // DEEP WORK') process.exit(8);
        if (PomodoroCore.getModeSessionLabel('focus', -3) !== 'SESSION 01 // DEEP WORK') process.exit(9);

        console.log('SUCCESS');
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_get_mode_stroke_standard_modes(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (typeof PomodoroCore.getModeStroke !== 'function') {
            console.error('FAIL: PomodoroCore.getModeStroke is not a function');
            process.exit(1);
        }

        // Standard modes map to correct CSS variable references
        if (PomodoroCore.getModeStroke('focus') !== 'var(--accent)') process.exit(2);
        if (PomodoroCore.getModeStroke('shortBreak') !== 'var(--green)') process.exit(3);
        if (PomodoroCore.getModeStroke('longBreak') !== 'var(--pink)') process.exit(4);

        console.log('SUCCESS');
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_get_mode_stroke_invalid_and_fallback(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Invalid or missing modes must fall back to var(--accent) instead of var(--pink)
        if (PomodoroCore.getModeStroke('unknown') !== 'var(--accent)') process.exit(1);
        if (PomodoroCore.getModeStroke(null) !== 'var(--accent)') process.exit(2);
        if (PomodoroCore.getModeStroke(undefined) !== 'var(--accent)') process.exit(3);
        if (PomodoroCore.getModeStroke('') !== 'var(--accent)') process.exit(4);
        if (PomodoroCore.getModeStroke(123) !== 'var(--accent)') process.exit(5);
        if (PomodoroCore.getModeStroke('__proto__') !== 'var(--accent)') process.exit(6);

        console.log('SUCCESS');
        """
        proc = subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_index_html_wires_mode_visual_helpers(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn(
            "PomodoroCore.getModeStroke",
            html,
            "index.html must use PomodoroCore.getModeStroke to decouple mode stroke styling"
        )
        self.assertIn(
            "PomodoroCore.getModeSessionLabel",
            html,
            "index.html must use PomodoroCore.getModeSessionLabel to decouple session label formatting"
        )


if __name__ == "__main__":
    unittest.main()
