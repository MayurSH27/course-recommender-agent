import json

from google import genai

from .config import GEMINI_API_KEY
from .models import RecommendationResponse, Student
from .prompts import SYSTEM_PROMPT


client = genai.Client(api_key=GEMINI_API_KEY)


def recommend(
    student: Student,
    courses: list,
) -> RecommendationResponse:

    course_data = [
        course.model_dump()
        for course in courses
    ]

    user_prompt = f"""
Student:

{json.dumps(student.model_dump(), indent=2)}

Eligible courses:

{json.dumps(course_data, indent=2)}

Select and rank the most useful courses for this student.
"""

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=user_prompt,
        config={
            "system_instruction": SYSTEM_PROMPT,
            "response_mime_type": "application/json",
            "response_schema": RecommendationResponse,
        },
    )

    return RecommendationResponse.model_validate_json(
        response.text
    )