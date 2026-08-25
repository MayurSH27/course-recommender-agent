import json
from pathlib import Path

from .models import Course, Student
from .rules import is_eligible


DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "courses.json"
)

def load_courses() -> list[Course]:
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    return [
        Course.model_validate(course)
        for course in data
    ]


def search_courses(
    student: Student,
    query: str,
    limit: int = 5,
) -> list[Course]:

    courses = load_courses()

    query_words = set(query.lower().split())

    eligible_courses = []

    for course in courses:
        if not is_eligible(student, course):
            continue

        searchable_text = (
            f"{course.name} {course.description}"
        ).lower()

        score = sum(
            word in searchable_text
            for word in query_words
        )

        if score > 0:
            eligible_courses.append((score, course))

    eligible_courses.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [
        course
        for _, course in eligible_courses[:limit]
    ]