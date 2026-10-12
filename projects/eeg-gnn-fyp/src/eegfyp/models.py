"""PyTorch models. No torch_geometric dependency: the GCN is a few lines of dense algebra.

EEGNet     : compact CNN (Lawhern et al., 2018) - strong non-graph deep baseline.
EEGGraphNet: shared per-electrode temporal encoder -> graph convolutions over a FIXED electrode
             graph -> flatten (keeps electrode identity, which matters for lateralised motor
             imagery) -> linear classifier. Only the adjacency matrix differs between the
             ablation variants, so every variant has exactly the same number of parameters.
"""
from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


def count_params(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


class EEGNet(nn.Module):
    def __init__(self, n_channels: int, n_times: int, n_classes: int = 2, f1: int = 8, d: int = 2,
                 f2: int = 16, kernel: int = 80, dropout: float = 0.5):
        super().__init__()
        self.block1 = nn.Sequential(
            nn.Conv2d(1, f1, (1, kernel), padding="same", bias=False),
            nn.BatchNorm2d(f1),
            nn.Conv2d(f1, f1 * d, (n_channels, 1), groups=f1, bias=False),   # depthwise spatial filters
            nn.BatchNorm2d(f1 * d),
            nn.ELU(),
            nn.AvgPool2d((1, 4)),
            nn.Dropout(dropout),
        )
        self.block2 = nn.Sequential(
            nn.Conv2d(f1 * d, f1 * d, (1, 16), padding="same", groups=f1 * d, bias=False),
            nn.Conv2d(f1 * d, f2, 1, bias=False),                              # separable conv
            nn.BatchNorm2d(f2),
            nn.ELU(),
            nn.AvgPool2d((1, 8)),
            nn.Dropout(dropout),
        )
        was_training = self.training
        self.eval()
        with torch.no_grad():
            n_feat = self._features(torch.zeros(1, n_channels, n_times)).shape[1]
        self.train(was_training)
        self.head = nn.Linear(n_feat, n_classes)

    def _features(self, x):                      # x: (B, C, T)
        x = self.block2(self.block1(x.unsqueeze(1)))
        return x.flatten(1)

    def forward(self, x):
        return self.head(self._features(x))


class NodeEncoder(nn.Module):
    """Temporal filter bank shared by all electrodes -> log band-power-like feature per filter."""

    def __init__(self, n_filters: int = 16, kernel: int = 40):
        super().__init__()
        self.conv = nn.Conv1d(1, n_filters, kernel, padding="same", bias=False)
        self.bn = nn.BatchNorm1d(n_filters)

    def forward(self, x):                        # x: (B, C, T)
        b, c, t = x.shape
        h = self.conv(x.reshape(b * c, 1, t))    # (B*C, F, T)
        h = torch.log(h.pow(2).mean(dim=-1) + 1e-6)   # (B*C, F): log power of each filtered signal
        h = self.bn(h)
        return h.reshape(b, c, -1)               # (B, C, F)


class GraphConv(nn.Module):
    def __init__(self, in_f: int, out_f: int):
        super().__init__()
        self.lin = nn.Linear(in_f, out_f)

    def forward(self, h, a_hat):                 # h: (B, C, F), a_hat: (C, C)
        return torch.einsum("ij,bjf->bif", a_hat, self.lin(h))


class EEGGraphNet(nn.Module):
    def __init__(self, n_channels: int, a_hat: np.ndarray, n_classes: int = 2, n_filters: int = 16,
                 kernel: int = 40, hidden: int = 32, n_layers: int = 2, dropout: float = 0.5):
        super().__init__()
        assert a_hat.shape == (n_channels, n_channels)
        self.register_buffer("a_hat", torch.as_tensor(a_hat, dtype=torch.float32))
        self.encoder = NodeEncoder(n_filters, kernel)
        dims = [n_filters] + [hidden] * n_layers
        self.convs = nn.ModuleList([GraphConv(dims[i], dims[i + 1]) for i in range(n_layers)])
        self.norms = nn.ModuleList([nn.LayerNorm(hidden) for _ in range(n_layers)])
        self.drop = nn.Dropout(dropout)
        self.head = nn.Linear(n_channels * hidden, n_classes)

    def forward(self, x):                        # x: (B, C, T)
        h = self.encoder(x)
        for conv, norm in zip(self.convs, self.norms):
            h = self.drop(F.elu(norm(conv(h, self.a_hat))))
        return self.head(h.flatten(1))
