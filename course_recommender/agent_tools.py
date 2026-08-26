from .models import Student
from .tools import load_courses, search_courses
from .rules import is_eligible


def search_courses_tool(
    student: Student,
    query: str,
    limit: int = 5,
) -> dict:
    """
    Search the course catalog for relevant courses.

    Important:
    This tool retrieves candidates. It does not decide
    whether the student satisfies prerequisites.
    """

    courses = search_courses(
        student=student,
        query=query,
        limit=limit,
    )

    return {
        "courses": [
            course.model_dump()
            for course in courses
        ]
    }


def check_course_eligibility(
    student: Student,
    course_id: int,
) -> dict:
    """
    Deterministically check whether the student satisfies
    the prerequisites for a specific course.
    """

    courses = load_courses()

    for course in courses:
        if course.id == course_id:
            eligible = is_eligible(
                student,
                course,
            )

            return {
                "course_id": course.id,
                "course_name": course.name,
                "description": course.description,
                "duration_hours": course.duration_hours,
                "eligible": eligible,
                "prerequisites": course.prerequisites,
            }

    return {
        "error": f"Course {course_id} not found."
    }


def get_course_details(
    course_id: int,
) -> dict:
    """
    Get complete information about a specific course.
    """

    courses = load_courses()

    for course in courses:
        if course.id == course_id:
            return {
                "course": course.model_dump()
            }

    return {
        "error": f"Course {course_id} not found."
    }