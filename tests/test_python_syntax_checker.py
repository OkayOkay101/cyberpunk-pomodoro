import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class TestPythonSyntaxChecker(unittest.TestCase):
    def test_checker_does_not_write_bytecode_artifacts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            scripts_dir = root / "scripts"
            tests_dir = root / "tests"
            scripts_dir.mkdir()
            tests_dir.mkdir()
            shutil.copy2(REPO_ROOT / "scripts" / "check_python_syntax.py", scripts_dir)
            (tests_dir / "sample.py").write_text("value = 1\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(scripts_dir / "check_python_syntax.py")],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            artifacts = list(root.rglob("*.pyc")) + list(root.rglob("__pycache__"))
            self.assertEqual(artifacts, [], f"Bytecode artifacts created: {artifacts}")


if __name__ == "__main__":
    unittest.main()
