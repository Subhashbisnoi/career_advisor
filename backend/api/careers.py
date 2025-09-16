"""
Career Recommendations API endpoints
Handles career path recommendations and exploration.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
from datetime import datetime

from database import get_db
from models import (
    User, CareerPath, CareerRecommendation, CareerAssessment, Skill, CareerSkill,
    CareerRecommendationRequest, CareerPathResponse, CareerRecommendationResponse,
    MarketTrendsResponse, MessageResponse
)
from api.auth import get_current_user
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os

router = APIRouter(prefix="/careers", tags=["Career Recommendations"])

# Pydantic models for structured LLM output
class SalaryRange(BaseModel):
    entry_level: str = Field(description="Entry level salary in INR")
    mid_level: str = Field(description="Mid level salary in INR") 
    senior_level: str = Field(description="Senior level salary in INR")

class CareerRecommendationData(BaseModel):
    career_title: str = Field(description="Specific job title")
    field: str = Field(description="Career field: technology|healthcare|finance|business|education|government|creative|science")
    match_score: float = Field(description="Match score from 0-100 based on user profile")
    confidence_score: float = Field(description="AI confidence in recommendation from 0-100")
    reasoning: str = Field(description="Detailed explanation of why this career matches the user")
    matching_skills: List[str] = Field(description="Skills the user already has that match this career")
    missing_skills: List[str] = Field(description="Skills the user needs to develop for this career")
    skills_gap_score: float = Field(description="Skills gap score from 0-100, lower is better")
    salary_range: SalaryRange = Field(description="Salary expectations for different experience levels")
    growth_prospects: str = Field(description="Career growth prospects: excellent|good|moderate|limited")
    entry_requirements: str = Field(description="Education and experience requirements")
    career_progression: str = Field(description="Typical career advancement path")
    work_environment: str = Field(description="Description of typical work setting and culture")
    key_responsibilities: List[str] = Field(description="Main job responsibilities and duties")
    future_outlook: str = Field(description="Industry growth trends and job security prospects")

class StructuredCareerRecommendations(BaseModel):
    recommendations: List[CareerRecommendationData] = Field(description="List of career recommendations ranked by match score")

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
)

@router.post("/recommendations")
async def generate_career_recommendations(
    request: CareerRecommendationRequest = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate personalized career recommendations based on user profile and assessment."""
    print(f"[CAREERS DEBUG] Generating recommendations for user {current_user.id}")
    
    # Extract assessment_id from request if provided
    assessment_id = None
    if request and hasattr(request, 'assessment_id'):
        assessment_id = request.assessment_id
    
    print(f"[CAREERS DEBUG] Assessment ID: {assessment_id}")
    
    try:
        # Check if recommendations already exist for this assessment
        if assessment_id:
            existing_recommendations = db.query(CareerRecommendation).filter(
                CareerRecommendation.assessment_id == assessment_id,
                CareerRecommendation.user_id == current_user.id
            ).join(CareerPath).all()
            
            if existing_recommendations:
                print(f"[CAREERS DEBUG] Found {len(existing_recommendations)} existing recommendations for assessment {assessment_id}")
                # Return existing recommendations
                formatted_recommendations = []
                for rec in existing_recommendations:
                    formatted_rec = {
                        "id": rec.id,
                        "career": await _format_career_response(rec.career, db),
                        "match_score": rec.match_score,
                        "confidence_score": rec.confidence_score,
                        "reasoning": rec.reasoning,
                        "matching_skills": rec.matching_skills,
                        "missing_skills": rec.missing_skills,
                        "skills_gap_score": rec.skills_gap_score,
                        "is_pinned": rec.is_pinned,
                        "created_at": rec.created_at.isoformat() if rec.created_at else None
                    }
                    formatted_recommendations.append(formatted_rec)
                
                return {"recommendations": formatted_recommendations}
        
        # Generate new recommendations if none exist
        print(f"[CAREERS DEBUG] Generating new recommendations...")
        
        # Build comprehensive user profile
        user_profile = await _build_comprehensive_user_profile(current_user.id, assessment_id, db)
        print(f"[CAREERS DEBUG] Built user profile: {user_profile}")
        
        # Generate AI-powered recommendations using structured output
        recommendations_data = await _generate_structured_ai_recommendations(user_profile)
        print(f"[CAREERS DEBUG] Generated {len(recommendations_data)} recommendations")
        
        # Store and format recommendations
        saved_recommendations = []
        for rec_data in recommendations_data:
            print(f"[CAREERS DEBUG] Processing recommendation: {rec_data.career_title}")
            
            # Get or create career path
            career = await _get_or_create_career_path(rec_data.dict(), db)
            
            # Create recommendation record
            recommendation = CareerRecommendation(
                user_id=current_user.id,
                career_id=career.id,
                assessment_id=assessment_id,
                match_score=rec_data.match_score,
                confidence_score=rec_data.confidence_score,
                reasoning=rec_data.reasoning,
                matching_skills=rec_data.matching_skills,
                missing_skills=rec_data.missing_skills,
                skills_gap_score=rec_data.skills_gap_score
            )
            
            db.add(recommendation)
            db.flush()
            saved_recommendations.append(recommendation)
        
        db.commit()
        print(f"[CAREERS DEBUG] Saved {len(saved_recommendations)} recommendations to database")
        
        # Return formatted recommendations
        formatted_recommendations = []
        for rec in saved_recommendations:
            formatted_rec = {
                "id": rec.id,
                "career": await _format_career_response(rec.career, db),
                "match_score": rec.match_score,
                "confidence_score": rec.confidence_score,
                "reasoning": rec.reasoning,
                "matching_skills": rec.matching_skills,
                "missing_skills": rec.missing_skills,
                "skills_gap_score": rec.skills_gap_score,
                "is_pinned": rec.is_pinned,
                "created_at": rec.created_at.isoformat() if rec.created_at else None
            }
            formatted_recommendations.append(formatted_rec)
        
        return {"recommendations": formatted_recommendations}
        
    except Exception as e:
        db.rollback()
        print(f"[CAREERS DEBUG] Error generating recommendations: {str(e)}")
        import traceback
        print(f"[CAREERS DEBUG] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

async def generate_career_recommendations_for_dashboard(current_user: User, db: Session, assessment: CareerAssessment = None):
    """Helper function to generate recommendations for dashboard and assessment integration (DEPRECATED - use database storage instead)."""
    print(f"[CAREERS DEBUG] Helper function called for user {current_user.id}")
    
    try:
        assessment_id = assessment.id if assessment else None
        user_profile = await _build_comprehensive_user_profile(current_user.id, assessment_id, db)
        recommendations_data = await _generate_structured_ai_recommendations(user_profile)
        
        formatted_recommendations = []
        for rec_data in recommendations_data:
            formatted_rec = {
                "career_title": rec_data.career_title,
                "field": rec_data.field,
                "match_score": rec_data.match_score,
                "confidence_score": rec_data.confidence_score,
                "reasoning": rec_data.reasoning,
                "matching_skills": rec_data.matching_skills,
                "missing_skills": rec_data.missing_skills,
                "skills_gap_score": rec_data.skills_gap_score,
                "salary_range": rec_data.salary_range.dict(),
                "growth_prospects": rec_data.growth_prospects,
                "entry_requirements": rec_data.entry_requirements,
                "work_environment": rec_data.work_environment,
                "key_responsibilities": rec_data.key_responsibilities,
                "future_outlook": rec_data.future_outlook
            }
            formatted_recommendations.append(formatted_rec)
        
        return {"recommendations": formatted_recommendations}
        
    except Exception as e:
        print(f"[CAREERS DEBUG] Error in helper function: {str(e)}")
        return {"recommendations": []}

@router.get("/recommendations", response_model=List[CareerRecommendationResponse])
async def get_user_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all career recommendations for the current user."""
    recommendations = db.query(CareerRecommendation).filter(
        CareerRecommendation.user_id == current_user.id
    ).order_by(CareerRecommendation.match_score.desc()).all()
    
    return [
        CareerRecommendationResponse(
            id=rec.id,
            career=await _format_career_response(rec.career, db),
            match_score=rec.match_score,
            confidence_score=rec.confidence_score,
            reasoning=rec.reasoning,
            matching_skills=rec.matching_skills,
            missing_skills=rec.missing_skills,
            skills_gap_score=rec.skills_gap_score,
            is_pinned=rec.is_pinned,
            created_at=rec.created_at
        )
        for rec in recommendations
    ]

@router.get("/explore", response_model=List[CareerPathResponse])
async def explore_career_paths(
    field: Optional[str] = None,
    min_salary: Optional[float] = None,
    max_salary: Optional[float] = None,
    growth_rate: Optional[float] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Explore available career paths with filtering options."""
    query = db.query(CareerPath)
    
    if field:
        query = query.filter(CareerPath.field == field)
    
    if min_salary:
        query = query.filter(CareerPath.entry_level_salary >= min_salary)
    
    if max_salary:
        query = query.filter(CareerPath.senior_level_salary <= max_salary)
    
    if growth_rate:
        query = query.filter(CareerPath.growth_rate >= growth_rate)
    
    careers = query.order_by(CareerPath.demand_score.desc()).limit(limit).all()
    
    return [await _format_career_response(career, db) for career in careers]

@router.get("/details/{career_id}", response_model=CareerPathResponse)
async def get_career_details(
    career_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific career path."""
    career = db.query(CareerPath).filter(CareerPath.id == career_id).first()
    
    if not career:
        raise HTTPException(status_code=404, detail="Career path not found")
    
    return await _format_career_response(career, db)

@router.get("/market-trends", response_model=MarketTrendsResponse)
async def get_market_trends(
    field: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get job market trends and insights for career planning."""
    # Get trending skills
    skills_query = db.query(Skill).order_by(Skill.trending_score.desc())
    if field:
        skills_query = skills_query.filter(Skill.field == field)
    trending_skills = skills_query.limit(10).all()
    
    # Get emerging careers
    careers_query = db.query(CareerPath).order_by(
        CareerPath.demand_score.desc(),
        CareerPath.growth_rate.desc()
    )
    if field:
        careers_query = careers_query.filter(CareerPath.field == field)
    emerging_careers = careers_query.limit(5).all()
    
    # Get high demand fields
    high_demand_query = db.query(CareerPath.field, db.func.avg(CareerPath.demand_score).label('avg_demand')) \
        .group_by(CareerPath.field) \
        .order_by(db.func.avg(CareerPath.demand_score).desc()) \
        .limit(5)
    
    high_demand_fields = [row[0] for row in high_demand_query.all()]
    
    # Generate salary insights
    salary_insights = await _generate_salary_insights(field, db)
    
    # Calculate industry growth
    industry_growth = {}
    all_fields = db.query(CareerPath.field, db.func.avg(CareerPath.growth_rate)).group_by(CareerPath.field).all()
    for field_name, avg_growth in all_fields:
        if field_name:
            industry_growth[field_name] = float(avg_growth or 0.0)
    
    return MarketTrendsResponse(
        trending_skills=[
            {
                "id": skill.id,
                "name": skill.name,
                "category": skill.category,
                "field": skill.field,
                "description": skill.description,
                "market_demand": skill.market_demand,
                "trending_score": skill.trending_score
            }
            for skill in trending_skills
        ],
        emerging_careers=[await _format_career_response(career, db) for career in emerging_careers],
        high_demand_fields=high_demand_fields,
        salary_insights=salary_insights,
        industry_growth=industry_growth
    )

@router.post("/pin/{recommendation_id}")
async def pin_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Pin a career recommendation for easy access."""
    recommendation = db.query(CareerRecommendation).filter(
        CareerRecommendation.id == recommendation_id,
        CareerRecommendation.user_id == current_user.id
    ).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    try:
        recommendation.is_pinned = not recommendation.is_pinned
        db.commit()
        
        action = "pinned" if recommendation.is_pinned else "unpinned"
        return {"message": f"Recommendation {action} successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update recommendation: {str(e)}")

@router.get("/compare")
async def compare_careers(
    career_ids: str,  # Comma-separated career IDs
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compare multiple career paths side by side."""
    try:
        career_id_list = [int(id.strip()) for id in career_ids.split(",")]
        
        if len(career_id_list) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 careers can be compared")
        
        careers = db.query(CareerPath).filter(CareerPath.id.in_(career_id_list)).all()
        
        if len(careers) != len(career_id_list):
            raise HTTPException(status_code=404, detail="One or more careers not found")
        
        comparison = {
            "careers": [await _format_career_response(career, db) for career in careers],
            "comparison_matrix": await _generate_comparison_matrix(careers, current_user.id, db)
        }
        
        return comparison
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid career IDs provided")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compare careers: {str(e)}")

# Helper functions

async def _build_comprehensive_user_profile(user_id: int, assessment_id: Optional[int], db: Session) -> Dict[str, Any]:
    """Build comprehensive user profile for recommendations."""
    print(f"[CAREERS DEBUG] Building profile for user {user_id}, assessment {assessment_id}")
    
    user = db.query(User).filter(User.id == user_id).first()
    
    profile = {
        "user_info": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "education_level": getattr(user, 'education_level', None),
            "field_of_study": getattr(user, 'field_of_study', None),
            "institution": getattr(user, 'institution', None),
            "graduation_year": getattr(user, 'graduation_year', None),
            "location": getattr(user, 'location', None)
        },
        "skills": [],
        "assessment_results": None,
        "preferences": {}
    }
    
    # Get user skills
    try:
        from models import UserSkill
        user_skills = db.query(UserSkill).join(Skill).filter(UserSkill.user_id == user_id).all()
        profile["skills"] = [
            {
                "name": us.skill.name,
                "category": us.skill.category,
                "proficiency": us.proficiency_level,
                "market_demand": getattr(us.skill, 'market_demand', 5.0)
            }
            for us in user_skills
        ]
        print(f"[CAREERS DEBUG] Found {len(profile['skills'])} user skills")
    except Exception as e:
        print(f"[CAREERS DEBUG] Error getting user skills: {e}")
        profile["skills"] = []
    
    # Get assessment results if provided
    if assessment_id:
        assessment = db.query(CareerAssessment).filter(
            CareerAssessment.id == assessment_id,
            CareerAssessment.user_id == user_id
        ).first()
        
        if assessment:
            print(f"[CAREERS DEBUG] Found assessment: {assessment.status}")
            if hasattr(assessment, 'analysis_results') and assessment.analysis_results:
                profile["assessment_results"] = assessment.analysis_results
            
            # Extract assessment responses for analysis
            try:
                from models import AssessmentMessage
                messages = db.query(AssessmentMessage).filter(
                    AssessmentMessage.assessment_id == assessment_id,
                    AssessmentMessage.message_type == "answer"
                ).all()
                
                assessment_responses = []
                for msg in messages:
                    response_data = {
                        "content": msg.content,
                        "question_id": msg.metadata.get("question_id") if msg.metadata else None
                    }
                    assessment_responses.append(response_data)
                
                profile["assessment_responses"] = assessment_responses
                print(f"[CAREERS DEBUG] Found {len(assessment_responses)} assessment responses")
                
            except Exception as e:
                print(f"[CAREERS DEBUG] Error getting assessment responses: {e}")
    
    return profile

async def _generate_structured_ai_recommendations(user_profile: Dict[str, Any]) -> List[CareerRecommendationData]:
    """Generate AI-powered career recommendations using structured output."""
    print(f"[CAREERS DEBUG] Generating structured recommendations...")
    
    # Create structured generator using with_structured_output (modern approach)
    structured_generator = llm.with_structured_output(StructuredCareerRecommendations)
    
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are an expert career counselor for Indian students and professionals. Generate personalized career recommendations based on the user profile.

Consider:
1. Current skills and proficiency levels
2. Educational background and field of study  
3. Assessment responses and preferences
4. Indian job market trends and opportunities
5. Salary expectations and growth prospects
6. Geographic preferences and mobility
7. Work-life balance considerations

Generate 5-7 career recommendations, ranking them by match score. Each recommendation should be comprehensive and actionable.

Focus on careers that are:
- Realistic given the user's current skills and background
- In-demand in the Indian job market
- Have good growth prospects
- Match the user's interests and preferences

Return a structured response with career recommendations."""),
        HumanMessage(content=f"""Generate career recommendations for this profile:

User Profile: {json.dumps(user_profile, indent=2)}

Please provide personalized, actionable career recommendations suitable for the Indian job market with detailed reasoning and skill analysis.""")
    ])
    
    try:
        print(f"[CAREERS DEBUG] Calling LLM with structured output...")
        result = await structured_generator.ainvoke(prompt.format_messages())
        print(f"[CAREERS DEBUG] Successfully generated {len(result.recommendations)} recommendations")
        
        return result.recommendations
        
    except Exception as e:
        print(f"[CAREERS DEBUG] Error in LLM generation: {e}")
        # Return fallback recommendations with proper structure
        fallback_recommendations = [
            CareerRecommendationData(
                career_title="Software Developer",
                field="technology",
                match_score=75.0,
                confidence_score=80.0,
                reasoning="Based on technical aptitude and market demand in India's growing IT sector",
                matching_skills=["Programming", "Problem Solving"],
                missing_skills=["Framework Experience", "Version Control"],
                skills_gap_score=30.0,
                salary_range=SalaryRange(
                    entry_level="INR 4,00,000",
                    mid_level="INR 8,00,000", 
                    senior_level="INR 15,00,000"
                ),
                growth_prospects="excellent",
                entry_requirements="Bachelor's degree in Computer Science or related field",
                career_progression="Junior Developer → Senior Developer → Team Lead → Engineering Manager",
                work_environment="Collaborative office or remote environment with modern development tools",
                key_responsibilities=["Write clean code", "Debug applications", "Collaborate with teams", "Participate in code reviews"],
                future_outlook="Excellent growth prospects with India's expanding digital economy"
            ),
            CareerRecommendationData(
                career_title="Data Analyst",
                field="technology",
                match_score=70.0,
                confidence_score=75.0,
                reasoning="Strong analytical skills and growing demand for data-driven insights",
                matching_skills=["Analytical Thinking", "Excel"],
                missing_skills=["Python", "SQL", "Tableau"],
                skills_gap_score=40.0,
                salary_range=SalaryRange(
                    entry_level="INR 3,50,000",
                    mid_level="INR 7,00,000",
                    senior_level="INR 12,00,000"
                ),
                growth_prospects="good",
                entry_requirements="Bachelor's degree in any field with strong analytical skills",
                career_progression="Junior Analyst → Senior Analyst → Lead Analyst → Data Scientist",
                work_environment="Office environment with focus on data tools and visualization software",
                key_responsibilities=["Analyze datasets", "Create reports", "Identify trends", "Present insights"],
                future_outlook="High demand as companies increasingly rely on data-driven decisions"
            )
        ]
        
        print(f"[CAREERS DEBUG] Returning {len(fallback_recommendations)} fallback recommendations")
        return fallback_recommendations

async def _build_user_profile(user_id: int, assessment_id: Optional[int], db: Session) -> Dict[str, Any]:
    """Build comprehensive user profile for recommendations."""
    user = db.query(User).filter(User.id == user_id).first()
    
    profile = {
        "user_info": {
            "id": user.id,
            "education_level": user.education_level,
            "field_of_study": user.field_of_study,
            "institution": user.institution,
            "graduation_year": user.graduation_year,
            "location": user.location
        },
        "skills": [],
        "assessment_results": None
    }
    
    # Get user skills
    from models import UserSkill
    user_skills = db.query(UserSkill).join(Skill).filter(UserSkill.user_id == user_id).all()
    profile["skills"] = [
        {
            "name": us.skill.name,
            "category": us.skill.category,
            "proficiency": us.proficiency_level,
            "market_demand": us.skill.market_demand
        }
        for us in user_skills
    ]
    
    # Get assessment results if provided
    if assessment_id:
        assessment = db.query(CareerAssessment).filter(
            CareerAssessment.id == assessment_id,
            CareerAssessment.user_id == user_id
        ).first()
        
        if assessment and assessment.analysis_results:
            profile["assessment_results"] = assessment.analysis_results
    
    return profile

async def _generate_ai_recommendations(user_profile: Dict[str, Any], preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate AI-powered career recommendations."""
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are an expert career counselor for Indian students and professionals. Generate personalized career recommendations based on the user profile.

Consider:
1. Current skills and proficiency levels
2. Educational background and field of study
3. Assessment results (if available)
4. User preferences and constraints
5. Indian job market trends and opportunities
6. Salary expectations and growth prospects
7. Geographic preferences and mobility
8. Work-life balance considerations

Generate 5-8 career recommendations, ranking them by match score. For each recommendation:

Return JSON format:
{
    "recommendations": [
        {
            "career_title": "specific job title",
            "field": "technology|healthcare|finance|business|education|government|creative|science",
            "match_score": 0-100,
            "confidence_score": 0-100,
            "reasoning": "detailed explanation of why this career matches",
            "matching_skills": ["skills user already has"],
            "missing_skills": ["skills user needs to develop"],
            "skills_gap_score": 0-100,
            "salary_range": {
                "entry_level": "INR amount",
                "mid_level": "INR amount", 
                "senior_level": "INR amount"
            },
            "growth_prospects": "excellent|good|moderate|limited",
            "entry_requirements": "education and experience needed",
            "career_progression": "typical career path",
            "work_environment": "description of work setting",
            "key_responsibilities": ["main job responsibilities"],
            "future_outlook": "industry growth and job security prospects"
        }
    ]
}"""),
        HumanMessage(content=f"""Generate career recommendations for this profile:

User Profile: {json.dumps(user_profile, indent=2)}
Preferences: {json.dumps(preferences, indent=2)}

Please provide personalized, actionable career recommendations suitable for the Indian job market.""")
    ])
    
    response = await llm.ainvoke(prompt.format_messages())
    
    try:
        # Try to parse JSON response manually for fallback
        import json as json_lib
        result = json_lib.loads(response.content)
        return result.get("recommendations", [])
    except Exception as e:
        # Return fallback recommendations
        return [
            {
                "career_title": "Software Developer",
                "field": "technology",
                "match_score": 75.0,
                "confidence_score": 80.0,
                "reasoning": "Based on technical skills and market demand",
                "matching_skills": [],
                "missing_skills": [],
                "skills_gap_score": 25.0
            }
        ]

async def _get_or_create_career_path(career_data: Dict[str, Any], db: Session) -> CareerPath:
    """Get existing career path or create new one."""
    career = db.query(CareerPath).filter(
        CareerPath.title == career_data["career_title"]
    ).first()
    
    if not career:
        salary_range = career_data.get("salary_range", {})
        
        career = CareerPath(
            title=career_data["career_title"],
            field=career_data["field"],
            description=career_data.get("reasoning", ""),
            entry_level_salary=_parse_salary(salary_range.get("entry_level")),
            mid_level_salary=_parse_salary(salary_range.get("mid_level")),
            senior_level_salary=_parse_salary(salary_range.get("senior_level")),
            growth_rate=_parse_growth_rate(career_data.get("growth_prospects", "moderate")),
            job_market_score=career_data.get("match_score", 50.0) / 10,
            demand_score=8.0,  # Default high demand
            future_outlook=career_data.get("future_outlook", "positive")
        )
        
        db.add(career)
        db.flush()
    
    return career

async def _format_career_response(career: CareerPath, db: Session):
    """Format career path for API response."""
    # Get required and preferred skills
    career_skills = db.query(CareerSkill).join(Skill).filter(
        CareerSkill.career_id == career.id
    ).all()
    
    required_skills = []
    preferred_skills = []
    
    for cs in career_skills:
        skill_data = {
            "id": cs.skill.id,
            "name": cs.skill.name,
            "category": cs.skill.category,
            "field": cs.skill.field,
            "description": cs.skill.description,
            "market_demand": cs.skill.market_demand,
            "trending_score": cs.skill.trending_score
        }
        
        if cs.importance_level == "required":
            required_skills.append(skill_data)
        else:
            preferred_skills.append(skill_data)
    
    return CareerPathResponse(
        id=career.id,
        title=career.title,
        field=career.field,
        description=career.description,
        entry_level_salary=career.entry_level_salary,
        mid_level_salary=career.mid_level_salary,
        senior_level_salary=career.senior_level_salary,
        growth_rate=career.growth_rate,
        job_market_score=career.job_market_score,
        demand_score=career.demand_score,
        future_outlook=career.future_outlook,
        required_skills=required_skills,
        preferred_skills=preferred_skills
    )

def _parse_salary(salary_str: Optional[str]) -> Optional[float]:
    """Parse salary string to float value."""
    if not salary_str:
        return None
    
    try:
        # Remove INR, commas, and other non-numeric characters
        import re
        numeric_str = re.sub(r'[^0-9.]', '', salary_str)
        return float(numeric_str) if numeric_str else None
    except:
        return None

def _parse_growth_rate(growth_str: str) -> float:
    """Convert growth prospects to numeric rate."""
    growth_map = {
        "excellent": 15.0,
        "good": 10.0,
        "moderate": 5.0,
        "limited": 2.0
    }
    return growth_map.get(growth_str.lower(), 5.0)

async def _generate_salary_insights(field: Optional[str], db: Session) -> Dict[str, Any]:
    """Generate salary insights for the field."""
    query = db.query(CareerPath)
    if field:
        query = query.filter(CareerPath.field == field)
    
    careers = query.all()
    
    if not careers:
        return {}
    
    entry_salaries = [c.entry_level_salary for c in careers if c.entry_level_salary]
    mid_salaries = [c.mid_level_salary for c in careers if c.mid_level_salary]
    senior_salaries = [c.senior_level_salary for c in careers if c.senior_level_salary]
    
    return {
        "entry_level": {
            "min": min(entry_salaries) if entry_salaries else 0,
            "max": max(entry_salaries) if entry_salaries else 0,
            "avg": sum(entry_salaries) / len(entry_salaries) if entry_salaries else 0
        },
        "mid_level": {
            "min": min(mid_salaries) if mid_salaries else 0,
            "max": max(mid_salaries) if mid_salaries else 0,
            "avg": sum(mid_salaries) / len(mid_salaries) if mid_salaries else 0
        },
        "senior_level": {
            "min": min(senior_salaries) if senior_salaries else 0,
            "max": max(senior_salaries) if senior_salaries else 0,
            "avg": sum(senior_salaries) / len(senior_salaries) if senior_salaries else 0
        }
    }

async def _generate_comparison_matrix(careers: List[CareerPath], user_id: int, db: Session) -> Dict[str, Any]:
    """Generate comparison matrix for careers."""
    comparison = {
        "salary_comparison": {},
        "growth_comparison": {},
        "demand_comparison": {},
        "skills_match": {}
    }
    
    # Get user skills for skills matching
    from models import UserSkill
    user_skills = db.query(UserSkill).filter(UserSkill.user_id == user_id).all()
    user_skill_names = {us.skill.name.lower() for us in user_skills}
    
    for career in careers:
        career_id = str(career.id)
        
        # Salary comparison
        comparison["salary_comparison"][career_id] = {
            "entry": career.entry_level_salary,
            "mid": career.mid_level_salary,
            "senior": career.senior_level_salary
        }
        
        # Growth comparison
        comparison["growth_comparison"][career_id] = career.growth_rate
        
        # Demand comparison
        comparison["demand_comparison"][career_id] = career.demand_score
        
        # Skills match
        career_skills = db.query(CareerSkill).join(Skill).filter(
            CareerSkill.career_id == career.id
        ).all()
        
        total_skills = len(career_skills)
        matching_skills = sum(
            1 for cs in career_skills 
            if cs.skill.name.lower() in user_skill_names
        )
        
        match_percentage = (matching_skills / total_skills * 100) if total_skills > 0 else 0
        comparison["skills_match"][career_id] = {
            "match_percentage": match_percentage,
            "matching_skills": matching_skills,
            "total_skills": total_skills
        }
    
    return comparison
