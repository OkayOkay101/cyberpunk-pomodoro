import os
import sys
import py_compile

def check_syntax():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    errors = 0
    for dirpath, _, filenames in os.walk(root):
        if any(ignored in dirpath for ignored in ['.git', '__pycache__', 'venv', '.venv']):
            continue
        for f in filenames:
            if f.endswith('.py'):
                full_path = os.path.join(dirpath, f)
                try:
                    py_compile.compile(full_path, doraise=True)
                except py_compile.PyCompileError as err:
                    print(f"Syntax error in {full_path}: {err}")
                    errors += 1
    if errors > 0:
        sys.exit(1)
    print("Python syntax check passed: 0 errors.")

if __name__ == '__main__':
    check_syntax()
