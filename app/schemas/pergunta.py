"""Question API schemas."""

from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    """Input for the future academic-assistance question workflow."""

    student_code: str = Field(min_length=1, max_length=50)
    question: str = Field(min_length=1, max_length=5000)

