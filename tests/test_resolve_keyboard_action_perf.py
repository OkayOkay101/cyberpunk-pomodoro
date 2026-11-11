import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestResolveKeyboardActionPerformance(unittest.TestCase):
    def test_resolve_keyboard_action_avoids_unconditional_to_upper_case(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const fnStr = PomodoroCore.resolveKeyboardAction.toString();
        // The unoptimized implementation unconditionally calls .toUpperCase() on targetTagName:
        // const tag = (typeof targetTagName === 'string') ? targetTagName.toUpperCase() : '';
        if (/targetTagName\\.toUpperCase\\(\\)\\s*:\\s*''/.test(fnStr)) {
            console.error('FAIL: resolveKeyboardAction still unconditionally converts targetTagName to uppercase on every keypress');
            process.exit(2);
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

    def test_resolve_keyboard_action_exact_equality_with_baseline(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        function baselineResolveKeyboardAction(params) {
            if (!params || typeof params !== 'object') return null;
            const { key, code, targetTagName, isModalOpen } = params;

            if (isModalOpen) {
                if (key === 'Escape') return 'closeModal';
                return null;
            }

            const tag = (typeof targetTagName === 'string') ? targetTagName.toUpperCase() : '';
            if (tag === 'INPUT' || tag === 'TEXTAREA') {
                return null;
            }

            if (code === 'Space' && ['BUTTON', 'SELECT', 'OPTION', 'A', 'AREA', 'SUMMARY', 'AUDIO', 'VIDEO'].includes(tag)) {
                return null;
            }

            if (code === 'Space') return 'toggleTimer';
            if (key === 'r' || key === 'R') return 'resetTimer';
            if (key === 's' || key === 'S') return 'skipMode';
            if (key === 'm' || key === 'M') return 'toggleMute';
            if (key === 'f' || key === 'F') return 'toggleFullscreen';

            return null;
        }

        const cases = [
            // Standard shortcuts on common elements
            { key: ' ', code: 'Space', targetTagName: 'BODY', isModalOpen: false },
            { key: ' ', code: 'Space', targetTagName: 'BUTTON', isModalOpen: false },
            { key: ' ', code: 'Space', targetTagName: 'select', isModalOpen: false },
            { key: ' ', code: 'Space', targetTagName: 'A', isModalOpen: false },
            { key: 'r', code: 'KeyR', targetTagName: 'BODY', isModalOpen: false },
            { key: 'R', code: 'KeyR', targetTagName: 'BUTTON', isModalOpen: false },
            { key: 's', code: 'KeyS', targetTagName: 'DIV', isModalOpen: false },
            { key: 'S', code: 'KeyS', targetTagName: 'MAIN', isModalOpen: false },
            { key: 'm', code: 'KeyM', targetTagName: 'SECTION', isModalOpen: false },
            { key: 'M', code: 'KeyM', targetTagName: 'HEADER', isModalOpen: false },
            { key: 'f', code: 'KeyF', targetTagName: 'NAV', isModalOpen: false },
            { key: 'F', code: 'KeyF', targetTagName: 'FOOTER', isModalOpen: false },

            // Unmapped keys
            { key: 'a', code: 'KeyA', targetTagName: 'BODY', isModalOpen: false },
            { key: 'Tab', code: 'Tab', targetTagName: 'BUTTON', isModalOpen: false },
            { key: 'ArrowRight', code: 'ArrowRight', targetTagName: 'BUTTON', isModalOpen: false },
            { key: 'ArrowLeft', code: 'ArrowLeft', targetTagName: 'BUTTON', isModalOpen: false },
            { key: 'ArrowDown', code: 'ArrowDown', targetTagName: 'BUTTON', isModalOpen: false },
            { key: 'ArrowUp', code: 'ArrowUp', targetTagName: 'BUTTON', isModalOpen: false },
            { key: 'Home', code: 'Home', targetTagName: 'BUTTON', isModalOpen: false },
            { key: 'End', code: 'End', targetTagName: 'BUTTON', isModalOpen: false },
            { key: 'Enter', code: 'Enter', targetTagName: 'BUTTON', isModalOpen: false },

            // Input suppression (uppercase, lowercase, mixed case)
            { key: 'r', code: 'KeyR', targetTagName: 'INPUT', isModalOpen: false },
            { key: 'r', code: 'KeyR', targetTagName: 'input', isModalOpen: false },
            { key: 'r', code: 'KeyR', targetTagName: 'Input', isModalOpen: false },
            { key: ' ', code: 'Space', targetTagName: 'TEXTAREA', isModalOpen: false },
            { key: ' ', code: 'Space', targetTagName: 'textarea', isModalOpen: false },
            { key: ' ', code: 'Space', targetTagName: 'TextArea', isModalOpen: false },

            // Modal open states
            { key: 'Escape', code: 'Escape', targetTagName: 'BODY', isModalOpen: true },
            { key: 'Escape', code: 'Escape', targetTagName: 'INPUT', isModalOpen: true },
            { key: ' ', code: 'Space', targetTagName: 'BODY', isModalOpen: true },
            { key: 'r', code: 'KeyR', targetTagName: 'BODY', isModalOpen: true },
            { key: 'Escape', code: 'Escape', targetTagName: 'BODY', isModalOpen: false },

            // Prototype keys / edge property lookups
            { key: 'toString', code: 'KeyT', targetTagName: 'BODY', isModalOpen: false },
            { key: 'valueOf', code: 'KeyV', targetTagName: 'BODY', isModalOpen: false },
            { key: 'constructor', code: 'KeyC', targetTagName: 'BODY', isModalOpen: false },
            { key: '__proto__', code: 'KeyP', targetTagName: 'BODY', isModalOpen: false },

            // Non-string or missing targetTagName
            { key: 'r', code: 'KeyR', targetTagName: null, isModalOpen: false },
            { key: 'r', code: 'KeyR', targetTagName: undefined, isModalOpen: false },
            { key: 'r', code: 'KeyR', targetTagName: 123, isModalOpen: false },
            { key: 'r', code: 'KeyR', targetTagName: {}, isModalOpen: false },

            // Invalid / edge param structures
            null,
            undefined,
            'invalid',
            123,
            {},
            { isModalOpen: true },
            { code: 'Space' }
        ];

        for (const input of cases) {
            const actual = PomodoroCore.resolveKeyboardAction(input);
            const expected = baselineResolveKeyboardAction(input);
            if (actual !== expected) {
                console.error(`Mismatch for input: ${JSON.stringify(input)} -> expected: ${expected}, actual: ${actual}`);
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


if __name__ == "__main__":
    unittest.main()
