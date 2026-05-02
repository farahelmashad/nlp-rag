from pydantic import BaseModel
from typing import List

class ChatMessage(BaseModel):
    role: str
    content: str

class QueryRequest(BaseModel):
    question: str
    chat_history: List[ChatMessage] = []

class QueryResponse(BaseModel):
    answer: str
    sources: list