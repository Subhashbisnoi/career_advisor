import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
import os
import tempfile
from pathlib import Path
from typing import List, Dict, Any
import json

# Import from the parent directory
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import InterviewState, InterviewSession, ChatMessage, User
from database import get_db
from common import extract_resume_text
from generator import generate_question
from feedback import feedback_generator
from roadmap import generate_roadmap

# Import authentication
from api.auth import get_current_user

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB

router = APIRouter(prefix="/interview", tags=["interview"])

# Store interview sessions in memory (in production, use a database)
interview_sessions: Dict[str, Dict[str, Any]] = {}
uploaded_resumes: Dict[str, Dict[str, str]] = {}

@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload resume PDF, extract text, and return it."""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        content = await file.read()
        
        # Check file size
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="File too large (max 10MB)")
        
        # Save to a temporary file for text extraction
        temp_path = None
        try:
            # Write the content to a temporary file (in case we need it for debugging)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name
            
            # Extract text from the PDF using the already read content
            resume_text = extract_resume_text(content)
            
            if not resume_text.strip():
                raise HTTPException(status_code=400, detail="Failed to extract text from PDF")
                
            return {"resume_text": resume_text}
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
            
        finally:
            # Clean up the temporary file if it was created
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass
                    
        return {
            "message": "Resume uploaded successfully",
            "resume_id": resume_id,
            "filename": file.filename
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.post("/start")
async def start_interview(
    interview_data: Dict[str, Any], 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a new interview session by generating questions only."""
    try:
        role = interview_data.get("role")
        company = interview_data.get("company")
        resume_text = interview_data.get("resume_text", "")

        if not role or not company:
            raise HTTPException(status_code=400, detail="Missing required fields: role, company")

        if not resume_text:
            raise HTTPException(status_code=400, detail="Resume text is required")
        
        initial_state: InterviewState = {
            "role": role,
            "company": company,
            "resume_text": resume_text,
            "question": [],
            "answer": [],
            "feedback": [],
            "roadmap": "",
        }

        # Generate questions directly
        gen = generate_question(initial_state)
        questions = gen.get("question", [])
        if not questions or len(questions) < 3:
            raise HTTPException(status_code=500, detail="Failed to generate interview questions")
        
        # Create unique session ID
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        # Ensure uniqueness in database (double-check for safety)
        existing_count = 0
        while db.query(InterviewSession).filter(InterviewSession.thread_id == session_id).first():
            existing_count += 1
            session_id = f"session_{uuid.uuid4().hex[:8]}"
            # Prevent infinite loop (though extremely unlikely with UUID)
            if existing_count > 10:
                session_id = f"session_{uuid.uuid4().hex}"
                break
        
        # Create database session
        db_session = InterviewSession(
            user_id=current_user.id,  # Link to the authenticated user
            thread_id=session_id,
            role=role,
            company=company,
            status="in_progress",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_session)
        db.commit()
        
        # Store in memory for the duration of the interview
        interview_sessions[session_id] = {
            "state": initial_state,
            "questions": questions,
        }
        
        return {
            "message": "Interview started successfully",
            "session_id": session_id,
            "questions": questions,
            "role": role,
            "company": company
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error starting interview: {str(e)}")

@router.post("/submit-answers")
async def submit_answers(
    session_data: Dict[str, Any], 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit all answers and generate feedback and roadmap."""
    try:
        session_id = session_data.get("session_id")
        if not session_id:
            raise HTTPException(status_code=400, detail="Session ID is required")
        
        # Check if session exists in database and belongs to the user
        session = db.query(InterviewSession).filter(
            InterviewSession.thread_id == session_id,
            InterviewSession.user_id == current_user.id
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        answers: List[str] = session_data.get("answers", [])
        if len(answers) != 3:
            raise HTTPException(status_code=400, detail="Exactly 3 answers are required")
        
        # Get questions from in-memory storage for now (we can improve this later)
        if session_id not in interview_sessions:
            raise HTTPException(status_code=404, detail="Session questions not found")
            
        session_data_memory = interview_sessions[session_id]
        questions: List[str] = session_data_memory.get("questions", [])
        state: InterviewState = session_data_memory.get("state", {})  # type: ignore
        
        complete_state: InterviewState = {
            **state,
            "question": questions,
            "answer": answers,
        }

        # Generate feedback
        feedback_result = feedback_generator(complete_state)
        feedback_items = feedback_result.get("feedback", [])
        complete_state["feedback"] = feedback_items
        
        # Generate roadmap with the complete state including feedback
        roadmap_result = generate_roadmap(complete_state)
        complete_state["roadmap"] = roadmap_result.get("roadmap", "")

        # Store questions in database as chat messages
        for i, question in enumerate(questions):
            question_msg = ChatMessage(
                session_id=session.id,  # Use the session's primary key
                thread_id=session_id,   # Store the thread_id for reference
                role="assistant",
                content=question,
                message_type="question",
                question_number=i + 1,
                created_at=datetime.utcnow()
            )
            db.add(question_msg)
        
        # Store answers and feedback in database as chat messages
        total_score = 0
        for i, (answer, feedback_item) in enumerate(zip(answers, feedback_items)):
            # Store answer
            answer_msg = ChatMessage(
                session_id=session.id,  # Use the session's primary key
                thread_id=session_id,   # Store the thread_id for reference
                role="user",
                content=answer,
                message_type="answer",
                question_number=i + 1,
                created_at=datetime.utcnow()
            )
            db.add(answer_msg)
            
            # Store feedback
            feedback_msg = ChatMessage(
                session_id=session.id,  # Use the session's primary key
                thread_id=session_id,   # Store the thread_id for reference
                role="assistant",
                content=feedback_item.get('feedback', ''),
                message_type="feedback",
                question_number=i + 1,
                marks=feedback_item.get('marks', 0),
                created_at=datetime.utcnow()
            )
            db.add(feedback_msg)
            total_score += feedback_item.get('marks', 0)
        
        # Store roadmap
        roadmap_msg = ChatMessage(
            session_id=session.id,  # Use the session's primary key
            thread_id=session_id,   # Store the thread_id for reference
            role="assistant",
            content=complete_state["roadmap"],
            message_type="roadmap",
            created_at=datetime.utcnow()
        )
        db.add(roadmap_msg)
        
        # Update session status and scores
        avg_score = total_score / len(feedback_items) if feedback_items else 0
        session.status = "completed"
        session.total_score = total_score
        session.average_score = avg_score
        session.updated_at = datetime.utcnow()
        session.completed_at = datetime.utcnow()
        
        db.commit()

        # Clean up in-memory session
        if session_id in interview_sessions:
            del interview_sessions[session_id]

        return {
            "message": "Interview completed successfully",
            "session_id": session_id,
            "feedback": feedback_items,
            "roadmap": complete_state["roadmap"],
            "total_score": total_score,
            "average_score": avg_score,
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error completing interview: {str(e)}")

@router.get("/session/{session_id}")
async def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get interview session details."""
    session = db.query(InterviewSession).filter(InterviewSession.thread_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session.thread_id,
        "role": session.role,
        "company": session.company,
        "status": session.status,
        "total_score": session.total_score,
        "average_score": session.average_score,
        "created_at": session.created_at,
        "updated_at": session.updated_at
    }

@router.get("/session/{session_id}/chat")
async def get_session_chat_history(session_id: str, db: Session = Depends(get_db)):
    """Get chat history for a specific session."""
    # Check if session exists
    session = db.query(InterviewSession).filter(InterviewSession.thread_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get all chat messages for this session using the session's primary key
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session.id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    return {
        "session_id": session_id,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "type": msg.message_type,
                "question_number": msg.question_number,
                "marks": msg.marks,
                "timestamp": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    }

@router.get("/sessions")
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all interview sessions for the current user."""
    try:
        # Get all sessions for the current user
        sessions = db.query(InterviewSession).filter(
            InterviewSession.user_id == current_user.id
        ).order_by(InterviewSession.created_at.desc()).all()
        
        print(f"DEBUG: Found {len(sessions)} sessions for user {current_user.email}")
        
        # Format sessions for the frontend
        formatted_sessions = []
        for session in sessions:
            # Check if session has feedback messages (completed)
            has_feedback = db.query(ChatMessage).filter(
                ChatMessage.session_id == session.id,
                ChatMessage.message_type == "feedback"
            ).first() is not None
            
            print(f"DEBUG: Session {session.thread_id} - status: {session.status}, has_feedback: {has_feedback}, score: {session.average_score}")
            
            session_data = {
                "thread_id": session.thread_id,  # Use thread_id for frontend consistency
                "session_id": session.thread_id,  # Keep session_id for backward compatibility
                "created_at": session.created_at.isoformat(),
                "status": "completed" if has_feedback else "in_progress",
                "score": session.average_score if session.average_score > 0 else None,
                "company": session.company,
                "role": session.role,
                "has_results": has_feedback,
                "is_pinned": session.is_pinned
            }
            
            formatted_sessions.append(session_data)
        
        print(f"DEBUG: Returning {len(formatted_sessions)} formatted sessions")
        return {"sessions": formatted_sessions}
        
    except Exception as e:
        print(f"Error fetching sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch sessions")

@router.get("/analytics")
async def get_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for the current user."""
    try:
        # Get all sessions for the current user
        sessions = db.query(InterviewSession).filter(
            InterviewSession.user_id == current_user.id
        ).all()
        
        print(f"DEBUG: Found {len(sessions)} sessions for user {current_user.email}")
        
        total_interviews = len(sessions)
        
        # Get completed sessions (those with feedback)
        completed_sessions = []
        companies = set()
        roles = set()
        
        for session in sessions:
            print(f"DEBUG: Session {session.thread_id} - status: {session.status}, avg_score: {session.average_score}")
            
            companies.add(session.company)
            roles.add(session.role)
            
            # Check if session has feedback (is completed)
            has_feedback = db.query(ChatMessage).filter(
                ChatMessage.session_id == session.id,
                ChatMessage.message_type == "feedback"
            ).first() is not None
            
            print(f"DEBUG: Session {session.thread_id} has_feedback: {has_feedback}")
            
            if has_feedback:
                completed_sessions.append(session)
        
        completed_interviews = len(completed_sessions)
        
        print(f"DEBUG: Completed sessions: {completed_interviews}")
        
        # Calculate average and best scores from completed sessions
        scores = [session.average_score for session in completed_sessions if session.average_score > 0]
        average_score = sum(scores) / len(scores) if scores else 0
        best_score = max(scores) if scores else 0
        
        print(f"DEBUG: Scores: {scores}, avg: {average_score}, best: {best_score}")
        
        return {
            "total_interviews": total_interviews,
            "completed_interviews": completed_interviews,
            "average_score": round(average_score, 1),
            "best_score": round(best_score, 1),
            "companies": list(companies),
            "roles": list(roles)
        }
        
    except Exception as e:
        print(f"Error fetching analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch analytics")

@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an interview session."""
    try:
        # Find the session for the current user
        session = db.query(InterviewSession).filter(
            InterviewSession.thread_id == session_id,
            InterviewSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Delete associated chat messages first
        db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
        ).delete()
        
        # Delete the session
        db.delete(session)
        db.commit()
        
        return {"message": "Session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete session")

@router.post("/pin/{session_id}")
async def pin_interview_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Pin an interview session."""
    try:
        # Find the session for the current user
        session = db.query(InterviewSession).filter(
            InterviewSession.thread_id == session_id,
            InterviewSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Pin the session
        session.is_pinned = True
        db.commit()
        
        return {"message": "Session pinned successfully", "is_pinned": True}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error pinning session: {e}")
        raise HTTPException(status_code=500, detail="Failed to pin session")

@router.post("/unpin/{session_id}")
async def unpin_interview_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unpin an interview session."""
    try:
        # Find the session for the current user
        session = db.query(InterviewSession).filter(
            InterviewSession.thread_id == session_id,
            InterviewSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Unpin the session
        session.is_pinned = False
        db.commit()
        
        return {"message": "Session unpinned successfully", "is_pinned": False}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error unpinning session: {e}")
        raise HTTPException(status_code=500, detail="Failed to unpin session")

@router.get("/pinned")
async def get_pinned_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all pinned interview sessions for the current user."""
    try:
        sessions = db.query(InterviewSession).filter(
            InterviewSession.user_id == current_user.id,
            InterviewSession.is_pinned == True
        ).order_by(InterviewSession.updated_at.desc()).all()
        
        sessions_data = []
        for session in sessions:
            # Get the last few messages for context
            messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session.id
            ).order_by(ChatMessage.created_at.desc()).limit(10).all()
            
            # Extract feedback and roadmap if available
            feedback_msg = next((msg for msg in messages if msg.message_type == "feedback"), None)
            roadmap_msg = next((msg for msg in messages if msg.message_type == "roadmap"), None)
            
            session_data = {
                "thread_id": session.thread_id,
                "session_id": session.id,
                "role": session.role,
                "company": session.company,
                "status": session.status,
                "total_score": session.total_score,
                "average_score": session.average_score,
                "is_pinned": session.is_pinned,
                "created_at": session.created_at,
                "completed_at": session.completed_at,
                "feedback": feedback_msg.content if feedback_msg else None,
                "roadmap": roadmap_msg.content if roadmap_msg else None
            }
            sessions_data.append(session_data)
        
        return {"pinned_sessions": sessions_data}
        
    except Exception as e:
        print(f"Error fetching pinned sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch pinned sessions")