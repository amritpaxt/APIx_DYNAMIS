from app.index.confidence import score
from app.index.tornqvist import tornqvist_step
from app.pipeline.outliers import mad_flags


def test_mad_flags_extreme_value_without_deleting_it():
    assert mad_flags([100, 102, 101, 300]) == [False, False, False, True]


def test_tornqvist_step_matches_balanced_price_change():
    value = tornqvist_step(100, {1: 100, 2: 100}, {1: 110, 2: 110}, {1: .5, 2: .5})
    assert round(value, 6) == 110


def test_low_coverage_creates_explicit_chain_break():
    result = score(20, 50, 0, 20, threshold=.60)
    assert result.chain_break is True
    assert result.coverage_pct == 40
