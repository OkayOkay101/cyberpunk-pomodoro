import sys
import tokenize
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent
    py_files = list(root.glob("tests/**/*.py")) + [Path(__file__)]
    for py_file in py_files:
        try:
            with tokenize.open(py_file) as source_file:
                compile(source_file.read(), str(py_file), "exec")
        except Exception as e:
            print(f"Syntax error in {py_file}: {e}", file=sys.stderr)
            return 1
    print(f"Checked {len(py_files)} Python file(s): syntax OK.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
