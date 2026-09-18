from math import sqrt


def metrics(actual: list[float], predicted: list[float]) -> dict[str, float | None]:
    if len(actual) != len(predicted) or not actual:
        return {"rmse": None, "mape": None}
    rmse = sqrt(sum((a - p) ** 2 for a, p in zip(actual, predicted)) / len(actual))
    non_zero = [(a, p) for a, p in zip(actual, predicted) if a]
    mape = sum(abs((a - p) / a) for a, p in non_zero) / len(non_zero) * 100 if non_zero else None
    return {"rmse": round(rmse, 4), "mape": round(mape, 4) if mape is not None else None}
