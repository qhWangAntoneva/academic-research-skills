# Cover Letter — TNNLS Submission

**Title:** Critical Bandwidth Modality Testing for Estimating the Number of Clusters
**Authors:** Qi-Hao Wang
**Journal:** IEEE Transactions on Neural Networks and Learning Systems (TNNLS)

---

Dear Editor,

I am pleased to submit the enclosed manuscript entitled "Critical Bandwidth Modality Testing for Estimating the Number of Clusters" for consideration for publication in IEEE Transactions on Neural Networks and Learning Systems.

## Contribution

This paper introduces Critical Bandwidth Validation (CBV), the first cluster validation index grounded in critical bandwidth modality testing. Unlike all existing CVIs, which evaluate k-means partition quality through geometric criteria, CBV estimates the number of clusters through statistical inference about the data density—specifically, by testing how many modes the density supports in each feature dimension and aggregating these votes with bimodality-strength weighting. This shift from geometric optimization to statistical testing represents a fundamentally new perspective on the problem of estimating the number of clusters.

## Key Findings

1. On a benchmark of 58 datasets against 10 established CVIs, CBV achieves 51.4% ± 0.8% exact-match accuracy, ranking second behind the Gap Statistic (53.8%) and above all geometric indices, with the lowest variance (σ = 0.8%) of any index tested.

2. CBV and geometric CVIs succeed on structurally different data regimes (mean Jaccard = 0.412), demonstrating genuine complementarity: an OR-ensemble of CBV and the Gap Statistic achieves 67.2% accuracy—a 13.8 pp improvement over the best single index.

3. The Complementarity Index of 0.667 between CBV and the Gap Statistic confirms that CBV provides diagnostic information that geometric indices cannot access.

## Why TNNLS

This work bridges statistical modality testing (traditionally published in statistics journals) with practical machine learning. TNNLS's readership—spanning neural networks, learning systems, and unsupervised learning methodology—is the ideal audience for a CVI that offers a statistically grounded complement to the dominant geometric paradigm. The paper's comprehensive benchmarking methodology and theoretical analysis (Proposition 1 establishing mode recovery conditions for Gaussian mixtures) align with TNNLS's standards for rigorous empirical and theoretical contributions.

## Prior Work

This manuscript has not been previously published, nor is it under consideration elsewhere. An earlier technical report (arXiv:XXXX.XXXXX) provided preliminary results on a smaller benchmark (31 datasets); the present manuscript significantly expands the evaluation to 58 datasets with 10 comparison indices, adds theoretical analysis (Proposition 1, Corollary 1), introduces CBVHybrid and CBVProjection variants, and provides comprehensive failure mode characterization.

## Additional Materials

Supplementary materials (per-dataset results table, complementarity matrix, and additional figures) are provided as a separate supplement.

Thank you for considering this manuscript. I look forward to your review.

Sincerely,

Qi-Hao Wang
School of Computer Science and Technology, Xidian University
Email: qhwang@xidian.edu.cn
