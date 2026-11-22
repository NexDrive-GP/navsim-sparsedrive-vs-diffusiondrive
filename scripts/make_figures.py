"""Regenerate the static figures (for GitHub / dataset card) from results.csv and scenarios.csv.

Usage (from the dataset repo root):  python scripts/make_figures.py
Models come from results.csv. A row with an empty `score` is drawn as a reserved,
hatched "pending" slot, so adding a model's rows to both CSVs and re-running is all it takes.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "figures"); os.makedirs(OUT, exist_ok=True)
res = pd.read_csv(os.path.join(ROOT, "results.csv"))
scen = pd.read_csv(os.path.join(ROOT, "scenarios.csv"))

models = res["model"].tolist()
pending = set(res.loc[res["score"].isna(), "model"])
PALETTE = ["#4C78A8", "#F58518", "#54A24B", "#B279A2", "#E45756", "#72B7B2"]
color = {m: PALETTE[i % len(PALETTE)] for i, m in enumerate(models)}
label = lambda m: f"{m} (pending)" if m in pending else m
SUB = ["NC", "DAC", "DDC", "TTC", "EP", "Comf"]
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})

def legend_handles():
    return [Patch(facecolor="white" if m in pending else color[m], edgecolor=color[m],
                  hatch="//" if m in pending else None, linestyle="--" if m in pending else "-",
                  label=label(m)) for m in models]

# 1) PDMS + sub-metrics (percent). Axis starts at 70 to separate the models; stated in the title.
fig, ax = plt.subplots(figsize=(11, 4.8))
metrics = ["PDMS"] + SUB
w = 0.8 / len(models); x = np.arange(len(metrics))
for i, m in enumerate(models):
    pos = x - 0.4 + w * (i + 0.5)
    if m in pending:
        ax.bar(pos, [2.0] * len(metrics), w * 0.92, bottom=70, fill=False, hatch="//",
               edgecolor=color[m], linestyle="--", linewidth=0.8, alpha=0.7)
        for p_ in pos: ax.text(p_, 72.3, "?", ha="center", va="bottom", fontsize=9, color=color[m])
        continue
    row = res[res.model == m].iloc[0]
    vals = [row["score"]] + [row[k] for k in SUB]
    bars = ax.bar(pos, vals, w * 0.92, color=color[m])
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.3, f"{v:.2f}", ha="center", va="bottom", fontsize=7)
ax.set_xticks(x); ax.set_xticklabels(metrics); ax.set_ylim(70, 101); ax.set_ylabel("Score (%)")
ax.set_title("NAVSIM navtest (PDMS): aggregate and sub-metrics  (y-axis starts at 70)")
ax.legend(handles=legend_handles(), loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=len(models), frameon=False)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "submetrics.png"), dpi=160); plt.close(fig)

# 2) Failure counts: scenarios scoring 0 on a metric (computed from scenarios.csv). Axis starts at 0.
fm = ["NC", "DAC", "DDC", "TTC", "PDMS"]
names = {"NC": "NC = 0\n(collision)", "DAC": "DAC = 0\n(off-road)", "DDC": "DDC = 0\n(wrong way)",
         "TTC": "TTC = 0\n(time-to-collision)", "PDMS": "PDMS = 0\n(total failure)"}
fig, ax = plt.subplots(figsize=(10, 4.6)); x = np.arange(len(fm))
for i, m in enumerate(models):
    pos = x - 0.4 + w * (i + 0.5)
    if m in pending:
        real = [mm for mm in models if mm not in pending]
        stub = 0.04 * max((scen[scen.model.isin(real)][fm] == 0).groupby(scen.model).sum().max().max(), 1)
        ax.bar(pos, [stub] * len(fm), w * 0.92, fill=False, hatch="//", edgecolor=color[m],
               linestyle="--", linewidth=0.8, alpha=0.7)
        for p_ in pos: ax.text(p_, stub + 5, "?", ha="center", va="bottom", fontsize=9, color=color[m])
        continue
    d = scen[scen.model == m]; vals = [(d[k] == 0).sum() for k in fm]
    bars = ax.bar(pos, vals, w * 0.92, color=color[m])
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 5, str(v), ha="center", va="bottom", fontsize=8)
ax.set_xticks(x); ax.set_xticklabels([names[k] for k in fm]); ax.set_ylabel("Scenarios (of 12,146)")
ax.set_title("Failure counts on navtest (lower is better)")
ax.legend(handles=legend_handles(), loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=len(models), frameon=False)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "failures.png"), dpi=160); plt.close(fig)

# 3) ECDF of per-scenario PDMS (fraction of scenarios scoring at most x).
fig, ax = plt.subplots(figsize=(8, 4.6))
for m in models:
    if m in pending: ax.plot([], [], color=color[m], linestyle="--", label=label(m)); continue
    v = np.sort(scen.loc[scen.model == m, "PDMS"].values)
    ax.plot(v, np.arange(1, len(v) + 1) / len(v), color=color[m], label=m, linewidth=1.8)
ax.set_xlabel("Per-scenario PDMS"); ax.set_ylabel("Fraction of scenarios ≤ x")
ax.set_title("Distribution of per-scenario PDMS (curve further right/lower is better)")
ax.legend(frameon=False, loc="upper left"); ax.grid(alpha=0.25)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "pdms_ecdf.png"), dpi=160); plt.close(fig)
print("figures written to", OUT)
