# core/chains.py
from langchain_core.output_parsers import StrOutputParser
from core.models import get_llm, GradeDocuments
from core.prompts import GRADE_PROMPT, RAG_PROMPT, REWRITE_PROMPT


def get_retrieval_grader():
    """Creates the LLM chain for grading document relevance."""
    llm = get_llm()
    # Structured output을 활용하여 안정적인 결과 도출 (Pydantic 모델 사용)
    structured_llm_grader = llm.with_structured_output(GradeDocuments)
    return GRADE_PROMPT | structured_llm_grader


def get_rag_chain():
    """Creates the LLM chain for generating answers."""
    llm = get_llm()
    return RAG_PROMPT | llm | StrOutputParser()


def get_question_rewriter():
    """Creates the LLM chain for rewriting questions for web search."""
    llm = get_llm()
    return REWRITE_PROMPT | llm | StrOutputParser()
