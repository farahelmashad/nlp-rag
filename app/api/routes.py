from fastapi import APIRouter
from app.models.schemas import QueryRequest, QueryResponse
from app.services.rag_service import get_answer

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
def query_rag(request: QueryRequest):
    history = [msg.dict() for msg in request.chat_history]
    answer = get_answer(request.question, history)
    return answer