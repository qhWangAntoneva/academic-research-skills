# Data Access Patterns — 10-Paper Framework

A quick-reference guide for acquiring and handling data for each paper in the suite.

---

## Paper 1: Political Polarization

| Dataset | Access | URL | Notes |
|---------|--------|-----|-------|
| ANES Time Series | Public | electionstudies.org | 1948–2024, biennial |
| European Social Survey | Public | europeansocialsurvey.org | 2002–2024, biennial |
| World Values Survey | Public | worldvaluessurvey.org | 1981–2022, waves 1–7 |

**Format**: SPSS `.sav` or CSV. Use `critband.io.read_data()` for CSV.

---

## Paper 2: Income Distribution

| Dataset | Access | URL | Notes |
|---------|--------|-----|-------|
| WID (World Inequality Database) | Public | wid.world | Top income shares, pre-tax/post-tax |
| LIS (Luxembourg Income Study) | Application | lisdatacenter.org | Microdata, requires registration |
| EU-SILC | Restricted | ec.europa.eu/eurostat | EU countries, application |

**Note**: LIS and EU-SILC require data use agreements. Start with WID public data for initial exploration.

---

## Paper 3: scRNA-seq Subpopulations

| Dataset | Access | URL | Notes |
|---------|--------|-----|-------|
| 10x Genomics PBMC | Public | 10xgenomics.com/resources/datasets | 2.7K–68K cells |
| Human Cell Atlas | Public | data.humancellatlas.org | Multiple tissues |
| GEO (scRNA-seq) | Public | ncbi.nlm.nih.gov/geo | Search for specific studies |

**Processing**: Requires Scanpy/Seurat preprocessing. Save normalized expression matrix as CSV for critband input.

---

## Paper 4: Climate Regime Shifts

| Dataset | Access | URL | Notes |
|---------|--------|-----|-------|
| ERA5 Monthly | Public | cds.climate.copernicus.eu | 1940–present, 0.25° grid |
| CRU TS v4 | Public | crudata.uea.ac.uk | 1901–present, 0.5° grid |
| HadCRUT5 | Public | metoffice.gov.uk/hadobs | Global temperature anomalies |

**Note**: Gridded data requires spatial subsetting. Focus on specific regions first, scale up later.

---

## Paper 5: Reaction Time Distributions

| Dataset | Access | URL | Notes |
|---------|--------|-----|-------|
| OpenNeuro (Stroop/Flanker) | Public | openneuro.org | BIDS-formatted behavioral data |
| OSF repositories | Public | osf.io | Search for published RT data |
| Simulated DDM data | Generated | — | Use pyDDM or HDDM to generate |

**Note**: RT data is typically right-skewed. Consider log transformation before analysis.

---

## Paper 6: Educational Achievement

| Dataset | Access | URL | Notes |
|---------|--------|-----|-------|
| PISA | Public | oecd.org/pisa | 2000–2025, 80+ countries |
| TIMSS | Public | timssandpirls.bc.edu | 1995–2023, grades 4 and 8 |
| NAEP | Public | nces.ed.gov/nationsreportcard | US national/state data |

**Note**: PISA uses plausible values (5 or 10 per student). Analyze each plausible value separately and pool results.

---

## Paper 7: Galaxy Populations

| Dataset | Access | URL | Notes |
|---------|--------|-----|-------|
| SDSS DR18 | Public | sdss.org | Optical photometry/spectroscopy |
| DESI EDR | Public | desi.lbl.gov | Spectroscopic data |
| JWST CEERS | Public | jwst-catalog.stsci.edu | NIRCam imaging |

**Format**: FITS tables. Use `astropy` to read, extract to CSV for critband.

---

## Paper 8: Biomarker Thresholds

| Dataset | Access | URL | Notes |
|---------|--------|-----|-------|
| NHANES | Public | cdc.gov/nchs/nhanes | 1999–2024, US nationally representative |
| UK Biobank | Application | ukbiobank.ac.uk | 500K participants, requires approval |

**Note**: NHANES uses complex survey design with weights. Consider weighted KDE or use critband on unweighted data with sensitivity analysis.

---

## Paper 9: Latent Attitude Profiles

| Dataset | Access | URL | Notes |
|---------|--------|-----|-------|
| ISSP | Public | issp.org | 1985–2023, 40+ countries |
| EVS | Public | europeanvaluesstudy.eu | 1981–2021, 4 waves |
| WVS | Public | worldvaluessurvey.org | 1981–2022, 7 waves |

**Note**: Likert-scale items are discrete (1–5 or 1–7). Add small uniform jitter before KDE.

---

## Paper 10: Cluster Validation

| Dataset | Access | URL | Notes |
|---------|--------|-----|-------|
| scikit-learn synthetic | Generated | scikit-learn.org | `make_blobs`, `make_classification` |
| UCI Repository | Public | archive.ics.uci.edu | 500+ real-world datasets |

**Note**: Synthetic data is sufficient for initial method development. Use UCI for external validation.
