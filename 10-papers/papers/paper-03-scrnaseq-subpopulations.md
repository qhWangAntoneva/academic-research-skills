# Paper 03: Single-Cell Modality Landscapes — Detecting Transcriptional Subpopulations via Critical Bandwidth

> **Domain**: Computational Biology / Bioinformatics
> **Target Journal**: *PLOS Computational Biology*
> **Paper ID**: paper-03

---

## Research Protocol

### 1. Research Question

Can Silverman-style critical bandwidth analysis on individual gene expression distributions identify rare cell subpopulations more reliably than standard clustering-based scRNA-seq pipelines?

### 2. Protocol Steps

1. **Dataset acquisition**: PBMC 68K, brain tissue, tumor microenvironment
2. **Preprocessing**: Standard Scanpy pipeline (QC, normalization, log1p, HVG selection)
3. **Per-gene modality scan**: Compute `critical_bandwidth()` for each highly variable gene across cells
4. **Modality score as feature selection**: Filter genes by bimodality strength → use as input for clustering
5. **Benchmarking**: Compare modality-based pipeline against standard Seurat/Scanpy results
6. **Ground-truth validation**: Use synthetic mixtures with known rare population fractions (0.5%, 1%, 2%, 5%)

### 3. critband Functions

- `critical_bandwidth(x, k=2, return_ci=True)` — per-gene bimodality detection
- `find_modes(x, h=h_crit)` — locate subpopulation expression centers
- `detect_components(x)` — decompose into expressing/non-expressing groups
- `silverman_test(x, n_boot=199)` — statistically rigorous gene selection

### 4. Data Sources

- 10x Genomics PBMC (public): 10xgenomics.com
- Human Cell Atlas (public): data.humancellatlas.org
- GEO scRNA-seq studies (public): ncbi.nlm.nih.gov/geo

### 5. Expected Challenges

- Dropout events (excess zeros) in scRNA-seq → modality artifacts
- Multiple testing across thousands of genes → FDR correction
- Cell-type-specific expression patterns confounded by library size variation

### 6. Key References

**Must-cite**: Zhang & Wang (2026); critband (PyPI)

**Domain**: Stuart et al. (2019); Wolf et al. (2018); Lähnemann et al. (2020); Kiselev et al. (2019)

**Method**: Silverman (1981, 1986); Finak et al. (2015)

### 7. Next Steps

- [ ] Download and preprocess PBMC 68K dataset
- [ ] Per-gene modality scan across all HVGs (~2000 genes)
- [ ] Clustering benchmark (modality-based vs. standard)
- [ ] Rare-population simulation study
- [ ] Manuscript draft
