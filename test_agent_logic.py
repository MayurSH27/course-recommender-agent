from course_recommender.agent import count_eligible_courses


def test_count_eligible_courses():
    observations = [
        {
            "tool": "check_course_eligibility",
            "arguments": {"course_id": 1},
            "result": {
                "course_id": 1,
                "eligible": True,
            },
        },
        {
            "tool": "check_course_eligibility",
            "arguments": {"course_id": 2},
            "result": {
                "course_id": 2,
                "eligible": True,
            },
        },
        {
            "tool": "check_course_eligibility",
            "arguments": {"course_id": 4},
            "result": {
                "course_id": 4,
                "eligible": False,
            },
        },
    ]

    assert count_eligible_courses(observations) == 2


def test_duplicate_eligible_course_only_counted_once():
    observations = [
        {
            "tool": "check_course_eligibility",
            "arguments": {"course_id": 2},
            "result": {
                "course_id": 2,
                "eligible": True,
            },
        },
        {
            "tool": "check_course_eligibility",
            "arguments": {"course_id": 2},
            "result": {
                "course_id": 2,
                "eligible": True,
            },
        },
    ]

    assert count_eligible_courses(observations) == 1


def test_non_eligibility_tools_are_ignored():
    observations = [
        {
            "tool": "search_courses",
            "arguments": {},
            "result": {
                "courses": [
                    {"id": 1},
                    {"id": 2},
                ]
            },
        }
    ]

    assert count_eligible_courses(observations) == 0