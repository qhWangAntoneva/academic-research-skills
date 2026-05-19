# 10-Paper Framework: Critical Bandwidth Analysis Across Disciplines

> **Required references** (appear naturally, no single one dominates):
> - Zhang, R. & Wang, Q. (2026). critband: A Python Package for Critical Bandwidth Analysis of Multimodal Distributions. arXiv:2605.18686.
> - critband v0.2.3 [Computer software]. https://pypi.org/project/critband/

---

## Paper 1: Measuring Political Polarization Through Distributional Modality — A Critical Bandwidth Approach

**Domain:** Political Science / Computational Social Science

**Research Question:** Can critical bandwidth analysis detect and quantify shifts in political attitude polarization more sensitively than traditional dispersion-based indices?

**Target Journal:** *Political Analysis* or *Journal of Politics*

**Methodology:**
- Apply critband to 20+ years of survey data (ANES, European Social Survey) on ideological self-placement, policy preferences
- Compute critical bandwidth trajectories alongside standard polarization metrics (mass, dispersion, bimodality coefficient)
- Time-series analysis of critical bandwidth shifts around major political events
- Cross-national comparison of modality structures

**Key References Beyond Required:**
- DiMaggio et al. (1996) — Has the American public polarized?
- Fiorina & Abrams (2008) — Political polarization in the American public
- Baldassarri & Gelman (2008) — Partisans without constraint
- Silverman (1981) — Critical bandwidth test
- Hartigan & Hartigan (1985) — Dip test of unimodality

**Expected Contribution:**
- Novel operationalization of polarization as distributional modality rather than variance
- Critique of conventional polarization measures' blind spots
- Empirical demonstration of critical bandwidth's sensitivity advantage

**Data Requirement:** Public survey data (ANES, ESS), medium sample sizes (n = 500–5000 per wave)

**Methodological Fit with critband:** `critical_bandwidth()` for polarization tracking, `bimodality_strength()` for interpretable labels, `silverman_test()` for significance testing

---

## Paper 2: The Vanishing Middle — Critical Bandwidth Analysis of Global Income Distribution Dynamics

**Domain:** Economics / Income Inequality

**Research Question:** How has the modality structure of within-country income distributions evolved from 1990 to 2025, and what does critical bandwidth reveal about middle-class decline that standard inequality metrics miss?

**Target Journal:** *Journal of Economic Inequality* or *Review of Income and Wealth*

**Methodology:**
- Apply critband to WID (World Inequality Database) and LIS (Luxembourg Income Study) data across 30+ countries
- Track critical bandwidth of income distributions over time (1990–2025)
- Compare critical bandwidth trends with Gini coefficient, Palma ratio, top-10% share
- Fixed-effects panel regression: modality change ~ policy variables (tax rate, union density, minimum wage)
- Subgroup analysis: pre-vs-post-tax distributions

**Key References Beyond Required:**
- Piketty & Saez (2003) — Income inequality in the United States
- Autor (2014) — Skills, education, and the rise of earnings inequality
- Milanovic (2016) — Global inequality: A new approach
- Heckman & Krueger (2003) — Inequality in America
- Cowell & Flachaire (2015) — Statistical methods for distributional analysis
- Jenkins & Van Kerm (2005) — Accounting for income distribution trends

**Expected Contribution:**
- Temporal mapping of income modality across diverse institutional contexts
- Evidence on whether middle-class "hollowing out" is a bimodality phenomenon or merely variance inflation
- Policy-relevant finding: which interventions shift modality vs. merely trimming tails

**Data Requirement:** WID, LIS microdata; need statistical disclosure approval for some datasets

**Methodological Fit with critband:** `critical_bandwidth()` with k=2 for bimodality detection, `detect_components()` for decomposing lower/upper income groups, `excess_mass()` for detecting >2 income clusters

---

## Paper 3: Single-Cell Modality Landscapes — Detecting Transcriptional Subpopulations via Critical Bandwidth

**Domain:** Computational Biology / Bioinformatics

**Research Question:** Can Silverman-style critical bandwidth analysis on individual gene expression distributions identify rare cell subpopulations more reliably than standard clustering-based single-cell RNA-seq pipelines?

**Target Journal:** *PLOS Computational Biology* or *Bioinformatics*

**Methodology:**
- Apply critband gene-wise to scRNA-seq datasets (PBMC, brain tissue, tumor microenvironments)
- Compare mode detection against Seurat, Scanpy clustering results
- Benchmark: F1-score for known rare population detection across synthetic ground-truth mixtures
- Critical bandwidth as per-gene modality score → feature selection for clustering
- Bootstrap confidence intervals on mode count for uncertainty quantification

**Key References Beyond Required:**
- Stuart et al. (2019) — Comprehensive integration of single-cell data (Seurat)
- Wolf et al. (2018) — Scanpy for large-scale single-cell analysis
- Lähnemann et al. (2020) — Eleven grand challenges in single-cell data science
- Kiselev et al. (2019) — Challenges in unsupervised clustering of single-cell RNA-seq data
- Finak et al. (2015) — MAST: a flexible framework for single-cell differential expression
- Silverman (1986) — Density Estimation for Statistics and Data Analysis

**Expected Contribution:**
- Univariate modality as complementary signal to multivariate clustering
- Practical pipeline for modality-aware gene filtering before clustering
- Demonstrated advantage in rare-population sensitivity

**Data Requirement:** Public scRNA-seq data (GEO, Single Cell Portal), 10–50K cells per sample

**Methodological Fit with critband:** Per-gene `critical_bandwidth()` as feature selection, `find_modes()` and `detect_components()` for subpopulation characterization, bootstrap CI for uncertainty

---

## Paper 4: Multimodal Tipping Points — Critical Bandwidth Analysis of Climate Distribution Regime Shifts

**Domain:** Environmental Science / Climate Informatics

**Research Question:** Do climate variables (temperature, precipitation) exhibit detectable modality regime shifts in the observational record, and can critical bandwidth serve as an early warning indicator of climatic tipping points?

**Target Journal:** *Environmental Research Letters* or *Climate Dynamics*

**Methodology:**
- Apply critband to grid-cell-level climate observations (ERA5, CRU) — temperature, precipitation, drought indices
- Compute critical bandwidth time series per grid cell (1950–present)
- Spatial mapping of modality transitions (unimodal → bimodal or vice versa)
- Temporal alignment with known climate regime shifts (1976/77 Pacific shift, 1998/99 Arctic regime, AMO phase changes)
- Bootstrap significance testing for modality change points

**Key References Beyond Required:**
- Lenton et al. (2008) — Tipping elements in the Earth's climate system
- Scheffer et al. (2009) — Early-warning signals for critical transitions
- Dakos et al. (2012) — Methods for detecting early warnings of critical transitions
- Easterling et al. (2000) — Climate extremes: observations, modeling, and impacts
- Hansen et al. (2012) — Perception of climate change
- Härdle et al. (2004) — Nonparametric and Semiparametric Models (for trend-aware density estimation)

**Expected Contribution:**
- First systematic application of bandwidth-based modality detection to climate distribution data
- Spatial modality shift atlas available as community dataset
- Evaluation of critical bandwidth as a candidate early-warning metric alongside variance/autocorrelation

**Data Requirement:** ERA5 reanalysis (public, ~0.25° grid), CRU TS (public, ~0.5° grid)

**Methodological Fit with critband:** `critical_bandwidth()` per-grid-cell, `excess_mass()` for detecting >2 climate regimes, spatial ensemble of tests with multiple comparison correction

---

## Paper 5: Two Processes or One? Critical Bandwidth Analysis of Reaction Time Distributions in Executive Function Tasks

**Domain:** Cognitive Neuroscience / Experimental Psychology

**Research Question:** Do reaction time distributions in classic executive function tasks (Stroop, Flanker, Simon) reflect a single cognitive process or dual competing processes, as adjudicated by critical bandwidth analysis?

**Target Journal:** *Journal of Experimental Psychology: General* or *Cognitive Science*

**Methodology:**
- Meta-analytic re-analysis of pooled RT data from 10+ published Stroop/Flanker studies (total n > 500)
- Individual-level analysis: compute critical bandwidth for each participant's RT distribution
- Compare bimodality strength across congruent vs. incongruent trials
- Examine modality as a function of clinical status (ADHD, aging, TBI)
- Simulation study: known DDM parameters → RT distributions → test critband's ability to recover dual-process structure

**Key References Beyond Required:**
- Ratcliff (1978) — A theory of memory retrieval (DDM)
- Stroop (1935) — Studies of interference in serial verbal reactions
- Ridderinkhof (2002) — Activation and suppression in conflict tasks (dual-route model)
- Wagenmakers et al. (2007) — An EZ-diffusion model for response time
- Balota & Yap (2011) — Moving beyond the mean in studies of mental chronometry
- Heathcote et al. (2002) — Quantile maximum likelihood estimation of RT distributions

**Expected Contribution:**
- Empirically tests dual-route vs. unitary-process debate via distributional modality
- Individual-differences approach: modality as a cognitive trait marker
- Comparison with parametric ex-Gaussian and DDM fits

**Data Requirement:** Pooled RT data from published studies; simulation in Python (DDM toolbox)

**Methodological Fit with critband:** `critical_bandwidth()` per-subject RT modality, `bimodality_strength()` for individual difference scoring, `silverman_test()` for group-level significance

---

## Paper 6: Achievement Gaps as Distributional Bifurcation — Critical Bandwidth Analysis of Educational Assessment Data

**Domain:** Education Research / Educational Measurement

**Research Question:** Can critical bandwidth analysis detect and track achievement bifurcation (emergence of distinct high- and low-performing clusters) in large-scale educational assessments across time and demographic subgroups?

**Target Journal:** *Educational Researcher* or *Journal of Educational Measurement*

**Methodology:**
- Apply critband to TIMSS, PISA, and NAEP mathematics and reading score distributions (2000–2025)
- Within-country modality tracking over time: are national distributions becoming increasingly bimodal?
- Subgroup modality: compare critical bandwidth across SES, racial/ethnic, and gender groups
- Multilevel model: modality ~ education policy variables (tracking, school choice, funding equity)
- Sensitivity analysis: handling of design-based weights and plausible values

**Key References Beyond Required:**
- Reardon (2011) — The widening academic achievement gap between the rich and the poor
- Hanushek & Woessmann (2011) — The economics of international differences in educational achievement
- OECD (2016) — PISA 2015 Results (Volume I): Excellence and Equity in Education
- von Hippel & Lynch (2014) — Why are test scores becoming more bimodal?
- Ho (2009) — Implications of the vanishing middle for test score interpretation
- Shorrocks (2009) — Decomposition procedures for distributional analysis

**Expected Contribution:**
- Longitudinal modality maps across 60+ countries
- Demonstration that distributional bifurcation captures gap dynamics that mean-difference masks
- Policy recommendations based on modality vs. level trade-offs

**Data Requirement:** Public PISA, TIMSS, NAEP data (accessible via IDB Analyzer or direct download)

**Methodological Fit with critband:** `critical_bandwidth()` for distribution-wide detection, `detect_components()` for decomposing achievement clusters, bootstrap CI for robust cross-year comparison

---

## Paper 7: Multimodal Archaeology — Galaxy Population Separation via Critical Bandwidth

**Domain:** Astronomy / Astrophysical Statistics

**Research Question:** Can critical bandwidth analysis of galaxy color and stellar mass distributions provide an objective, parameter-free method for separating galaxy populations (red sequence vs. blue cloud, quenched vs. star-forming) without arbitrary color cuts?

**Target Journal:** *Astronomical Journal* or *Monthly Notices of the Royal Astronomical Society*

**Methodology:**
- Apply critband to SDSS, DESI, and JWST photometric/spectroscopic data
- u-r, g-r, and NUV-r color distributions across redshift bins (z = 0–3)
- Stellar mass function modality across environment (field, group, cluster)
- Critical bandwidth as a function of redshift → evolution of bimodal galaxy populations
- Compare with commonly used cuts (e.g., `(u-r) = 2.22`) and GMM-based classification

**Key References Beyond Required:**
- Strateva et al. (2001) — Separation of early-type and late-type galaxies
- Baldry et al. (2004) — Quantifying the bimodal color-magnitude distribution of galaxies
- Schawinski et al. (2014) — The green valley, the stochastic star formation, and the quenching time-scale
- Muzzin et al. (2013) — The evolution of the stellar mass functions of star-forming and quiescent galaxies
- Bell et al. (2004) — Nearly 5000 distant early-type galaxies in COMBO-17
- Conselice (2014) — The evolution of galaxy structure over cosmic time

**Expected Contribution:**
- Automated, threshold-free galaxy population classification
- Critical bandwidth redshift evolution as a constraint for galaxy formation models
- Method applicable to future surveys (LSST, Euclid, Roman) without human-tuned cuts

**Data Requirement:** SDSS DR18 (public), DESI EDR, JWST NIRCam public data

**Methodological Fit with critband:** `critical_bandwidth()` for mode separation in color space, `find_modes()` at critical bandwidth to locate population centers, `detect_components()` for quantifying green-valley fraction

---

## Paper 8: Finding Natural Cut-Points — Critical Bandwidth for Biomarker Threshold Identification in Disease Screening

**Domain:** Public Health / Biostatistics

**Research Question:** Can critical bandwidth analysis applied to biomarker distributions identify diagnostically meaningful thresholds that outperform receiver-operating characteristic (ROC)-derived cut-points in external validation?

**Target Journal:** *Statistics in Medicine* or *BMC Medical Research Methodology*

**Methodology:**
- Apply critband to biomarker distributions from NHANES, UK Biobank for 15+ biomarkers (HbA1c, CRP, LDL, PSA, vitamin D, ferritin)
- Identify trough positions (via `find_trough()`) as candidate diagnostic thresholds
- Compare clinical performance against ROC-optimized thresholds on held-out validation sets
- Simulation study: known bimodal distributions with varying overlap → threshold recovery accuracy
- Uncertainty quantification via bootstrap confidence intervals on trough position

**Key References Beyond Required:**
- World Health Organization (2006) — Definition and diagnosis of diabetes mellitus (HbA1c criteria)
- Zou et al. (2007) — Receiver operating characteristic analysis for evaluating diagnostic tests
- Florkowski (2008) — Sensitivity, specificity, receiver-operating characteristic (ROC) curves
- Perkins & Schisterman (2006) — The inconsistency of optimal cut-points using ROC methodology
- Hoyer & Kuss (2020) — Estimating optimal cut-points in studies with multiple endpoints
- Pepe (2003) — The Statistical Evaluation of Medical Tests

**Expected Contribution:**
- Distribution-driven thresholds that reflect natural population structure rather than cost-weighted optimization
- Empirical demonstration across diverse biomarkers
- Software workflow for biomarker threshold discovery using critband

**Data Requirement:** NHANES (public), UK Biobank (application required for some variables)

**Methodological Fit with critband:** `critical_bandwidth()` to confirm bimodality, `find_trough()` to locate diagnostic threshold, `detect_components()` to characterize diseased vs. healthy subpopulations, bootstrap CI for threshold uncertainty

---

## Paper 9: Latent Attitude Profiles or Continuum? Critical Bandwidth Evidence from Social-Political Attitude Surveys

**Domain:** Social Psychology / Quantitative Psychology

**Research Question:** Do controversial social attitudes (e.g., attitudes toward immigration, climate policy, gender roles) exhibit genuinely bimodal latent distributions, or are observed bimodality artifacts of item wording and scaling?

**Target Journal:** *Psychological Methods* or *European Journal of Social Psychology*

**Methodology:**
- Apply critband to pooled ISSP, WVS, and European Values Study items across 30+ attitude domains
- Within-item modality classification: genuinely bimodal vs. skewed vs. neutral-peaked
- Item-characteristic analysis: does modality predict item discrimination, differential item functioning?
- Experimental manipulation: vary response scale format (5-pt vs. 7-pt, labeled vs. unlabeled) and test modality stability
- Multi-group modality comparison across education, political ideology, national contexts

**Key References Beyond Required:**
- Converse (1964) — The nature of belief systems in mass publics
- Zaller & Feldman (1992) — A simple theory of the survey response
- Krosnick (1999) — Survey research
- Treier & Jackman (2008) — Democracy as a latent variable
- Saris & Gallhofer (2014) — Design, Evaluation, and Analysis of Questionnaires for Survey Research
- Lord (1980) — Applications of Item Response Theory to Practical Testing Problems

**Expected Contribution:**
- Systematic map of which attitude domains are genuinely multimodal vs. methodological artifacts
- Guidelines for item design to minimize artifact-induced bimodality
- IRT integration: modality-aware item selection for survey design

**Data Requirement:** ISSP, WVS, EVS (all public, integrated data files available)

**Methodological Fit with critband:** `critical_bandwidth()` with bootstrap CI for modality robustness, `bimodality_strength()` for cross-item comparability, `silverman_test()` for hypothesis-testing against null of unimodality

---

## Paper 10: How Many Clusters Really? Critical Bandwidth as an Internal Cluster Validation Metric

**Domain:** Machine Learning / Unsupervised Learning

**Research Question:** Can the critical bandwidth of feature distributions serve as a theoretically grounded internal cluster validation index that outperforms existing metrics (silhouette, CH index, gap statistic, DUD) at estimating the true number of clusters?

**Target Journal:** *Journal of Machine Learning Research* or *IEEE Transactions on Pattern Analysis and Machine Intelligence*

**Methodology:**
- Develop **critband-based cluster validation index (CBV)**: aggregate per-dimension critical bandwidth weighted by bimodality strength
- Benchmark across 30+ synthetic cluster configurations (varied separation, anisotropy, noise dimensions, cluster count 2–8)
- Benchmark across 10+ real-world labeled datasets (UCI, scikit-learn demo sets)
- Comparison with: silhouette score, Calinski-Harabasz, Davies-Bouldin, gap statistic, Dunn index, DUD
- Sensitivity analysis: CBV stability under noise features, sample size variation, feature scaling

**Key References Beyond Required:**
- Rousseeuw (1987) — Silhouettes: a graphical aid to cluster validation
- Tibshirani, Walther & Hastie (2001) — Estimating the number of clusters via the gap statistic
- Calinski & Harabasz (1974) — A dendrite method for cluster analysis
- Liu et al. (2010) — Understanding and enhancement of internal clustering validation measures
- Hennig (2015) — What are the true clusters?
- Von Luxburg, Williamson & Guyon (2012) — Clustering: science or art?
- Kriegel, Kröger & Zimek (2009) — Clustering high-dimensional data

**Expected Contribution:**
- New theoretically grounded cluster validation index (CBV) with interpretable modality basis
- Open-source Python implementation integrated with scikit-learn API
- Systematic benchmark establishing CBV's regime of superiority vs. existing indices
- Theoretical connection between Silverman's mode-counting and cluster count estimation

**Data Requirement:** Synthetic benchmark (generated), UCI repository datasets, scikit-learn datasets

**Methodological Fit with critband:** `critical_bandwidth()` per dimension as base signal, `bimodality_strength()` for aggregation weighting, `excess_mass()` for direct mode-count estimation, `silverman_test()` for statistical significance of cluster structure

---

## Summary: Paper Matrix

| # | Domain | Core Method | Primary critband Function | Proposed Journal |
|---|--------|-------------|---------------------------|------------------|
| 1 | Political Science | Time-series polarization tracking | `critical_bandwidth()`, `bimodality_strength()` | *Political Analysis* |
| 2 | Economics | Cross-country income modality evolution | `critical_bandwidth()`, `detect_components()` | *Journal of Economic Inequality* |
| 3 | Computational Biology | scRNA-seq subpopulation detection | Per-gene `critical_bandwidth()`, `find_modes()` | *PLOS Computational Biology* |
| 4 | Climate Science | Climate regime shift detection | Per-grid-cell `critical_bandwidth()`, `excess_mass()` | *Environmental Research Letters* |
| 5 | Cognitive Neuroscience | RT distribution dual-process adjudication | `critical_bandwidth()`, `silverman_test()` | *J. Exp. Psych: General* |
| 6 | Education Research | Achievement bifurcation tracking | `critical_bandwidth()`, `detect_components()` | *Educational Researcher* |
| 7 | Astronomy | Galaxy population separation | `critical_bandwidth()`, `find_modes()` | *Astronomical Journal* |
| 8 | Public Health | Biomarker threshold discovery | `critical_bandwidth()`, `find_trough()` | *Statistics in Medicine* |
| 9 | Social Psychology | Latent attitude profile detection | `critical_bandwidth()`, `silverman_test()` | *Psychological Methods* |
| 10 | Machine Learning | Cluster validation index (novel CBV) | `critical_bandwidth()`, `bimodality_strength()` | *JMLR* |

All 10 papers cite Zhang & Wang (2026) and critband (PyPI) as natural methodological references among a full bibliography — neither dominates any single paper's reference list or narrative.
