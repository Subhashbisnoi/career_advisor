"""
Skills Analysis API endpoints
Handles skills assessment and gap analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
from datetime import datetime
import pdfplumber
import io

from database import get_db
from models import (
    User, Skill, UserSkill, CareerPath, CareerSkill,
    SkillAnalysisRequest, SkillResponse, MessageResponse
)
from api.auth import get_current_user
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
import os

router = APIRouter(prefix="/skills", tags=["Skills Analysis"])

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
)

@router.post("/analyze-document")
async def analyze_skills_from_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze skills from uploaded resume or transcript."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Extract text from PDF
        content = await file.read()
        text_content = ""
        
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\\n"
        
        if not text_content.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        # Analyze skills using AI
        skills_data = await _analyze_skills_with_ai(text_content, "document")
        
        # Store skills in database
        await _store_user_skills(current_user.id, skills_data, "document", db)
        
        return {
            "message": "Skills analyzed successfully",
            "extracted_text_length": len(text_content),
            "skills_found": len(skills_data.get("technical_skills", [])) + len(skills_data.get("soft_skills", [])),
            "analysis": skills_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze document: {str(e)}")

@router.post("/analyze-manual")
async def analyze_manual_skills(
    request: SkillAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze manually entered skills or resume text."""
    try:
        analysis_text = ""
        source = "manual"
        
        if request.resume_text:
            analysis_text = request.resume_text
            source = "resume_text"
        elif request.transcript_text:
            analysis_text = request.transcript_text
            source = "transcript"
        elif request.manual_skills:
            analysis_text = "Skills: " + ", ".join(request.manual_skills)
            source = "manual_entry"
        else:
            raise HTTPException(status_code=400, detail="Please provide text or skills to analyze")
        
        # Analyze skills using AI
        skills_data = await _analyze_skills_with_ai(analysis_text, source)
        
        # Store skills in database
        await _store_user_skills(current_user.id, skills_data, source, db)
        
        return {
            "message": "Skills analyzed successfully",
            "source": source,
            "skills_found": len(skills_data.get("technical_skills", [])) + len(skills_data.get("soft_skills", [])),
            "analysis": skills_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze skills: {str(e)}")

@router.get("/my-skills", response_model=List[SkillResponse])
async def get_user_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all skills for the current user."""
    user_skills = db.query(UserSkill).join(Skill).filter(
        UserSkill.user_id == current_user.id
    ).all()
    
    return [
        SkillResponse(
            id=us.skill.id,
            name=us.skill.name,
            category=us.skill.category,
            field=us.skill.field,
            description=us.skill.description,
            market_demand=us.skill.market_demand,
            trending_score=us.skill.trending_score,
            user_proficiency=us.proficiency_level
        )
        for us in user_skills
    ]

@router.get("/gaps/{career_path_id}")
async def analyze_skills_gap(
    career_path_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze skills gap for a specific career path."""
    # Get career path
    career = db.query(CareerPath).filter(CareerPath.id == career_path_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career path not found")
    
    # Get required skills for career
    career_skills = db.query(CareerSkill).join(Skill).filter(
        CareerSkill.career_id == career_path_id
    ).all()
    
    # Get user's current skills
    user_skills = db.query(UserSkill).join(Skill).filter(
        UserSkill.user_id == current_user.id
    ).all()
    
    user_skill_map = {us.skill.name.lower(): us for us in user_skills}
    
    # Analyze gaps
    matching_skills = []
    missing_skills = []
    
    for cs in career_skills:
        skill_name = cs.skill.name.lower()
        if skill_name in user_skill_map:
            us = user_skill_map[skill_name]
            matching_skills.append({
                "skill": cs.skill.name,
                "user_level": us.proficiency_level,
                "required_level": cs.proficiency_required,
                "importance": cs.importance_level,
                "gap": _calculate_skill_gap(us.proficiency_level, cs.proficiency_required)
            })
        else:
            missing_skills.append({
                "skill": cs.skill.name,
                "required_level": cs.proficiency_required,
                "importance": cs.importance_level,
                "category": cs.skill.category,
                "description": cs.skill.description
            })
    
    # Calculate overall gap score
    total_skills = len(career_skills)
    matching_count = len(matching_skills)
    gap_score = (matching_count / total_skills * 100) if total_skills > 0 else 0
    
    return {
        "career_path": {
            "id": career.id,
            "title": career.title,
            "field": career.field
        },
        "gap_analysis": {
            "total_required_skills": total_skills,
            "matching_skills_count": matching_count,
            "missing_skills_count": len(missing_skills),
            "gap_score": gap_score,
            "readiness_level": _get_readiness_level(gap_score)
        },
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "recommendations": await _generate_skill_recommendations(missing_skills, career.field)
    }

@router.get("/trending")
async def get_trending_skills(
    field: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get trending skills in the Indian job market."""
    query = db.query(Skill).order_by(Skill.trending_score.desc())
    
    if field:
        query = query.filter(Skill.field == field)
    
    skills = query.limit(limit).all()
    
    return [
        SkillResponse(
            id=skill.id,
            name=skill.name,
            category=skill.category,
            field=skill.field,
            description=skill.description,
            market_demand=skill.market_demand,
            trending_score=skill.trending_score
        )
        for skill in skills
    ]

@router.get("/market-demand")
async def get_market_demand_analysis(
    field: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get market demand analysis for skills."""
    query = db.query(Skill)
    
    if field:
        query = query.filter(Skill.field == field)
    
    skills = query.all()
    
    # Group skills by category and field
    analysis = {
        "by_category": {},
        "by_field": {},
        "top_demand": [],
        "emerging_skills": []
    }
    
    for skill in skills:
        # By category
        if skill.category not in analysis["by_category"]:
            analysis["by_category"][skill.category] = {
                "avg_demand": 0,
                "skill_count": 0,
                "skills": []
            }
        
        analysis["by_category"][skill.category]["skills"].append({
            "name": skill.name,
            "demand": skill.market_demand,
            "trending": skill.trending_score
        })
        analysis["by_category"][skill.category]["skill_count"] += 1
        
        # By field
        if skill.field:
            if skill.field not in analysis["by_field"]:
                analysis["by_field"][skill.field] = {
                    "avg_demand": 0,
                    "skill_count": 0
                }
            analysis["by_field"][skill.field]["skill_count"] += 1
        
        # Top demand skills
        if skill.market_demand >= 8.0:
            analysis["top_demand"].append({
                "name": skill.name,
                "demand": skill.market_demand,
                "field": skill.field,
                "category": skill.category
            })
        
        # Emerging skills (high trending score)
        if skill.trending_score >= 8.0:
            analysis["emerging_skills"].append({
                "name": skill.name,
                "trending": skill.trending_score,
                "field": skill.field,
                "category": skill.category
            })
    
    # Calculate averages
    for category_data in analysis["by_category"].values():
        if category_data["skill_count"] > 0:
            category_data["avg_demand"] = sum(
                s["demand"] for s in category_data["skills"]
            ) / category_data["skill_count"]
    
    # Sort results
    analysis["top_demand"].sort(key=lambda x: x["demand"], reverse=True)
    analysis["emerging_skills"].sort(key=lambda x: x["trending"], reverse=True)
    
    return analysis

@router.post("/update-proficiency")
async def update_skill_proficiency(
    skill_id: int,
    proficiency_level: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's skill proficiency level."""
    valid_levels = ["beginner", "intermediate", "advanced", "expert"]
    if proficiency_level not in valid_levels:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid proficiency level. Must be one of: {', '.join(valid_levels)}"
        )
    
    user_skill = db.query(UserSkill).filter(
        UserSkill.user_id == current_user.id,
        UserSkill.skill_id == skill_id
    ).first()
    
    if not user_skill:
        raise HTTPException(status_code=404, detail="User skill not found")
    
    try:
        user_skill.proficiency_level = proficiency_level
        user_skill.updated_at = datetime.utcnow()
        user_skill.self_assessed = True
        
        db.commit()
        
        return {"message": "Skill proficiency updated successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update skill: {str(e)}")

# Helper functions

async def _analyze_skills_with_ai(text: str, source: str) -> Dict[str, Any]:
    """Analyze skills from text using AI."""
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are an expert skills analyzer for the Indian job market. Analyze the provided text to identify technical and soft skills.

Focus on skills relevant to:
1. Technology (Programming, Cloud, AI/ML, Data Science, etc.)
2. Business (Management, Strategy, Finance, Marketing, etc.)
3. Healthcare (Medical skills, Research, Clinical expertise, etc.)
4. Engineering (Mechanical, Civil, Electrical, etc.)
5. Creative (Design, Content, Media, etc.)
6. Soft skills valued in Indian workplace culture

For each skill identified, assess the proficiency level based on context clues like:
- Years of experience mentioned
- Projects or achievements described
- Educational background
- Certifications or training

Return JSON analysis:
{
    "technical_skills": [
        {
            "skill": "skill_name",
            "category": "programming|cloud|data|design|etc",
            "proficiency": "beginner|intermediate|advanced|expert",
            "evidence": "text supporting this assessment",
            "market_demand": 1-10,
            "field": "technology|healthcare|finance|etc"
        }
    ],
    "soft_skills": [
        {
            "skill": "skill_name",
            "proficiency": "beginner|intermediate|advanced|expert", 
            "evidence": "text supporting this assessment",
            "importance": "high|medium|low"
        }
    ],
    "languages": [
        {
            "language": "language_name",
            "proficiency": "basic|conversational|fluent|native"
        }
    ],
    "summary": {
        "overall_skill_level": "entry|mid|senior|expert",
        "key_strengths": ["list of key strengths"],
        "growth_areas": ["areas for improvement"],
        "career_readiness": "ready|needs_development|significant_gaps"
    }
}"""),
        HumanMessage(content=f"Analyze skills from this {source}:\\n\\n{text}")
    ])
    
    response = await llm.ainvoke(prompt.format_messages())
    
    try:
        parser = JsonOutputParser()
        return parser.parse(response.content)
    except Exception as e:
        # Return basic analysis if parsing fails
        return {
            "technical_skills": [],
            "soft_skills": [],
            "languages": [],
            "summary": {
                "overall_skill_level": "unknown",
                "key_strengths": [],
                "growth_areas": [],
                "career_readiness": "needs_assessment"
            }
        }

async def _store_user_skills(user_id: int, skills_data: Dict[str, Any], source: str, db: Session):
    """Store analyzed skills in database."""
    try:
        # Store technical skills
        for skill_data in skills_data.get("technical_skills", []):
            skill = _get_or_create_skill(
                skill_data["skill"],
                skill_data["category"],
                skill_data.get("field"),
                skill_data.get("market_demand", 5.0),
                db
            )
            
            # Check if user already has this skill
            existing = db.query(UserSkill).filter(
                UserSkill.user_id == user_id,
                UserSkill.skill_id == skill.id
            ).first()
            
            if not existing:
                user_skill = UserSkill(
                    user_id=user_id,
                    skill_id=skill.id,
                    proficiency_level=skill_data["proficiency"],
                    source=source,
                    self_assessed=False
                )
                db.add(user_skill)
            else:
                # Update if new source provides better evidence
                existing.proficiency_level = skill_data["proficiency"]
                existing.source = source
                existing.updated_at = datetime.utcnow()
        
        # Store soft skills
        for skill_data in skills_data.get("soft_skills", []):
            skill = _get_or_create_skill(
                skill_data["skill"],
                "soft_skills",
                None,
                8.0 if skill_data.get("importance") == "high" else 6.0,
                db
            )
            
            existing = db.query(UserSkill).filter(
                UserSkill.user_id == user_id,
                UserSkill.skill_id == skill.id
            ).first()
            
            if not existing:
                user_skill = UserSkill(
                    user_id=user_id,
                    skill_id=skill.id,
                    proficiency_level=skill_data["proficiency"],
                    source=source,
                    self_assessed=False
                )
                db.add(user_skill)
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise e

def _get_or_create_skill(name: str, category: str, field: Optional[str], market_demand: float, db: Session) -> Skill:
    """Get existing skill or create new one."""
    skill = db.query(Skill).filter(Skill.name.ilike(name)).first()
    
    if not skill:
        skill = Skill(
            name=name,
            category=category,
            field=field,
            market_demand=market_demand,
            trending_score=5.0  # Default trending score
        )
        db.add(skill)
        db.flush()  # Get ID without committing
    
    return skill

def _calculate_skill_gap(user_level: str, required_level: str) -> int:
    """Calculate skill gap between user and required level."""
    levels = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
    user_score = levels.get(user_level, 0)
    required_score = levels.get(required_level, 4)
    return max(0, required_score - user_score)

def _get_readiness_level(gap_score: float) -> str:
    """Determine readiness level based on gap score."""
    if gap_score >= 80:
        return "ready"
    elif gap_score >= 60:
        return "mostly_ready"
    elif gap_score >= 40:
        return "needs_preparation"
    else:
        return "significant_gaps"

async def _generate_skill_recommendations(missing_skills: List[Dict], field: str) -> List[Dict[str, Any]]:
    """Generate recommendations for missing skills."""
    if not missing_skills:
        return []
    
    skills_text = ", ".join([skill["skill"] for skill in missing_skills])
    
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=f"""Generate learning recommendations for these missing skills in the {field} field: {skills_text}

For each skill, provide:
1. Best learning resources (online courses, books, tutorials)
2. Estimated learning time
3. Prerequisites
4. Practical projects to build proficiency
5. Certifications that would be valuable

Focus on resources available to Indian students, including:
- Free and paid online platforms
- Indian educational institutions
- Industry certifications recognized in India
- Practical projects that can be done with minimal resources

Return as JSON array of recommendations."""),
        HumanMessage(content=f"Generate learning recommendations for {field} skills: {skills_text}")
    ])
    
    try:
        response = await llm.ainvoke(prompt.format_messages())
        parser = JsonOutputParser()
        return parser.parse(response.content)
    except:
        return [{"skill": skill["skill"], "recommendation": "Research online courses and tutorials"} for skill in missing_skills]
