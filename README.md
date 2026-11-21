---
license: cc-by-4.0
pretty_name: NAVSIM Planner Comparison
tags:
  - autonomous-driving
  - end-to-end-planning
  - navsim
  - benchmark
configs:
  - config_name: results
    data_files: results.csv
  - config_name: efficiency
    data_files: efficiency.csv
---

# navsim-sparsedrive-vs-diffusiondrive

Comparison of SparseDrive v2, DiffusionDrive, and DiffusionDrive v2 on NAVSIM,
covering planning scores, sub-metrics, efficiency, and where each model falls short.

## Contents
- `results.csv`: one row per model × split × metric version
- `efficiency.csv`: params, FLOPs, latency, memory
- `scenarios.csv` (optional): per-scenario-type breakdown

## Evaluation protocol
- Benchmark: NAVSIM <version>, split <navtest / navhard>
- Metric: <PDMS / EPDMS>
- Inputs: <cameras / LiDAR>, backbone: <...>
- Hardware for latency: <GPU>, batch size <n>

## Provenance
Each row has a `source` field: `paper` (reported) or `reproduced`
(with checkpoint, commit hash, and seed).

## Limitations
<differences in protocol, backbone, or training data between models>

## Licensing and citation
Only results and plots are released. NAVSIM / nuPlan / OpenScene data is not
redistributed. Please cite the original papers: <bibtex>.
