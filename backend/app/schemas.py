from typing import Any, Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ToolCallLog(BaseModel):
    name: str
    input: dict[str, Any]
    result: Any


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    tool_calls: list[ToolCallLog] = []


class RequirementOut(BaseModel):
    environment: str
    area_min: Optional[float] = None
    height_min: Optional[float] = None
    doors: Optional[int] = None
    extra: dict[str, Any] = {}

    class Config:
        from_attributes = True


class IngestRequest(BaseModel):
    source: str
    text: str
