from dataclasses import dataclass


@dataclass(frozen=True)
class Confidence:
    score: float
    coverage_pct: float
    outlier_rate: float
    chain_break: bool


def score(available_cells: int, expected_cells: int, outlier_count: int, quote_count: int, threshold: float = .60) -> Confidence:
    coverage = available_cells / expected_cells if expected_cells else 0.0
    outlier_rate = outlier_count / quote_count if quote_count else 0.0
    return Confidence(score=round(100 * coverage * (1 - outlier_rate), 2), coverage_pct=round(100 * coverage, 2),
                      outlier_rate=round(100 * outlier_rate, 2), chain_break=coverage < threshold)
