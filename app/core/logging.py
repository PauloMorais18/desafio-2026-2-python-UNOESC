"""Central logging configuration extension point."""

import logging


def configure_logging(level: str) -> None:
    """Configure application logging before production observability is added."""
    # TODO: Add structured logs, correlation IDs, and external exporters.
    logging.basicConfig(level=level)

