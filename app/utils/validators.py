"""Domain-validation extension points."""


def is_valid_student_code(value: str) -> bool:
    """Perform only a minimal placeholder validation for a student code."""
    # TODO: Replace with the institution's real student-code validation rule.
    return bool(value.strip())

