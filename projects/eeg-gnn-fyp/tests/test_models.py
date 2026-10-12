"""Torch wiring tests. Run these FIRST on your machine / Colab (they were not executable where the
code was written):   python tests/run_tests.py   (or pytest tests/test_models.py)"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

try:
    import torch
    HAVE_TORCH = True
except ImportError:
    HAVE_TORCH = False

if HAVE_TORCH:
    from eegfyp.graphs import build_adjacency, normalize_adjacency
    from eegfyp.models import EEGGraphNet, EEGNet, count_params
    from eegfyp.data import make_synthetic

C, T = 32, 320


def _ahat(kind="distance"):
    ds = make_synthetic(n_subjects=2, trials_per_subject=4, n_channels=C, n_times=T)
    return normalize_adjacency(build_adjacency(kind, ds.pos, None, k=4))


def test_eegnet_shapes():
    m = EEGNet(C, T)
    assert m(torch.randn(5, C, T)).shape == (5, 2)


def test_gcn_shapes_and_equal_param_counts_across_graphs():
    counts = set()
    for kind in ["identity", "uniform", "random", "distance"]:
        m = EEGGraphNet(C, _ahat(kind))
        assert m(torch.randn(5, C, T)).shape == (5, 2)
        counts.add(count_params(m))
    assert len(counts) == 1, counts      # fair ablation: only the adjacency differs


def test_graph_changes_the_function_but_identity_blocks_message_passing():
    torch.manual_seed(0)
    x = torch.randn(3, C, T)
    m_id = EEGGraphNet(C, _ahat("identity")).eval()
    m_g = EEGGraphNet(C, _ahat("distance")).eval()
    m_g.load_state_dict({k: v for k, v in m_id.state_dict().items() if k != "a_hat"} | {"a_hat": m_g.a_hat}, strict=True)
    assert not torch.allclose(m_id(x), m_g(x))     # same weights, different graph -> different output
    h_id = m_id.encoder(x)
    for conv, norm in zip(m_id.convs, m_id.norms):
        h_id = torch.nn.functional.elu(norm(conv(h_id, m_id.a_hat)))
    x2 = x.clone(); x2[:, 7] += 5.0                # perturb ONE electrode
    h2 = m_id.encoder(x2)
    for conv, norm in zip(m_id.convs, m_id.norms):
        h2 = torch.nn.functional.elu(norm(conv(h2, m_id.a_hat)))
    other = [i for i in range(C) if i != 7]
    assert torch.allclose(h_id[:, other], h2[:, other], atol=1e-5)   # no leakage between nodes with identity graph


def test_models_can_overfit_a_tiny_batch():
    torch.manual_seed(0)
    x = torch.randn(16, C, T); y = torch.tensor([0, 1] * 8)
    for model in [EEGNet(C, T, dropout=0.0), EEGGraphNet(C, _ahat(), dropout=0.0)]:
        opt = torch.optim.Adam(model.parameters(), lr=5e-3)
        first = None
        for _ in range(60):
            opt.zero_grad()
            loss = torch.nn.functional.cross_entropy(model(x), y)
            loss.backward(); opt.step()
            first = first if first is not None else loss.item()
        assert loss.item() < 0.5 * first, (type(model).__name__, first, loss.item())
