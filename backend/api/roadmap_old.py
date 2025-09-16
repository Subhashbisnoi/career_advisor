"""
Learning Roadmap API endpoints - Enhanced with checkpoint tracking
Handles personalized learning roadmap generation and progress tracking.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
from datetime import datetime, timedelta

from database import get_db
from models import (
    User, LearningRoadmap, RoadmapCheckpoint, CareerRecommendation, CareerPath,
    LearningRoadmapRequest, RoadmapProgressRequest, LearningRoadmapResponse,
    RoadmapStep, RoadmapPhase, MessageResponse
)
from api.auth import get_current_user

router = APIRouter(prefix="/roadmap", tags=["Learning Roadmaps"])

@router.post("/generate-from-recommendation")
async def generate_roadmap_from_recommendation(
    request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate and store a learning roadmap from career recommendation data."""
    print(f"[ROADMAP DEBUG] Generating roadmap from recommendation for user {current_user.id}")
    print(f"[ROADMAP DEBUG] Request data: {request}")
    
    try:
        career_data = request.get("career", {})
        recommendation_data = request.get("recommendation", {})
        skills_to_develop = request.get("skills_to_develop", [])
        current_skills = request.get("matching_skills", [])
        
        # Check if roadmap already exists for this career
        existing_roadmap = db.query(LearningRoadmap).filter(
            LearningRoadmap.user_id == current_user.id,
            LearningRoadmap.title.like(f"%{career_data.get('title', '')}%"),
            LearningRoadmap.is_active == True
        ).first()
        
        if existing_roadmap:
            print(f"[ROADMAP DEBUG] Found existing roadmap: {existing_roadmap.id}")
            return _format_roadmap_for_frontend(existing_roadmap, db)
        
        # Generate new roadmap structure
        roadmap_data = _create_roadmap_structure(career_data, skills_to_develop, current_skills)
        
        # Store in database
        roadmap = LearningRoadmap(
            user_id=current_user.id,
            career_recommendation_id=recommendation_data.get("id"),
            title=f"Learning Path: {career_data.get('title', 'Career Development')}",
            description=f"Comprehensive learning roadmap to become a {career_data.get('title', 'professional')}",
            estimated_duration_months=roadmap_data["timeline_months"],
            difficulty_level="intermediate",
            total_steps=roadmap_data["total_steps"],
            completed_steps=0,
            progress_percentage=0.0,
            roadmap_data=roadmap_data
        )
        
        db.add(roadmap)
        db.commit()
        db.refresh(roadmap)
        
        # Create checkpoints for each step
        _create_roadmap_checkpoints(roadmap, roadmap_data, db)
        
        print(f"[ROADMAP DEBUG] Created new roadmap with ID: {roadmap.id}")
        
        return _format_roadmap_for_frontend(roadmap, db)
        
    except Exception as e:
        db.rollback()
        print(f"[ROADMAP DEBUG] Error: {str(e)}")
        import traceback
        print(f"[ROADMAP DEBUG] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to generate roadmap: {str(e)}")

def _create_roadmap_structure(career_data, skills_to_develop, current_skills):
    """Create a structured roadmap based on career and skills data."""
    phases = []
    total_steps = 0
    
    # Phase 1: Foundation Phase
    if skills_to_develop:
        foundation_skills = skills_to_develop[:3] if len(skills_to_develop) > 3 else skills_to_develop
        steps = []
        
        for idx, skill in enumerate(foundation_skills):
            step = {
                "step_id": f"foundation_{idx + 1}",
                "title": f"Learn {skill} Fundamentals",
                "description": f"Master the basics of {skill} through structured learning",
                "estimated_hours": 40,
                "difficulty_level": "beginner",
                "step_type": "learning",
                "resources": [
                    {
                        "type": "course",
                        "title": f"{skill} Fundamentals Course",
                        "provider": "Online Platform",
                        "url": "#",
                        "cost": "Free"
                    },
                    {
                        "type": "practice",
                        "title": f"{skill} Practice Exercises",
                        "provider": "Interactive Platform",
                        "url": "#",
                        "cost": "Free"
                    }
                ]
            }
            steps.append(step)
            total_steps += 1
        
        phases.append({
            "phase_id": "foundation",
            "title": "Foundation Phase",
            "description": "Build essential skills for your career path",
            "estimated_duration_weeks": 6,
            "steps": steps,
            "skills_focus": foundation_skills
        })
    
    # Phase 2: Intermediate Phase
    if len(skills_to_develop) > 3:
        intermediate_skills = skills_to_develop[3:6]
        steps = []
        
        for idx, skill in enumerate(intermediate_skills):
            step = {
                "step_id": f"intermediate_{idx + 1}",
                "title": f"Apply {skill} in Projects",
                "description": f"Build practical projects using {skill}",
                "estimated_hours": 60,
                "difficulty_level": "intermediate",
                "step_type": "project",
                "resources": [
                    {
                        "type": "project",
                        "title": f"{skill} Project Tutorial",
                        "provider": "Project Platform",
                        "url": "#",
                        "cost": "Free"
                    },
                    {
                        "type": "documentation",
                        "title": f"{skill} Documentation",
                        "provider": "Official Docs",
                        "url": "#",
                        "cost": "Free"
                    }
                ]
            }
            steps.append(step)
            total_steps += 1
        
        phases.append({
            "phase_id": "intermediate",
            "title": "Practical Application",
            "description": "Apply skills through hands-on projects",
            "estimated_duration_weeks": 8,
            "steps": steps,
            "skills_focus": intermediate_skills
        })
    
    # Phase 3: Advanced Phase
    steps = [
        {
            "step_id": "portfolio_1",
            "title": "Build Professional Portfolio",
            "description": "Create a comprehensive portfolio showcasing your skills",
            "estimated_hours": 80,
            "difficulty_level": "advanced",
            "step_type": "project",
            "resources": [
                {
                    "type": "guide",
                    "title": "Portfolio Building Guide",
                    "provider": "Career Platform",
                    "url": "#",
                    "cost": "Free"
                }
            ]
        },
        {
            "step_id": "interview_prep",
            "title": "Interview Preparation",
            "description": "Prepare for technical interviews and assessments",
            "estimated_hours": 40,
            "difficulty_level": "intermediate",
            "step_type": "practice",
            "resources": [
                {
                    "type": "practice",
                    "title": "Mock Interview Platform",
                    "provider": "Interview Platform",
                    "url": "#",
                    "cost": "Free"
                }
            ]
        },
        {
            "step_id": "networking",
            "title": "Professional Networking",
            "description": "Build connections and explore job opportunities",
            "estimated_hours": 20,
            "difficulty_level": "beginner",
            "step_type": "networking",
            "resources": [
                {
                    "type": "platform",
                    "title": "LinkedIn Networking",
                    "provider": "LinkedIn",
                    "url": "#",
                    "cost": "Free"
                }
            ]
        }
    ]
    
    total_steps += len(steps)
    
    phases.append({
        "phase_id": "advanced",
        "title": "Career Preparation",
        "description": "Prepare for professional opportunities",
        "estimated_duration_weeks": 6,
        "steps": steps,
        "skills_focus": ["Portfolio Development", "Interview Skills", "Networking"]
    })
    
    total_weeks = sum(phase["estimated_duration_weeks"] for phase in phases)
    
    return {
        "career_path": career_data.get("title", "Career Development"),
        "description": career_data.get("description", "Comprehensive learning path"),
        "timeline_months": max(1, total_weeks // 4),
        "phases": phases,
        "total_steps": total_steps,
        "skills_to_develop": skills_to_develop,
        "current_skills": current_skills
    }

def _create_roadmap_checkpoints(roadmap: LearningRoadmap, roadmap_data: Dict, db: Session):
    """Create checkpoint records for each step in the roadmap."""
    for phase in roadmap_data["phases"]:
        phase_id = phase["phase_id"]
        
        for step in phase["steps"]:
            checkpoint = RoadmapCheckpoint(
                roadmap_id=roadmap.id,
                phase_id=phase_id,
                step_id=step["step_id"],
                step_title=step["title"],
                step_description=step["description"],
                is_completed=False,
                estimated_hours=step["estimated_hours"],
                difficulty_level=step["difficulty_level"],
                step_type=step["step_type"],
                resources=step["resources"]
            )
            db.add(checkpoint)
    
    db.commit()

def _format_roadmap_for_frontend(roadmap: LearningRoadmap, db: Session):
    """Format roadmap data for frontend consumption with checkpoints."""
    # Get checkpoints for this roadmap
    checkpoints = db.query(RoadmapCheckpoint).filter(
        RoadmapCheckpoint.roadmap_id == roadmap.id
    ).all()
    
    # Group checkpoints by phase
    phases_with_checkpoints = []
    roadmap_data = roadmap.roadmap_data or {}
    
    for phase in roadmap_data.get("phases", []):
        phase_checkpoints = [cp for cp in checkpoints if cp.phase_id == phase["phase_id"]]
        
        # Add checkpoint data to steps
        steps_with_progress = []
        for step in phase.get("steps", []):
            step_checkpoint = next((cp for cp in phase_checkpoints if cp.step_id == step["step_id"]), None)
            
            step_data = {**step}
            if step_checkpoint:
                step_data.update({
                    "is_completed": step_checkpoint.is_completed,
                    "completed_at": step_checkpoint.completed_at.isoformat() if step_checkpoint.completed_at else None,
                    "user_notes": step_checkpoint.user_notes
                })
            else:
                step_data.update({
                    "is_completed": False,
                    "completed_at": None,
                    "user_notes": None
                })
            
            steps_with_progress.append(step_data)
        
        phase_with_progress = {**phase}
        phase_with_progress["steps"] = steps_with_progress
        phases_with_checkpoints.append(phase_with_progress)
    
    return {
        "id": roadmap.id,
        "career_path": roadmap.title.replace("Learning Path: ", ""),
        "description": roadmap.description,
        "timeline_months": roadmap.estimated_duration_months,
        "phases": phases_with_checkpoints,
        "total_steps": roadmap.total_steps,
        "completed_steps": roadmap.completed_steps,
        "progress": {
            "completed_steps": roadmap.completed_steps,
            "total_steps": roadmap.total_steps,
            "overall_progress": roadmap.progress_percentage
        },
        "created_at": roadmap.created_at.isoformat() if roadmap.created_at else None
    }

@router.get("/", response_model=Dict[str, Any])
async def get_user_roadmaps_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all roadmaps for the user (for dashboard and roadmap page)."""
    print(f"[ROADMAP DEBUG] Getting roadmaps for user {current_user.id}")
    
    try:
        roadmaps = db.query(LearningRoadmap).filter(
            LearningRoadmap.user_id == current_user.id,
            LearningRoadmap.is_active == True
        ).order_by(LearningRoadmap.created_at.desc()).all()
        
        formatted_roadmaps = [_format_roadmap_for_frontend(roadmap, db) for roadmap in roadmaps]
        
        print(f"[ROADMAP DEBUG] Found {len(formatted_roadmaps)} roadmaps")
        
        return {
            "roadmaps": formatted_roadmaps,
            "total_roadmaps": len(formatted_roadmaps),
            "active_roadmaps": len([r for r in formatted_roadmaps if r["progress"]["overall_progress"] < 100])
        }
        
    except Exception as e:
        print(f"[ROADMAP DEBUG] Error getting roadmaps: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get roadmaps: {str(e)}")

@router.post("/update-progress")
async def update_step_progress(
    request: RoadmapProgressRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update progress on a roadmap step."""
    print(f"[ROADMAP DEBUG] Updating step progress for roadmap {request.roadmap_id}")
    
    try:
        # Find the checkpoint
        checkpoint = db.query(RoadmapCheckpoint).filter(
            RoadmapCheckpoint.roadmap_id == request.roadmap_id,
            RoadmapCheckpoint.phase_id == request.phase_id,
            RoadmapCheckpoint.step_id == request.step_id
        ).first()
        
        if not checkpoint:
            raise HTTPException(status_code=404, detail="Step not found")
        
        # Update checkpoint
        checkpoint.is_completed = True
        checkpoint.completed_at = datetime.utcnow()
        if request.notes:
            checkpoint.user_notes = request.notes
        
        # Update roadmap progress
        roadmap = db.query(LearningRoadmap).filter(
            LearningRoadmap.id == request.roadmap_id,
            LearningRoadmap.user_id == current_user.id
        ).first()
        
        if roadmap:
            # Count completed steps
            completed_count = db.query(RoadmapCheckpoint).filter(
                RoadmapCheckpoint.roadmap_id == roadmap.id,
                RoadmapCheckpoint.is_completed == True
            ).count()
            
            roadmap.completed_steps = completed_count
            roadmap.progress_percentage = (completed_count / roadmap.total_steps * 100) if roadmap.total_steps > 0 else 0
            roadmap.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "message": "Progress updated successfully",
            "completed_steps": roadmap.completed_steps if roadmap else 0,
            "total_steps": roadmap.total_steps if roadmap else 0,
            "progress_percentage": roadmap.progress_percentage if roadmap else 0
        }
        
    except Exception as e:
        db.rollback()
        print(f"[ROADMAP DEBUG] Error updating progress: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update progress: {str(e)}")

@router.get("/{roadmap_id}")
async def get_roadmap_details(
    roadmap_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific roadmap."""
    roadmap = db.query(LearningRoadmap).filter(
        LearningRoadmap.id == roadmap_id,
        LearningRoadmap.user_id == current_user.id
    ).first()
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    return _format_roadmap_for_frontend(roadmap, db)

@router.delete("/{roadmap_id}")
async def delete_roadmap(
    roadmap_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a learning roadmap."""
    roadmap = db.query(LearningRoadmap).filter(
        LearningRoadmap.id == roadmap_id,
        LearningRoadmap.user_id == current_user.id
    ).first()
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    try:
        # Delete associated checkpoints
        db.query(RoadmapCheckpoint).filter(
            RoadmapCheckpoint.roadmap_id == roadmap_id
        ).delete()
        
        # Mark roadmap as inactive
        roadmap.is_active = False
        
        db.commit()
        
        return {"message": "Roadmap deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete roadmap: {str(e)}")

@router.get("/analytics/{roadmap_id}")
async def get_roadmap_analytics(
    roadmap_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics and insights for a roadmap."""
    roadmap = db.query(LearningRoadmap).filter(
        LearningRoadmap.id == roadmap_id,
        LearningRoadmap.user_id == current_user.id
    ).first()
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    # Get checkpoints
    checkpoints = db.query(RoadmapCheckpoint).filter(
        RoadmapCheckpoint.roadmap_id == roadmap_id
    ).all()
    
    completed_checkpoints = [cp for cp in checkpoints if cp.is_completed]
    
    # Time-based analytics
    start_date = roadmap.created_at
    current_date = datetime.utcnow()
    elapsed_days = (current_date - start_date).days
    estimated_total_days = roadmap.estimated_duration_months * 30
    
    # Calculate analytics
    expected_progress = (elapsed_days / estimated_total_days * 100) if estimated_total_days > 0 else 0
    actual_progress = roadmap.progress_percentage
    pace = "on_track" if abs(actual_progress - expected_progress) <= 10 else ("ahead" if actual_progress > expected_progress else "behind")
    
    return {
        "roadmap_id": roadmap_id,
        "overall_progress": {
            "completion_percentage": roadmap.progress_percentage,
            "completed_steps": len(completed_checkpoints),
            "total_steps": len(checkpoints),
            "elapsed_days": elapsed_days,
            "estimated_total_days": estimated_total_days
        },
        "pace_analysis": {
            "expected_progress": expected_progress,
            "actual_progress": actual_progress,
            "pace": pace
        },
        "step_breakdown": [
            {
                "step_title": cp.step_title,
                "is_completed": cp.is_completed,
                "estimated_hours": cp.estimated_hours,
                "difficulty_level": cp.difficulty_level,
                "step_type": cp.step_type
            }
            for cp in checkpoints
        ]
    }

@router.post("/generate-from-recommendation")
async def generate_roadmap_from_recommendation(
    request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate and store a learning roadmap from career recommendation data."""
    print(f"[ROADMAP DEBUG] Generating roadmap from recommendation for user {current_user.id}")
    print(f"[ROADMAP DEBUG] Request data: {request}")
    
    try:
        career_data = request.get("career", {})
        recommendation_data = request.get("recommendation", {})
        skills_to_develop = request.get("skills_to_develop", [])
        current_skills = request.get("matching_skills", [])
        
        # Check if roadmap already exists for this career
        existing_roadmap = db.query(LearningRoadmap).filter(
            LearningRoadmap.user_id == current_user.id,
            LearningRoadmap.title.like(f"%{career_data.get('title', '')}%"),
            LearningRoadmap.is_active == True
        ).first()
        
        if existing_roadmap:
            print(f"[ROADMAP DEBUG] Found existing roadmap: {existing_roadmap.id}")
            return _format_roadmap_for_frontend(existing_roadmap)
        
        # Generate new roadmap structure
        roadmap_data = _create_roadmap_structure(career_data, skills_to_develop, current_skills)
        
        # Store in database
        roadmap = LearningRoadmap(
            user_id=current_user.id,
            career_recommendation_id=recommendation_data.get("id"),
            title=f"Learning Path: {career_data.get('title', 'Career Development')}",
            description=f"Comprehensive learning roadmap to become a {career_data.get('title', 'professional')}",
            estimated_duration_months=roadmap_data["timeline_months"],
            difficulty_level="intermediate",
            total_milestones=len(roadmap_data["phases"]),
            completed_milestones=0,
            progress_percentage=0.0,
            phases=roadmap_data["phases"],
            generated_content=roadmap_data
        )
        
        db.add(roadmap)
        db.commit()
        db.refresh(roadmap)
        
        print(f"[ROADMAP DEBUG] Created new roadmap with ID: {roadmap.id}")
        
        return _format_roadmap_for_frontend(roadmap)
        
    except Exception as e:
        db.rollback()
        print(f"[ROADMAP DEBUG] Error: {str(e)}")
        import traceback
        print(f"[ROADMAP DEBUG] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to generate roadmap: {str(e)}")

def _create_roadmap_structure(career_data, skills_to_develop, current_skills):
    """Create a structured roadmap based on career and skills data."""
    phases = []
    
    # Foundation Phase
    if skills_to_develop:
        foundation_skills = skills_to_develop[:3] if len(skills_to_develop) > 3 else skills_to_develop
        phases.append({
            "id": 1,
            "title": "Foundation Phase",
            "description": "Build essential skills for your career path",
            "duration_weeks": 4,
            "status": "not_started",
            "completion_percentage": 0,
            "milestones": [
                {
                    "id": idx + 1,
                    "title": f"Master {skill}",
                    "completed": False,
                    "description": f"Learn the fundamentals of {skill}"
                } for idx, skill in enumerate(foundation_skills)
            ],
            "resources": [
                {
                    "id": idx + 1,
                    "title": f"{skill} Fundamentals",
                    "description": f"Complete course on {skill} basics",
                    "type": "course",
                    "duration": "2-3 weeks",
                    "rating": 4.5,
                    "completed": False,
                    "url": f"#{skill.lower().replace(' ', '-')}"
                } for idx, skill in enumerate(foundation_skills)
            ]
        })
    
    # Intermediate Phase
    if len(skills_to_develop) > 3:
        intermediate_skills = skills_to_develop[3:6]
        phases.append({
            "id": 2,
            "title": "Intermediate Phase", 
            "description": "Develop practical skills and build projects",
            "duration_weeks": 6,
            "status": "not_started",
            "completion_percentage": 0,
            "milestones": [
                {
                    "id": idx + 4,
                    "title": f"Apply {skill}",
                    "completed": False,
                    "description": f"Build projects using {skill}"
                } for idx, skill in enumerate(intermediate_skills)
            ],
            "resources": [
                {
                    "id": idx + 4,
                    "title": f"{skill} Projects",
                    "description": f"Hands-on projects to practice {skill}",
                    "type": "project",
                    "duration": "1-2 weeks",
                    "rating": 4.7,
                    "completed": False,
                    "url": f"#{skill.lower().replace(' ', '-')}-projects"
                } for idx, skill in enumerate(intermediate_skills)
            ]
        })
    
    # Advanced Phase - Career Preparation
    phases.append({
        "id": 3,
        "title": "Career Preparation",
        "description": "Master advanced concepts and prepare for the role",
        "duration_weeks": 8,
        "status": "not_started", 
        "completion_percentage": 0,
        "milestones": [
            {
                "id": 7,
                "title": "Build Portfolio",
                "completed": False,
                "description": "Create a comprehensive portfolio showcasing your skills"
            },
            {
                "id": 8,
                "title": "Practice Interviews",
                "completed": False,
                "description": "Prepare for technical interviews and behavioral questions"
            },
            {
                "id": 9,
                "title": "Network & Apply",
                "completed": False,
                "description": "Connect with professionals and apply for positions"
            }
        ],
        "resources": [
            {
                "id": 7,
                "title": "Portfolio Development",
                "description": "Build a professional portfolio website",
                "type": "project",
                "duration": "2-3 weeks",
                "rating": 4.8,
                "completed": False,
                "url": "#portfolio"
            },
            {
                "id": 8,
                "title": "Interview Preparation",
                "description": "Mock interviews and coding challenges",
                "type": "practice",
                "duration": "2 weeks", 
                "rating": 4.6,
                "completed": False,
                "url": "#interviews"
            }
        ]
    })
    
    total_weeks = sum(phase["duration_weeks"] for phase in phases)
    
    return {
        "career_path": career_data.get("title", "Career Development"),
        "description": career_data.get("description", "Comprehensive learning path"),
        "timeline_months": max(1, total_weeks // 4),
        "phases": phases,
        "total_resources": sum(len(phase.get("resources", [])) for phase in phases),
        "skills_to_develop": skills_to_develop,
        "current_skills": current_skills
    }

def _format_roadmap_for_frontend(roadmap):
    """Format roadmap data for frontend consumption."""
    return {
        "id": roadmap.id,
        "career_path": roadmap.title.replace("Learning Path: ", ""),
        "description": roadmap.description,
        "timeline_months": roadmap.estimated_duration_months,
        "phases": roadmap.phases,
        "total_resources": roadmap.total_milestones,
        "progress": {
            "completed_phases": roadmap.completed_milestones,
            "completed_milestones": roadmap.completed_milestones,
            "hours_spent": 0,
            "overall_progress": roadmap.progress_percentage
        },
        "created_at": roadmap.created_at.isoformat() if roadmap.created_at else None
    }

# Pydantic models for structured LLM output
class LearningResource(BaseModel):
    type: str = Field(description="Type of resource: course|book|project|certification|practice")
    title: str = Field(description="Title of the learning resource")
    provider: str = Field(description="Platform, author, or provider name")
    url: Optional[str] = Field(description="URL link if available", default=None)
    cost: str = Field(description="Cost information: free|paid|specific amount")
    duration: str = Field(description="Estimated time to complete")
    difficulty: str = Field(description="Difficulty level: beginner|intermediate|advanced")

class RoadmapMilestone(BaseModel):
    id: str = Field(description="Unique identifier for the milestone")
    title: str = Field(description="Clear, actionable milestone title")
    description: str = Field(description="Detailed description of what to achieve")
    estimated_duration_weeks: int = Field(description="Estimated weeks to complete", ge=1, le=12)
    skills_covered: List[str] = Field(description="List of specific skills to develop")
    prerequisites: List[str] = Field(description="Required prior knowledge or completed milestones")
    resources: List[LearningResource] = Field(description="Learning resources for this milestone")
    deliverables: List[str] = Field(description="Concrete outputs or achievements")
    assessment_criteria: List[str] = Field(description="How to measure successful completion")
    is_completed: bool = Field(description="Completion status", default=False)

class CareerPreparation(BaseModel):
    portfolio_projects: List[str] = Field(description="Key projects to build for portfolio")
    networking_activities: List[str] = Field(description="Activities to build professional network")
    job_search_preparation: List[str] = Field(description="Resume, interview, and job search tips")

class RoadmapResources(BaseModel):
    books: List[str] = Field(description="Recommended books and publications")
    online_platforms: List[str] = Field(description="MOOC platforms and learning sites")
    communities: List[str] = Field(description="Professional communities and forums to join")
    tools: List[str] = Field(description="Software and tools to learn")
    certifications: List[str] = Field(description="Valuable certifications to pursue")
    practice_platforms: List[str] = Field(description="Platforms for hands-on practice")

class StructuredRoadmap(BaseModel):
    title: str = Field(description="Compelling title for the learning roadmap")
    description: str = Field(description="Comprehensive description of the learning journey")
    difficulty_level: str = Field(description="Overall difficulty: beginner|intermediate|advanced")
    milestones: List[RoadmapMilestone] = Field(description="Sequential learning milestones")
    resources: RoadmapResources = Field(description="Categorized learning resources")
    success_metrics: List[str] = Field(description="How to measure overall progress and success")
    career_preparation: CareerPreparation = Field(description="Career readiness activities")

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
)

@router.post("/generate-for-career")
@router.get("/", response_model=Dict[str, Any])
async def get_user_roadmaps_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all roadmaps for the user (for dashboard and roadmap page)."""
    print(f"[ROADMAP DEBUG] Getting roadmaps for user {current_user.id}")
    
    try:
        roadmaps = db.query(LearningRoadmap).filter(
            LearningRoadmap.user_id == current_user.id,
            LearningRoadmap.is_active == True
        ).order_by(LearningRoadmap.created_at.desc()).all()
        
        formatted_roadmaps = [_format_roadmap_for_frontend(roadmap) for roadmap in roadmaps]
        
        print(f"[ROADMAP DEBUG] Found {len(formatted_roadmaps)} roadmaps")
        
        return {
            "roadmaps": formatted_roadmaps,
            "total_roadmaps": len(formatted_roadmaps),
            "active_roadmaps": len([r for r in formatted_roadmaps if r["progress"]["overall_progress"] < 100])
        }
        
    except Exception as e:
        print(f"[ROADMAP DEBUG] Error getting roadmaps: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get roadmaps: {str(e)}")

@router.post("/start-phase/{roadmap_id}/{phase_index}")
async def start_phase(
    roadmap_id: int,
    phase_index: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a specific phase in a roadmap."""
    print(f"[ROADMAP DEBUG] Starting phase {phase_index} for roadmap {roadmap_id}")
    
    try:
        roadmap = db.query(LearningRoadmap).filter(
            LearningRoadmap.id == roadmap_id,
            LearningRoadmap.user_id == current_user.id
        ).first()
        
        if not roadmap:
            raise HTTPException(status_code=404, detail="Roadmap not found")
        
        # Update phase status
        phases = roadmap.phases.copy()
        if 0 <= phase_index < len(phases):
            phases[phase_index]["status"] = "in_progress"
            roadmap.phases = phases
            
            db.commit()
            
            return {
                "message": f"Started {phases[phase_index]['title']}",
                "phase": phases[phase_index]
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid phase index")
            
    except Exception as e:
        db.rollback()
        print(f"[ROADMAP DEBUG] Error starting phase: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start phase: {str(e)}")

@router.post("/generate-from-recommendation", response_model=Dict[str, Any])
async def generate_roadmap_from_recommendation(
    career_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a learning roadmap for a specific career recommendation."""
    print(f"[ROADMAP DEBUG] Generating roadmap for user {current_user.id}")
    print(f"[ROADMAP DEBUG] Career data: {career_data}")
    
    try:
        # Create a simple roadmap structure without complex LLM calls
        roadmap_data = _create_roadmap_structure(
            career_data, 
            career_data.get("missing_skills", []),
            career_data.get("matching_skills", [])
        )
        
        # Create roadmap in database
        roadmap = LearningRoadmap(
            user_id=current_user.id,
            career_recommendation_id=None,  # Direct career roadmap
            title=f"Learning Path: {career_data.get('title', 'Career Development')}",
            description=career_data.get("description", "Comprehensive learning roadmap"),
            estimated_duration_months=career_data.get("timeline_months", 12),
            difficulty_level=roadmap_data.difficulty_level,
            total_milestones=len(roadmap_data.milestones),
            milestones=[milestone.dict() for milestone in roadmap_data.milestones],
            resources=roadmap_data.resources.dict()
        )
        
        db.add(roadmap)
        db.commit()
        db.refresh(roadmap)
        
        print(f"[ROADMAP DEBUG] Saved roadmap with ID: {roadmap.id}")
        
        return {
            "roadmap_id": roadmap.id,
            "title": roadmap.title,
            "description": roadmap.description,
            "milestones": roadmap.milestones,
            "resources": roadmap.resources,
            "estimated_duration_months": roadmap.estimated_duration_months,
            "difficulty_level": roadmap.difficulty_level,
            "success_metrics": roadmap_data.success_metrics,
            "career_preparation": roadmap_data.career_preparation.dict()
        }
        
    except Exception as e:
        db.rollback()
        print(f"[ROADMAP DEBUG] Error generating roadmap: {str(e)}")
        import traceback
        print(f"[ROADMAP DEBUG] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to generate roadmap: {str(e)}")

@router.get("/my-roadmaps", response_model=List[LearningRoadmapResponse])
async def get_user_roadmaps(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all learning roadmaps for the current user."""
    roadmaps = db.query(LearningRoadmap).filter(
        LearningRoadmap.user_id == current_user.id,
        LearningRoadmap.is_active == True
    ).order_by(LearningRoadmap.created_at.desc()).all()
    
    return [await _format_roadmap_response(roadmap) for roadmap in roadmaps]

@router.get("/{roadmap_id}", response_model=LearningRoadmapResponse)
async def get_roadmap_details(
    roadmap_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific roadmap."""
    roadmap = db.query(LearningRoadmap).filter(
        LearningRoadmap.id == roadmap_id,
        LearningRoadmap.user_id == current_user.id
    ).first()
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    return await _format_roadmap_response(roadmap)

@router.post("/update-progress")
async def update_milestone_progress(
    request: RoadmapProgressRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update progress on a roadmap milestone."""
    roadmap = db.query(LearningRoadmap).filter(
        LearningRoadmap.id == request.roadmap_id,
        LearningRoadmap.user_id == current_user.id
    ).first()
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    try:
        # Update milestone in the milestones JSON
        milestones = roadmap.milestones or []
        milestone_found = False
        
        for milestone in milestones:
            if milestone.get("id") == request.milestone_id:
                milestone["is_completed"] = True
                milestone["completed_at"] = datetime.utcnow().isoformat()
                if request.notes:
                    milestone["completion_notes"] = request.notes
                milestone_found = True
                break
        
        if not milestone_found:
            raise HTTPException(status_code=404, detail="Milestone not found")
        
        # Update roadmap progress
        completed_count = sum(1 for m in milestones if m.get("is_completed", False))
        total_count = len(milestones)
        
        roadmap.milestones = milestones
        roadmap.completed_milestones = completed_count
        roadmap.progress_percentage = (completed_count / total_count * 100) if total_count > 0 else 0
        roadmap.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "message": "Progress updated successfully",
            "completed_milestones": completed_count,
            "total_milestones": total_count,
            "progress_percentage": roadmap.progress_percentage
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update progress: {str(e)}")

@router.post("/customize/{roadmap_id}")
async def customize_roadmap(
    roadmap_id: int,
    customization_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Customize an existing roadmap based on user feedback."""
    roadmap = db.query(LearningRoadmap).filter(
        LearningRoadmap.id == roadmap_id,
        LearningRoadmap.user_id == current_user.id
    ).first()
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    try:
        # Generate customized roadmap
        customized_data = await _customize_roadmap_with_ai(roadmap, customization_request)
        
        # Update roadmap with customizations
        roadmap.milestones = customized_data.get("milestones", roadmap.milestones)
        roadmap.resources = customized_data.get("resources", roadmap.resources)
        roadmap.estimated_duration_months = customized_data.get("duration", roadmap.estimated_duration_months)
        roadmap.total_milestones = len(roadmap.milestones)
        roadmap.updated_at = datetime.utcnow()
        
        # Reset progress if milestones changed significantly
        if customization_request.get("reset_progress", False):
            roadmap.completed_milestones = 0
            roadmap.progress_percentage = 0.0
            for milestone in roadmap.milestones:
                milestone["is_completed"] = False
                milestone.pop("completed_at", None)
                milestone.pop("completion_notes", None)
        
        db.commit()
        
        return {
            "message": "Roadmap customized successfully",
            "roadmap": await _format_roadmap_response(roadmap)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to customize roadmap: {str(e)}")

@router.get("/analytics/{roadmap_id}")
async def get_roadmap_analytics(
    roadmap_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics and insights for a roadmap."""
    roadmap = db.query(LearningRoadmap).filter(
        LearningRoadmap.id == roadmap_id,
        LearningRoadmap.user_id == current_user.id
    ).first()
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    # Calculate analytics
    milestones = roadmap.milestones or []
    completed_milestones = [m for m in milestones if m.get("is_completed", False)]
    
    # Time-based analytics
    start_date = roadmap.created_at
    current_date = datetime.utcnow()
    elapsed_days = (current_date - start_date).days
    estimated_total_days = roadmap.estimated_duration_months * 30
    
    # Completion rate analytics
    expected_progress = (elapsed_days / estimated_total_days * 100) if estimated_total_days > 0 else 0
    actual_progress = roadmap.progress_percentage
    pace = "on_track" if abs(actual_progress - expected_progress) <= 10 else ("ahead" if actual_progress > expected_progress else "behind")
    
    # Skills coverage analysis
    all_skills = set()
    completed_skills = set()
    
    for milestone in milestones:
        milestone_skills = set(milestone.get("skills_covered", []))
        all_skills.update(milestone_skills)
        
        if milestone.get("is_completed", False):
            completed_skills.update(milestone_skills)
    
    skills_coverage = (len(completed_skills) / len(all_skills) * 100) if all_skills else 0
    
    # Recommendations for improvement
    recommendations = await _generate_improvement_recommendations(roadmap, pace, skills_coverage)
    
    return {
        "roadmap_id": roadmap_id,
        "overall_progress": {
            "completion_percentage": roadmap.progress_percentage,
            "completed_milestones": len(completed_milestones),
            "total_milestones": len(milestones),
            "elapsed_days": elapsed_days,
            "estimated_total_days": estimated_total_days
        },
        "pace_analysis": {
            "expected_progress": expected_progress,
            "actual_progress": actual_progress,
            "pace": pace,
            "days_ahead_behind": (actual_progress - expected_progress) * estimated_total_days / 100
        },
        "skills_analysis": {
            "total_skills": len(all_skills),
            "completed_skills": len(completed_skills),
            "skills_coverage_percentage": skills_coverage,
            "remaining_skills": list(all_skills - completed_skills)
        },
        "milestone_breakdown": [
            {
                "milestone_title": m.get("title", ""),
                "is_completed": m.get("is_completed", False),
                "skills_count": len(m.get("skills_covered", [])),
                "estimated_weeks": m.get("estimated_duration_weeks", 0)
            }
            for m in milestones
        ],
        "recommendations": recommendations
    }

@router.delete("/{roadmap_id}")
async def delete_roadmap(
    roadmap_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a learning roadmap."""
    roadmap = db.query(LearningRoadmap).filter(
        LearningRoadmap.id == roadmap_id,
        LearningRoadmap.user_id == current_user.id
    ).first()
    
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    
    try:
        roadmap.is_active = False
        db.commit()
        
        return {"message": "Roadmap deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete roadmap: {str(e)}")

# Helper functions

async def _build_comprehensive_user_context(user_id: int, career_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Build comprehensive user context for roadmap generation."""
    print(f"[ROADMAP DEBUG] Building context for user {user_id}")
    
    user = db.query(User).filter(User.id == user_id).first()
    
    # Get user skills
    context = {
        "user_profile": {
            "education_level": getattr(user, 'education_level', None),
            "field_of_study": getattr(user, 'field_of_study', None),
            "graduation_year": getattr(user, 'graduation_year', None),
            "location": getattr(user, 'location', None),
            "email": user.email,
            "full_name": user.full_name
        },
        "current_skills": [],
        "target_career": {
            "title": career_data.get("career_title", ""),
            "field": career_data.get("field", ""),
            "reasoning": career_data.get("reasoning", "")
        },
        "skills_analysis": {
            "matching_skills": career_data.get("matching_skills", []),
            "missing_skills": career_data.get("missing_skills", []),
            "gap_score": career_data.get("skills_gap_score", 50.0)
        },
        "career_details": career_data
    }
    
    # Get user skills if available
    try:
        from models import UserSkill, Skill
        user_skills = db.query(UserSkill).join(Skill).filter(UserSkill.user_id == user_id).all()
        context["current_skills"] = [
            {
                "name": us.skill.name,
                "category": us.skill.category,
                "proficiency": us.proficiency_level
            }
            for us in user_skills
        ]
        print(f"[ROADMAP DEBUG] Found {len(context['current_skills'])} user skills")
    except Exception as e:
        print(f"[ROADMAP DEBUG] Error getting user skills: {e}")
        context["current_skills"] = []
    
    return context

async def _generate_structured_roadmap(user_context: Dict[str, Any], timeline_months: int, learning_style: str) -> StructuredRoadmap:
    """Generate structured roadmap using Pydantic models."""
    print(f"[ROADMAP DEBUG] Generating structured roadmap for {timeline_months} months")
    
    # Create structured generator using with_structured_output (modern approach)
    structured_generator = llm.with_structured_output(StructuredRoadmap)
    
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=f"""You are an expert learning and career development advisor for Indian students and professionals. Create a comprehensive, actionable learning roadmap.

Consider:
1. User's current skill level and background
2. Target career requirements and market demands in India
3. Available learning resources (online and offline) accessible in India
4. Timeline of {timeline_months} months
5. Learning style preference: {learning_style}
6. Indian job market context and salary expectations
7. Budget-friendly and accessible resources
8. Practical projects and portfolio building
9. Networking and industry exposure opportunities
10. Certification and credentialing paths relevant to Indian employers

Create a structured roadmap with clear milestones, realistic timelines, and actionable steps.
Each milestone should be 1-8 weeks and include specific, measurable deliverables.
Focus on practical skills that directly translate to job readiness."""),
        HumanMessage(content=f"""Create a {timeline_months}-month learning roadmap for this profile:

User Context: {json.dumps(user_context, indent=2)}

Focus on:
- Addressing specific skill gaps identified in the analysis
- Building a strong portfolio of projects
- Preparing for the Indian job market
- Including both free and paid resources accessible to Indian learners
- Providing measurable milestones and deliverables
- Ensuring practical, hands-on learning experiences

Make the roadmap specific, actionable, and tailored to Indian market needs.""")
    ])
    
    try:
        print(f"[ROADMAP DEBUG] Calling LLM with structured output...")
        result = await structured_generator.ainvoke(prompt.format_messages())
        print(f"[ROADMAP DEBUG] Successfully generated roadmap with {len(result.milestones)} milestones")
        
        return result
        
    except Exception as e:
        print(f"[ROADMAP DEBUG] Error in LLM generation: {e}")
        # Return fallback structured roadmap
        career_title = user_context.get("target_career", {}).get("title", "Target Career")
        missing_skills = user_context.get("skills_analysis", {}).get("missing_skills", [])
        
        fallback_milestones = []
        for i, skill in enumerate(missing_skills[:6]):  # Limit to 6 milestones
            milestone = RoadmapMilestone(
                id=f"milestone_{i+1}",
                title=f"Master {skill}",
                description=f"Develop proficiency in {skill} through structured learning and practice",
                estimated_duration_weeks=min(4, max(1, timeline_months // 3)),
                skills_covered=[skill],
                prerequisites=[],
                resources=[
                    LearningResource(
                        type="course",
                        title=f"Introduction to {skill}",
                        provider="Online Platform",
                        url=None,
                        cost="free",
                        duration="4-6 weeks",
                        difficulty="beginner"
                    )
                ],
                deliverables=[f"Complete {skill} project", f"Build {skill} portfolio"],
                assessment_criteria=[f"Demonstrate {skill} proficiency", "Complete hands-on project"],
                is_completed=False
            )
            fallback_milestones.append(milestone)
        
        return StructuredRoadmap(
            title=f"Learning Path to {career_title}",
            description=f"A comprehensive {timeline_months}-month roadmap to develop skills needed for {career_title} role",
            difficulty_level="intermediate",
            milestones=fallback_milestones,
            resources=RoadmapResources(
                books=["Relevant industry books"],
                online_platforms=["Coursera", "Udemy", "edX", "FreeCodeCamp"],
                communities=["LinkedIn groups", "Reddit communities", "Discord servers"],
                tools=["Industry-standard tools"],
                certifications=["Relevant certifications"],
                practice_platforms=["HackerRank", "LeetCode", "GitHub"]
            ),
            success_metrics=[
                "Complete all milestone projects",
                "Build a comprehensive portfolio",
                "Achieve target skill proficiency levels",
                "Network with industry professionals"
            ],
            career_preparation=CareerPreparation(
                portfolio_projects=[f"Build 3-5 {career_title} projects"],
                networking_activities=["Join professional communities", "Attend industry events"],
                job_search_preparation=["Update resume", "Practice interviews", "Build LinkedIn profile"]
            )
        )

async def _build_user_context(user_id: int, recommendation: CareerRecommendation, db: Session) -> Dict[str, Any]:
    """Build user context for roadmap generation."""
    user = db.query(User).filter(User.id == user_id).first()
    
    # Get user skills
    from models import UserSkill, Skill
    user_skills = db.query(UserSkill).join(Skill).filter(UserSkill.user_id == user_id).all()
    
    context = {
        "user_profile": {
            "education_level": user.education_level,
            "field_of_study": user.field_of_study,
            "graduation_year": user.graduation_year,
            "location": user.location
        },
        "current_skills": [
            {
                "name": us.skill.name,
                "category": us.skill.category,
                "proficiency": us.proficiency_level
            }
            for us in user_skills
        ],
        "target_career": {
            "title": recommendation.career.title,
            "field": recommendation.career.field,
            "description": recommendation.career.description
        },
        "skills_analysis": {
            "matching_skills": recommendation.matching_skills,
            "missing_skills": recommendation.missing_skills,
            "gap_score": recommendation.skills_gap_score
        },
        "recommendation_reasoning": recommendation.reasoning
    }
    
    return context

async def _generate_ai_roadmap(user_context: Dict[str, Any], timeline_months: int, learning_style: str) -> Dict[str, Any]:
    """Generate AI-powered learning roadmap."""
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=f"""You are an expert learning and career development advisor for Indian students and professionals. Create a comprehensive, actionable learning roadmap.

Consider:
1. User's current skill level and background
2. Target career requirements and market demands
3. Available learning resources in India (online and offline)
4. Timeline of {timeline_months} months
5. Learning style preference: {learning_style}
6. Indian job market context and requirements
7. Budget-friendly and accessible resources
8. Practical projects and portfolio building
9. Networking and industry exposure opportunities
10. Certification and credentialing paths

Create a structured roadmap with clear milestones, timelines, and actionable steps.

Return JSON format:
{{
    "title": "roadmap title",
    "description": "comprehensive description of the learning journey",
    "difficulty_level": "beginner|intermediate|advanced",
    "milestones": [
        {{
            "id": "unique_milestone_id",
            "title": "milestone title",
            "description": "detailed description of what to achieve",
            "estimated_duration_weeks": 1-8,
            "skills_covered": ["list of skills to develop"],
            "prerequisites": ["required prior knowledge"],
            "resources": [
                {{
                    "type": "course|book|project|certification|practice",
                    "title": "resource title",
                    "provider": "platform or author",
                    "url": "link if available",
                    "cost": "free|paid|amount",
                    "duration": "estimated time to complete",
                    "difficulty": "beginner|intermediate|advanced"
                }}
            ],
            "deliverables": ["what to create or achieve"],
            "assessment_criteria": ["how to measure success"],
            "is_completed": false
        }}
    ],
    "resources": {{
        "books": ["recommended books"],
        "online_platforms": ["MOOC platforms, coding sites"],
        "communities": ["professional communities to join"],
        "tools": ["software and tools to learn"],
        "certifications": ["valuable certifications to pursue"],
        "practice_platforms": ["platforms for hands-on practice"]
    }},
    "success_metrics": [
        "how to measure overall progress and success"
    ],
    "career_preparation": {{
        "portfolio_projects": ["key projects to build"],
        "networking_activities": ["how to build professional network"],
        "job_search_preparation": ["resume, interview, portfolio tips"]
    }}
}}"""),
        HumanMessage(content=f"""Create a {timeline_months}-month learning roadmap for this profile:

User Context: {json.dumps(user_context, indent=2)}

Focus on:
- Addressing skill gaps identified in the analysis
- Building a strong foundation in missing skills
- Creating a portfolio that demonstrates capabilities
- Preparing for the Indian job market
- Providing practical, actionable steps
- Including both free and paid resources accessible to Indian learners""")
    ])
    
    response = await llm.ainvoke(prompt.format_messages())
    
    try:
        # Try to parse JSON response manually for fallback
        import json as json_lib
        return json_lib.loads(response.content)
    except Exception as e:
        # Return fallback roadmap
        return {
            "title": f"Learning Path to {user_context['target_career']['title']}",
            "description": "A structured learning plan to develop required skills",
            "difficulty_level": "intermediate",
            "milestones": [
                {
                    "id": "milestone_1",
                    "title": "Foundation Building",
                    "description": "Build fundamental skills",
                    "estimated_duration_weeks": 4,
                    "skills_covered": user_context["skills_analysis"]["missing_skills"][:3],
                    "prerequisites": [],
                    "resources": [],
                    "deliverables": ["Complete basic courses"],
                    "assessment_criteria": ["Pass course assessments"],
                    "is_completed": False
                }
            ],
            "resources": {
                "books": [],
                "online_platforms": ["Coursera", "Udemy", "edX"],
                "communities": [],
                "tools": [],
                "certifications": [],
                "practice_platforms": []
            }
        }

async def _format_roadmap_response(roadmap: LearningRoadmap) -> LearningRoadmapResponse:
    """Format roadmap for API response."""
    milestones = []
    
    for milestone_data in roadmap.milestones or []:
        milestone = LearningMilestone(
            id=milestone_data.get("id", ""),
            title=milestone_data.get("title", ""),
            description=milestone_data.get("description", ""),
            estimated_duration_weeks=milestone_data.get("estimated_duration_weeks", 1),
            resources=milestone_data.get("resources", []),
            skills_covered=milestone_data.get("skills_covered", []),
            prerequisites=milestone_data.get("prerequisites", []),
            is_completed=milestone_data.get("is_completed", False)
        )
        milestones.append(milestone)
    
    return LearningRoadmapResponse(
        id=roadmap.id,
        title=roadmap.title,
        description=roadmap.description,
        estimated_duration_months=roadmap.estimated_duration_months,
        difficulty_level=roadmap.difficulty_level,
        total_milestones=roadmap.total_milestones,
        completed_milestones=roadmap.completed_milestones,
        progress_percentage=roadmap.progress_percentage,
        milestones=milestones,
        is_active=roadmap.is_active,
        created_at=roadmap.created_at,
        updated_at=roadmap.updated_at
    )

async def _customize_roadmap_with_ai(roadmap: LearningRoadmap, customization_request: Dict[str, Any]) -> Dict[str, Any]:
    """Customize roadmap based on user feedback using AI."""
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are an expert learning advisor. Customize the existing roadmap based on user feedback and requirements.

Consider the user's:
1. Specific feedback and pain points
2. Time constraints and availability
3. Learning style preferences
4. Budget considerations
5. Current progress and achievements
6. New goals or focus areas

Modify the roadmap while maintaining:
- Logical learning progression
- Realistic timelines
- Quality resources
- Clear milestones

Return the same JSON structure as the original roadmap but with modifications."""),
        HumanMessage(content=f"""Customize this roadmap based on user feedback:

Current Roadmap: {json.dumps({
    'title': roadmap.title,
    'milestones': roadmap.milestones,
    'resources': roadmap.resources
}, indent=2)}

User Customization Request: {json.dumps(customization_request, indent=2)}

Please provide the updated roadmap structure.""")
    ])
    
    response = await llm.ainvoke(prompt.format_messages())
    
    try:
        # Try to parse JSON response manually for fallback
        import json as json_lib
        return json_lib.loads(response.content)
    except Exception as e:
        # Return original roadmap if customization fails
        return {
            "milestones": roadmap.milestones,
            "resources": roadmap.resources,
            "duration": roadmap.estimated_duration_months
        }

async def _generate_improvement_recommendations(roadmap: LearningRoadmap, pace: str, skills_coverage: float) -> List[str]:
    """Generate recommendations for roadmap improvement."""
    recommendations = []
    
    if pace == "behind":
        recommendations.append("Consider dedicating more time daily to learning activities")
        recommendations.append("Focus on completing smaller milestones first to build momentum")
        recommendations.append("Look for more efficient learning resources or methods")
    
    elif pace == "ahead":
        recommendations.append("Great progress! Consider adding more advanced topics")
        recommendations.append("Look for opportunities to apply skills in real projects")
        recommendations.append("Consider mentoring others or contributing to open source")
    
    if skills_coverage < 50:
        recommendations.append("Focus on completing practical exercises and projects")
        recommendations.append("Join study groups or find learning partners")
        recommendations.append("Allocate more time to hands-on practice")
    
    if roadmap.progress_percentage < 25:
        recommendations.append("Break down large milestones into smaller, manageable tasks")
        recommendations.append("Set daily learning goals and track them")
        recommendations.append("Find an accountability partner or mentor")
    
    # Add general recommendations
    recommendations.extend([
        "Regularly update your portfolio with new projects",
        "Engage with professional communities in your field",
        "Practice interview skills and technical assessments",
        "Stay updated with industry trends and new technologies"
    ])
    
    return recommendations[:5]  # Return top 5 recommendations
