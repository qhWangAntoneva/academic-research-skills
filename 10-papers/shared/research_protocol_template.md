# Research Protocol Template — 10-Paper Framework

Use this template when planning the execution of any paper in the 10-paper suite.

---

## 1. Title & Scope

- **Paper ID**: `paper-XX`
- **Title**: 
- **Research Question**: 
- **Target Journal**: 
- **Anticipated Contribution**: 

## 2. Data

- **Source(s)**: 
- **Access**: Public / Application required / Proprietary
- **Sample size range**: 
- **Preprocessing needed**: 
- **Ethics / disclosure required**: 

## 3. Methodology Pipeline

### 3.1 Core critband Functions

| Function | Purpose | Parameters |
|----------|---------|------------|
| `critical_bandwidth(x, k, return_ci)` | Primary mode detection | k=2 (default), bootstrap CI |
| `bimodality_strength(x)` | Interpretable strength label | — |
| `silverman_test(x)` | Frequentist significance | Bootstrap iterations |
| `excess_mass(x, n_boot)` | Multi-mode detection | n_boot >= 199 |
| `find_modes(x, h)` | Mode location at bandwidth h | h can be critical bandwidth |
| `find_trough(x, h)` | Valley between peaks | For threshold identification |
| `detect_components(x)` | Gaussian decomposition | Returns BimodalDecomposition |
| `silverman_bandwidth(x)` | Baseline bandwidth | Rule-of-thumb reference |

### 3.2 Analysis Pipeline

```python
import numpy as np
import pandas as pd
from critband import (critical_bandwidth, bimodality_strength,
                      silverman_test, excess_mass, detect_components,
                      find_trough, find_modes)

# 1. Load and preprocess data
x = load_data(...)

# 2. Compute critical bandwidth
h_crit, converged = critical_bandwidth(x, return_ci=True)

# 3. Interpret bimodality strength
strength = bimodality_strength(x)

# 4. Significance test
silverman_result = silverman_test(x, n_boot=999)

# 5. Multi-mode assessment (if applicable)
excess_result = excess_mass(x, n_boot=199)

# 6. Component decomposition (if bimodal)
if strength.strength_score > threshold:
    decomposition = detect_components(x)

# 7. Threshold identification (if applicable)
trough = find_trough(x, h_crit)
```

### 3.3 Validation Strategy

- Bootstrap confidence intervals on all point estimates
- Sensitivity analysis: parameter variation (bandwidth, binning)
- Comparison with baseline method (existing standard in the field)
- Simulation study with ground-truth modality

### 3.4 Statistical Reporting

Per ARS statistical reporting standards:
- Report effect sizes with uncertainty intervals
- Multiple comparison correction when testing across many units (genes, grid cells, survey items)
- Disclosure of all parameter choices and preprocessing decisions

## 4. Expected Challenges

- **Small sample size**: Bootstrap CI may be wide; report honestly
- **Sparse data**: critband may fail to converge; fall back to `excess_mass`
- **Discrete / integer data**: Add small jitter before KDE; document this
- **Survey weights**: Handle weighted modality detection explicitly
- **Multiple testing**: Bonferroni / FDR across many distributions

## 5. Key References

### Must-cite (appear in every paper)
- Zhang, R. & Wang, Q. (2026). critband: A Python Package for Critical Bandwidth Analysis of Multimodal Distributions. arXiv:2605.18686.
- critband v0.2.3 [Computer software]. https://pypi.org/project/critband/

### Foundational
- Silverman, B.W. (1981). Using kernel density estimates to investigate multimodality. *JRSS-B*, 43(1), 97–99.
- Silverman, B.W. (1986). *Density Estimation for Statistics and Data Analysis*. Chapman and Hall.
- Hartigan, J.A. & Hartigan, P.M. (1985). The Dip Test of Unimodality. *Annals of Statistics*, 13(1), 70–84.
- Müller, D.W. & Sawitzki, G. (1991). Excess Mass Estimates and Tests for Multimodality. *JASA*, 86(415), 738–746.

## 6. Next Steps

- [ ] Literature search (using ARS deep-research)
- [ ] Data acquisition and preprocessing
- [ ] Exploratory modality analysis
- [ ] Main analysis pipeline
- [ ] Simulation / validation study
- [ ] Manuscript drafting (using ARS academic-paper)
- [ ] Peer review simulation (using ARS academic-paper-reviewer)
