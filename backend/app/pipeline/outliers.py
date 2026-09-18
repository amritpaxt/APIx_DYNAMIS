from statistics import median
from typing import Iterable


def mad_flags(values: Iterable[float], threshold: float = 3.0) -> list[bool]:
    """MAD flags are review metadata, never a deletion instruction."""
    vals = list(values)
    if len(vals) < 3:
        return [False] * len(vals)
    center = median(vals)
    mad = median(abs(v - center) for v in vals)
    if mad == 0:
        return [False] * len(vals)
    return [abs(v - center) / mad > threshold for v in vals]
