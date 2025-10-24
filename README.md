### README.md


# LangGraph CRAG Agent with Upstage & SerpAPI

이 프로젝트는 LangGraph를 사용하여 Corrective Retrieval Augmented Generation (CRAG) 에이전트 시스템을 구현한 예제입니다. Upstage의 Solar 모델과 Document Parser, Embedding을 활용하며, SerpAPI를 통한 실시간 웹 검색 기능을 통합하여 RAG 파이프라인의 정확성과 최신성을 고도화합니다.


## 주요 특징

- **Corrective RAG (CRAG)**: 검색된 문서의 관련성을 평가(Grade)하고, 관련성이 낮다고 판단되면 질문을 재작성(Re-write)하여 웹 검색을 수행하는 고도화된 RAG 워크플로우를 구현합니다.
- **LangGraph Implementation**: 복잡한 에이전트의 흐름을 상태 머신(State Machine) 기반의 그래프로 정의하여 직관적이고 유연하게 제어합니다.
- **Upstage Integration**: Upstage의 강력한 LLM(Solar), 고품질 임베딩 모델, 그리고 HTML 기반 문서 파서를 활용합니다.
- **Real-time Web Search**: SerpAPI를 연동하여 최신 정보를 실시간으로 수집하고 활용합니다.
- **Modular Architecture**: 관심사 분리(Separation of Concerns) 원칙에 따라 코드를 모듈화하여 유지보수성과 확장성을 높였습니다.

## System Architecture

이 프로젝트는 CRAG 논문의 핵심 개념을 LangGraph를 사용하여 구현합니다.

![CRAG Workflow](https://github.com/user-attachments/assets/532a17d2-bc80-46e6-9b24-05de5fb3894b)

1.  **Retrieve**: 사용자의 질문과 관련된 문서를 내부 Vector DB에서 검색합니다.
2.  **Grade**: 검색된 각 문서가 질문과 실제로 관련이 있는지 LLM을 사용하여 평가합니다.
3.  **Decision Point**: 평가 결과를 바탕으로 다음 단계를 결정합니다.
    - **Generate (Relevant)**: 문서들이 충분히 관련 있다면, 해당 문서들을 기반으로 답변을 생성합니다.
    - **Query Rewrite (Not Relevant)**: 관련 없는 문서가 포함되어 있다면, LLM을 사용하여 질문을 웹 검색에 최적화된 형태로 재작성합니다.
4.  **Web Search**: 재작성된 질문을 사용하여 SerpAPI로 외부 웹 검색을 수행합니다.
5.  **Generate (Web)**: 웹 검색 결과를 기반으로 답변을 생성합니다.

## Module Architecture

```

langgraph\_crag\_agent/
│
├── agent/               \# LangGraph 에이전트 핵심 로직
│   ├── state.py         \# 그래프 상태(GraphState) 정의. 에이전트의 메모리 역할.
│   ├── nodes.py         \# 그래프의 각 노드(Node) 로직 구현 (검색, 평가, 생성 등). 실제 작업을 수행.
│   └── workflow.py      \# 노드 간의 흐름(Edges)을 정의하고 그래프를 컴파일하여 실행 가능한 앱으로 만듦.
│
├── core/                \# 시스템 핵심 구성 요소 (LLM, 프롬프트, 설정)
│   ├── config.py        \# 환경 설정 및 API 키 관리.
│   ├── models.py        \# 데이터 모델(Pydantic) 정의 및 LLM(ChatUpstage) 초기화.
│   ├── prompts.py       \# 모든 LLM 프롬프트 템플릿을 중앙 집중식으로 관리.
│   └── chains.py        \# prompts와 models을 결합하여 실행 가능한 LangChain 체인(Grader, Generator 등) 생성.
│
├── data/
│   └── ingestion.py     \# 데이터 파이프라인 담당 (문서 다운로드, Upstage Parser, 임베딩, Chroma DB 초기화).
│
├── tools/
│   └── web\_search.py    \# 외부 도구 (SerpAPI 웹 검색 및 UnstructuredURLLoader) 로직 캡슐화.
│
├── main.py              \# 애플리케이션 진입점. 모든 모듈을 오케스트레이션하고 에이전트를 실행.
└── requirements.txt     \# 필요 패키지 목록.

````

### 모듈을 왜 이렇게 디자인했을까?

기존의 단일 노트북 파일을 위와 같이 모듈화한 이유는 다음과 같습니다.

1.  **관심사 분리 (Separation of Concerns)**:
    - 데이터 처리(`data/`), LLM 로직(`core/`), 에이전트 흐름 제어(`agent/`), 외부 도구(`tools/`)를 분리했습니다. 이를 통해 각 모듈이 하나의 책임에만 집중하도록 하여 코드의 복잡성을 줄였습니다.
2.  **유지보수성 향상 (Maintainability)**:
    - 프롬프트를 변경하고 싶다면 `core/prompts.py`만 수정하면 됩니다. 데이터 소스를 바꾸려면 `data/ingestion.py`를 수정하면 됩니다. 변경의 영향 범위가 명확해져 버그 수정과 기능 추가가 용이합니다.
3.  **재사용성 및 확장성 (Reusability & Scalability)**:
    - `tools/web_search.py`는 다른 프로젝트에서도 쉽게 재사용할 수 있습니다. 새로운 도구(예: 계산기)를 추가하고 싶다면 `tools/` 디렉토리에 새 모듈을 만들고 `agent/nodes.py`에서 이를 활용하도록 쉽게 확장할 수 있습니다.
4.  **테스트 용이성 (Testability)**:
    - `agent/nodes.py`에서는 의존성 주입(Dependency Injection) 패턴을 사용하여 외부 컴포넌트(Retriever, Chains)를 주입받습니다. 이를 통해 각 노드의 로직을 독립적으로 테스트(Unit Test)하기 쉬운 구조가 되었습니다.

## 🚀 시작하기

### Prerequisites

- Python 3.10 이상
- Upstage API Key ([Upstage Console](https://console.upstage.ai/))
- SerpAPI API Key ([SerpAPI](https://serpapi.com/))

### Installation

1. 리포지토리를 클론합니다:

   ```bash
   git clone [https://github.com/YOUR_USERNAME/langgraph-crag-agent.git](https://github.com/YOUR_USERNAME/langgraph-crag-agent.git)
   cd langgraph-crag-agent
````

2.  가상 환경을 설정하고 필요한 파이썬 패키지를 설치합니다:

    ```bash
    conda create -n langgraph-crag-agent python=3.12
    pip install -r requirements.txt
    ```

### Usage

스크립트를 실행하면 Upstage와 SerpAPI 키를 입력하라는 프롬프트가 나타납니다.

```bash
python main.py
```

키를 입력하면, 에이전트는 사전 정의된 예제 질문("How does the o1 model perform in jailbreak evaluations compared to GPT-4o...")에 대해 CRAG 워크플로우를 실행하고 결과를 출력합니다.

**(참고)** 매번 키를 입력하는 대신, 환경 변수로 미리 설정해 두거나 .env 파일로 관리할 수 있습니다.

```bash
export UPSTAGE_API_KEY='YOUR_UPSTAGE_KEY'
export SERPAPI_API_KEY='YOUR_SERPAPI_KEY'
python main.py
```

**실행 과정 예시:**

```
--- Initializing Environment ---
Enter your Upstage API key: [입력]
Enter your SERPAPI API key: [입력]
...
--- Initializing Data Pipeline ---
Downloading document...
Loading and parsing document... (This may take approx. 50 seconds)
...
--- Starting Agent Execution ---
Question: How does the o1 model perform in jailbreak evaluations...

<<<RETRIEVE>>>

<<<CHECK DOCUMENT RELEVANCE TO QUESTION>>>
---GRADE: DOCUMENT RELEVANT---
---GRADE: DOCUMENT NOT RELEVANT---
---GRADE: DOCUMENT RELEVANT---

<<<ASSESS GRADED DOCUMENTS>>>
---DECISION: DOCUMENTS ARE NOT SUFFICIENTLY RELEVANT, TRANSFORM QUERY & WEB SEARCH---

<<<TRANSFORM QUERY>>>
Rewritten Question: o1 model vs GPT-4o jailbreak evaluation and adversarial prompt resistance measures

<<<WEB SEARCH>>>
--- WEB SEARCHING: o1 model vs GPT-4o jailbreak evaluation... ---
...

<<<GENERATE>>>

=================== Final Answer ===================
The o1 model demonstrates significantly improved resistance to jailbreaks compared to GPT-4o...
```

## 주의사항

  - SerpAPI는 무료 플랜에서 월별 검색 횟수 제한(현재 월 250회)이 있습니다.
  - 노트북 코드에서 언급된 바와 같이, LLM의 출력 포매팅 이슈로 인해 `Grade` 단계에서 드물게 오류가 발생할 수 있습니다. `agent/nodes.py`에 기본적인 예외 처리가 포함되어 있으나, 더 강력한 출력 파싱 로직이 필요할 수 있습니다.