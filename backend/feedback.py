from .common import feedback_llm
from .models import InterviewState
from langchain_core.messages import SystemMessage, HumanMessage

def generate_feedback(question: str, answer: str, role: str, company: str) -> dict:
    """Generate feedback for a single question-answer pair."""
    if not question or not answer or answer == "[No answer provided]":
        return {
            'feedback': 'No answer was provided for this question.',
            'marks': 0
        }
    
    messages = [
        SystemMessage(content="""You are an experienced interviewer. Provide constructive feedback on the candidate's answer.
        For the answer, provide:
        1. Specific feedback on what was good and what could be improved
        2. A numerical score from 1-10 (10 being best)
        
        Be professional and helpful in your feedback. Format your response as:
        
        Feedback: [Your feedback here]
        Score: [1-10]"""),
        HumanMessage(content=f"""
        Interview for {role} at {company}:
        
        Question: {question}
        Answer: {answer}
        
        Please provide your feedback for this answer.""")
    ]
    
    try:
        response = feedback_llm.invoke(messages)
        feedback_text = response.content.strip()
        
        # Parse the score from the feedback (look for "Score: X" pattern)
        score = 5  # Default score
        if "Score:" in feedback_text:
            score_part = feedback_text.split("Score:", 1)[1].strip().split()[0]
            try:
                score = min(10, max(1, int(score_part)))
            except (ValueError, IndexError):
                pass
        
        # Clean up the feedback text
        feedback = feedback_text.split("Score:")[0].replace("Feedback:", "").strip()
        
        return {
            'feedback': feedback if feedback else 'No specific feedback was generated.',
            'marks': score
        }
    except Exception as e:
        print(f"Error generating feedback: {str(e)}")
        return {
            'feedback': 'An error occurred while generating feedback.',
            'marks': 5
        }

def feedback_generator(state: InterviewState) -> dict:
    """Generate feedback for all interview answers.
    
    Args:
        state: Current interview state containing questions and answers.
        
    Returns:
        dict: Dictionary containing the feedback for all answers.
    """
    if not state.get('question') or len(state['question']) < 3 or not state.get('answer') or len(state['answer']) < 3:
        return {"feedback": [{"feedback": "Not enough questions or answers to generate feedback.", "marks": 0}]}
    
    feedback_items = []
    
    # Generate feedback for each question-answer pair
    for i in range(3):
        question = state['question'][i] if i < len(state['question']) else "No question provided"
        answer = state['answer'][i] if i < len(state['answer']) else "No answer provided"
        
        print(f"\nGenerating feedback for Question {i+1}...")
        feedback = generate_feedback(question, answer, state.get('role', 'the role'), state.get('company', 'the company'))
        feedback_items.append(feedback)
        
        # Print the feedback for the user
        print(f"\n{'='*40}")
        print(f"FEEDBACK FOR QUESTION {i+1}:")
        print("-" * 40)
        print(feedback['feedback'])
        print(f"\nScore: {feedback['marks']}/10")
        print(f"{'='*40}\n")
    
    return {"feedback": feedback_items}