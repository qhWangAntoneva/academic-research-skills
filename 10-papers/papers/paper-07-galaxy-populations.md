# Paper 07: Multimodal Archaeology — Galaxy Population Separation via Critical Bandwidth

> **Domain**: Astronomy / Astrophysical Statistics
> **Target Journal**: *Astronomical Journal*
> **Paper ID**: paper-07

---

## Research Protocol

### 1. Research Question

Can critical bandwidth analysis of galaxy color and stellar mass distributions provide an objective, parameter-free method for separating galaxy populations without arbitrary color cuts?

### 2. Protocol Steps

1. **Data acquisition**: SDSS DR18 (optical), DESI EDR (spectroscopic), JWST CEERS (NIRCam imaging)
2. **Color distributions**: u-r, g-r, NUV-r color distributions across redshift bins (z=0–3)
3. **Stellar mass function modality**: log(M*) distributions by environment (field/group/cluster)
4. **Redshift evolution**: critical_bandwidth(z) → constraint on quenching models
5. **Comparison with standard cuts**: Strateva cut `(u-r)=2.22`, GMM-based classification, random forest classifier

### 3. critband Functions

- `critical_bandwidth(x, k=2, return_ci=True)` — galaxy population separation
- `find_modes(x, h=h_crit)` — locate red sequence and blue cloud centers
- `detect_components(x)` — quantify green valley fraction via component weights
- `bimodality_strength(x)` — redshift-dependent bimodality

### 4. Data Sources

- SDSS DR18 (public): sdss.org
- DESI Early Data Release (public): desi.lbl.gov
- JWST CEERS (public): jwst-catalog.stsci.edu

### 5. Expected Challenges

- Malmquist bias at high redshift → completeness corrections
- Color uncertainties varying with magnitude → weighted analysis
- Dust extinction confounding color modality → SED-based correction
- Large survey volumes → computationally efficient implementation

### 6. Key References

**Must-cite**: Zhang & Wang (2026); critband (PyPI)

**Domain**: Strateva et al. (2001); Baldry et al. (2004); Schawinski et al. (2014); Bell et al. (2004)

**Method**: Silverman (1981, 1986); Conselice (2014)

### 7. Next Steps

- [ ] SDSS DR18 galaxy catalog download (color-selected sample)
- [ ] Per-redshift-bin modality computation (z=0–0.3)
- [ ] Red sequence / blue cloud decomposition via `detect_components()`
- [ ] Critical bandwidth-z relation and comparison with quenching models
- [ ] Manuscript draft
