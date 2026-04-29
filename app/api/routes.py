from fastapi import APIRouter
from app.models.schemas import QueryRequest, QueryResponse
from app.services.rag_service import get_answer

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
def query_rag(request: QueryRequest):
    answer = get_answer(request.question)
    return answer