from course_recommender.models import Course, Student
from course_recommender.rules import is_eligible

def test_student_meets_prerequisites():
    student = Student(
        name="Alex",
        goal="AI Engineer",
        skills={
            "python": "advanced",
            "statistics": "intermediate",
        },
        available_hours_per_week=10,
    )

    course = Course(
        id=1,
        name="Advanced ML",
        description="Advanced ML",
        level="advanced",
        prerequisites={
            "python": "advanced",
            "statistics": "intermediate",
        },
        duration_hours=50,
    )

    assert is_eligible(student, course)


def test_student_fails_prerequisites():
    student = Student(
        name="Alex",
        goal="AI Engineer",
        skills={
            "python": "advanced",
            "statistics": "beginner",
        },
        available_hours_per_week=10,
    )

    course = Course(
        id=1,
        name="Advanced ML",
        description="Advanced ML",
        level="advanced",
        prerequisites={
            "python": "advanced",
            "statistics": "intermediate",
        },
        duration_hours=50,
    )

    assert not is_eligible(student, course)