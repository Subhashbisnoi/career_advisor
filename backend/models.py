from typing import TypedDict, List
from pydantic import BaseModel, Field

class FeedbackItem(BaseModel):
    """Feedback for a single interview question answer."""
    feedback: str = Field(..., description="Constructive feedback in one concise statement.")
    marks: int = Field(..., ge=0, le=10, description="Score for the answer out of 10.")

class InterviewQuestions(BaseModel):
    """Model for interview questions."""
    questions: List[str] = Field(..., description="A list of 3 interview questions.")

class StructuredEvaluator(BaseModel):
    """Model for structured evaluation of interview answers."""
    feedback_list: List[FeedbackItem] = Field(
        ..., description="List containing feedback and marks for each answer."
    )

class InterviewState(TypedDict):
    """State of the interview process."""
    role: str
    company: str
    resume_text: str  # Changed from resume_path to resume_text
    question: List[str]
    answer: List[str]
    feedback: List[dict]
    roadmap: str