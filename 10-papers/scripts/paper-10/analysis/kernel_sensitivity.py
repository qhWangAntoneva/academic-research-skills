"""
Phase F-9 M3 — Kernel Sensitivity Analysis for Paper #10.

Tests different kernel functions (Gaussian, Epanechnikov, Triangular, Uniform)
by directly calling critical_bandwidth() with each kernel.
"""

import sys
from pathlib import Path
import time
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from critband import critical_bandwidth, silverman_bandwidth
from benchmark import SyntheticDataGenerator, RealDataLoader


def cbv_with_kernel(X, kernel, k_range=(2, 10), tol=1.3, tau=15):
    """Run CBV voting with a specific kernel."""
    n, d = X.shape
    k_min, k_max = k_range
    
    # Adaptive tolerance
    t = 1.0 + 0.5 * (1.0 - np.exp(-d / tau))
    
    votes = np.full(d, float(k_min))
    weights = np.zeros(d)
    
    for j in range(d):
        x_j = X[:, j]
        if np.ptp(x_j) == 0:
            continue
        
        h_silver = silverman_bandwidth(x_j)
        
        for k in range(k_min, k_max + 1):
            try:
                result = critical_bandwidth(x_j, k=k, kernel=kernel, return_ci=False)
                h_crit = result[0] if isinstance(result, tuple) else result
                converged = result[1] if isinstance(result, tuple) else True
                
                if converged and np.isfinite(h_crit) and h_crit < tol * h_silver:
                    votes[j] = float(k)
                    break
            except Exception:
                break
        
        # Simple bimodality weight: ratio of h_crit(2) to h_silver
        try:
            result2 = critical_bandwidth(x_j, k=2, kernel=kernel, return_ci=False)
            h_crit2 = result2[0] if isinstance(result2, tuple) else result2
            weights[j] = max(0, 1.0 - h_crit2 / h_silver) if h_silver > 0 else 0
        except Exception:
            weights[j] = 0
    
    # Weighted mode aggregation
    valid = weights > 0.15
    if valid.sum() == 0:
        return k_min
    
    valid_votes = votes[valid]
    valid_weights = weights[valid]
    
    # Weighted mode
    unique_k = np.unique(valid_votes)
    best_k = k_min
    best_w = -1
    for uk in unique_k:
        w = valid_weights[valid_votes == uk].sum()
        if w > best_w:
            best_w = w
            best_k = uk
    
    return int(best_k)


def main():
    print("=" * 60)
    print("  M3: Kernel Sensitivity Analysis")
    print("=" * 60)
    
    # Build datasets
    gen = SyntheticDataGenerator(random_state=42)
    synthetic = gen.generate_benchmark_suite()
    loader = RealDataLoader()
    real = loader.load_all()
    
    all_datasets = []
    for d in synthetic:
        all_datasets.append((d["name"], d["X"], d["k_true"]))
    for d in real:
        all_datasets.append((d["name"], d["X"], d["k_true"]))
    
    print(f"Loaded {len(all_datasets)} datasets")
    
    # Test kernels
    kernels = ["gaussian", "epanechnikov", "triangular", "uniform"]
    
    results = {}
    for kernel in kernels:
        print(f"\n── Testing kernel: {kernel} ──")
        t0 = time.time()
        correct = 0
        total = 0
        
        for name, X, k_true in all_datasets:
            try:
                k_hat = cbv_with_kernel(X, kernel)
                if k_hat == k_true:
                    correct += 1
                total += 1
            except Exception as e:
                pass
        
        elapsed = time.time() - t0
        acc = correct / total if total > 0 else 0
        results[kernel] = {"accuracy": acc, "correct": correct, "total": total, "time": elapsed}
        print(f"  Accuracy: {correct}/{total} = {acc:.1%} ({elapsed:.1f}s)")
    
    # Summary
    print("\n── Summary ──")
    print(f"{'Kernel':15s}  {'Accuracy':>10s}  {'Correct':>8s}  {'Time':>8s}")
    print("-" * 50)
    for k, r in results.items():
        marker = " <--" if k == "gaussian" else ""
        print(f"{k:15s}  {r['accuracy']:10.1%}  {r['correct']:5d}/{r['total']:<3d}  {r['time']:7.1f}s{marker}")
    
    base = results["gaussian"]["accuracy"]
    print(f"\nDifference from Gaussian:")
    for k, r in results.items():
        delta = r["accuracy"] - base
        print(f"  {k:15s}: {delta:+.1%}")


if __name__ == "__main__":
    main()
