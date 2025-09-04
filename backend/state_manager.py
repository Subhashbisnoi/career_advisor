"""
State management using LangGraph for interview sessions with threading support.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, END
import json

from database import get_db, SessionLocal
from models import User, InterviewSession, ChatMessage, InterviewState
from generator import generate_question
from feedback import feedback_generator
from roadmap import generate_roadmap

class InterviewStateManager:
    """Manages interview state using LangGraph with database persistence."""
    
    def __init__(self):
        # Keep a small in-memory cache for active sessions
        self.states: Dict[str, InterviewState] = {}
        self.graph = self._create_interview_graph()
    
    def _load_state_from_db(self, thread_id: str) -> Optional[InterviewState]:
        """Load interview state from database."""
        db = SessionLocal()
        try:
            # Get session from database
            db_session = db.query(InterviewSession).filter(InterviewSession.thread_id == thread_id).first()
            if not db_session:
                return None
            
            # Get all messages
            messages = db.query(ChatMessage).filter(
                ChatMessage.thread_id == thread_id
            ).order_by(ChatMessage.created_at).all()
            
            # Reconstruct state from database
            questions = []
            answers = []
            feedback = []
            marks = []
            current_question = 0
            
            question_count = 0
            for msg in messages:
                if msg.message_type == "question":
                    questions.append(msg.content)
                    question_count += 1
                elif msg.message_type == "answer":
                    answers.append(msg.content)
                    current_question = question_count
                elif msg.message_type == "feedback":
                    feedback.append(msg.content)
                    if msg.marks is not None:
                        marks.append(msg.marks)
            
            # Fill in any missing questions if needed
            while len(questions) < 3:
                questions.append(f"Interview question {len(questions) + 1}")
            
            state: InterviewState = {
                "thread_id": thread_id,
                "session_id": db_session.id,
                "user_id": db_session.user_id,
                "role": db_session.role,
                "company": db_session.company,
                "resume_text": db_session.resume_text or "",
                "questions": questions,
                "current_question": current_question,
                "answers": answers,
                "feedback": feedback,
                "marks": marks,
                "roadmap": "",
                "status": db_session.status,
                "total_score": db_session.total_score or 0.0,
                "average_score": db_session.average_score or 0.0
            }
            
            return state
            
        finally:
            db.close()
    
    def _save_state_to_db(self, state: InterviewState) -> None:
        """Save interview state to database."""
        db = SessionLocal()
        try:
            # Update session
            db_session = db.query(InterviewSession).filter(
                InterviewSession.thread_id == state["thread_id"]
            ).first()
            
            if db_session:
                db_session.status = state["status"]
                db_session.total_score = state.get("total_score", 0.0)
                db_session.average_score = state.get("average_score", 0.0)
                if state["status"] == "completed":
                    db_session.completed_at = datetime.now(timezone.utc)
                db.commit()
                
        finally:
            db.close()
    
    def _create_interview_graph(self) -> StateGraph:
        """Create the LangGraph workflow for interview management."""
        
        def start_interview(state: InterviewState) -> InterviewState:
            """Start a new interview session and generate questions."""
            print(f"Starting interview for role: {state['role']} at {state['company']}")
            
            # Generate questions
            question_result = generate_question({
                "role": state["role"],
                "company": state["company"],
                "resume_text": state["resume_text"]
            })
            
            questions = question_result.get("questions", [])
            if len(questions) < 3:
                questions = ["Tell me about yourself.", "What are your strengths?", "Why do you want this role?"]
            
            # Update state
            state.update({
                "questions": questions,
                "current_question": 0,
                "answers": [],
                "feedback": [],
                "marks": [],
                "status": "in_progress",
                "chat_history": [
                    {
                        "type": "system",
                        "content": f"Interview started for {state['role']} position at {state['company']}",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                ]
            })
            
            # Add questions to chat history
            for i, question in enumerate(questions):
                state["chat_history"].append({
                    "type": "question",
                    "content": question,
                    "question_number": i + 1,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
            return state
        
        def process_answer(state: InterviewState) -> InterviewState:
            """Process an answer and update the state."""
            current_q = state.get("current_question", 0)
            answers = state.get("answers", [])
            
            if current_q < len(answers):
                answer = answers[current_q]
                
                # Add answer to chat history
                state["chat_history"].append({
                    "type": "answer",
                    "content": answer,
                    "question_number": current_q + 1,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
                state["current_question"] = current_q + 1
            
            return state
        
        def generate_feedback(state: InterviewState) -> InterviewState:
            """Generate feedback for all answers."""
            if len(state.get("answers", [])) >= 3:
                # Prepare state for feedback generation
                feedback_state = {
                    "role": state["role"],
                    "company": state["company"],
                    "resume_text": state["resume_text"],
                    "question": state["questions"],
                    "answer": state["answers"],
                    "feedback": [],
                    "roadmap": ""
                }
                
                # Generate feedback
                feedback_result = feedback_generator(feedback_state)
                feedback_items = feedback_result.get("feedback", [])
                
                # Extract marks and feedback
                marks = [item.get("marks", 0) for item in feedback_items]
                total_score = sum(marks)
                avg_score = total_score / len(marks) if marks else 0
                
                # Update state
                state.update({
                    "feedback": feedback_items,
                    "marks": marks,
                    "total_score": total_score,
                    "average_score": avg_score
                })
                
                # Add feedback to chat history
                for i, feedback_item in enumerate(feedback_items):
                    state["chat_history"].append({
                        "type": "feedback",
                        "content": feedback_item.get("feedback", ""),
                        "marks": feedback_item.get("marks", 0),
                        "question_number": i + 1,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
            
            return state
        
        def generate_roadmap_step(state: InterviewState) -> InterviewState:
            """Generate learning roadmap."""
            if state.get("feedback"):
                # Prepare state for roadmap generation
                roadmap_state = {
                    "role": state["role"],
                    "company": state["company"],
                    "resume_text": state["resume_text"],
                    "question": state["questions"],
                    "answer": state["answers"],
                    "feedback": state["feedback"],
                    "roadmap": ""
                }
                
                # Generate roadmap
                roadmap_result = generate_roadmap(roadmap_state)
                roadmap_content = roadmap_result.get("roadmap", "No roadmap generated.")
                
                # Update state
                state.update({
                    "roadmap": roadmap_content,
                    "status": "completed",
                    "completed_at": datetime.now(timezone.utc).isoformat()
                })
                
                # Add roadmap to chat history
                state["chat_history"].append({
                    "type": "roadmap",
                    "content": roadmap_content,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
            return state
        
        def should_continue(state: InterviewState) -> str:
            """Determine next step in the interview process."""
            answers = state.get("answers", [])
            current_q = state.get("current_question", 0)
            
            if len(answers) < 3:
                return "wait_for_answer"
            elif not state.get("feedback"):
                return "generate_feedback"
            elif not state.get("roadmap"):
                return "generate_roadmap"
            else:
                return "end"
        
        # Create the graph
        workflow = StateGraph(InterviewState)
        
        # Add nodes
        workflow.add_node("start_interview", start_interview)
        workflow.add_node("process_answer", process_answer)
        workflow.add_node("generate_feedback", generate_feedback)
        workflow.add_node("generate_roadmap", generate_roadmap_step)
        
        # Set entry point
        workflow.set_entry_point("start_interview")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "start_interview",
            should_continue,
            {
                "wait_for_answer": "process_answer",
                "generate_feedback": "generate_feedback",
                "generate_roadmap": "generate_roadmap",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "process_answer",
            should_continue,
            {
                "wait_for_answer": END,  # Wait for next answer
                "generate_feedback": "generate_feedback",
                "generate_roadmap": "generate_roadmap",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "generate_feedback",
            should_continue,
            {
                "generate_roadmap": "generate_roadmap",
                "end": END
            }
        )
        
        workflow.add_edge("generate_roadmap", END)
        
        return workflow.compile()
    
    def create_interview_session(self, user_id: int, role: str, company: str, resume_text: str) -> Dict[str, Any]:
        """Create a new interview session with a unique thread ID."""
        
        # Generate unique thread ID
        thread_id = f"interview_{uuid.uuid4().hex}"
        
        # Create database session
        db = SessionLocal()
        try:
            # Create interview session in database
            db_session = InterviewSession(
                user_id=user_id,
                thread_id=thread_id,
                role=role,
                company=company,
                resume_text=resume_text,
                status="active"
            )
            db.add(db_session)
            db.commit()
            db.refresh(db_session)
            
            # Initialize state
            initial_state: InterviewState = {
                "thread_id": thread_id,
                "user_id": user_id,
                "session_id": db_session.id,
                "role": role,
                "company": company,
                "resume_text": resume_text,
                "questions": [],
                "answers": [],
                "current_question": 0,
                "feedback": [],
                "marks": [],
                "total_score": 0.0,
                "average_score": 0.0,
                "roadmap": "",
                "status": "started",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "completed_at": None,
                "chat_history": []
            }
            
            # Run the initial step
            config = {"configurable": {"thread_id": thread_id}}
            result = self.graph.invoke(initial_state, config)
            
            # Store state in memory
            self.states[thread_id] = result
            
            # Save initial questions to database
            if result.get("questions"):
                for i, question in enumerate(result["questions"][:3]):  # Save up to 3 questions
                    question_message = ChatMessage(
                        session_id=db_session.id,
                        thread_id=thread_id,
                        message_type="question",
                        role="assistant",
                        content=question,
                        question_number=i + 1
                    )
                    db.add(question_message)
                db.commit()
            
            return {
                "thread_id": thread_id,
                "session_id": db_session.id,
                "questions": result.get("questions", []),
                "status": result.get("status", "started")
            }
            
        finally:
            db.close()
    
    def submit_answer(self, thread_id: str, question_number: int, answer: str) -> Dict[str, Any]:
        """Submit an answer for a specific question."""
        
        # Get current state from memory or load from database
        if thread_id not in self.states:
            state = self._load_state_from_db(thread_id)
            if not state:
                raise ValueError("Interview session not found")
        else:
            state = self.states[thread_id].copy()
        
        # Update answers
        answers = state.get("answers", [])
        while len(answers) < question_number:
            answers.append("")
        
        if question_number <= len(answers):
            answers[question_number - 1] = answer
        else:
            answers.append(answer)
        
        state["answers"] = answers
        
        # Save answer to database
        db = SessionLocal()
        try:
            # Get session from database
            db_session = db.query(InterviewSession).filter(InterviewSession.thread_id == thread_id).first()
            if not db_session:
                raise ValueError("Interview session not found in database")
            
            # Save answer message
            answer_message = ChatMessage(
                session_id=db_session.id,
                thread_id=thread_id,
                message_type="answer",
                role="user",
                content=answer,
                question_number=question_number
            )
            db.add(answer_message)
            db.commit()
            
            # Run the workflow to process the answer
            config = {"configurable": {"thread_id": thread_id}}
            result = self.graph.invoke(state, config)
            
            # Update state in memory
            self.states[thread_id] = result
            
            # Save feedback and marks to database if generated
            if result.get("feedback") and len(result["feedback"]) >= question_number:
                feedback_content = result["feedback"][question_number - 1]
                marks = result.get("marks", [])
                mark_value = marks[question_number - 1] if len(marks) >= question_number else None
                
                feedback_message = ChatMessage(
                    session_id=db_session.id,
                    thread_id=thread_id,
                    message_type="feedback",
                    role="assistant",
                    content=feedback_content,
                    question_number=question_number,
                    marks=mark_value
                )
                db.add(feedback_message)
            
            # Update session if completed
            if result.get("status") == "completed":
                db_session.status = "completed"
                db_session.total_score = result.get("total_score", 0.0)
                db_session.average_score = result.get("average_score", 0.0)
                db_session.completed_at = datetime.now(timezone.utc)
                
                # Add roadmap message
                if result.get("roadmap"):
                    roadmap_message = ChatMessage(
                        session_id=db_session.id,
                        thread_id=thread_id,
                        message_type="roadmap",
                        role="assistant",
                        content=result["roadmap"]
                    )
                    db.add(roadmap_message)
            
            db.commit()
            
        finally:
            db.close()
        
        return {
            "thread_id": thread_id,
            "question_number": question_number,
            "status": result.get("status", "in_progress"),
            "current_question": result.get("current_question", 0),
            "total_score": result.get("total_score", 0.0),
            "average_score": result.get("average_score", 0.0),
            "completed": result.get("status") == "completed"
        }
        while len(answers) < question_number:
            answers.append("")
        
        answers[question_number - 1] = answer
        state["answers"] = answers
        
        # Run the graph to process the answer
        config = {"configurable": {"thread_id": thread_id}}
        result = self.graph.invoke(state, config)
        
        # Update stored state
        self.states[thread_id] = result
        
        # Update database
        db = SessionLocal()
        try:
            session_id = result["session_id"]
            
            # Add answer to chat messages
            answer_message = ChatMessage(
                session_id=session_id,
                thread_id=thread_id,
                message_type="answer",
                role="user",
                content=answer,
                question_number=question_number
            )
            db.add(answer_message)
            
            # If feedback is generated, add it too
            if result.get("feedback") and question_number <= len(result["feedback"]):
                feedback_item = result["feedback"][question_number - 1]
                feedback_message = ChatMessage(
                    session_id=session_id,
                    thread_id=thread_id,
                    message_type="feedback",
                    role="assistant",
                    content=feedback_item.get("feedback", ""),
                    question_number=question_number,
                    marks=feedback_item.get("marks", 0),
                    message_metadata=feedback_item
                )
                db.add(feedback_message)
            
            # Update session if completed
            if result.get("status") == "completed":
                db_session = db.query(InterviewSession).filter(InterviewSession.thread_id == thread_id).first()
                if db_session:
                    db_session.status = "completed"
                    db_session.total_score = result.get("total_score", 0.0)
                    db_session.average_score = result.get("average_score", 0.0)
                    db_session.completed_at = datetime.now(timezone.utc)
                    
                    # Add roadmap message
                    if result.get("roadmap"):
                        roadmap_message = ChatMessage(
                            session_id=session_id,
                            thread_id=thread_id,
                            message_type="roadmap",
                            role="assistant",
                            content=result["roadmap"]
                        )
                        db.add(roadmap_message)
            
            db.commit()
            
        finally:
            db.close()
        
        return {
            "thread_id": thread_id,
            "question_number": question_number,
            "status": result.get("status", "in_progress"),
            "current_question": result.get("current_question", 0),
            "total_score": result.get("total_score", 0.0),
            "average_score": result.get("average_score", 0.0),
            "completed": result.get("status") == "completed"
        }
    
    def get_chat_history(self, thread_id: str) -> Dict[str, Any]:
        """Get complete chat history for a thread."""
        
        db = SessionLocal()
        try:
            # Get session from database
            db_session = db.query(InterviewSession).filter(InterviewSession.thread_id == thread_id).first()
            if not db_session:
                raise ValueError("Interview session not found")
            
            # Get all messages
            messages = db.query(ChatMessage).filter(
                ChatMessage.thread_id == thread_id
            ).order_by(ChatMessage.created_at).all()
            
            # Format messages
            chat_messages = []
            for msg in messages:
                message_data = {
                    "id": msg.id,
                    "type": msg.message_type,
                    "role": msg.role,
                    "content": msg.content,
                    "question_number": msg.question_number,
                    "marks": msg.marks,
                    "created_at": msg.created_at.isoformat(),
                    "metadata": msg.message_metadata
                }
                chat_messages.append(message_data)
            
            return {
                "thread_id": thread_id,
                "session_id": db_session.id,
                "role": db_session.role,
                "company": db_session.company,
                "status": db_session.status,
                "total_score": db_session.total_score or 0.0,
                "average_score": db_session.average_score or 0.0,
                "created_at": db_session.created_at.isoformat(),
                "completed_at": db_session.completed_at.isoformat() if db_session.completed_at else None,
                "messages": chat_messages
            }
            
        finally:
            db.close()
    
    def get_user_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all interview sessions for a user."""
        
        db = SessionLocal()
        try:
            sessions = db.query(InterviewSession).filter(
                InterviewSession.user_id == user_id
            ).order_by(InterviewSession.created_at.desc()).all()
            
            session_list = []
            for session in sessions:
                session_data = {
                    "thread_id": session.thread_id,
                    "session_id": session.id,
                    "role": session.role,
                    "company": session.company,
                    "status": session.status,
                    "total_score": session.total_score or 0.0,
                    "average_score": session.average_score or 0.0,
                    "created_at": session.created_at.isoformat(),
                    "completed_at": session.completed_at.isoformat() if session.completed_at else None
                }
                session_list.append(session_data)
            
            return session_list
            
        finally:
            db.close()
    
# Global instance
interview_manager = InterviewStateManager()
