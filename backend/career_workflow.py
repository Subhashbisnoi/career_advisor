"""
Career Assessment Workflow using LangGraph
Orchestrates the career guidance process for students.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from models import CareerAssessmentState, AssessmentType, CareerField
import os

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
)

class CareerAssessmentWorkflow:
    """Orchestrates the career assessment and recommendation process."""
    
    def __init__(self):
        self.graph = self._create_workflow_graph()
    
    def _create_workflow_graph(self) -> StateGraph:
        """Create the career assessment workflow graph."""
        workflow = StateGraph(CareerAssessmentState)
        
        # Add nodes
        workflow.add_node("start_assessment", self.start_assessment)
        workflow.add_node("generate_questions", self.generate_questions)
        workflow.add_node("process_responses", self.process_responses)
        workflow.add_node("analyze_skills", self.analyze_skills)
        workflow.add_node("analyze_aptitude", self.analyze_aptitude)
        workflow.add_node("analyze_interests", self.analyze_interests)
        workflow.add_node("analyze_personality", self.analyze_personality)
        workflow.add_node("match_careers", self.match_careers)
        workflow.add_node("identify_gaps", self.identify_gaps)
        workflow.add_node("generate_recommendations", self.generate_recommendations)
        workflow.add_node("complete_assessment", self.complete_assessment)
        
        # Define edges
        workflow.set_entry_point("start_assessment")
        workflow.add_edge("start_assessment", "generate_questions")
        workflow.add_edge("generate_questions", "process_responses")
        workflow.add_edge("process_responses", "analyze_skills")
        workflow.add_edge("analyze_skills", "analyze_aptitude")
        workflow.add_edge("analyze_aptitude", "analyze_interests")
        workflow.add_edge("analyze_interests", "analyze_personality")
        workflow.add_edge("analyze_personality", "match_careers")
        workflow.add_edge("match_careers", "identify_gaps")
        workflow.add_edge("identify_gaps", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "complete_assessment")
        workflow.add_edge("complete_assessment", END)
        
        return workflow.compile()
    
    async def start_assessment(self, state: CareerAssessmentState) -> CareerAssessmentState:
        """Initialize the career assessment."""
        state["status"] = "started"
        state["started_at"] = datetime.utcnow().isoformat()
        state["current_question"] = 0
        state["questions"] = []
        state["responses"] = []
        state["chat_history"] = []
        
        # Add welcome message
        welcome_msg = {
            "role": "assistant",
            "content": "Welcome to your personalized career assessment! I'll help you discover career paths that align with your interests, skills, and aspirations. Let's begin with understanding your background and goals.",
            "timestamp": datetime.utcnow().isoformat()
        }
        state["chat_history"].append(welcome_msg)
        
        return state
    
    async def generate_questions(self, state: CareerAssessmentState) -> CareerAssessmentState:
        """Generate assessment questions based on assessment type and user background."""
        assessment_type = state["assessment_type"]
        user_background = state.get("user_background", {})
        
        # Create prompt for question generation
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"""You are an expert career counselor for Indian students. Generate comprehensive assessment questions for a {assessment_type} assessment.

Consider the Indian job market context, educational system, and cultural factors. Questions should be:
1. Culturally relevant to Indian students
2. Cover both traditional and emerging career paths
3. Assess skills relevant to the modern Indian job market
4. Consider family expectations and personal aspirations
5. Include technical and soft skills assessment

User Background: {json.dumps(user_background, indent=2)}

Generate 15-20 questions that will help assess:
- Technical skills and competencies
- Soft skills and interpersonal abilities
- Career interests and preferences
- Learning style and adaptability
- Leadership and teamwork capabilities
- Problem-solving approach
- Career goals and aspirations

Return a JSON object with the following structure:
{{
    "questions": [
        {{
            "id": "unique_question_id",
            "category": "technical|soft_skills|interests|personality|goals",
            "question": "The question text",
            "type": "multiple_choice|rating|text|scenario",
            "options": [
                {{"value": "option_key", "label": "Display Text"}},
                {{"value": "option_key2", "label": "Display Text 2"}}
            ] // for multiple choice - use value/label format, empty array for text/scenario
        }}
    ]
}}"""),
            HumanMessage(content=f"Generate assessment questions for {assessment_type} assessment.")
        ])
        
        # Generate questions
        response = await llm.ainvoke(prompt.format_messages())
        
        try:
            parser = JsonOutputParser()
            questions_data = parser.parse(response.content)
            state["questions"] = questions_data.get("questions", [])
        except Exception as e:
            # Fallback questions if parsing fails
            state["questions"] = self._get_fallback_questions(assessment_type)
        
        return state
    
    async def process_responses(self, state: CareerAssessmentState) -> CareerAssessmentState:
        """Process user responses to assessment questions."""
        # This method will be called after all responses are collected
        state["status"] = "processing"
        
        # Add processing message
        processing_msg = {
            "role": "assistant", 
            "content": "Thank you for completing the assessment! I'm now analyzing your responses to provide personalized career recommendations.",
            "timestamp": datetime.utcnow().isoformat()
        }
        state["chat_history"].append(processing_msg)
        
        return state
    
    async def analyze_skills(self, state: CareerAssessmentState) -> CareerAssessmentState:
        """Analyze technical and soft skills from responses."""
        responses = state.get("responses", [])
        questions = state.get("questions", [])
        
        # Filter skill-related responses
        skill_responses = [
            r for r in responses 
            if any(q["id"] == r["question_id"] and q["category"] in ["technical", "soft_skills"] 
                  for q in questions)
        ]
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert skills assessor for the Indian job market. Analyze the user's responses to identify their technical and soft skills.

Consider:
1. Technical skills relevant to Indian industries (IT, Healthcare, Finance, Manufacturing, etc.)
2. Soft skills valued in Indian workplace culture
3. Communication skills (English proficiency, regional languages)
4. Leadership and teamwork abilities
5. Problem-solving and analytical thinking
6. Adaptability and learning agility

Return a JSON analysis with:
{
    "technical_skills": [
        {
            "skill": "skill_name",
            "proficiency": "beginner|intermediate|advanced|expert",
            "evidence": "supporting evidence from responses",
            "market_relevance": "high|medium|low"
        }
    ],
    "soft_skills": [
        {
            "skill": "skill_name", 
            "proficiency": "beginner|intermediate|advanced|expert",
            "evidence": "supporting evidence from responses",
            "importance": "high|medium|low"
        }
    ],
    "skills_score": 0-100,
    "strengths": ["list of key strengths"],
    "areas_for_improvement": ["list of improvement areas"]
}"""),
            HumanMessage(content=f"Analyze these skill-related responses:\n{json.dumps(skill_responses, indent=2)}")
        ])
        
        response = await llm.ainvoke(prompt.format_messages())
        
        try:
            parser = JsonOutputParser()
            skills_analysis = parser.parse(response.content)
            state["skills_analysis"] = skills_analysis
            state["skills_score"] = skills_analysis.get("skills_score", 0.0)
        except Exception as e:
            state["skills_analysis"] = {"error": "Failed to analyze skills"}
            state["skills_score"] = 0.0
        
        return state
    
    async def analyze_aptitude(self, state: CareerAssessmentState) -> CareerAssessmentState:
        """Analyze logical reasoning and analytical aptitude."""
        responses = state.get("responses", [])
        questions = state.get("questions", [])
        
        # Filter aptitude-related responses
        aptitude_responses = [
            r for r in responses 
            if any(q["id"] == r["question_id"] and "aptitude" in q.get("category", "").lower() 
                  for q in questions)
        ]
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""Analyze the user's aptitude and cognitive abilities based on their responses.

Assess:
1. Logical reasoning and analytical thinking
2. Problem-solving approach and methodology
3. Mathematical and quantitative abilities
4. Spatial and visual reasoning
5. Verbal and linguistic comprehension
6. Pattern recognition and abstract thinking

Return JSON analysis:
{
    "aptitude_areas": {
        "logical_reasoning": 0-100,
        "analytical_thinking": 0-100,
        "quantitative_skills": 0-100,
        "verbal_reasoning": 0-100,
        "spatial_intelligence": 0-100
    },
    "aptitude_score": 0-100,
    "learning_style": "visual|auditory|kinesthetic|mixed",
    "problem_solving_approach": "systematic|intuitive|collaborative|independent",
    "cognitive_strengths": ["list of strengths"],
    "development_areas": ["areas to develop"]
}"""),
            HumanMessage(content=f"Analyze aptitude from responses:\n{json.dumps(aptitude_responses, indent=2)}")
        ])
        
        response = await llm.ainvoke(prompt.format_messages())
        
        try:
            parser = JsonOutputParser()
            aptitude_analysis = parser.parse(response.content)
            state["aptitude_analysis"] = aptitude_analysis
            state["aptitude_score"] = aptitude_analysis.get("aptitude_score", 0.0)
        except Exception as e:
            state["aptitude_analysis"] = {"error": "Failed to analyze aptitude"}
            state["aptitude_score"] = 0.0
        
        return state
    
    async def analyze_interests(self, state: CareerAssessmentState) -> CareerAssessmentState:
        """Analyze career interests and preferences."""
        responses = state.get("responses", [])
        questions = state.get("questions", [])
        
        # Filter interest-related responses
        interest_responses = [
            r for r in responses 
            if any(q["id"] == r["question_id"] and q["category"] in ["interests", "goals"] 
                  for q in questions)
        ]
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""Analyze the user's career interests and preferences for the Indian job market.

Consider:
1. Industry preferences (Technology, Healthcare, Finance, Education, Government, etc.)
2. Work environment preferences (Corporate, Startup, Government, NGO, Academia)
3. Career goals and aspirations
4. Work-life balance priorities
5. Geographic preferences (Metro cities, Tier-2 cities, Remote work)
6. Innovation vs Stability preferences
7. Leadership vs Individual contributor preferences

Return JSON analysis:
{
    "industry_interests": [
        {
            "industry": "industry_name",
            "interest_level": "high|medium|low",
            "specific_areas": ["list of specific areas"]
        }
    ],
    "work_preferences": {
        "environment": "corporate|startup|government|academia|ngo",
        "team_size": "small|medium|large",
        "work_style": "independent|collaborative|mixed",
        "innovation_level": "high|medium|low"
    },
    "career_values": ["list of important values"],
    "interest_score": 0-100,
    "top_interests": ["top 5 career interests"]
}"""),
            HumanMessage(content=f"Analyze interests from responses:\n{json.dumps(interest_responses, indent=2)}")
        ])
        
        response = await llm.ainvoke(prompt.format_messages())
        
        try:
            parser = JsonOutputParser()
            interest_analysis = parser.parse(response.content)
            state["interest_analysis"] = interest_analysis
            state["interest_score"] = interest_analysis.get("interest_score", 0.0)
        except Exception as e:
            state["interest_analysis"] = {"error": "Failed to analyze interests"}
            state["interest_score"] = 0.0
        
        return state
    
    async def analyze_personality(self, state: CareerAssessmentState) -> CareerAssessmentState:
        """Analyze personality traits relevant to career fit."""
        responses = state.get("responses", [])
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""Analyze personality traits that influence career success and satisfaction.

Assess:
1. Extroversion vs Introversion tendencies
2. Decision-making style (Analytical vs Intuitive)
3. Stress management and resilience
4. Communication and interpersonal style
5. Leadership potential and style
6. Risk tolerance and adaptability
7. Cultural fit for Indian workplace dynamics

Return JSON analysis:
{
    "personality_traits": {
        "extroversion": 0-100,
        "analytical_thinking": 0-100,
        "resilience": 0-100,
        "leadership_potential": 0-100,
        "risk_tolerance": 0-100,
        "adaptability": 0-100
    },
    "personality_type": "description of personality type",
    "communication_style": "direct|diplomatic|collaborative|assertive",
    "leadership_style": "democratic|autocratic|transformational|servant",
    "ideal_work_culture": "description of ideal work environment",
    "personality_score": 0-100
}"""),
            HumanMessage(content=f"Analyze personality from all responses:\n{json.dumps(responses, indent=2)}")
        ])
        
        response = await llm.ainvoke(prompt.format_messages())
        
        try:
            parser = JsonOutputParser()
            personality_analysis = parser.parse(response.content)
            state["personality_analysis"] = personality_analysis
        except Exception as e:
            state["personality_analysis"] = {"error": "Failed to analyze personality"}
        
        return state
    
    async def match_careers(self, state: CareerAssessmentState) -> CareerAssessmentState:
        """Match user profile with suitable career paths."""
        skills_analysis = state.get("skills_analysis", {})
        aptitude_analysis = state.get("aptitude_analysis", {})
        interest_analysis = state.get("interest_analysis", {})
        personality_analysis = state.get("personality_analysis", {})
        user_background = state.get("user_background", {})
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert career counselor for Indian students. Match the user's profile with suitable career paths.

Consider the current and emerging Indian job market, including:
1. Traditional careers (Engineering, Medicine, Teaching, Government services)
2. Growing tech careers (AI/ML, Data Science, Cybersecurity, Cloud Computing)
3. Business careers (Consulting, Finance, Marketing, Entrepreneurship)
4. Creative careers (Design, Content, Media, Entertainment)
5. Social impact careers (NGO, Policy, Sustainability)
6. New age careers (Product Management, UX/UI, DevOps, etc.)

User Profile Summary:
- Skills Analysis: {skills_analysis}
- Aptitude Analysis: {aptitude_analysis}
- Interest Analysis: {interest_analysis}
- Personality Analysis: {personality_analysis}
- Background: {user_background}

Return JSON with career matches:
{{
    "career_matches": [
        {{
            "career_title": "specific career title",
            "field": "technology|healthcare|finance|education|government|business|creative|science",
            "match_score": 0-100,
            "reasoning": "why this career matches the user",
            "growth_prospects": "excellent|good|moderate|limited",
            "salary_range": "entry-level to senior-level range in INR",
            "required_skills": ["list of required skills"],
            "preferred_skills": ["list of preferred skills"],
            "entry_requirements": "education and experience requirements",
            "career_path": "typical progression path",
            "work_environment": "description of typical work environment"
        }}
    ],
    "top_3_recommendations": ["top 3 career titles"],
    "alternative_paths": ["alternative career options"]
}}"""),
            HumanMessage(content="Match career paths based on the analyzed profile.")
        ])
        
        response = await llm.ainvoke(prompt.format_messages(
            skills_analysis=json.dumps(skills_analysis, indent=2),
            aptitude_analysis=json.dumps(aptitude_analysis, indent=2),
            interest_analysis=json.dumps(interest_analysis, indent=2),
            personality_analysis=json.dumps(personality_analysis, indent=2),
            user_background=json.dumps(user_background, indent=2)
        ))
        
        try:
            parser = JsonOutputParser()
            career_matches = parser.parse(response.content)
            state["career_matches"] = career_matches.get("career_matches", [])
        except Exception as e:
            state["career_matches"] = []
        
        return state
    
    async def identify_gaps(self, state: CareerAssessmentState) -> CareerAssessmentState:
        """Identify skills gaps for recommended careers."""
        career_matches = state.get("career_matches", [])
        skills_analysis = state.get("skills_analysis", {})
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""Analyze skills gaps between the user's current capabilities and the requirements for their top career matches.

For each recommended career, identify:
1. Skills the user already possesses
2. Skills they need to develop
3. Priority level of each missing skill
4. Estimated time to acquire each skill
5. Learning resources and pathways

Current Skills: {current_skills}
Career Matches: {career_matches}

Return JSON analysis:
{{
    "skills_gaps": [
        {{
            "career_title": "career name",
            "matching_skills": ["skills user already has"],
            "missing_skills": [
                {{
                    "skill": "skill name",
                    "priority": "high|medium|low",
                    "estimated_learning_time": "time estimate",
                    "learning_difficulty": "easy|moderate|challenging",
                    "resources": ["suggested learning resources"]
                }}
            ],
            "gap_score": 0-100,
            "readiness_level": "ready|needs_preparation|significant_gap"
        }}
    ],
    "overall_readiness": "assessment of overall career readiness"
}}"""),
            HumanMessage(content="Analyze skills gaps for career readiness.")
        ])
        
        response = await llm.ainvoke(prompt.format_messages(
            current_skills=json.dumps(skills_analysis, indent=2),
            career_matches=json.dumps(career_matches, indent=2)
        ))
        
        try:
            parser = JsonOutputParser()
            skills_gaps = parser.parse(response.content)
            state["skills_gaps"] = skills_gaps
        except Exception as e:
            state["skills_gaps"] = {"error": "Failed to analyze skills gaps"}
        
        return state
    
    async def generate_recommendations(self, state: CareerAssessmentState) -> CareerAssessmentState:
        """Generate comprehensive career recommendations and next steps."""
        career_matches = state.get("career_matches", [])
        skills_gaps = state.get("skills_gaps", {})
        user_background = state.get("user_background", {})
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""Generate comprehensive, actionable career recommendations for the Indian student.

Create personalized recommendations that include:
1. Top career path recommendations with reasoning
2. Immediate next steps (within 6 months)
3. Medium-term goals (6 months to 2 years)
4. Long-term career vision (2-5 years)
5. Specific skill development plan
6. Educational pathways and certifications
7. Networking and industry exposure suggestions
8. Resources for continuous learning

Consider:
- Indian job market dynamics
- Educational system compatibility
- Family and cultural considerations
- Financial aspects and ROI
- Geographic opportunities

Career Analysis:
- Career Matches: {career_matches}
- Skills Gaps: {skills_gaps}
- User Background: {user_background}

Return comprehensive JSON recommendations:
{{
    "primary_recommendation": {{
        "career_path": "recommended career",
        "reasoning": "detailed reasoning",
        "action_plan": {{
            "immediate_steps": ["0-6 months actions"],
            "medium_term_goals": ["6 months - 2 years"],
            "long_term_vision": ["2-5 years goals"]
        }},
        "skill_development_plan": [
            {{
                "skill": "skill name",
                "current_level": "current proficiency",
                "target_level": "target proficiency", 
                "timeline": "learning timeline",
                "resources": ["specific resources"],
                "milestones": ["learning milestones"]
            }}
        ],
        "educational_pathways": ["courses, certifications, degrees"],
        "industry_exposure": ["networking, internships, projects"],
        "success_metrics": ["how to measure progress"]
    }},
    "alternative_paths": [
        {{
            "career_path": "alternative career",
            "key_differences": "how it differs from primary",
            "transition_strategy": "how to pivot if needed"
        }}
    ],
    "resources": {{
        "online_courses": ["specific course recommendations"],
        "books": ["relevant books"],
        "websites": ["useful websites"],
        "communities": ["professional communities"],
        "certifications": ["valuable certifications"]
    }},
    "timeline_summary": {{
        "3_months": "key milestones",
        "6_months": "key milestones", 
        "1_year": "key milestones",
        "2_years": "key milestones"
    }}
}}"""),
            HumanMessage(content="Generate comprehensive career recommendations.")
        ])
        
        response = await llm.ainvoke(prompt.format_messages(
            career_matches=json.dumps(career_matches, indent=2),
            skills_gaps=json.dumps(skills_gaps, indent=2),
            user_background=json.dumps(user_background, indent=2)
        ))
        
        try:
            parser = JsonOutputParser()
            recommendations = parser.parse(response.content)
            state["recommendations"] = recommendations
        except Exception as e:
            state["recommendations"] = {"error": "Failed to generate recommendations"}
        
        return state
    
    async def complete_assessment(self, state: CareerAssessmentState) -> CareerAssessmentState:
        """Complete the assessment and prepare final summary."""
        state["status"] = "completed"
        state["completed_at"] = datetime.utcnow().isoformat()
        
        # Calculate overall score
        skills_score = state.get("skills_score", 0.0)
        aptitude_score = state.get("aptitude_score", 0.0)
        interest_score = state.get("interest_score", 0.0)
        
        state["overall_score"] = (skills_score + aptitude_score + interest_score) / 3
        
        # Add completion message
        completion_msg = {
            "role": "assistant",
            "content": "Congratulations! Your career assessment is complete. I've analyzed your skills, interests, and aptitude to provide personalized career recommendations. You can now explore your recommended career paths and start your journey towards your ideal career!",
            "timestamp": datetime.utcnow().isoformat()
        }
        state["chat_history"].append(completion_msg)
        
        return state
    
    def _get_fallback_questions(self, assessment_type: str) -> List[Dict[str, Any]]:
        """Provide fallback questions if AI generation fails."""
        fallback_questions = [
            {
                "id": "q1",
                "category": "technical",
                "question": "Which of the following technical areas interests you most?",
                "type": "multiple_choice",
                "options": [
                    {"value": "programming", "label": "Programming & Software Development"},
                    {"value": "data_analysis", "label": "Data Analysis & Analytics"},
                    {"value": "design", "label": "Design & User Experience"},
                    {"value": "marketing", "label": "Digital Marketing"},
                    {"value": "other", "label": "Other"}
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
            }
        ]
        return fallback_questions

# Create workflow instance
career_workflow = CareerAssessmentWorkflow()
