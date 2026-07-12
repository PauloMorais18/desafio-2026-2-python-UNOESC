"""Question API schemas."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class QuestionRequest(BaseModel):
    """Input accepted by the academic-assistance question endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    student_code: str = Field(alias="codigoAluno", min_length=1, max_length=50)
    question: str = Field(alias="pergunta", min_length=1, max_length=5000)

    @field_validator("student_code", mode="before")
    @classmethod
    def normalize_student_code(cls, value: str | int) -> str:
        """Accept the numeric format presented in the project specification."""
        return str(value)
