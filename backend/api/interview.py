from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
import os
import tempfile
from pathlib import Path
from typing import List, Dict, Any
import json

from models import InterviewState
from common import extract_resume_text
from generator import generate_question
from feedback import feedback_generator
from roadmap import generate_roadmap

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
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Extract text from the PDF
            resume_text = extract_resume_text(temp_path)
            
            if not resume_text.strip():
                raise HTTPException(status_code=400, detail="Failed to extract text from PDF")
                
            return {"resume_text": resume_text}
            
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_path)
            except Exception:
                pass
                
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Don't parse here; store only
        resume_id = os.path.basename(temp_file_path)
        uploaded_resumes[resume_id] = {
            "path": temp_file_path,
            "filename": file.filename,
        }
        
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
async def start_interview(interview_data: Dict[str, Any]):
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
        
        # Create session
        session_id = f"session_{len(interview_sessions) + 1}"
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
        raise HTTPException(status_code=500, detail=f"Error starting interview: {str(e)}")

@router.post("/submit-answers")
async def submit_answers(session_data: Dict[str, Any]):
    """Submit all answers and generate feedback and roadmap."""
    try:
        session_id = session_data.get("session_id")
        if not session_id or session_id not in interview_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        answers: List[str] = session_data.get("answers", [])
        if len(answers) != 3:
            raise HTTPException(status_code=400, detail="Exactly 3 answers are required")
        
        session = interview_sessions[session_id]
        questions: List[str] = session.get("questions", [])
        state: InterviewState = session.get("state", {})  # type: ignore
        
        complete_state: InterviewState = {
            **state,
            "question": questions,
            "answer": answers,
        }

        # Generate feedback
        feedback_result = feedback_generator(complete_state)
        feedback_items = feedback_result.get("feedback", [])
        complete_state["feedback"] = feedback_items
        
        # Debug: Print feedback items
        print("\n" + "="*80)
        print("FEEDBACK ITEMS:")
        print("="*80)
        print(f"Number of feedback items: {len(feedback_items)}")
        for i, item in enumerate(feedback_items):
            print(f"\nFeedback {i+1}:")
            print(f"- Feedback: {item.get('feedback', 'No feedback')}")
            print(f"- Marks: {item.get('marks', 0)}")
        print("="*80 + "\n")
        
        # Generate roadmap with the complete state including feedback
        print("\n" + "="*80)
        print("GENERATING ROADMAP...")
        print("="*80)
        print(f"Complete state keys: {complete_state.keys()}")
        print(f"Feedback in complete_state: {bool(complete_state.get('feedback'))}")
        print("="*80 + "\n")
        
        roadmap_result = generate_roadmap(complete_state)
        complete_state["roadmap"] = roadmap_result.get("roadmap", "")

        # Persist results in session
        interview_sessions[session_id]["results"] = {
            "feedback": complete_state["feedback"],
            "roadmap": complete_state["roadmap"],
        }
        
        total_score = sum([f.get("marks", 0) for f in complete_state["feedback"]])
        avg_score = total_score / len(complete_state["feedback"]) if complete_state["feedback"] else 0

        return {
            "message": "Interview completed successfully",
            "session_id": session_id,
            "feedback": complete_state["feedback"],
            "roadmap": complete_state["roadmap"],
            "total_score": total_score,
            "average_score": avg_score,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing interview: {str(e)}")

@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get interview session details."""
    if session_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = interview_sessions[session_id]
    return {
        "session_id": session_id,
        "questions": session.get("questions", []),
        "results": session.get("results", {})
    }

@router.get("/sessions")
async def list_sessions():
    """List all interview sessions."""
    return {
        "sessions": [
            {
                "session_id": session_id,
                "has_results": "results" in session
            }
            for session_id, session in interview_sessions.items()
        ]
    }