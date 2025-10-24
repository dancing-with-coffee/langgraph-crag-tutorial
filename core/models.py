# core/models.py
from pydantic import BaseModel, Field
from langchain_upstage import ChatUpstage

# --- Data Models ---


class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )


# --- LLM Initialization ---


def get_llm(temperature=0):
    """Returns an instance of the ChatUpstage LLM."""
    # RAG 및 에이전트 시스템에서는 temperature를 낮게 설정하는 것이 일반적입니다.
    return ChatUpstage(temperature=temperature)
