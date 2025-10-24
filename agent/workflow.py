# agent/workflow.py
from langgraph.graph import END, StateGraph, START
from agent.state import GraphState
from agent.nodes import AgentNodes


def build_workflow(node_handler: AgentNodes):
    """LangGraph 워크플로우를 빌드하고 컴파일합니다."""
    workflow = StateGraph(GraphState)

    # Define the nodes
    workflow.add_node("retrieve", node_handler.retrieve)
    workflow.add_node("grade_documents", node_handler.grade_documents)
    workflow.add_node("generate", node_handler.generate)
    workflow.add_node("search_docs", node_handler.search_docs)
    workflow.add_node("query_rewrite", node_handler.query_rewrite)

    # Build graph (CRAG 흐름 구현)
    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "grade_documents")

    # 조건부 엣지 설정
    workflow.add_conditional_edges(
        "grade_documents",
        AgentNodes.decide_to_generate,  # Static method 사용
        {
            "query_rewrite": "query_rewrite",  # 웹 검색 필요 시
            "generate": "generate",  # 바로 생성 시
        },
    )

    # 웹 검색 경로
    workflow.add_edge("query_rewrite", "search_docs")
    workflow.add_edge("search_docs", "generate")  # 웹 검색 후 생성 단계로 이동

    workflow.add_edge("generate", END)

    # Compile
    app = workflow.compile()
    return app
