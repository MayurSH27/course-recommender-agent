from .models import Course, Student

LEVEL_VALUE = {
    "beginner": 1,
    "intermediate": 2,
    "advanced": 3,
}

def meets_requirement(
        student_level: str | None,
        required_level: str,
) -> bool:
    if student_level is None:
        return False

    return LEVEL_VALUE[student_level] >= LEVEL_VALUE[required_level]

def is_eligible(student: Student, course: Course) -> bool:
    for skill, required_level in course.prerequisites.items():
        student_level = student.skills.get(skill)

        if not meets_requirement(student_level, required_level):
            return False

    return True