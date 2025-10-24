# core/prompts.py
from langchain_core.prompts import ChatPromptTemplate

# 1. Grader Prompt (문서 관련성 평가)
GRADER_SYSTEM = """You are a grader assessing relevance of a retrieved document to a user question. \n
    If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant. \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""

GRADER_USER = """<<<Retrieved document>>>
{document}

<<<User question>>>
{question}

<<<Output Format>>>
`Score: <yes or no>`
"""
GRADE_PROMPT = ChatPromptTemplate.from_messages(
    [("system", GRADER_SYSTEM), ("human", GRADER_USER)]
)

# 2. Generation Prompt (RAG 답변 생성)
GENERATION_SYSTEM = """
Answer the question based on context.
"""
GENERATION_USER = """
Question: {question}
Context: {context}

<<<Output Format>>>
`Answer: <Answer based on the document.>`
"""
RAG_PROMPT = ChatPromptTemplate.from_messages(
    [("system", GENERATION_SYSTEM), ("human", GENERATION_USER)]
)

# 3. Re-writer Prompt (질문 재작성)
REWRITER_SYSTEM = """
You a question re-writer that converts an input question to a better version that is optimized
for web search. Look at the input and try to reason about the underlying semantic intent / meaning."""

REWRITER_USER = """
Here is the initial question: {question}
Formulate an improved question.

<<<Output Format>>>
`new question: <new question that is optimized for the web search>`
"""
REWRITE_PROMPT = ChatPromptTemplate.from_messages(
    [("system", REWRITER_SYSTEM), ("human", REWRITER_USER)]
)
