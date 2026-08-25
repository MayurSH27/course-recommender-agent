from typing import Literal
from pydantic import BaseModel, Field

SkillLevel = Literal["beginner", "intermediate", "advanced"]
Priority = Literal["high", "medium", "low"]

class Student(BaseModel):
    name: str
    goal: str
    skills: dict[str, SkillLevel]
    available_hours_per_week: int = Field(ge=1)

class Course(BaseModel):
    id: int
    name: str
    description:str
    level: SkillLevel
    prerequisites: dict[str, SkillLevel]
    duration_hours: int = Field(gt=0)

class Recommendation(BaseModel):
    course_id: int
    course_name: str
    priority: Priority
    reason: str

class RecommendationResponse(BaseModel):
    recommendations: list[Recommendation]
    