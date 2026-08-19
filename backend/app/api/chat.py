from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import ChatRequest, ChatResponse
from ..agent.agent import run_agent

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    return run_agent(db, req.session_id, req.message)
