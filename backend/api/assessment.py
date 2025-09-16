"""
Career Assessment API endpoints
Handles career assessment process and recommendations.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
from datetime import datetime, timedelta

from database import get_db
from models import (
    User, CareerAssessment, AssessmentMessage, UserSkill, Skill,
    CareerAssessmentRequest, AssessmentSubmissionRequest, SkillAssessmentResponse,
    CareerAssessmentState, AssessmentSummaryResponse, MessageResponse
)
from api.auth import get_current_user
from career_workflow import career_workflow
from api.careers import generate_career_recommendations_for_dashboard
import uuid

router = APIRouter(prefix="/assessment", tags=["Career Assessment"])

@router.post("/start", response_model=Dict[str, Any])
async def start_career_assessment(
    request: CareerAssessmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new career assessment session."""
    print(f"[ASSESSMENT DEBUG] Starting assessment for user {current_user.id}")
    print(f"[ASSESSMENT DEBUG] Request: {request}")
    print(f"[ASSESSMENT DEBUG] Assessment type: {request.assessment_type}")
    print(f"[ASSESSMENT DEBUG] User background: {request.user_background}")
    
    try:
        # Create new assessment session
        thread_id = str(uuid.uuid4())
        print(f"[ASSESSMENT DEBUG] Generated thread_id: {thread_id}")
        
        assessment = CareerAssessment(
            user_id=current_user.id,
            thread_id=thread_id,
            assessment_type=request.assessment_type.value,
            status="active"
        )
        
        print(f"[ASSESSMENT DEBUG] Created assessment object: {assessment}")
        
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        
        print(f"[ASSESSMENT DEBUG] Assessment saved to DB with ID: {assessment.id}")
        
        # Initialize assessment state
        initial_state: CareerAssessmentState = {
            "thread_id": thread_id,
            "user_id": current_user.id,
            "assessment_id": assessment.id,
            "assessment_type": request.assessment_type.value,
            "user_background": request.user_background or {},
            "questions": [],
            "responses": [],
            "current_question": 0,
            "skills_analysis": {},
            "aptitude_analysis": {},
            "interest_analysis": {},
            "personality_analysis": {},
            "skills_score": 0.0,
            "aptitude_score": 0.0,
            "interest_score": 0.0,
            "overall_score": 0.0,
            "career_matches": [],
            "skills_gaps": {},
            "recommendations": {},
            "status": "started",
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "chat_history": []
        }
        
        # Run workflow to generate questions
        config = {"configurable": {"thread_id": thread_id}}
        
        print(f"[ASSESSMENT DEBUG] Starting workflow with config: {config}")
        
        # Start the assessment workflow
        try:
            print(f"[ASSESSMENT DEBUG] Calling career_workflow.graph.ainvoke...")
            result = await career_workflow.graph.ainvoke(initial_state, config)
            questions = result.get("questions", [])
            print(f"[ASSESSMENT DEBUG] Workflow returned {len(questions)} questions")
            print(f"[ASSESSMENT DEBUG] First question sample: {questions[0] if questions else 'No questions'}")
        except Exception as e:
            print(f"[ASSESSMENT DEBUG] Error in workflow: {e}")
            print(f"[ASSESSMENT DEBUG] Using fallback questions...")
            # Use fallback questions if workflow fails
            questions = career_workflow._get_fallback_questions(request.assessment_type.value)
        
        # Transform questions to frontend format
        def transform_questions(questions_list):
            """Transform AI-generated questions to frontend format"""
            transformed = []
            for q in questions_list:
                question_type = q.get("type")
                
                # Convert 'rating' type to 'scale' for frontend compatibility
                if question_type == "rating":
                    question_type = "scale"
                
                transformed_q = {
                    "id": q.get("id"),
                    "category": q.get("category"),
                    "question": q.get("question"),
                    "type": question_type
                }
                
                # Transform options based on question type
                if q.get("type") == "multiple_choice" and q.get("options"):
                    if isinstance(q["options"][0], str):
                        # Convert string options to object format
                        transformed_q["options"] = [
                            {"value": opt.lower().replace(" ", "_").replace("&", "and"), "label": opt}
                            for opt in q["options"]
                        ]
                    else:
                        # Already in correct format
                        transformed_q["options"] = q["options"]
                elif q.get("type") == "rating" and q.get("options"):
                    # For rating questions converted to scale, set up scale labels
                    transformed_q["scale_labels"] = {
                        "min": "1 - Poor",
                        "max": "5 - Excellent"
                    }
                    # Don't include options array for scale questions
                    transformed_q["options"] = []
                else:
                    # For text and scenario questions, or if no options
                    transformed_q["options"] = q.get("options", [])
                
                transformed.append(transformed_q)
            return transformed
        
        questions = transform_questions(questions)
        
        print(f"[ASSESSMENT DEBUG] Transformed questions: {len(questions)} questions")
        print(f"[ASSESSMENT DEBUG] Returning first 5 questions to frontend")
        
        # Store initial messages
        for message in result.get("chat_history", []):
            assessment_message = AssessmentMessage(
                assessment_id=assessment.id,
                thread_id=thread_id,
                message_type="system",
                role=message["role"],
                content=message["content"],
                metadata={"timestamp": message.get("timestamp")}
            )
            db.add(assessment_message)
        
        db.commit()
        
        response_data = {
            "assessment_id": assessment.id,
            "thread_id": thread_id,
            "assessment_type": request.assessment_type.value,
            "questions": questions[:5],  # Return first 5 questions
            "total_questions": len(questions),
            "current_question": 0,
            "status": "active",
            "message": "Assessment started successfully"
        }
        
        print(f"[ASSESSMENT DEBUG] Returning response: {response_data}")
        return response_data
        
    except Exception as e:
        db.rollback()
        print(f"[ASSESSMENT DEBUG] Error starting assessment: {str(e)}")
        print(f"[ASSESSMENT DEBUG] Error type: {type(e)}")
        import traceback
        print(f"[ASSESSMENT DEBUG] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to start assessment: {str(e)}")

@router.get("/questions/{thread_id}")
async def get_assessment_questions(
    thread_id: str,
    start: int = 0,
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get assessment questions for a session."""
    assessment = db.query(CareerAssessment).filter(
        CareerAssessment.thread_id == thread_id,
        CareerAssessment.user_id == current_user.id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment session not found")
    
    # Get current state from workflow
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        # Get current state from workflow or use fallback questions
        config = {"configurable": {"thread_id": thread_id}}
        
        # Try to get questions from workflow state
        # For now, use comprehensive fallback questions
        fallback_questions = [
            {
                "id": "q1",
                "category": "technical",
                "question": "Which programming languages are you comfortable with?",
                "type": "multiple_choice",
                "options": [
                    {"value": "python", "label": "Python"},
                    {"value": "javascript", "label": "JavaScript"},
                    {"value": "java", "label": "Java"},
                    {"value": "cpp", "label": "C++"},
                    {"value": "none", "label": "I'm not familiar with programming"}
                ]
            },
            {
                "id": "q2", 
                "category": "interests",
                "question": "What type of work environment do you prefer?",
                "type": "multiple_choice",
                "options": [
                    {"value": "startup", "label": "Fast-paced startup"},
                    {"value": "corporate", "label": "Structured corporate"},
                    {"value": "government", "label": "Government/Public sector"},
                    {"value": "nonprofit", "label": "Non-profit organization"},
                    {"value": "freelance", "label": "Freelance/Remote"}
                ]
            },
            {
                "id": "q3",
                "category": "goals",
                "question": "What is your primary career goal?",
                "type": "multiple_choice", 
                "options": [
                    {"value": "salary", "label": "High salary potential"},
                    {"value": "balance", "label": "Work-life balance"},
                    {"value": "impact", "label": "Social impact"},
                    {"value": "creativity", "label": "Innovation & creativity"},
                    {"value": "security", "label": "Job security"}
                ]
            },
            {
                "id": "q4",
                "category": "technical",
                "question": "Which of these technical areas interests you most?",
                "type": "multiple_choice",
                "options": [
                    {"value": "web_dev", "label": "Web Development"},
                    {"value": "data_science", "label": "Data Science & Analytics"},
                    {"value": "mobile_dev", "label": "Mobile App Development"},
                    {"value": "cybersecurity", "label": "Cybersecurity"},
                    {"value": "cloud", "label": "Cloud Computing"}
                ]
            },
            {
                "id": "q5",
                "category": "soft_skills",
                "question": "How do you prefer to solve complex problems?",
                "type": "multiple_choice",
                "options": [
                    {"value": "breakdown", "label": "Break them into smaller parts"},
                    {"value": "research", "label": "Research extensively first"},
                    {"value": "collaborate", "label": "Collaborate with others"},
                    {"value": "experiment", "label": "Experiment and iterate"},
                    {"value": "methodology", "label": "Follow proven methodologies"}
                ]
            }
        ]
        
        # Return questions within the requested range
        total_questions = len(fallback_questions)
        end_index = min(start + limit, total_questions)
        questions = fallback_questions[start:end_index]
        
        return {
            "questions": questions,
            "total_questions": total_questions,
            "current_batch": start // limit + 1,
            "has_more": end_index < total_questions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get questions: {str(e)}")

@router.post("/submit-responses")
async def submit_assessment_responses(
    request: AssessmentSubmissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit responses to assessment questions."""
    print(f"[SUBMIT DEBUG] Received submission request")
    print(f"[SUBMIT DEBUG] Thread ID: {request.thread_id}")
    print(f"[SUBMIT DEBUG] User ID: {current_user.id}")
    print(f"[SUBMIT DEBUG] Number of responses: {len(request.responses)}")
    print(f"[SUBMIT DEBUG] Responses: {[r.dict() for r in request.responses]}")
    
    assessment = db.query(CareerAssessment).filter(
        CareerAssessment.thread_id == request.thread_id,
        CareerAssessment.user_id == current_user.id
    ).first()
    
    print(f"[SUBMIT DEBUG] Found assessment: {assessment}")
    
    if not assessment:
        print(f"[SUBMIT DEBUG] Assessment not found!")
        raise HTTPException(status_code=404, detail="Assessment session not found")
    
    print(f"[SUBMIT DEBUG] Assessment status: {assessment.status}")
    if assessment.status != "active":
        print(f"[SUBMIT DEBUG] Assessment not active!")
        raise HTTPException(status_code=422, detail=f"Assessment is not active. Current status: {assessment.status}")
    
    try:
        print(f"[SUBMIT DEBUG] Storing responses in database...")
        # Store responses in database
        for i, response in enumerate(request.responses):
            print(f"[SUBMIT DEBUG] Processing response {i+1}: {response.dict()}")
            assessment_message = AssessmentMessage(
                assessment_id=assessment.id,
                thread_id=request.thread_id,
                message_type="answer",
                role="user",
                content=response.response,
                question_number=None,  # Will be derived from question_id
                message_metadata={
                    "question_id": response.question_id,
                    "confidence_level": response.confidence_level
                }
            )
            db.add(assessment_message)
        
        print(f"[SUBMIT DEBUG] Creating structured assessment result...")
        # Create structured submission summary
        submission_summary = {
            "total_questions": len(request.responses),
            "completion_time": datetime.utcnow().isoformat(),
            "user_responses": [r.dict() for r in request.responses]
        }
        
        # Store assessment result in separate table with error handling
        try:
            # Import AssessmentResult model
            from models import AssessmentResult
            
            assessment_result = AssessmentResult(
                assessment_id=assessment.id,
                user_id=current_user.id,
                submission_summary=json.dumps(submission_summary),
                processing_status="completed",
                total_questions=len(request.responses),
                completion_time=datetime.utcnow(),
                time_spent_seconds=0,  # Can be calculated if needed
                skills_analysis=json.dumps({}),  # Will be populated by analysis
                personality_insights=json.dumps({}),  # Will be populated by analysis
                career_fit_analysis=json.dumps({})  # Will be populated by analysis
            )
            
            db.add(assessment_result)
            print(f"[SUBMIT DEBUG] Added structured assessment result successfully")
            
        except Exception as e:
            print(f"[SUBMIT DEBUG] Error creating structured assessment result: {e}")
            print(f"[SUBMIT DEBUG] Continuing without structured result storage")
            # Continue without failing - the basic assessment will still be stored
        
        print(f"[SUBMIT DEBUG] Updating assessment status to completed...")
        # Update assessment status to completed and store responses
        assessment.status = "completed"
        assessment.responses = [r.dict() for r in request.responses]
        assessment.completed_at = datetime.utcnow()
        
        # Set some basic scores for demo purposes
        assessment.overall_score = 75.0
        assessment.skills_score = 70.0
        assessment.aptitude_score = 80.0
        assessment.interest_score = 75.0
        
        db.commit()
        db.refresh(assessment)
        db.refresh(assessment_result)
        
        print(f"[SUBMIT DEBUG] Database operations completed successfully")
        
        response_data = {
            "assessment_results": {
                "submission_summary": submission_summary,
                "processing_status": "completed"
            },
            "message": "Assessment completed successfully",
            "assessment_id": assessment.id,
            "overall_score": assessment.overall_score,
            "next_step": "generate_recommendations"
        }
        
        print(f"[SUBMIT DEBUG] Returning success response: {response_data}")
        return response_data
        
    except Exception as e:
        db.rollback()
        print(f"[SUBMIT DEBUG] Error submitting responses: {str(e)}")
        print(f"[SUBMIT DEBUG] Error type: {type(e)}")
        import traceback
        print(f"[SUBMIT DEBUG] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to submit responses: {str(e)}")

@router.get("/results/{assessment_id}", response_model=Dict[str, Any])
async def get_assessment_results(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get assessment results and recommendations from database."""
    assessment = db.query(CareerAssessment).filter(
        CareerAssessment.id == assessment_id,
        CareerAssessment.user_id == current_user.id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    if assessment.status not in ["completed", "processing"]:
        return {
            "assessment_id": assessment_id,
            "status": assessment.status,
            "message": "Assessment is not completed yet"
        }
    
    # Get analysis results
    analysis_results = assessment.analysis_results or {}
    
    # Get existing career recommendations from database (don't generate new ones)
    from models import CareerRecommendation, CareerPath
    
    existing_recommendations = db.query(CareerRecommendation).filter(
        CareerRecommendation.assessment_id == assessment_id,
        CareerRecommendation.user_id == current_user.id
    ).join(CareerPath).order_by(CareerRecommendation.match_score.desc()).all()
    
    print(f"[RESULTS DEBUG] Found {len(existing_recommendations)} existing recommendations for assessment {assessment_id}")
    
    if existing_recommendations:
        # Use existing recommendations from database
        career_recommendations = {
            "recommendations": [
                {
                    "id": rec.id,
                    "career": {
                        "id": rec.career.id,
                        "title": rec.career.title,
                        "field": rec.career.field,
                        "description": rec.career.description,
                        "entry_level_salary": rec.career.entry_level_salary,
                        "mid_level_salary": rec.career.mid_level_salary,
                        "senior_level_salary": rec.career.senior_level_salary,
                        "growth_rate": rec.career.growth_rate,
                        "job_market_score": rec.career.job_market_score,
                        "demand_score": rec.career.demand_score,
                        "future_outlook": rec.career.future_outlook
                    },
                    "match_score": rec.match_score,
                    "confidence_score": rec.confidence_score,
                    "reasoning": rec.reasoning,
                    "matching_skills": rec.matching_skills or [],
                    "missing_skills": rec.missing_skills or [],
                    "skills_gap_score": rec.skills_gap_score,
                    "is_pinned": rec.is_pinned,
                    "created_at": rec.created_at.isoformat() if rec.created_at else None
                }
                for rec in existing_recommendations
            ]
        }
        print(f"[RESULTS DEBUG] Returning {len(existing_recommendations)} stored recommendations")
    else:
        # No recommendations found - they should be generated via the /careers/recommendations endpoint
        print(f"[RESULTS DEBUG] No existing recommendations found for assessment {assessment_id}")
        career_recommendations = {"recommendations": []}
    
    return {
        "assessment_id": assessment_id,
        "status": assessment.status,
        "assessment_type": assessment.assessment_type,
        "scores": {
            "skills_score": assessment.skills_score,
            "aptitude_score": assessment.aptitude_score,
            "interest_score": assessment.interest_score,
            "overall_score": assessment.overall_score
        },
        "assessment_results": analysis_results,
        "career_recommendations": career_recommendations,
        "completed_at": assessment.completed_at.isoformat() if assessment.completed_at else None,
        "created_at": assessment.created_at.isoformat() if assessment.created_at else None,
        "generated_at": datetime.utcnow().isoformat()
    }

@router.get("/history", response_model=List[AssessmentSummaryResponse])
async def get_assessment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's assessment history."""
    assessments = db.query(CareerAssessment).filter(
        CareerAssessment.user_id == current_user.id
    ).order_by(CareerAssessment.created_at.desc()).all()
    
    return [
        AssessmentSummaryResponse(
            id=assessment.id,
            assessment_type=assessment.assessment_type,
            status=assessment.status,
            skills_score=assessment.skills_score,
            aptitude_score=assessment.aptitude_score,
            interest_score=assessment.interest_score,
            overall_score=assessment.overall_score,
            created_at=assessment.created_at,
            completed_at=assessment.completed_at
        )
        for assessment in assessments
    ]

@router.delete("/{assessment_id}")
async def delete_assessment(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an assessment session."""
    assessment = db.query(CareerAssessment).filter(
        CareerAssessment.id == assessment_id,
        CareerAssessment.user_id == current_user.id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    try:
        # Delete related messages
        db.query(AssessmentMessage).filter(
            AssessmentMessage.assessment_id == assessment_id
        ).delete()
        
        # Delete assessment
        db.delete(assessment)
        db.commit()
        
        return {"message": "Assessment deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete assessment: {str(e)}")

@router.post("/restart/{assessment_id}")
async def restart_assessment(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Restart an assessment session."""
    assessment = db.query(CareerAssessment).filter(
        CareerAssessment.id == assessment_id,
        CareerAssessment.user_id == current_user.id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    try:
        # Reset assessment
        assessment.status = "active"
        assessment.skills_score = 0.0
        assessment.aptitude_score = 0.0
        assessment.interest_score = 0.0
        assessment.overall_score = 0.0
        assessment.responses = None
        assessment.analysis_results = None
        assessment.completed_at = None
        assessment.updated_at = datetime.utcnow()
        
        # Delete old messages
        db.query(AssessmentMessage).filter(
            AssessmentMessage.assessment_id == assessment_id
        ).delete()
        
        db.commit()
        
        return {"message": "Assessment restarted successfully", "assessment_id": assessment_id}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to restart assessment: {str(e)}")

@router.get("/dashboard")
async def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard data including assessments and career recommendations from database."""
    print(f"[DASHBOARD DEBUG] Getting dashboard data for user {current_user.id}")
    
    try:
        # Get user's assessment history
        assessments = db.query(CareerAssessment).filter(
            CareerAssessment.user_id == current_user.id
        ).order_by(CareerAssessment.created_at.desc()).all()
        
        print(f"[DASHBOARD DEBUG] Found {len(assessments)} assessments")
        
        # Get career recommendations from database (don't generate new ones)
        from models import CareerRecommendation, CareerPath
        
        career_recommendations_query = db.query(CareerRecommendation).filter(
            CareerRecommendation.user_id == current_user.id
        ).join(CareerPath).order_by(CareerRecommendation.created_at.desc())
        
        career_recommendations_raw = career_recommendations_query.limit(10).all()
        
        print(f"[DASHBOARD DEBUG] Found {len(career_recommendations_raw)} stored recommendations")
        
        # Format career recommendations
        career_recommendations = []
        for rec in career_recommendations_raw:
            rec_data = {
                "id": rec.id,
                "career": {
                    "id": rec.career.id,
                    "title": rec.career.title,
                    "field": rec.career.field,
                    "description": rec.career.description,
                    "entry_level_salary": rec.career.entry_level_salary,
                    "mid_level_salary": rec.career.mid_level_salary,
                    "senior_level_salary": rec.career.senior_level_salary,
                    "growth_rate": rec.career.growth_rate,
                    "job_market_score": rec.career.job_market_score,
                    "demand_score": rec.career.demand_score,
                    "future_outlook": rec.career.future_outlook
                },
                "match_score": rec.match_score,
                "confidence_score": rec.confidence_score,
                "reasoning": rec.reasoning,
                "matching_skills": rec.matching_skills or [],
                "missing_skills": rec.missing_skills or [],
                "skills_gap_score": rec.skills_gap_score,
                "is_pinned": rec.is_pinned,
                "created_at": rec.created_at.isoformat() if rec.created_at else None
            }
            career_recommendations.append(rec_data)
        
        # Format assessment history
        assessment_history = []
        for assessment in assessments[:10]:  # Limit to 10 most recent
            assessment_data = {
                "id": assessment.id,
                "assessment_type": assessment.assessment_type,
                "status": assessment.status,
                "skills_score": assessment.skills_score,
                "aptitude_score": assessment.aptitude_score,
                "interest_score": assessment.interest_score,
                "overall_score": assessment.overall_score,
                "created_at": assessment.created_at.isoformat() if assessment.created_at else None,
                "completed_at": assessment.completed_at.isoformat() if assessment.completed_at else None
            }
            assessment_history.append(assessment_data)
        
        # Calculate summary statistics
        completed_assessments = [a for a in assessments if a.status == "completed"]
        
        stats = {
            "total_assessments": len(assessments),
            "completed_assessments": len(completed_assessments),
            "average_overall_score": sum([a.overall_score or 0 for a in completed_assessments]) / len(completed_assessments) if completed_assessments else 0,
            "latest_assessment_date": assessments[0].created_at.isoformat() if assessments else None,
            "total_recommendations": len(career_recommendations)
        }
        
        dashboard_data = {
            "user_info": {
                "id": current_user.id,
                "email": current_user.email,
                "full_name": current_user.full_name,
                "created_at": current_user.created_at.isoformat() if current_user.created_at else None
            },
            "assessment_history": assessment_history,
            "career_recommendations": career_recommendations,
            "statistics": stats
        }
        
        print(f"[DASHBOARD DEBUG] Returning dashboard data with {len(assessment_history)} assessments and {len(career_recommendations)} stored recommendations")
        return dashboard_data
        
    except Exception as e:
        print(f"[DASHBOARD DEBUG] Error getting dashboard data: {str(e)}")
        import traceback
        print(f"[DASHBOARD DEBUG] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")