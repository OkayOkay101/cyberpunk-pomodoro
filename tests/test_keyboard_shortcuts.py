import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestKeyboardShortcuts(unittest.TestCase):
    def test_resolve_keyboard_action_normal_shortcuts(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const cases = [
            [{ code: 'Space', key: ' ', targetTagName: 'BODY', isModalOpen: false }, 'toggleTimer'],
            [{ code: 'KeyR', key: 'r', targetTagName: 'BODY', isModalOpen: false }, 'resetTimer'],
            [{ code: 'KeyR', key: 'R', targetTagName: 'BUTTON', isModalOpen: false }, 'resetTimer'],
            [{ code: 'KeyS', key: 's', targetTagName: 'DIV', isModalOpen: false }, 'skipMode'],
            [{ code: 'KeyS', key: 'S', targetTagName: 'BODY', isModalOpen: false }, 'skipMode'],
            [{ code: 'KeyM', key: 'm', targetTagName: 'BODY', isModalOpen: false }, 'toggleMute'],
            [{ code: 'KeyM', key: 'M', targetTagName: 'BODY', isModalOpen: false }, 'toggleMute'],
            [{ code: 'KeyF', key: 'f', targetTagName: 'BODY', isModalOpen: false }, 'toggleFullscreen'],
            [{ code: 'KeyF', key: 'F', targetTagName: 'BODY', isModalOpen: false }, 'toggleFullscreen'],
            [{ code: 'KeyA', key: 'a', targetTagName: 'BODY', isModalOpen: false }, null],
            [{ code: 'Enter', key: 'Enter', targetTagName: 'BODY', isModalOpen: false }, null]
        ];

        for (const [params, expected] of cases) {
            const actual = PomodoroCore.resolveKeyboardAction(params);
            if (actual !== expected) {
                console.error(`Mismatch for ${JSON.stringify(params)}: expected ${expected}, got ${actual}`);
                process.exit(1);
            }
        }
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

    def test_resolve_keyboard_action_suppresses_when_input_focused(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const inputCases = [
            { code: 'Space', key: ' ', targetTagName: 'INPUT', isModalOpen: false },
            { code: 'Space', key: ' ', targetTagName: 'input', isModalOpen: false },
            { code: 'Space', key: ' ', targetTagName: 'TEXTAREA', isModalOpen: false },
            { code: 'KeyR', key: 'r', targetTagName: 'INPUT', isModalOpen: false },
            { code: 'KeyS', key: 's', targetTagName: 'INPUT', isModalOpen: false },
            { code: 'KeyM', key: 'm', targetTagName: 'INPUT', isModalOpen: false },
            { code: 'KeyF', key: 'f', targetTagName: 'INPUT', isModalOpen: false }
        ];

        for (const params of inputCases) {
            const actual = PomodoroCore.resolveKeyboardAction(params);
            if (actual !== null) {
                console.error(`Expected null for input focused ${JSON.stringify(params)}, got ${actual}`);
                process.exit(1);
            }
        }
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

    def test_resolve_keyboard_action_modal_behavior(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // When modal is open:
        // Escape should return 'closeModal' regardless of active element
        const escCase1 = PomodoroCore.resolveKeyboardAction({ key: 'Escape', code: 'Escape', targetTagName: 'BODY', isModalOpen: true });
        if (escCase1 !== 'closeModal') {
            console.error('Escape in modal should return closeModal, got ' + escCase1);
            process.exit(1);
        }

        const escCase2 = PomodoroCore.resolveKeyboardAction({ key: 'Escape', code: 'Escape', targetTagName: 'INPUT', isModalOpen: true });
        if (escCase2 !== 'closeModal') {
            console.error('Escape in modal input should return closeModal, got ' + escCase2);
            process.exit(2);
        }

        // All other shortcuts must be blocked when modal is open
        const blockedCases = [
            { code: 'Space', key: ' ', targetTagName: 'BUTTON', isModalOpen: true },
            { code: 'KeyR', key: 'r', targetTagName: 'BODY', isModalOpen: true },
            { code: 'KeyS', key: 's', targetTagName: 'BODY', isModalOpen: true },
            { code: 'KeyM', key: 'm', targetTagName: 'BODY', isModalOpen: true },
            { code: 'KeyF', key: 'f', targetTagName: 'BODY', isModalOpen: true }
        ];

        for (const params of blockedCases) {
            const actual = PomodoroCore.resolveKeyboardAction(params);
            if (actual !== null) {
                console.error(`Shortcut must be blocked in modal: ${JSON.stringify(params)}, got ${actual}`);
                process.exit(3);
            }
        }
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

    def test_resolve_keyboard_action_guards_invalid_and_edge_inputs(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (PomodoroCore.resolveKeyboardAction(null) !== null) process.exit(1);
        if (PomodoroCore.resolveKeyboardAction(undefined) !== null) process.exit(2);
        if (PomodoroCore.resolveKeyboardAction('not an object') !== null) process.exit(3);
        if (PomodoroCore.resolveKeyboardAction({}) !== null) process.exit(4);

        // Escape when modal is closed does nothing
        if (PomodoroCore.resolveKeyboardAction({ key: 'Escape', isModalOpen: false }) !== null) process.exit(5);

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

    def test_index_html_wires_resolve_keyboard_action(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn(
            "PomodoroCore.resolveKeyboardAction",
            html,
            "index.html must use PomodoroCore.resolveKeyboardAction for keyboard shortcuts"
        )
        self.assertIn(
            "settingsModal.classList.contains('open')",
            html,
            "index.html must check modal open state for keyboard routing"
        )

    def test_resolve_keyboard_action_suppresses_with_ctrl_key(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const cases = [
            { code: 'Space', key: ' ', targetTagName: 'BODY', isModalOpen: false, ctrlKey: true },
            { code: 'KeyR', key: 'r', targetTagName: 'BODY', isModalOpen: false, ctrlKey: true },
            { code: 'KeyR', key: 'R', targetTagName: 'BODY', isModalOpen: false, ctrlKey: true },
            { code: 'KeyS', key: 's', targetTagName: 'BODY', isModalOpen: false, ctrlKey: true },
            { code: 'KeyS', key: 'S', targetTagName: 'BODY', isModalOpen: false, ctrlKey: true },
            { code: 'KeyM', key: 'm', targetTagName: 'BODY', isModalOpen: false, ctrlKey: true },
            { code: 'KeyF', key: 'f', targetTagName: 'BODY', isModalOpen: false, ctrlKey: true },
            { code: 'KeyF', key: 'F', targetTagName: 'BODY', isModalOpen: false, ctrlKey: true }
        ];

        for (const params of cases) {
            const actual = PomodoroCore.resolveKeyboardAction(params);
            if (actual !== null) {
                console.error(`Expected null when ctrlKey is true for ${JSON.stringify(params)}, got ${actual}`);
                process.exit(1);
            }
        }
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

    def test_resolve_keyboard_action_suppresses_with_meta_key(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const cases = [
            { code: 'Space', key: ' ', targetTagName: 'BODY', isModalOpen: false, metaKey: true },
            { code: 'KeyR', key: 'r', targetTagName: 'BODY', isModalOpen: false, metaKey: true },
            { code: 'KeyS', key: 's', targetTagName: 'BODY', isModalOpen: false, metaKey: true },
            { code: 'KeyM', key: 'm', targetTagName: 'BODY', isModalOpen: false, metaKey: true },
            { code: 'KeyF', key: 'f', targetTagName: 'BODY', isModalOpen: false, metaKey: true }
        ];

        for (const params of cases) {
            const actual = PomodoroCore.resolveKeyboardAction(params);
            if (actual !== null) {
                console.error(`Expected null when metaKey is true for ${JSON.stringify(params)}, got ${actual}`);
                process.exit(1);
            }
        }
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

    def test_resolve_keyboard_action_suppresses_with_alt_key(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const cases = [
            { code: 'Space', key: ' ', targetTagName: 'BODY', isModalOpen: false, altKey: true },
            { code: 'KeyR', key: 'r', targetTagName: 'BODY', isModalOpen: false, altKey: true },
            { code: 'KeyS', key: 's', targetTagName: 'BODY', isModalOpen: false, altKey: true },
            { code: 'KeyM', key: 'm', targetTagName: 'BODY', isModalOpen: false, altKey: true },
            { code: 'KeyF', key: 'f', targetTagName: 'BODY', isModalOpen: false, altKey: true }
        ];

        for (const params of cases) {
            const actual = PomodoroCore.resolveKeyboardAction(params);
            if (actual !== null) {
                console.error(`Expected null when altKey is true for ${JSON.stringify(params)}, got ${actual}`);
                process.exit(1);
            }
        }
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

    def test_resolve_keyboard_action_modal_escape_with_modifiers(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Escape to close modal should work regardless of modifier flags
        const res = PomodoroCore.resolveKeyboardAction({ key: 'Escape', isModalOpen: true, ctrlKey: false });
        if (res !== 'closeModal') {
            console.error('Escape with modal open should return closeModal, got ' + res);
            process.exit(1);
        }

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

    def test_index_html_passes_modifier_keys(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn(
            "ctrlKey: e.ctrlKey",
            html,
            "index.html must pass ctrlKey to PomodoroCore.resolveKeyboardAction"
        )
        self.assertIn(
            "metaKey: e.metaKey",
            html,
            "index.html must pass metaKey to PomodoroCore.resolveKeyboardAction"
        )
        self.assertIn(
            "altKey: e.altKey",
            html,
            "index.html must pass altKey to PomodoroCore.resolveKeyboardAction"
        )


if __name__ == "__main__":
    unittest.main()
