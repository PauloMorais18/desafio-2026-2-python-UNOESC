"""Statistics use-case boundary."""


class StatisticsService:
    """Provide future aggregate reporting from question logs."""

    def get_summary(self) -> dict[str, int | float]:
        """Return placeholder statistics until repository aggregation is added."""
        # TODO: Query QuestionLogRepository for metrics.
        return {}

