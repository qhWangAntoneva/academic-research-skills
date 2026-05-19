# Paper 08: Finding Natural Cut-Points — Critical Bandwidth for Biomarker Threshold Identification

> **Domain**: Public Health / Biostatistics
> **Target Journal**: *Statistics in Medicine*
> **Paper ID**: paper-08

---

## Research Protocol

### 1. Research Question

Can critical bandwidth analysis identify diagnostically meaningful biomarker thresholds that outperform ROC-derived cut-points in external validation?

### 2. Protocol Steps

1. **Biomarker selection**: HbA1c, CRP, LDL, PSA, vitamin D, ferritin, creatinine from NHANES
2. **Modality confirmation**: Compute `critical_bandwidth()` for each biomarker → confirm bimodality
3. **Threshold identification**: Use `find_trough()` to locate valley between peaks
4. **Validation**: Compare trough-derived vs. ROC-optimized thresholds on held-out NHANES waves
5. **Simulation study**: Generate known bimodal data with varying overlap → threshold recovery accuracy
6. **Uncertainty quantification**: Bootstrap CI on trough positions

### 3. critband Functions

- `critical_bandwidth(x, k=2, return_ci=True)` — confirm bimodality
- `find_trough(x, h=h_crit)` — diagnostic threshold (primary contribution)
- `detect_components(x)` — characterize diseased/healthy subpopulations
- `bimodality_strength(x)` — threshold reliability indicator

### 4. Data Sources

- NHANES (public, 1999–2024): cdc.gov/nchs/nhanes
- UK Biobank (application): ukbiobank.ac.uk

### 5. Expected Challenges

- NHANES complex survey design → weighted vs. unweighted modality
- Biomarker distributions often log-normal → log transformation
- Laboratory method changes across survey waves → harmonization
- Disease prevalence < 5% → bimodality may be asymmetric

### 6. Key References

**Must-cite**: Zhang & Wang (2026); critband (PyPI)

**Domain**: WHO (2006), HbA1c diagnostic criteria; Florkowski (2008); Pepe (2003)

**Method**: Silverman (1981, 1986); Perkins & Schisterman (2006); Hoyer & Kuss (2020)

### 7. Next Steps

- [ ] NHANES biomarker data download and harmonization
- [ ] Per-biomarker modality assessment (15 biomarkers)
- [ ] Trough threshold identification
- [ ] ROC comparison and external validation
- [ ] Manuscript draft
