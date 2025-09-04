from typing import List, Optional, Dict, Any, TypedDict
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from database import Base

# SQLAlchemy Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    interviews = relationship("InterviewSession", back_populates="user")

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    thread_id = Column(String, unique=True, index=True)  # LangGraph thread ID
    role = Column(String)
    company = Column(String)
    resume_text = Column(Text)  # Store resume text directly
    status = Column(String, default="active")  # active, completed, archived
    total_score = Column(Float, default=0.0)
    average_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="interviews")
    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"))
    thread_id = Column(String, index=True)  # LangGraph thread ID for quick access
    message_type = Column(String)  # question, answer, feedback, roadmap, system
    role = Column(String)  # user, assistant, system
    content = Column(Text)
    question_number = Column(Integer, nullable=True)  # For tracking which question this relates to
    marks = Column(Integer, nullable=True)  # Marks for answers (0-10)
    created_at = Column(DateTime, default=datetime.utcnow)
    message_metadata = Column("metadata", JSON)  # For storing additional structured data
    
    # Relationships
    session = relationship("InterviewSession", back_populates="messages")

# Pydantic Models (for request/response validation)

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

# Enhanced state management for LangGraph
class InterviewState(TypedDict):
    """Enhanced state of the interview process with threading support."""
    # Session info
    thread_id: str
    user_id: int
    session_id: int
    
    # Interview details
    role: str
    company: str
    resume_text: str
    
    # Interview progress
    questions: List[str]
    answers: List[str]
    current_question: int
    
    # Evaluation data
    feedback: List[dict]
    marks: List[int]
    total_score: float
    average_score: float
    
    # Final output
    roadmap: str
    
    # Status and metadata
    status: str  # started, in_progress, completed
    started_at: str
    completed_at: Optional[str]
    chat_history: List[dict]

# Pydantic models for API requests/responses
class InterviewStartRequest(BaseModel):
    role: str = Field(..., min_length=1, description="Job role for the interview")
    company: str = Field(..., min_length=1, description="Company name")
    resume_text: str = Field(..., min_length=10, description="Resume text content")

class AnswerSubmissionRequest(BaseModel):
    thread_id: str = Field(..., description="Thread ID of the interview session")
    question_number: int = Field(..., ge=1, le=3, description="Question number (1-3)")
    answer: str = Field(..., min_length=1, description="Answer to the question")

class ChatHistoryResponse(BaseModel):
    thread_id: str
    session_id: int
    role: str
    company: str
    status: str
    total_score: float
    average_score: float
    created_at: datetime
    completed_at: Optional[datetime]
    messages: List[Dict[str, Any]]

class InterviewSessionResponse(BaseModel):
    thread_id: str
    session_id: int
    role: str
    company: str
    status: str
    questions: List[str]
    current_question: int
    total_score: float
    average_score: float
    created_at: datetime