"""
Enhanced Interview API with LangGraph state management and threading support.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid

from database import get_db
from models import (
    User, InterviewSession, ChatMessage,
    InterviewStartRequest, AnswerSubmissionRequest,
    ChatHistoryResponse, InterviewSessionResponse
)
from api.auth import get_current_user
from state_manager import interview_manager

router = APIRouter(prefix="/interview/v2", tags=["interview-v2"])

@router.post("/start", response_model=Dict[str, Any])
async def start_interview_session(
    request: InterviewStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a new interview session with LangGraph state management.
    """
    try:
        # Create interview session using state manager
        result = interview_manager.create_interview_session(
            user_id=current_user.id,
            role=request.role,
            company=request.company,
            resume_text=request.resume_text
        )
        
        return {
            "message": "Interview session started successfully",
            "thread_id": result["thread_id"],
            "session_id": result["session_id"],
            "questions": result["questions"],
            "status": result["status"],
            "role": request.role,
            "company": request.company
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start interview session: {str(e)}"
        )

@router.post("/submit-answer", response_model=Dict[str, Any])
async def submit_answer(
    request: AnswerSubmissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit an answer for a specific question in the interview.
    """
    try:
        # Verify the thread belongs to the current user
        db_session = db.query(InterviewSession).filter(
            InterviewSession.thread_id == request.thread_id,
            InterviewSession.user_id == current_user.id
        ).first()
        
        if not db_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found or access denied"
            )
        
        # Submit answer using state manager
        result = interview_manager.submit_answer(
            thread_id=request.thread_id,
            question_number=request.question_number,
            answer=request.answer
        )
        
        return {
            "message": "Answer submitted successfully",
            "thread_id": result["thread_id"],
            "question_number": result["question_number"],
            "status": result["status"],
            "current_question": result["current_question"],
            "total_score": result["total_score"],
            "average_score": result["average_score"],
            "completed": result["completed"]
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit answer: {str(e)}"
        )

@router.get("/chat-history/{thread_id}")
async def get_chat_history(
    thread_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get complete chat history for an interview session.
    """
    try:
        # Verify the thread belongs to the current user
        db_session = db.query(InterviewSession).filter(
            InterviewSession.thread_id == thread_id,
            InterviewSession.user_id == current_user.id
        ).first()
        
        if not db_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found or access denied"
            )
        
        # Get chat history using state manager
        chat_history = interview_manager.get_chat_history(thread_id)
        
        return chat_history
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chat history: {str(e)}"
        )

@router.get("/sessions")
async def get_user_interview_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all interview sessions for the current user.
    """
    try:
        sessions = interview_manager.get_user_sessions(current_user.id)
        
        return {
            "message": "Interview sessions retrieved successfully",
            "user_id": current_user.id,
            "sessions": sessions,
            "total_sessions": len(sessions)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get interview sessions: {str(e)}"
        )

@router.get("/session/{thread_id}/status")
async def get_session_status(
    thread_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current status and progress of an interview session.
    """
    try:
        # Verify the thread belongs to the current user
        db_session = db.query(InterviewSession).filter(
            InterviewSession.thread_id == thread_id,
            InterviewSession.user_id == current_user.id
        ).first()
        
        if not db_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found or access denied"
            )
        
        # Get current state from state manager
        if thread_id in interview_manager.states:
            state = interview_manager.states[thread_id]
            
            return {
                "thread_id": thread_id,
                "session_id": db_session.id,
                "role": db_session.role,
                "company": db_session.company,
                "status": state.get("status", db_session.status),
                "current_question": state.get("current_question", 0),
                "total_questions": len(state.get("questions", [])),
                "answers_submitted": len([a for a in state.get("answers", []) if a]),
                "total_score": state.get("total_score", db_session.total_score or 0.0),
                "average_score": state.get("average_score", db_session.average_score or 0.0),
                "created_at": db_session.created_at.isoformat(),
                "completed_at": db_session.completed_at.isoformat() if db_session.completed_at else None
            }
        else:
            # Fallback to database information
            return {
                "thread_id": thread_id,
                "session_id": db_session.id,
                "role": db_session.role,
                "company": db_session.company,
                "status": db_session.status,
                "total_score": db_session.total_score or 0.0,
                "average_score": db_session.average_score or 0.0,
                "created_at": db_session.created_at.isoformat(),
                "completed_at": db_session.completed_at.isoformat() if db_session.completed_at else None
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session status: {str(e)}"
        )

@router.delete("/session/{thread_id}")
async def delete_interview_session(
    thread_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an interview session and all associated data.
    """
    try:
        # Verify the thread belongs to the current user
        db_session = db.query(InterviewSession).filter(
            InterviewSession.thread_id == thread_id,
            InterviewSession.user_id == current_user.id
        ).first()
        
        if not db_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found or access denied"
            )
        
        # Delete chat messages
        db.query(ChatMessage).filter(ChatMessage.session_id == db_session.id).delete()
        
        # Delete session
        db.delete(db_session)
        db.commit()
        
        # Remove from state manager memory
        if thread_id in interview_manager.states:
            del interview_manager.states[thread_id]
        
        return {
            "message": "Interview session deleted successfully",
            "thread_id": thread_id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete interview session: {str(e)}"
        )

@router.get("/analytics")
async def get_user_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get analytics and performance metrics for the user's interviews.
    """
    try:
        sessions = db.query(InterviewSession).filter(
            InterviewSession.user_id == current_user.id,
            InterviewSession.status == "completed"
        ).all()
        
        if not sessions:
            return {
                "message": "No completed interviews found",
                "total_interviews": 0,
                "analytics": {}
            }
        
        # Calculate analytics
        total_interviews = len(sessions)
        total_scores = [s.total_score for s in sessions if s.total_score]
        average_scores = [s.average_score for s in sessions if s.average_score]
        
        analytics = {
            "total_interviews": total_interviews,
            "average_total_score": sum(total_scores) / len(total_scores) if total_scores else 0,
            "average_score_per_question": sum(average_scores) / len(average_scores) if average_scores else 0,
            "best_performance": max(average_scores) if average_scores else 0,
            "worst_performance": min(average_scores) if average_scores else 0,
            "companies_interviewed": list(set(s.company for s in sessions if s.company)),
            "roles_interviewed": list(set(s.role for s in sessions if s.role)),
            "completion_rate": len([s for s in sessions if s.status == "completed"]) / len(sessions) * 100 if sessions else 0
        }
        
        return {
            "message": "Analytics retrieved successfully",
            "user_id": current_user.id,
            "analytics": analytics
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )
#