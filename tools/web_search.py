# tools/web_search.py
from serpapi import GoogleSearch
from langchain.document_loaders import UnstructuredURLLoader


def search_and_load(query: str, num_results: int = 2) -> list[str]:
    """Performs a web search using SerpAPI and loads the content of the results."""
    print(f"--- WEB SEARCHING: {query} ---")
    params = {"engine": "google", "q": query, "num": str(num_results)}

    try:
        # SerpAPI를 사용하여 검색 수행 (API 키는 config.py에서 설정됨)
        search = GoogleSearch(params)
        search_result = search.get_dict()
    except Exception as e:
        print(f"Web search failed: {e}")
        return []

    if "organic_results" not in search_result:
        print("No organic results found.")
        return []

    urls = [result["link"] for result in search_result["organic_results"]]

    print(f"Loading content from {len(urls)} URLs...")
    try:
        # UnstructuredURLLoader를 사용하여 URL 내용 로드
        loader = UnstructuredURLLoader(urls=urls)
        data = loader.load()
        documents = [d.page_content for d in data]
    except Exception as e:
        print(f"Failed to load URLs: {e}. Falling back to snippets if available.")
        # URL 로딩 실패 시 스니펫으로 대체 (안정성 강화)
        documents = [
            result.get("snippet", "")
            for result in search_result["organic_results"]
            if result.get("snippet")
        ]

    return documents
