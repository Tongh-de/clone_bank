"""
AI客服控制器
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from auth import get_current_user
from sqlalchemy.orm import Session
from database import get_db
from ai_customer_service import chat_with_qwen
from schemas import ChatMessage

router = APIRouter(prefix="/api/ai", tags=["AI客服"])


class ChatRequest(BaseModel):
    message: str


class ChatHistoryRequest(BaseModel):
    messages: list[ChatMessage]


@router.post("/chat")
async def chat(request: ChatRequest, http_request: Request, db: Session = Depends(get_db)):
    """AI客服对话"""
    user = await get_current_user(http_request, db)
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        messages = [{"role": "user", "content": request.message}]
        response = await chat_with_qwen(messages)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI服务错误: {str(e)}")


@router.post("/chat/stream")
async def chat_stream(request: ChatHistoryRequest, http_request: Request, db: Session = Depends(get_db)):
    """AI客服对话（支持对话历史）"""
    user = await get_current_user(http_request, db)
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        response = await chat_with_qwen(messages)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI服务错误: {str(e)}")
