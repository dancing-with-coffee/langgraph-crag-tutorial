# main.py
from core.config import setup_environment
from data.ingestion import download_document, initialize_retriever
from core.chains import get_retrieval_grader, get_rag_chain, get_question_rewriter
from agent.nodes import AgentNodes
from agent.workflow import build_workflow
from langgraph.graph import END

# 문서 정보 설정
DOCUMENT_URL = "https://cdn.openai.com/o1-system-card-20241205.pdf"
SAVE_PATH = "openai-o1-system-card.pdf"


def main():
    # 1. 환경 설정 (API 키)
    print("--- Initializing Environment ---")
    if not setup_environment():
        print("Failed to setup environment. Exiting.")
        return

    # 2. 데이터 준비 (문서 다운로드 및 Retriever 생성)
    print("\n--- Initializing Data Pipeline ---")
    try:
        download_document(DOCUMENT_URL, SAVE_PATH)
        retriever = initialize_retriever(SAVE_PATH)
    except Exception as e:
        print(f"Failed to setup data pipeline: {e}. Exiting.")
        return

    # 3. 체인 초기화
    print("\n--- Initializing LLM Chains ---")
    retrieval_grader = get_retrieval_grader()
    rag_chain = get_rag_chain()
    question_rewriter = get_question_rewriter()

    # 4. 그래프 노드 핸들러 초기화 (컴포넌트 주입)
    node_handler = AgentNodes(retriever, retrieval_grader, rag_chain, question_rewriter)

    # 5. 워크플로우 빌드
    print("\n--- Building Workflow ---")
    app = build_workflow(node_handler)

    # 6. 실행
    questions = [
        "What distinguishes the o1 model’s reasoning capabilities from previous OpenAI models, and how does 'chain-of-thought' improve its performance?",
        "How does the o1 model perform in jailbreak evaluations compared to GPT-4o, and what measures have been implemented to resist adversarial prompts?",
    ]

    # 테스트 질문 선택 (노트북 예제 참고)
    user_question = questions[1]
    print(f"\n--- Starting Agent Execution ---\nQuestion: {user_question}\n")

    inputs = {"user_question": user_question}
    final_result = None
    try:
        # 스트림을 사용하여 실행 과정 출력
        for output in app.stream(inputs):
            # 노드 실행 상태 출력 (디버깅용)
            # for key, value in output.items():
            #     print(f"Node '{key}' executed")
            # print("\n---\n")

            # LangGraph 스트림의 마지막 출력은 END 노드의 결과입니다.
            if END in output:
                final_result = output[END]

    except Exception as e:
        print(f"\nAn error occurred during graph execution: {e}")
        print(
            "This might be due to LLM output formatting issues. Check the trace above."
        )
        return

    # Final generation
    if final_result and "generation" in final_result:
        print("\n=================== Final Answer ===================")
        print(final_result["generation"])
    else:
        print("\n--- Execution finished without generating a final answer. ---")


if __name__ == "__main__":
    main()
