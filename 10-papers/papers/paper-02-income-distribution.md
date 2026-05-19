# Paper 02: The Vanishing Middle — Critical Bandwidth Analysis of Global Income Distribution Dynamics

> **Domain**: Economics / Income Inequality
> **Target Journal**: *Journal of Economic Inequality*
> **Paper ID**: paper-02

---

## Research Protocol

### 1. Research Question

How has the modality structure of within-country income distributions evolved from 1990 to 2025, and what does critical bandwidth reveal about middle-class decline that Gini and other standard metrics miss?

### 2. Protocol Steps

1. **Data Assembly**: WID public data (30+ countries, 1990–2025)
2. **Preprocessing**: Equivalized household disposable income, within-country percentile data → individual distribution reconstruction
3. **Modality time series**: Per-country-year `critical_bandwidth()` computed on income distribution
4. **Decomposition**: Use `detect_components()` to characterize lower/upper income components
5. **Panel analysis**: critical_bandwidth ~ tax rate + union density + minimum wage + trade openness + financialization
6. **Comparison**: Modality vs. Gini, Palma ratio, top-10% share, P90/P10 ratio

### 3. critband Functions

- `critical_bandwidth(x, k=2, return_ci=True)` — income modality tracking
- `detect_components(x)` — decompose into lower/upper income groups
- `bimodality_strength(x)` — cross-country comparability
- `excess_mass(x)` — detect >2 income clusters

### 4. Data Sources

- WID (World Inequality Database, public): wid.world
- LIS (Luxembourg Income Study, application): lisdatacenter.org
- EU-SILC (restricted): ec.europa.eu/eurostat

### 5. Expected Challenges

- Top-coding and bottom-coding in survey data
- Equivalence scale choices (modified OECD vs. square root)
- Cross-country comparability of income concepts (market vs. disposable)

### 6. Key References

**Must-cite**: Zhang & Wang (2026); critband (PyPI)

**Domain**: Piketty & Saez (2003); Autor (2014); Milanovic (2016); Cowell & Flachaire (2015)

**Method**: Silverman (1981, 1986); Jenkins & Van Kerm (2005)

### 7. Next Steps

- [ ] Define country-year panel inclusion criteria
- [ ] WID data extraction and equivalence adjustment
- [ ] Modality time series computation for US, UK, Germany, Japan, France
- [ ] Panel regression specification
- [ ] Robustness: alternative equivalence scales
- [ ] Manuscript draft
