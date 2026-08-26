import json

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from .agent_tools import (
    check_course_eligibility,
    get_course_details,
    search_courses_tool,
)
from .config import GEMINI_API_KEY
from .models import Student


client = genai.Client(api_key=GEMINI_API_KEY)


# ---------------------------------------------------------
# Tool argument schemas
# ---------------------------------------------------------

class SearchCoursesArgs(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=10)


class GetCourseDetailsArgs(BaseModel):
    course_id: int = Field(gt=0)

class CheckCourseEligibilityArgs(BaseModel):
    course_id: int = Field(gt=0)

TOOL_ARGUMENT_MODELS = {
    "search_courses": SearchCoursesArgs,
    "check_course_eligibility": CheckCourseEligibilityArgs,
    "get_course_details": GetCourseDetailsArgs,
}

def count_eligible_courses(
    observations: list[dict],
) -> int:
    """Count courses confirmed eligible by the tool."""

    eligible_course_ids = set()

    for observation in observations:
        if observation["tool"] != "check_course_eligibility":
            continue

        result = observation["result"]

        if result.get("eligible") is True:
            course_id = result.get("course_id")

            if course_id is not None:
                eligible_course_ids.add(course_id)

    return len(eligible_course_ids)

# ---------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------

TOOL_REGISTRY = {
    "search_courses": search_courses_tool,
    "check_course_eligibility": check_course_eligibility,
    "get_course_details": get_course_details,
}

# ---------------------------------------------------------
# Gemini tool declarations
# ---------------------------------------------------------

SEARCH_COURSES_DECLARATION = types.FunctionDeclaration(
    name="search_courses",
    description=(
        "Search the course catalog for courses relevant "
        "to the student's goal. Only eligible courses "
        "are returned."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "query": types.Schema(
                type=types.Type.STRING,
                description=(
                    "Natural-language description of "
                    "what the student wants to learn."
                ),
            ),
            "limit": types.Schema(
                type=types.Type.INTEGER,
                description=(
                    "Maximum number of courses to return."
                ),
            ),
        },
        required=["query"],
    ),
)


GET_COURSE_DETAILS_DECLARATION = types.FunctionDeclaration(
    name="get_course_details",
    description=(
        "Get complete information about a specific course."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "course_id": types.Schema(
                type=types.Type.INTEGER,
                description="The course ID.",
            ),
        },
        required=["course_id"],
    ),
)

CHECK_ELIGIBILITY_DECLARATION = types.FunctionDeclaration(
    name="check_course_eligibility",
    description=(
        "Check whether a student satisfies the prerequisites "
        "for a specific course."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "course_id": types.Schema(
                type=types.Type.INTEGER,
                description="The course ID to evaluate.",
            ),
        },
        required=["course_id"],
    ),
)

TOOLS = types.Tool(
    function_declarations=[
        SEARCH_COURSES_DECLARATION,
        CHECK_ELIGIBILITY_DECLARATION,
        GET_COURSE_DETAILS_DECLARATION,
    ]
)

# ---------------------------------------------------------
# Tool execution
# ---------------------------------------------------------

def execute_tool(
    name: str,
    arguments: dict,
    student: Student,
) -> dict:

    print(f"\n[TOOL CALL] {name}")
    print(f"[ARGUMENTS] {arguments}")

    if name not in TOOL_REGISTRY:
        return {
            "error": f"Unknown tool: {name}"
        }

    argument_model = TOOL_ARGUMENT_MODELS[name]

    try:
        validated = argument_model.model_validate(arguments)
    except Exception as exc:
        return {
            "error": "Invalid tool arguments.",
            "details": str(exc),
        }

    try:
        if name == "search_courses":
            result = TOOL_REGISTRY[name](
                student=student,
                **validated.model_dump(),
            )

        elif name == "check_course_eligibility":
            result = TOOL_REGISTRY[name](
                student=student,
                **validated.model_dump(),
            )

        else:
            result = TOOL_REGISTRY[name](
                **validated.model_dump()
            )

        print(f"[TOOL RESULT] {result}")

        return result

    except Exception as exc:
        return {
            "error": "Tool execution failed.",
            "details": str(exc),
        }


# ---------------------------------------------------------
# Agent loop
# ---------------------------------------------------------

SYSTEM_PROMPT = """
You are a course recommendation agent.

Your job is to recommend the best courses for the student.

Follow this process:

1. Use search_courses to find relevant candidate courses.
2. Select the most promising candidates.
3. Use check_course_eligibility to verify prerequisites.
4. Do not inspect every course.
5. Do not repeatedly search for the same information.
6. Recommend at most 3 courses.
7. Only recommend courses confirmed to be eligible.
8. Never invent course information.
9. Consider the student's goal, skills, and available study time.
10. Once you have enough evidence, stop using tools and provide
    the final recommendation.
"""
def run_agent(
    student: Student,
    max_iterations: int = 5,
) -> str:

    student_json = json.dumps(
        student.model_dump(),
        indent=2,
    )

    user_message = f"""
Student profile:

{student_json}

Recommend the best courses for this student.

Use the available tools before making your
recommendations.
"""
    tool_observations = []

    print("[AGENT] Starting...")

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=SYSTEM_PROMPT
                        + "\n\n"
                        + user_message
                    )
                ],
            )
        ],
        config=types.GenerateContentConfig(
            tools=[TOOLS],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        ),
    )

    for iteration in range(max_iterations):

        print(
            f"\n[AGENT] Iteration {iteration + 1}"
        )

        function_calls = []

        for candidate in response.candidates:

            if not candidate.content:
                continue

            for part in candidate.content.parts:

                if part.function_call:
                    function_calls.append(
                        part.function_call
                    )

        if not function_calls:

            print("[AGENT] No more tool calls.")

            return response.text

        tool_response_parts = []

        for function_call in function_calls:

            tool_name = function_call.name

            arguments = dict(
                function_call.args or {}
            )

            result = execute_tool(
                name=tool_name,
                arguments=arguments,
                student=student,
            )

            tool_observations.append(
                {
                    "tool": tool_name,
                    "arguments": arguments,
                    "result": result,
                }
            )

            if count_eligible_courses(tool_observations) >= 3:
                print(
                    "\n[AGENT] Enough eligible courses found."
                )
                print(
                    "[AGENT] Switching to finalization."
                )

                break

            tool_response_parts.append(
                types.Part.from_function_response(
                    name=tool_name,
                    response=result,
                )
            )

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(
                            text=SYSTEM_PROMPT
                            + "\n\n"
                            + user_message
                        ),
                    ],
                ),
                response.candidates[0].content,
                types.Content(
                    role="user",
                    parts=tool_response_parts,
                ),
            ],
            config=types.GenerateContentConfig(
                tools=[TOOLS],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
            ),
        )

    print(
        "\n[AGENT] Agent tool phase complete."
    )

    print(
        "[AGENT] Switching to deterministic finalization."
    )

    final_prompt = f"""
You are the final answer generator for a course
recommendation system.

Student:

{student_json}

The agent gathered the following information:

{json.dumps(tool_observations, indent=2)}

Using ONLY the information above:

1. Recommend up to 3 relevant courses.
2. Do not invent courses or course details.
3. Consider the student's goal.
4. Consider the student's skills.
5. Consider available study time.
6. Explain each recommendation briefly.
7. Do not call any tools.
8. Return a concise final answer.
"""

    final_response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=final_prompt,
    )

    return final_response.text