"""Training loop. Model selection (early stopping) uses ONLY validation subjects drawn from the
training subjects; the test subjects are touched once, at the end, with the best-validation weights."""
from __future__ import annotations

import time

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset


def get_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


@torch.no_grad()
def predict_logits(model, X: np.ndarray, device, batch: int = 256) -> torch.Tensor:
    model.eval()
    outs = []
    for i in range(0, len(X), batch):
        outs.append(model(torch.from_numpy(X[i:i + batch]).to(device)).float().cpu())
    return torch.cat(outs)


def predict_proba(model, X: np.ndarray, device) -> np.ndarray:
    return torch.softmax(predict_logits(model, X, device), dim=1)[:, 1].numpy()


def fit_predict(model, X_tr, y_tr, X_val, y_val, X_te, train_cfg: dict, device, seed: int):
    """Returns (test probabilities of class 1, per-epoch history, best epoch)."""
    model.to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=train_cfg["lr"], weight_decay=train_cfg["weight_decay"])
    epochs = int(train_cfg["epochs"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
    gen = torch.Generator()
    gen.manual_seed(seed)
    loader = DataLoader(
        TensorDataset(torch.from_numpy(X_tr), torch.from_numpy(y_tr).long()),
        batch_size=int(train_cfg["batch_size"]), shuffle=True, generator=gen,
    )
    y_val_t = torch.from_numpy(y_val).long()
    best = {"acc": -1.0, "loss": float("inf"), "epoch": 0, "state": None}
    history, bad = [], 0
    for epoch in range(1, epochs + 1):
        t0 = time.time()
        model.train()
        total, n = 0.0, 0
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad(set_to_none=True)
            loss = F.cross_entropy(model(xb), yb)
            loss.backward()
            opt.step()
            total += loss.item() * len(xb)
            n += len(xb)
        sched.step()
        logits = predict_logits(model, X_val, device)
        val_loss = F.cross_entropy(logits, y_val_t).item()
        val_acc = (logits.argmax(1) == y_val_t).float().mean().item()
        history.append({"epoch": epoch, "train_loss": total / n, "val_loss": val_loss,
                        "val_acc": val_acc, "sec": time.time() - t0})
        better = val_acc > best["acc"] + 1e-9 or (abs(val_acc - best["acc"]) <= 1e-9 and val_loss < best["loss"])
        if better:
            best.update(acc=val_acc, loss=val_loss, epoch=epoch,
                        state={k: v.detach().cpu().clone() for k, v in model.state_dict().items()})
            bad = 0
        else:
            bad += 1
            if bad >= int(train_cfg["patience"]):
                break
    model.load_state_dict(best["state"])
    return predict_proba(model, X_te, device), history, best["epoch"]
