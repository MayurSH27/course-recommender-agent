from course_recommender.agent import run_agent
from course_recommender.models import Student

def main():

    student = Student(
        name="Alex",
        goal="Become an AI engineer",
        skills={
            "python": "intermediate",
            "statistics": "beginner",
            "linear_algebra": "beginner",
        },
        available_hours_per_week=10,
    )

    result = run_agent(student)

    print("\nFinal Recommendation\n")
    print(result)


if __name__ == "__main__":
    main()
