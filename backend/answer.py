from models import InterviewState

def get_user_input(prompt: str) -> str:
    """Helper function to get user input with validation."""
    while True:
        user_input = input(f"\n{prompt}\nYour answer (or 'skip' to skip): ").strip()
        if user_input.lower() == 'skip':
            return "[No answer provided]"
        if user_input:  # Only accept non-empty input
            return user_input
        print("Please provide a valid answer or type 'skip' to skip.")

def answer_1st_question(state: InterviewState) -> dict:
    """Get user input for the first interview question."""
    if not state.get('question') or len(state['question']) < 1:
        return {"answer": ["No question available"]}
    
    print("\n" + "="*80)
    print("QUESTION 1:")
    print("="*80)
    print(state['question'][0])
    print("="*80)
    
    answer = get_user_input("Please provide your answer:")
    
    # Ensure 'answer' list exists with at least 3 slots
    answers = state.get("answer", ["", "", ""])
    answers[0] = answer

    return {"answer": answers}

def answer_2nd_question(state: InterviewState) -> dict:
    """Get user input for the second interview question."""
    if not state.get('question') or len(state['question']) < 2:
        return {"answer": ["", "No question available"]}
    
    print("\n" + "="*80)
    print("QUESTION 2:")
    print("="*80)
    print(state['question'][1])
    print("="*80)
    
    answer = get_user_input("Please provide your answer:")
    
    # Ensure 'answer' list exists with at least 3 slots
    answers = state.get("answer", ["", "", ""])
    answers[1] = answer

    return {"answer": answers}

def answer_3rd_question(state: InterviewState) -> dict:
    """Get user input for the third interview question."""
    if not state.get('question') or len(state['question']) < 3:
        return {"answer": ["", "", "No question available"]}
    
    print("\n" + "="*80)
    print("QUESTION 3:")
    print("="*80)
    print(state['question'][2])
    print("="*80)
    
    answer = get_user_input("Please provide your answer:")
    
    # Ensure 'answer' list exists with at least 3 slots
    answers = state.get("answer", ["", "", ""])
    answers[2] = answer

    return {"answer": answers}