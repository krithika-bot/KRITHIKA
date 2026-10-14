"""Installed command-line entry point."""
from pathlib import Path
import runpy


def main() -> None:
    script = Path(__file__).resolve().parents[2] / "scripts" / "run_analysis.py"
    runpy.run_path(str(script), run_name="__main__")
