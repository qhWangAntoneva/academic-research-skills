# Paper 06: Achievement Gaps as Distributional Bifurcation

> **Domain**: Education Research / Educational Measurement
> **Target Journal**: *Educational Researcher*
> **Paper ID**: paper-06

---

## Research Protocol

### 1. Research Question

Can critical bandwidth analysis detect and track achievement bifurcation in large-scale educational assessments across time and demographic subgroups?

### 2. Protocol Steps

1. **Data acquisition**: PISA (2000–2025, mathematics + reading), TIMSS (1995–2023), NAEP (1990–2024)
2. **Within-country modality tracking**: Compute `critical_bandwidth()` per country-year per subject
3. **Subgroup analysis**: Decompose by SES quartile, racial/ethnic group, gender
4. **Modality ~ policy model**: critical_bandwidth ~ tracking age + school choice + funding equity + teacher quality
5. **Comparison with mean-based gap analysis**: When do modality and mean-difference diverge?

### 3. critband Functions

- `critical_bandwidth(x, k=2, return_ci=True)` — national distribution modality
- `detect_components(x)` — decompose into high/low performance clusters
- `bimodality_strength(x)` — cross-country comparability metric
- `find_trough(x, h=h_crit)` — achievement threshold between clusters

### 4. Data Sources

- PISA (public): oecd.org/pisa
- TIMSS (public): timssandpirls.bc.edu
- NAEP Data Explorer (public): nces.ed.gov/nationsreportcard

### 5. Expected Challenges

- PISA plausible values (10 per student) → analyze each, pool results
- Survey weights → weighted modality estimation
- Achievement data is approximately normal → bimodality may be subtle
- Trend breaks (PISA 2015 transition to computer-based)

### 6. Key References

**Must-cite**: Zhang & Wang (2026); critband (PyPI)

**Domain**: Reardon (2011); Hanushek & Woessmann (2011); von Hippel & Lynch (2014)

**Method**: Silverman (1981, 1986); Ho (2009); Shorrocks (2009)

### 7. Next Steps

- [ ] PISA data download and plausible value handling
- [ ] Country-level modality trends (selected countries)
- [ ] Subgroup modality comparison (US NAEP data)
- [ ] Policy variable collection
- [ ] Manuscript draft
