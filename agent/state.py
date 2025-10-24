# agent/state.py
from typing import List
from typing_extensions import TypedDict


class GraphState(TypedDict):
    """그래프의 state로 들어갈 항목 정의"""

    user_question: str  # 사용자 질문 (Re-write 시 업데이트 될 수 있음)
    documents: List[str]  # 검색된 문서들
    web_search: str  # 웹 검색 필요 여부 플래그 ("Yes" or "No")
    generation: str  # 최종 생성된 답변
