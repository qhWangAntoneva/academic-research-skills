# Paper 01: Measuring Political Polarization Through Distributional Modality

> **Domain**: Political Science / Computational Social Science
> **Target Journal**: *Political Analysis*
> **Paper ID**: paper-01

---

## Research Protocol

### 1. Research Question

Can critical bandwidth analysis detect and quantify shifts in political attitude polarization more sensitively than traditional dispersion-based indices?

### 2. Protocol Steps

1. **Data Assembly**: Pool ANES (2000–2024), ESS (2002–2024), WVS (wave 5–7) ideological self-placement items
2. **Per-wave computation**: For each country-year, compute `critical_bandwidth()` on the ideology distribution
3. **Comparison metrics**: Also compute mass polarization, bimodality coefficient, kurtosis, variance
4. **Event study**: Critical bandwidth before/after major political events (elections, crises, leadership changes)
5. **Multilevel model**: critical_bandwidth ~ time + electoral system + media environment + controls

### 3. critband Functions

- `critical_bandwidth(x, k=2, return_ci=True)` — main polarization measure
- `bimodality_strength(x)` — interpretable "strong/moderate/weak" labels
- `silverman_test(x, n_boot=999)` — significance against unimodal null
- `excess_mass(x)` — detect >2 ideological clusters

### 4. Data Sources

- ANES Time Series (public): electionstudies.org
- ESS Cumulative File (public): europeansocialsurvey.org
- WVS Wave 7 (public): worldvaluessurvey.org

### 5. Expected Challenges

- Likert-scale discreteness → apply small jitter
- Cross-country comparability of ideology scales
- Social desirability bias in self-placement

### 6. Key References

**Must-cite**: Zhang & Wang (2026); critband (PyPI)

**Domain**: DiMaggio et al. (1996); Fiorina & Abrams (2008); Baldassarri & Gelman (2008)

**Method**: Silverman (1981, 1986); Hartigan & Hartigan (1985)

### 7. Next Steps

- [ ] Define country-year inclusion criteria (n >= 500 per wave)
- [ ] Write preprocessing script (survey data → modality-ready arrays)
- [ ] Exploratory analysis on ANES (longest time series)
- [ ] Cross-country comparison (ESS: 30+ countries)
- [ ] Event-study specification
- [ ] Manuscript draft
