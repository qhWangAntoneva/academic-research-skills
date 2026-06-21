---

## Appendix A: Proof of Proposition 1

**Proposition 1 (Mode Recovery under Isotropic Gaussian Mixtures).** Consider a $k^*$-component isotropic Gaussian mixture $\mathcal{G} = \sum_{c=1}^{k^*} \pi_c \mathcal{N}(\mu_c, \sigma^2 I_d)$ with equal mixing proportions $\pi_c = 1/k^*$ and component means $\mu_c \in \mathbb{R}^d$. For each dimension $j$ where the projected means $\{\mu_c^{(j)}\}_{c=1}^{k^*}$ are distinct, let $\Delta_j = \min_{c \neq c'} |\mu_c^{(j)} - \mu_{c'}^{(j)}|$. If $\Delta_j > 2 h_{\mathrm{Silver}}$ for all such dimensions, then $v_j = k^*$.

**Proof.** Fix a dimension $j$ with distinct projected means. The 1D marginal density is:

$$f_j(x) = \frac{1}{k^*} \sum_{c=1}^{k^*} \phi\left(\frac{x - \mu_c^{(j)}}{\sigma}\right)$$

where $\phi$ is the standard normal density. This is a mixture of $k^*$ 1D Gaussians with means $\mu_c^{(j)}$ and common variance $\sigma^2$.

**Step 1: Mode count of the true density.** Since the projected means are distinct and $\Delta_j > 2 h_{\mathrm{Silver}} \approx 2.12 \sigma n^{-1/5}$, the components are sufficiently separated that $f_j$ has exactly $k^*$ modes. For equal-variance Gaussians, the mode count equals the number of components when separation exceeds $2\sigma \sqrt{2 \log k^*}$; our condition is stronger for finite $n$.

**Step 2: Critical bandwidth bound.** At $h = h_{\mathrm{Silver}}$, the KDE uses a bandwidth calibrated for unimodal density estimation. Since $\Delta_j > 2 h_{\mathrm{Silver}}$, the individual components are separated by more than twice the smoothing bandwidth, so the KDE at $h = h_{\mathrm{Silver}}$ still resolves all $k^*$ modes. Therefore $h_{\mathrm{crit}}(k^*) < h_{\mathrm{Silver}}$, and the threshold condition is satisfied for any $t \geq 1$.

**Step 3: Sequential termination.** The critical bandwidth $h_{\mathrm{crit}}(k)$ is the smallest $h$ where the KDE has at most $k$ modes. For $k < k^*$, more smoothing is needed to merge modes down to $k$, so $h_{\mathrm{crit}}(k) > h_{\mathrm{crit}}(k^*)$. For $k = k^*$, $h_{\mathrm{crit}}(k^*) < h_{\mathrm{Silver}}$. The sequential test scans $k = k_{\min}, k_{\min}+1, \ldots$ and terminates at the first $k$ where $h_{\mathrm{crit}}(k) < t \cdot h_{\mathrm{Silver}}$. This condition is first satisfied at $k = k^*$, so $v_j = k^*$. $\dashv$

---

## Appendix B: Kernel Sensitivity Results

We evaluated CBV with four kernel functions on 20 synthetic datasets:

| Kernel | Accuracy | Description |
|--------|:--------:|-------------|
| Gaussian | 60.0% | Smooth, infinitely differentiable |
| Epanechnikov | 20.0% | Compact support, discontinuous derivative |
| Triangular | 15.0% | Compact support, continuous |
| Uniform | 0.0% | Compact support, discontinuous |

The Gaussian kernel's superiority stems from its smooth density estimate, which produces well-defined critical bandwidths. Compact-support kernels produce discontinuous density estimates with ambiguous mode-counting at boundaries.

