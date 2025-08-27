from .common import generator_llm, extract_resume_text
from .models import InterviewState
from langchain_core.messages import SystemMessage, HumanMessage

def generate_roadmap(state: InterviewState) -> dict:
    """Generate a personalized learning roadmap based on interview feedback.
    
    Args:
        state: Current interview state containing feedback and other details.
        
    Returns:
        dict: Dictionary containing the generated roadmap.
    """
    print("\n" + "="*80)
    print("GENERATE_ROADMAP CALLED WITH STATE:")
    print("="*80)
    print(f"State keys: {state.keys()}")
    print(f"Feedback type: {type(state.get('feedback'))}")
    print(f"Feedback content: {state.get('feedback')}")
    print("="*80 + "\n")
    
    if not state.get('feedback'):
        return {"roadmap": "No feedback available to generate a roadmap."}
    
    # Prepare feedback summary
    try:
        feedback_text = "\n".join([
            f"Question {i+1} Feedback: {item.get('feedback', 'No feedback')} (Score: {item.get('marks', 0)}/10)"
            for i, item in enumerate(state['feedback'])
        ])
    except Exception as e:
        error_msg = f"Error processing feedback: {str(e)}"
        print("\n" + "="*80)
        print("FEEDBACK PROCESSING ERROR:")
        print("="*80)
        print(error_msg)
        print("="*80 + "\n")
        return {"roadmap": f"Error generating roadmap: {error_msg}"}
    
    print("\n" + "="*80)
    print("FEEDBACK TEXT PREPARED:")
    print("="*80)
    print(feedback_text)
    print("="*80 + "\n")
    
    # Get the candidate's answers for context
    answers_text = "\n".join([
        f"Question {i+1}: {state['question'][i]}\nAnswer: {state['answer'][i] if i < len(state.get('answer', [])) else 'No answer'}"
        for i in range(min(3, len(state.get('question', []))))
    ])
    
    print("\n" + "="*80)
    print("GENERATING PERSONALIZED LEARNING ROADMAP...")
    print("="*80)
    
    messages = [
        SystemMessage(content="""You are a career coach which focus on every single technical detail of the candidate's profile. Create a personalized learning roadmap based on interview feedback.
        The roadmap should be:
        1. Structured with clear sections
        2. Actionable with specific steps
        3. Include resources and skills to develop
        4. Focus on areas needing improvement
        5. Include a timeline for completion
        6. Focused on technical skill development
        7. Don't focus on non technical skills
        8. Have both free resources and paid resources
        9. Give a summary of the roadmap   
         

        
        Format the roadmap in markdown with clear headings and bullet points.
        Be encouraging and professional in your tone."""),
        HumanMessage(content=f"""
        CANDIDATE PROFILE:
        Role Applied For: {state.get('role', 'Not specified')}
        Company: {state.get('company', 'Not specified')}
        
        INTERVIEW QUESTIONS AND ANSWERS:
        {answers_text}
        
        FEEDBACK RECEIVED:
        {feedback_text}
        
        Please create a very detailed learning roadmap to help this candidate improve for future interviews.
        Focus on the areas where they need the most improvement based on the feedback.
        """)
    ]

    try:
        print("\n" + "="*80)
        print("CALLING GENERATOR_LLM.INVOKE...")
        print("="*80)
        
        # Call the LLM to generate the roadmap
        response = generator_llm.invoke(messages)
        
        print("\n" + "="*80)
        print("RESPONSE FROM GENERATOR_LLM:")
        print("="*80)
        print(f"Response type: {type(response)}")
        print(f"Response content: {response}")
        
        # Extract content from the response
        if hasattr(response, 'content'):
            roadmap = response.content
            print("\nExtracted content from response.content")
        else:
            roadmap = str(response)
            print("\nConverted response to string")
        
        print(f"\nRoadmap content type: {type(roadmap)}")
        print(f"Roadmap content length: {len(roadmap) if roadmap else 0}")
        print("="*80 + "\n")
        
        # Ensure the roadmap is properly formatted
        if not roadmap or not roadmap.strip():
            error_msg = "Generated roadmap is empty"
            print("\n" + "="*80)
            print("EMPTY ROADMAP GENERATED")
            print("="*80)
            print(error_msg)
            print("="*80 + "\n")
            return {"roadmap": "# Learning Roadmap\n\nCould not generate a roadmap. The generated content was empty. Please try again."}
        
        # Print the roadmap for debugging
        print("\n" + "="*80)
        print("PERSONALIZED LEARNING ROADMAP")
        print("="*80)
        print(roadmap)
        print("="*80 + "\n")
        
        # Ensure the roadmap is a string
        if not isinstance(roadmap, str):
            roadmap = str(roadmap)
        
        return {"roadmap": roadmap}
        
    except Exception as e:
        error_msg = f"An error occurred while generating the roadmap: {str(e)}"
        import traceback
        tb = traceback.format_exc()
        
        print("\n" + "="*80)
        print("ERROR GENERATING ROADMAP")
        print("="*80)
        print(error_msg)
        print("\nTraceback:")
        print(tb)
        print("="*80 + "\n")
        
        return {"roadmap": f"# Error Generating Roadmap\n\n{error_msg}\n\nPlease try again later or contact support if the issue persists."}