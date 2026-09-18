from app.backtest.validate import metrics


def test_backtest_metrics_are_deterministic():
    assert metrics([100, 200], [110, 190]) == {"rmse": 10.0, "mape": 7.5}
