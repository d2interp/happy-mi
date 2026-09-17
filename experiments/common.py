"""Shared reproducibility helpers; no model or dataset downloads."""

import json
from pathlib import Path
import random

import numpy as np
import torch


def seed_all(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(1)


def recovery(clean, corrupted, patched, atol=1e-6):
    """A ratio, not a probability; undefined for a vanishing baseline gap."""
    gap = clean - corrupted
    if abs(gap) < atol:
        raise ValueError("Baseline gap is too small for a recovery ratio")
    return (patched - corrupted) / gap


def save_json(result, name):
    directory = Path(__file__).resolve().parents[1] / 'artifacts'
    directory.mkdir(exist_ok=True)
    path = directory / name
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    return path
