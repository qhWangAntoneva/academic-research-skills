# Paper 09: Latent Attitude Profiles or Continuum? Critical Bandwidth Evidence from Surveys

> **Domain**: Social Psychology / Quantitative Psychology
> **Target Journal**: *Psychological Methods*
> **Paper ID**: paper-09

---

## Research Protocol

### 1. Research Question

Do controversial social attitudes exhibit genuinely bimodal latent distributions, or are observed bimodality artifacts of item wording and scaling?

### 2. Protocol Steps

1. **Item pool**: Select 50+ attitude items from ISSP, WVS, EVS across domains (immigration, climate, gender, redistribution, religion)
2. **Per-item modality classification**: Compute `critical_bandwidth()` on each item's distribution
3. **Item characteristics analysis**: Does modality relate to item discrimination, polarizing wording, extremity?
4. **Experimental simulation**: Manipulate scale format (5-pt vs. 7-pt, labeled vs. unlabeled endpoints) → test modality stability
5. **Multi-group analysis**: Modality across education, political ideology, and country contexts

### 3. critband Functions

- `critical_bandwidth(x, k=2, return_ci=True)` — per-item bimodality detection
- `bimodality_strength(x)` — cross-item comparability metric
- `silverman_test(x, n_boot=999)` — rigorous test against unimodal null
- `excess_mass(x, n_boot=199)` — detect >2 attitude clusters

### 4. Data Sources

- ISSP Cumulative File (public): issp.org
- European Values Study (public): europeanvaluesstudy.eu
- World Values Survey (public): worldvaluessurvey.org

### 5. Expected Challenges

- Likert scale discreteness (typically 5 points) → uniform jitter
- Acquiescence bias producing artificial peaks at endpoints
- Cross-cultural measurement invariance → group comparison
- Social desirability on sensitive items → modality artifacts

### 6. Key References

**Must-cite**: Zhang & Wang (2026); critband (PyPI)

**Domain**: Converse (1964); Zaller & Feldman (1992); Krosnick (1999)

**Method**: Silverman (1981, 1986); Treier & Jackman (2008); Saris & Gallhofer (2014)

### 7. Next Steps

- [ ] Item selection across attitude domains (50+ items)
- [ ] Per-item modality computation and classification
- [ ] Item-characteristics analysis (item discrimination vs. modality)
- [ ] Scale-format simulation study
- [ ] Manuscript draft
