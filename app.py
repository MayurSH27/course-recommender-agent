from course_recommender.models import Student
from course_recommender.recommender import recommend
from course_recommender.tools import search_courses


def main():
    student = Student(
        name = "Alex",
        goal = "Become an AI engineer",
        skills = {
            "python": "intermediate",
            "statistics": "beginner",
            "linear_algebra": "beginner",
        },
        available_hours_per_week = 10
    )

    candidates = search_courses(
        student=student,
        query="AI machine learning LLM",
        limit=5,
    )

    result = recommend(
        student=student,
        courses=candidates,
    )

    print("\nRecommended Courses\n")

    for recommendation in result.recommendations:
        print(
            f"{recommendation.course_name}"
            f" [{recommendation.priority}]"
        )
        print(f" {recommendation.reason}\n")

if __name__ == "__main__":
    main()