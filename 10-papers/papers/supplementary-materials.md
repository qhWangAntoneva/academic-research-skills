# Supplementary Materials — CBV Manuscript

## Contents

### S1: Per-Dataset Results Table
- File: supplementary_table_s1.csv
- Description: Full per-dataset results (58 datasets × 10 indices × 5 seeds)
- Contains: dataset name, true k, estimated k per seed, correctness flags

### S2: Pairwise Complementarity Matrix
- File: supplementary_fig2.csv
- Description: Full complementarity matrix across all index pairs

### S3: Additional Figures
The following figures are included in the `figures/` directory:
- `figure1_accuracy_comparison.png` — Bar chart of accuracy across 10 indices
- `figure2_rank_distribution.png` — CBV rank distribution heatmap
- `figure3_agreement_matrix.png` — Cross-index agreement visualization
- `figure4_failure_categories.png` — CBV failure category breakdown
- `cbv_vs_gap_scatter.png` — Per-dataset CBV vs. Gap accuracy scatter
- `jaccard_complementarity.png` — Jaccard similarity between CBV and geometric CVIs
- `complementarity_heatmap.png` — Correctness matrix across all indices and datasets

### S4: Post-Hoc Pairwise Statistical Tests
- File: supplementary_posthoc.csv
- Description: Full Wilcoxon signed-rank test results with Holm–Bonferroni correction

### S5: Core CBV Implementation
- Source: `cbv/index.py` — CBVIndex + sheather_jones_bandwidth
- Source: `cbv/hybrid.py` — CBVHybrid
- Source: `cbv/projection.py` — CBVProjection
- Source: `run_benchmark.py` — Full benchmark runner
