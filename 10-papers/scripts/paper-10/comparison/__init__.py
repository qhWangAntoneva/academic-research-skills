"""Comparison framework for Paper #10 (CBV - Critical Bandwidth Validation)."""

from comparison.indices import CVIWrapper, get_all_indices
from comparison.report import ComparisonReport

__all__ = ["CVIWrapper", "ComparisonReport", "get_all_indices"]
