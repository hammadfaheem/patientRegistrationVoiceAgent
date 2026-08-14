"""Small standalone helpers shared across tools."""


def digits_only(value: str) -> str:
    """Strip everything but digits from a phone number."""
    return "".join(ch for ch in value if ch.isdigit())
