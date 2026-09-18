def describe_pass_through(beta: float | None) -> str:
    if beta is None:
        return "Insufficient aligned ATF and index observations."
    return f"Estimated ATF pass-through coefficient: {beta:.3f}."
