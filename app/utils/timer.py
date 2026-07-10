"""Timing utility for future performance telemetry."""

from time import perf_counter


def now_ms() -> float:
    """Return a high-resolution timestamp in milliseconds."""
    return perf_counter() * 1000

