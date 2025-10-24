# data/ingestion.py
import os
import requests
from langchain_upstage import UpstageDocumentParseLoader, UpstageEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma


def download_document(url, save_path):
    """Downloads a document from the given URL using requests."""
    if not os.path.exists(save_path):
        print(f"Downloading document from {url}...")
        try:
            # !wget 대신 requests를 사용하여 파이썬 애플리케이션 내에서 처리
            response = requests.get(url)
            response.raise_for_status()
            with open(save_path, "wb") as f:
                f.write(response.content)
            print(f"Document saved to {save_path}")
        except requests.RequestException as e:
            print(f"Error downloading document: {e}")
            raise
    else:
        print(f"Document already exists at {save_path}")


def initialize_retriever(file_path):
    """Loads, splits the document, creates a vector store, and returns a retriever."""
    print(
        f"Loading and parsing document: {file_path} (This may take approx. 50 seconds)..."
    )
    # UpstageDocumentParseLoader 활용
    parser = UpstageDocumentParseLoader(
        file_path, output_format="html", coordinates=False
    )
    docs = parser.load()

    print("Splitting document...")
    # 노트북 설정값 사용 (chunk_size=200, chunk_overlap=50)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
    splits = text_splitter.split_documents(docs)
    print(f"Total splits created: {len(splits)}")

    print("Creating vector store and retriever...")
    # UpstageEmbeddings 활용
    embedding_model = UpstageEmbeddings(model="embedding-query")
    vectorstore = Chroma.from_documents(documents=splits, embedding=embedding_model)
    # MMR 방식으로 Retriever 설정 (k=3)
    retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 3})
    return retriever
