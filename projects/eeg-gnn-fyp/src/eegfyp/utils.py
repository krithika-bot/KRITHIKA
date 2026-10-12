from __future__ import annotations

import copy
import json
import platform
import random
import subprocess
from pathlib import Path

import numpy as np
import yaml


def load_config(path: str | Path = "configs/default.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch

        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


def env_info() -> dict:
    """Versions + git commit, saved next to every result for reproducibility."""
    info = {"python": platform.python_version(), "platform": platform.platform()}
    for name in ["numpy", "scipy", "sklearn", "pandas", "mne", "torch"]:
        try:
            mod = __import__(name)
            info[name] = getattr(mod, "__version__", "unknown")
        except ImportError:
            info[name] = None
    try:
        info["git_commit"] = (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
        )
    except Exception:
        info["git_commit"] = None
    return info


def save_run_info(out_dir: str | Path, cfg: dict, extra: dict | None = None) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {"env": env_info(), "config": copy.deepcopy(cfg)}
    if extra:
        payload.update(extra)
    with open(out_dir / "run_info.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
