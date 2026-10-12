"""Tiny test runner so you don't need pytest:  python tests/run_tests.py"""
import importlib.util
import sys
import time
import traceback
from pathlib import Path

root = Path(__file__).parent
failed = 0
for f in sorted(root.glob("test_*.py")):
    spec = importlib.util.spec_from_file_location(f.stem, f)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if f.stem == "test_models" and not getattr(mod, "HAVE_TORCH", False):
        print(f"SKIP  {f.stem} (torch not installed)")
        continue
    for name in [n for n in dir(mod) if n.startswith("test_")]:
        t0 = time.time()
        try:
            getattr(mod, name)()
            print(f"PASS  {f.stem}::{name}  ({time.time() - t0:.1f}s)")
        except Exception:
            failed += 1
            print(f"FAIL  {f.stem}::{name}")
            traceback.print_exc()
print("\nALL PASSED" if not failed else f"\n{failed} FAILED")
sys.exit(1 if failed else 0)
