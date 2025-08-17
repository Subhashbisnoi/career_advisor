from dotenv import load_dotenv
import os
load_dotenv()

from answer import answer_1st_question, answer_2nd_question, answer_3rd_question
from feedback import feedback_generator
from roadmap import generate_roadmap
from generator import generate_question
from langchain_openai import ChatOpenAI
from models import InterviewState, InterviewQuestions, StructuredEvaluator, FeedbackItem
from common import generator_llm, feedback_llm

from langgraph.graph import StateGraph, START, END
from typing import Literal, Annotated
from langchain_core.messages import SystemMessage, HumanMessage
import operator
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_BASE_URL"] = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
generator_llm = ChatOpenAI(model="gpt-4o-mini")
feedback_llm = ChatOpenAI(model="gpt-4o-mini")
# Initialize structured generators
structured_generator = generator_llm.with_structured_output(InterviewQuestions)
structured_evaluator = feedback_llm.with_structured_output(StructuredEvaluator)

import pdfplumber

def extract_resume_text(resume_path):
    with pdfplumber.open(resume_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

graph=StateGraph(InterviewState)

graph.add_node("generate_question",generate_question)
graph.add_node("answer_1st_question", answer_1st_question)
graph.add_node("answer_2nd_question", answer_2nd_question)
graph.add_node("answer_3rd_question", answer_3rd_question)
graph.add_node("feedback_generator", feedback_generator)
graph.add_node("generate_roadmap", generate_roadmap)

graph.add_edge(START, "generate_question")
graph.add_edge("generate_question", "answer_1st_question")
graph.add_edge("answer_1st_question", "answer_2nd_question")
graph.add_edge("answer_2nd_question", "answer_3rd_question")
graph.add_edge("answer_3rd_question",'feedback_generator')
graph.add_edge("feedback_generator", "generate_roadmap")
graph.add_edge("generate_roadmap", END)


workflow = graph.compile()