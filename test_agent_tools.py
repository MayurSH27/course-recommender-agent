from course_recommender.agent_tools import (
    check_course_eligibility,
)
from course_recommender.models import Student


def make_student() -> Student:
    return Student(
        name="Test Student",
        goal="Become an AI engineer",
        skills={
            "python": "intermediate",
            "statistics": "beginner",
            "linear_algebra": "beginner",
        },
        available_hours_per_week=10,
    )


def test_eligible_course():
    student = make_student()

    result = check_course_eligibility(
        student=student,
        course_id=2,
    )

    assert result["eligible"] is True
    assert result["course_id"] == 2


def test_ineligible_course():
    student = Student(
        name="Beginner Student",
        goal="Become an AI engineer",
        skills={
            "python": "beginner",
            "statistics": "beginner",
        },
        available_hours_per_week=5,
    )

    result = check_course_eligibility(
        student=student,
        course_id=2,
    )

    assert result["eligible"] is False


def test_unknown_course():
    student = make_student()

    result = check_course_eligibility(
        student=student,
        course_id=9999,
    )

    assert "error" in result