from typing import List, Optional, Dict, Any, TypedDict
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum

# Enums for structured data
class EducationLevel(str, enum.Enum):
    HIGH_SCHOOL = "high_school"
    BACHELOR = "bachelor"
    MASTER = "master"
    PHD = "phd"
    DIPLOMA = "diploma"
    CERTIFICATION = "certification"

class AssessmentType(str, enum.Enum):
    SKILLS = "skills"
    APTITUDE = "aptitude"
    INTEREST = "interest"
    PERSONALITY = "personality"
    COMPREHENSIVE = "comprehensive"

class SkillLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class CareerField(str, enum.Enum):
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    EDUCATION = "education"
    ENGINEERING = "engineering"
    BUSINESS = "business"
    CREATIVE = "creative"
    SCIENCE = "science"
    LAW = "law"
    GOVERNMENT = "government"

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
    assessments = relationship("CareerAssessment", back_populates="user")
    skills = relationship("UserSkill", back_populates="user")
    career_recommendations = relationship("CareerRecommendation", back_populates="user")
    learning_roadmaps = relationship("LearningRoadmap", back_populates="user")
    otps = relationship("OTP", back_populates="user")

class OTP(Base):
    __tablename__ = "otps"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    email = Column(String, index=True, nullable=False)
    otp_code = Column(String, nullable=False)
    purpose = Column(String, default="password_reset")
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="otps")

class CareerAssessment(Base):
    __tablename__ = "career_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    thread_id = Column(String, unique=True, index=True)  # LangGraph thread ID
    assessment_type = Column(String)  # skills, aptitude, interest, comprehensive
    status = Column(String, default="active")  # active, completed, archived
    
    # Assessment scores and results
    skills_score = Column(Float, default=0.0)
    aptitude_score = Column(Float, default=0.0)
    interest_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    
    # Assessment data
    responses = Column(JSON)  # Store assessment responses
    analysis_results = Column(JSON)  # Store AI analysis results
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="assessments")
    messages = relationship("AssessmentMessage", back_populates="assessment")

class AssessmentMessage(Base):
    __tablename__ = "assessment_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("career_assessments.id"))
    thread_id = Column(String, index=True)
    message_type = Column(String)  # question, answer, analysis, result
    role = Column(String)  # user, assistant, system
    content = Column(Text)
    question_number = Column(Integer, nullable=True)
    category = Column(String, nullable=True)  # technical, soft_skills, interests, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    message_metadata = Column(JSON)  # Changed from 'metadata' to avoid SQLAlchemy conflict
    
    # Relationships
    assessment = relationship("CareerAssessment", back_populates="messages")

class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=False)  # technical, soft, language, etc.
    field = Column(String, nullable=True)  # technology, healthcare, finance, etc.
    description = Column(Text, nullable=True)
    market_demand = Column(Float, default=0.0)  # Market demand score (0-10)
    trending_score = Column(Float, default=0.0)  # Trending score in Indian market
    
    # Relationships
    user_skills = relationship("UserSkill", back_populates="skill")
    career_skills = relationship("CareerSkill", back_populates="skill")

class UserSkill(Base):
    __tablename__ = "user_skills"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    skill_id = Column(Integer, ForeignKey("skills.id"))
    proficiency_level = Column(String)  # beginner, intermediate, advanced, expert
    self_assessed = Column(Boolean, default=True)
    verified = Column(Boolean, default=False)
    source = Column(String, nullable=True)  # assessment, resume, manual, certification
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="skills")
    skill = relationship("Skill", back_populates="user_skills")

class CareerPath(Base):
    __tablename__ = "career_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    field = Column(String, nullable=False)  # technology, healthcare, finance, etc.
    description = Column(Text)
    
    # Career details
    entry_level_salary = Column(Float, nullable=True)
    mid_level_salary = Column(Float, nullable=True)
    senior_level_salary = Column(Float, nullable=True)
    growth_rate = Column(Float, nullable=True)  # Expected annual growth rate
    job_market_score = Column(Float, default=0.0)  # Job availability score (0-10)
    
    # Requirements
    education_requirements = Column(JSON)  # List of education requirements
    experience_years_required = Column(Integer, default=0)
    
    # Market data
    demand_score = Column(Float, default=0.0)  # Market demand in India
    future_outlook = Column(String, nullable=True)  # positive, stable, declining
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    skills = relationship("CareerSkill", back_populates="career")
    recommendations = relationship("CareerRecommendation", back_populates="career")

class CareerSkill(Base):
    __tablename__ = "career_skills"
    
    id = Column(Integer, primary_key=True, index=True)
    career_id = Column(Integer, ForeignKey("career_paths.id"))
    skill_id = Column(Integer, ForeignKey("skills.id"))
    importance_level = Column(String)  # required, preferred, nice_to_have
    proficiency_required = Column(String)  # beginner, intermediate, advanced, expert
    
    # Relationships
    career = relationship("CareerPath", back_populates="skills")
    skill = relationship("Skill", back_populates="career_skills")

class CareerRecommendation(Base):
    __tablename__ = "career_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    career_id = Column(Integer, ForeignKey("career_paths.id"))
    assessment_id = Column(Integer, ForeignKey("career_assessments.id"), nullable=True)
    
    # Recommendation details
    match_score = Column(Float, nullable=False)  # How well the career matches (0-100)
    confidence_score = Column(Float, nullable=False)  # AI confidence in recommendation
    reasoning = Column(Text)  # Why this career was recommended
    
    # Skills analysis
    matching_skills = Column(JSON)  # Skills user already has
    missing_skills = Column(JSON)  # Skills user needs to develop
    skills_gap_score = Column(Float, default=0.0)  # Gap analysis score
    
    is_pinned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="career_recommendations")
    career = relationship("CareerPath", back_populates="recommendations")

class LearningRoadmap(Base):
    __tablename__ = "learning_roadmaps"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    career_recommendation_id = Column(Integer, ForeignKey("career_recommendations.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    
    # Roadmap details
    estimated_duration_months = Column(Integer)
    difficulty_level = Column(String)  # beginner, intermediate, advanced
    total_steps = Column(Integer, default=0)
    completed_steps = Column(Integer, default=0)
    progress_percentage = Column(Float, default=0.0)
    
    # Roadmap content - store structured data
    roadmap_data = Column(JSON)  # Complete structured roadmap with phases, steps, checkpoints
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="learning_roadmaps")
    checkpoints = relationship("RoadmapCheckpoint", back_populates="roadmap")

class RoadmapCheckpoint(Base):
    __tablename__ = "roadmap_checkpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("learning_roadmaps.id"))
    phase_id = Column(String, nullable=False)  # Phase identifier (e.g., "phase_1")
    step_id = Column(String, nullable=False)   # Step identifier (e.g., "step_1_1")
    step_title = Column(String, nullable=False)
    step_description = Column(Text)
    
    # Progress tracking
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    user_notes = Column(Text, nullable=True)
    
    # Step details
    estimated_hours = Column(Integer, default=0)
    difficulty_level = Column(String, default="beginner")  # beginner, intermediate, advanced
    step_type = Column(String, default="learning")  # learning, practice, project, assessment
    
    # Resources and links
    resources = Column(JSON)  # List of learning resources
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roadmap = relationship("LearningRoadmap", back_populates="checkpoints")

class AssessmentResult(Base):
    __tablename__ = "assessment_results"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("career_assessments.id"), unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Structured assessment results
    submission_summary = Column(JSON)  # Store the submission data
    processing_status = Column(String, default="completed")
    
    # Analysis results
    skills_analysis = Column(JSON)  # Detailed skills breakdown
    personality_insights = Column(JSON)  # Personality analysis
    career_fit_analysis = Column(JSON)  # Career fit analysis
    
    # Metadata
    total_questions = Column(Integer)
    completion_time = Column(DateTime)
    time_spent_seconds = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assessment = relationship("CareerAssessment", backref="result")
    user = relationship("User")

# Pydantic Models (for request/response validation)

class SkillAssessmentResponse(BaseModel):
    """Response for a skill assessment question."""
    question_id: str
    response: str
    confidence_level: int = Field(..., ge=1, le=5, description="Confidence level (1-5)")

class CareerAssessmentRequest(BaseModel):
    """Request to start a new career assessment."""
    assessment_type: AssessmentType = Field(..., description="Type of assessment to conduct")
    user_background: Optional[Dict[str, Any]] = Field(None, description="User background information")

class AssessmentSubmissionRequest(BaseModel):
    """Request to submit assessment responses."""
    thread_id: str = Field(..., description="Thread ID of the assessment session")
    responses: List[SkillAssessmentResponse] = Field(..., description="List of assessment responses")

class SkillAnalysisRequest(BaseModel):
    """Request for skills analysis from documents or manual input."""
    resume_text: Optional[str] = Field(None, description="Resume text content")
    transcript_text: Optional[str] = Field(None, description="Academic transcript content")
    manual_skills: Optional[List[str]] = Field(None, description="Manually entered skills")

class CareerRecommendationRequest(BaseModel):
    """Request for career recommendations."""
    assessment_id: Optional[int] = Field(None, description="Assessment ID to base recommendations on")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences and constraints")

class LearningRoadmapRequest(BaseModel):
    """Request to generate a learning roadmap."""
    career_recommendation_id: int = Field(..., description="Career recommendation to create roadmap for")
    target_timeline_months: Optional[int] = Field(12, description="Desired timeline in months")
    learning_style: Optional[str] = Field("mixed", description="Preferred learning style")

class RoadmapProgressRequest(BaseModel):
    """Request to update roadmap progress."""
    roadmap_id: int = Field(..., description="Roadmap ID")
    step_id: str = Field(..., description="Step ID to mark as completed")
    phase_id: str = Field(..., description="Phase ID containing the step")
    notes: Optional[str] = Field(None, description="Optional progress notes")

# Enhanced state management for LangGraph
class CareerAssessmentState(TypedDict):
    """State of the career assessment process."""
    # Session info
    thread_id: str
    user_id: int
    assessment_id: int
    
    # Assessment details
    assessment_type: str
    user_background: Dict[str, Any]
    
    # Assessment progress
    questions: List[Dict[str, Any]]
    responses: List[Dict[str, Any]]
    current_question: int
    
    # Analysis data
    skills_analysis: Dict[str, Any]
    aptitude_analysis: Dict[str, Any]
    interest_analysis: Dict[str, Any]
    personality_analysis: Dict[str, Any]
    
    # Scores
    skills_score: float
    aptitude_score: float
    interest_score: float
    overall_score: float
    
    # Results
    career_matches: List[Dict[str, Any]]
    skills_gaps: Dict[str, Any]
    recommendations: Dict[str, Any]
    
    # Status and metadata
    status: str  # started, in_progress, completed
    started_at: str
    completed_at: Optional[str]
    chat_history: List[dict]

# Response models
class UserProfileResponse(BaseModel):
    """User profile information."""
    id: int
    email: str
    full_name: Optional[str]
    created_at: datetime

class SkillResponse(BaseModel):
    """Skill information response."""
    id: int
    name: str
    category: str
    field: Optional[str]
    description: Optional[str]
    market_demand: float
    trending_score: float
    user_proficiency: Optional[str] = None

class CareerPathResponse(BaseModel):
    """Career path information response."""
    id: int
    title: str
    field: str
    description: Optional[str]
    entry_level_salary: Optional[float]
    mid_level_salary: Optional[float]
    senior_level_salary: Optional[float]
    growth_rate: Optional[float]
    job_market_score: float
    demand_score: float
    future_outlook: Optional[str]
    required_skills: List[SkillResponse]
    preferred_skills: List[SkillResponse]

class CareerRecommendationResponse(BaseModel):
    """Career recommendation response."""
    id: int
    career: CareerPathResponse
    match_score: float
    confidence_score: float
    reasoning: str
    matching_skills: List[str]
    missing_skills: List[str]
    skills_gap_score: float
    is_pinned: bool
    created_at: datetime

class RoadmapStep(BaseModel):
    """Roadmap step structure with checkpoint."""
    step_id: str
    title: str
    description: str
    estimated_hours: int
    difficulty_level: str  # beginner, intermediate, advanced
    step_type: str  # learning, practice, project, assessment
    resources: List[Dict[str, str]]
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    user_notes: Optional[str] = None

class RoadmapPhase(BaseModel):
    """Roadmap phase containing multiple steps."""
    phase_id: str
    title: str
    description: str
    estimated_duration_weeks: int
    steps: List[RoadmapStep]
    skills_focus: List[str]

class LearningRoadmapResponse(BaseModel):
    """Learning roadmap response."""
    id: int
    title: str
    description: Optional[str]
    estimated_duration_months: Optional[int]
    difficulty_level: Optional[str]
    total_steps: int
    completed_steps: int
    progress_percentage: float
    phases: List[RoadmapPhase]
    is_active: bool
    created_at: datetime
    updated_at: datetime

class RoadmapProgressRequest(BaseModel):
    """Request to update roadmap progress."""
    roadmap_id: int = Field(..., description="Roadmap ID")
    step_id: str = Field(..., description="Step ID to mark as completed")
    phase_id: str = Field(..., description="Phase ID containing the step")
    notes: Optional[str] = Field(None, description="Optional progress notes")

class AssessmentSummaryResponse(BaseModel):
    """Assessment summary response."""
    id: int
    assessment_type: str
    status: str
    skills_score: float
    aptitude_score: float
    interest_score: float
    overall_score: float
    created_at: datetime
    completed_at: Optional[datetime]

class MarketTrendsResponse(BaseModel):
    """Job market trends response."""
    trending_skills: List[SkillResponse]
    emerging_careers: List[CareerPathResponse]
    high_demand_fields: List[str]
    salary_insights: Dict[str, Any]
    industry_growth: Dict[str, float]

# OTP related models (keeping the same)
class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., description="Email address to send OTP")

class VerifyOTPRequest(BaseModel):
    email: str = Field(..., description="Email address")
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")

class ResetPasswordRequest(BaseModel):
    email: str = Field(..., description="Email address")
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")
    new_password: str = Field(..., min_length=6, description="New password")

class MessageResponse(BaseModel):
    message: str