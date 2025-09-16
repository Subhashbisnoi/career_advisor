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
