"""Add or update a model from a NAVSIM per-scenario results file (.csv or .xlsx).

    python scripts/add_model.py path/to/results.xlsx --model "SparseDrive v2" \
        --checkpoint <ckpt> --commit <hash> --seed 0 --backbone ResNet-34 --sensors "3 cams"

Appends the model's scenarios to scenarios.csv and fills its row in results.csv (aggregates are
recomputed from the scenarios, as percent). Then run scripts/make_figures.py. Re-running replaces
the model's previous rows. PDMS only: the file must have the six PDMS sub-metrics and `score`.
"""
import argparse, os
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP = {"no_at_fault_collisions": "NC", "drivable_area_compliance": "DAC", "driving_direction_compliance": "DDC",
       "time_to_collision_within_bound": "TTC", "ego_progress": "EP", "comfort": "Comf", "score": "PDMS"}

ap = argparse.ArgumentParser()
ap.add_argument("file"); ap.add_argument("--model", required=True)
ap.add_argument("--split", default="navtest"); ap.add_argument("--source", default="reproduced")
for k in ("checkpoint", "commit", "seed", "backbone", "sensors"): ap.add_argument(f"--{k}", default="")
a = ap.parse_args()

d = pd.read_excel(a.file) if a.file.lower().endswith((".xlsx", ".xls")) else pd.read_csv(a.file)
d = d.drop(columns=[c for c in d.columns if str(c).startswith("Unnamed")])
missing = [c for c in MAP if c not in d.columns]
if missing: raise SystemExit(f"missing columns: {missing}")
d = d[d["token"] != "average"].rename(columns=MAP)
d.insert(0, "model", a.model); d = d[["model", "token", "NC", "DAC", "DDC", "TTC", "EP", "Comf", "PDMS"]]
if d["token"].duplicated().any(): raise SystemExit("duplicate tokens in input")

sp = os.path.join(ROOT, "scenarios.csv"); rp = os.path.join(ROOT, "results.csv")
s = pd.read_csv(sp); s = pd.concat([s[s.model != a.model], d], ignore_index=True); s.to_csv(sp, index=False)

r = pd.read_csv(rp, dtype=str, keep_default_na=False)
m = d[["NC", "DAC", "DDC", "TTC", "EP", "Comf", "PDMS"]].mean() * 100
row = {c: "" for c in r.columns}
row.update(model=a.model, split=a.split, metric_version="PDMS", backbone=a.backbone, sensors=a.sensors,
           score=f"{m['PDMS']:.2f}", source=a.source, checkpoint=a.checkpoint, commit=a.commit, seed=a.seed,
           **{k: f"{m[k]:.2f}" for k in ["NC", "DAC", "DDC", "TTC", "EP", "Comf"]})
if (r.model == a.model).any():
    r.loc[r.model == a.model, list(row)] = list(row.values())
else:
    r = pd.concat([r, pd.DataFrame([row])], ignore_index=True)
r.to_csv(rp, index=False)
print(f"{a.model}: {len(d)} scenarios, PDMS {m['PDMS']:.2f}")
