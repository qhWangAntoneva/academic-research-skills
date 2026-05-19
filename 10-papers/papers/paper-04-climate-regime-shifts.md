# Paper 04: Multimodal Tipping Points — Critical Bandwidth Analysis of Climate Distribution Regime Shifts

> **Domain**: Environmental Science / Climate Informatics
> **Target Journal**: *Environmental Research Letters*
> **Paper ID**: paper-04

---

## Research Protocol

### 1. Research Question

Do climate variables (temperature, precipitation) exhibit detectable modality regime shifts in the observational record, and can critical bandwidth serve as an early warning indicator of climatic tipping points?

### 2. Protocol Steps

1. **Data acquisition**: ERA5 monthly temperature/precipitation, 1940–present
2. **Spatial subset**: Select key regions (Arctic, Sahel, monsoon regions, Amazon, Mediterranean)
3. **Per-grid-cell time series**: Compute rolling-window `critical_bandwidth()` (30-year window, 10-year step)
4. **Modality transition detection**: Unimodal → bimodal (or vice versa) regime shifts
5. **Alignment**: Temporal correlation with known shifts (1976/77 Pacific shift, 1998/99 Arctic regime)
6. **Spatial map**: Produce global modality regime shift atlas
7. **Comparison with conventional early-warning signals**: Variance, lag-1 autocorrelation, skewness

### 3. critband Functions

- `critical_bandwidth(x, k=2, return_ci=True)` — per-grid-cell modality
- `excess_mass(x, n_boot=199)` — detect >2 climate regimes
- `bimodality_strength(x)` — spatial map intensity

### 4. Data Sources

- ERA5 Monthly (public): cds.climate.copernicus.eu
- CRU TS v4 (public): crudata.uea.ac.uk
- HadCRUT5 (public): metoffice.gov.uk/hadobs

### 5. Expected Challenges

- Spatial autocorrelation in testing → field significance approach
- Seasonal cycle removal → anomaly computation
- Computing across thousands of grid cells → efficient batch processing
- Short time series for rolling windows → bootstrap CI interpretation

### 6. Key References

**Must-cite**: Zhang & Wang (2026); critband (PyPI)

**Domain**: Lenton et al. (2008); Scheffer et al. (2009); Dakos et al. (2012)

**Method**: Silverman (1981, 1986); Easterling et al. (2000)

### 7. Next Steps

- [ ] ERA5 data download (temperature, precipitation, regional subsets)
- [ ] Rolling-window modality computation for test region (Arctic)
- [ ] Spatial modality shift map for Northern Hemisphere
- [ ] Early-warning signal comparison
- [ ] Manuscript draft
