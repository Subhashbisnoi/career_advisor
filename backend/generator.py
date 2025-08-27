from .common import generator_llm, extract_resume_text
from .models import InterviewState, InterviewQuestions
from langchain_core.messages import SystemMessage, HumanMessage

def generate_question(state: InterviewState) -> dict:
    """Generate highly focused, role-specific interview questions 
    that deeply evaluate the candidate's technical expertise 
    based on their resume."""

    # Extract resume text
    resume_text = state.get("resume_text", "")

    structured_generator = generator_llm.with_structured_output(InterviewQuestions)

    messages = [
        SystemMessage(content="""
You are an AI technical interviewer. 
Your job is to ask exactly 3 interview questions that BEST test the candidate's readiness for the given role.
The role and company context will be provided, along with the candidate’s resume.
"""),
        
        HumanMessage(content=f"""
You are interviewing for the role of **{state['role']}** at **{state['company']}**.

Here is the candidate's resume text:
{resume_text}

Your task:
- Generate *exactly 3 questions*.  
- **Q1 and Q2**: VERY focused **technical deep-dive** questions directly from the candidate’s listed skills, projects, or technologies. 
    - They must require applied expertise, not just definitions or trivia.  
    - Example categories: debugging a system from their resume, optimizing real-world use cases, scaling an architecture they mentioned, analyzing algorithm tradeoffs they claim to know, etc.
- **Q3**: A technical collaboration/experience-based question. 
    - It should test how they explain, communicate, or handle **technical problem-solving in a team/real-world project scenario**, still tied to their resume or the role.  
    - Do NOT ask generic "tell me about a time" questions—ground it in resume-based real challenges.

Hard requirement:
- Ask ONLY the **most skill-revealing questions** possible (assume you get only these 3 chances to know their depth).  
- Do NOT ask fluffy or basic questions.  
- Do NOT ask about personality or general behavior.  
- Be role-specific + resume-specific.  

Generate ONLY the 3 final questions, nothing else.
""")
    ]

    response = structured_generator.invoke(messages)

    return {
        "question": response.questions
    }
