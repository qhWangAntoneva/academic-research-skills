# Paper 05: Two Processes or One? Critical Bandwidth Analysis of Reaction Time Distributions

> **Domain**: Cognitive Neuroscience / Experimental Psychology
> **Target Journal**: *Journal of Experimental Psychology: General*
> **Paper ID**: paper-05

---

## Research Protocol

### 1. Research Question

Do reaction time distributions in executive function tasks reflect a single cognitive process or dual competing processes, as adjudicated by critical bandwidth analysis?

### 2. Protocol Steps

1. **Data pooling**: Collect RT data from published Stroop, Flanker, Simon studies via OSF/OpenNeuro
2. **Individual-level analysis**: Compute `critical_bandwidth()` per participant per condition
3. **Condition comparison**: Congruent vs. incongruent trial modality
4. **Group comparison**: Clinical (ADHD, aging, TBI) vs. neurotypical modality differences
5. **Simulation study**: Generate RTs from known DDM parameters → test critband's ability to recover dual-process structure

### 3. critband Functions

- `critical_bandwidth(x, k=2, return_ci=True)` — per-subject RT modality
- `bimodality_strength(x)` — individual difference scoring
- `silverman_test(x, n_boot=999)` — group-level significance
- `detect_components(x)` — decompose fast/slow processes

### 4. Data Sources

- OpenNeuro (public): openneuro.org
- OSF repositories (public): osf.io
- Simulated DDM data (generated): pyDDM or HDDM Python packages

### 5. Expected Challenges

- RT data is heavily right-skewed → log transformation before analysis
- Contaminated data (fast guesses, slow outliers) → pre-screening protocol
- Small per-subject trial counts (typically 50–200) → bootstrap sensitivity
- Practice effects within session → block as covariate

### 6. Key References

**Must-cite**: Zhang & Wang (2026); critband (PyPI)

**Domain**: Ratcliff (1978); Stroop (1935); Ridderinkhof (2002); Balota & Yap (2011)

**Method**: Silverman (1981, 1986); Wagenmakers et al. (2007); Heathcote et al. (2002)

### 7. Next Steps

- [ ] Identify 5+ published studies with available RT data
- [ ] Data pooling and unified preprocessing
- [ ] Per-subject modality computation and individual-differences analysis
- [ ] DDM simulation for ground-truth validation
- [ ] Manuscript draft
