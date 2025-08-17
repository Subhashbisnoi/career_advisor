from common import generator_llm, extract_resume_text
from models import InterviewState, InterviewQuestions
from langchain_core.messages import SystemMessage, HumanMessage


def generate_question(state: InterviewState) -> dict:
    """Generate interview questions based on the candidate's resume.
    
    Args:
        state: Current interview state containing role, company, and resume path or text.
        
    Returns:
        dict: Dictionary containing the generated questions.
    """
    # Prefer resume_text if present; else extract from resume_path
    resume_text = state.get('resume_text') or (
        extract_resume_text(state['resume_path']) if state.get('resume_path') else ""
    )

    structured_generator = generator_llm.with_structured_output(InterviewQuestions)
    messages = [
        SystemMessage(content="You are an AI interviewer. You will ask focused, role-specific interview questions for the given company and role, based on the candidate's resume."),
        HumanMessage(content=f"""
You are interviewing for the role of {state['role']} at {state['company']}.
Here is the candidate's resume text:
{resume_text}
Use Resume Text to generate questions.
Keep these thing in mind:
->Do NOT ask generic behavioral or situational questions like 'tell me a time when....
->the candidate's technical depth in the specific skills mentioned in their resume.
->Questions must be challenging and require domain-specific application of knowledge.
->Questions should be specific to the role and company.

Generate exactly 3 interview questions meeting these criteria:
1. The first two questions must be highly specific technical questions or challenges related to the domain of the role and the candidate's resume.
2. The third question should touch on experience, communication, or collaboration skills, framed around handling a technical or domain-specific challenge in a real-world setting.

Return ONLY the list of 3 questions, nothing else.
""")
    ]
    response = structured_generator.invoke(messages)
    return {
        "question": response.questions
    }