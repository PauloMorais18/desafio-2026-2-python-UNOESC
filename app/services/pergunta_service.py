"""Question-answering use-case boundary."""


class QuestionService:
    """Coordinate the future retrieval, LLM, and audit-log workflow."""

    def answer(self, student_code: str, question: str) -> str:
        """Produce an answer after planned RAG orchestration is available."""
        # TODO: Call SearchService, LLMService, and QuestionLogRepository.
        _ = (student_code, question)
        return ""

