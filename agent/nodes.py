# agent/nodes.py
from agent.state import GraphState
from tools.web_search import search_and_load


class AgentNodes:
    # 의존성 주입 (Dependency Injection) 패턴 사용
    def __init__(self, retriever, retrieval_grader, rag_chain, question_rewriter):
        self.retriever = retriever
        self.retrieval_grader = retrieval_grader
        self.rag_chain = rag_chain
        self.question_rewriter = question_rewriter

    def _clean_output(self, output: str) -> str:
        """LLM 출력에서 접두사('Answer:', 'new question:')를 제거합니다. (노트북 로직 반영)"""
        if ":" in output:
            parts = output.split(":", 1)
            return parts[1].strip() if len(parts) > 1 else parts[0].strip()
        return output.strip()

    # --- Nodes ---

    def retrieve(self, state: GraphState) -> dict:
        """(2) Retrieve: 질문에 관련된 문서를 검색합니다."""
        print("<<<RETRIEVE>>>")
        user_question = state["user_question"]
        documents = self.retriever.get_relevant_documents(user_question)
        documents = [doc.page_content for doc in documents]
        # State 업데이트 시 필요한 키만 반환합니다.
        return {"documents": documents}

    def grade_documents(self, state: GraphState) -> dict:
        """(3) Grade: 검색된 문서가 적절한 지 판단합니다."""
        print("\n<<<CHECK DOCUMENT RELEVANCE TO QUESTION>>>")
        user_question = state["user_question"]
        docs = state["documents"]

        filtered_docs = []
        need_web_search = "No"
        for doc in docs:
            # 노트북에서 언급된 LLM 포매팅 이슈 대응을 위한 예외 처리
            try:
                score = self.retrieval_grader.invoke(
                    {"question": user_question, "document": doc}
                )
                grade = score.binary_score.lower()
            except Exception as e:
                print(
                    f"--- GRADE ERROR (Formatting issue?): {e}. Assuming not relevant. ---"
                )
                grade = "no"

            if grade == "yes":
                print("---GRADE: DOCUMENT RELEVANT---")
                filtered_docs.append(doc)
            else:
                print("---GRADE: DOCUMENT NOT RELEVANT---")
                # 하나라도 관련 없으면 웹 검색 고려 (노트북 로직 반영)
                need_web_search = "Yes"

        return {"documents": filtered_docs, "web_search": need_web_search}

    def generate(self, state: GraphState) -> dict:
        """(4/7) Generate: 질문과 문서를 기반으로 답변을 생성합니다."""
        print("\n<<<GENERATE>>>")
        user_question = state["user_question"]
        documents = state["documents"]

        if not documents:
            # 문서가 비어있는 경우 (예: 웹 검색 실패)
            return {
                "generation": "I could not find relevant information to answer the question."
            }

        # RAG generation
        generation_raw = self.rag_chain.invoke(
            {"context": "\n\n".join(documents), "question": user_question}
        )
        generation = self._clean_output(generation_raw)

        return {"generation": generation}

    def query_rewrite(self, state: GraphState) -> dict:
        """(5) Re-Write: 적절하지 않을 경우, 질문을 재정의합니다."""
        print("\n<<<TRANSFORM QUERY>>>")
        user_question = state["user_question"]

        # Re-write question
        web_question_raw = self.question_rewriter.invoke({"question": user_question})
        web_question = self._clean_output(web_question_raw)

        # web_search에서 이슈가 되는 따옴표 제거 (노트북 로직 반영)
        web_question = web_question.strip('"')

        print(f"Rewritten Question: {web_question}")
        # 재정의된 질문을 state에 업데이트합니다.
        return {"user_question": web_question}

    def search_docs(self, state: GraphState) -> dict:
        """(6) Web Search: 재정의된 질문을 기반으로 Web Search를 수행합니다."""
        print("\n<<<WEB SEARCH>>>")
        user_question = state["user_question"]  # 재정의된 질문 사용

        # Web search 수행
        new_documents = search_and_load(user_question)

        # 검색된 문서로 state를 업데이트합니다.
        return {"documents": new_documents}

    # --- Conditional Edge ---

    @staticmethod
    def decide_to_generate(state: GraphState) -> str:
        """검색을 종료하고 생성할 지 혹은 웹 검색을 수행할 지 결정합니다."""
        print("\n<<<ASSESS GRADED DOCUMENTS>>>")
        need_web_search = state["web_search"]

        if need_web_search == "Yes":
            print(
                "---DECISION: DOCUMENTS ARE NOT SUFFICIENTLY RELEVANT, TRANSFORM QUERY & WEB SEARCH---"
            )
            return "query_rewrite"
        else:
            print("---DECISION: GENERATE---")
            return "generate"
