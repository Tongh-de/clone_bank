"""
AI客服控制器
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.auth import get_current_user
from core.database import get_db
from services.ai_customer_service import chat_with_qwen
from services.ai_service import chat, generate_image, get_available_models
from schemas import AIChatRequest, AIChatResponse, ImageGenerateRequest, ImageGenerateResponse, ModelListResponse
from core.logger import ai_logger, log_ai_request

router = APIRouter(prefix="/api/ai", tags=["AI客服"])


class ChatRequest(BaseModel):
    message: str


class ChatHistoryRequest(BaseModel):
    messages: list


@router.post("/chat")
async def chat(request: ChatRequest, http_request: Request, db: Session = Depends(get_db)):
    """AI客服对话"""
    user = await get_current_user(http_request, db)
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        messages = [{"role": "user", "content": request.message}]
        response = await chat_with_qwen(messages)
        log_ai_request(user.username, request.message, "客服对话", True)
        return {"response": response}
    except Exception as e:
        log_ai_request(user.username, request.message, "客服对话", False)
        ai_logger.error(f"AI客服错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI服务错误: {str(e)}")


@router.post("/chat/stream")
async def chat_stream(request: ChatHistoryRequest, http_request: Request, db: Session = Depends(get_db)):
    """AI客服对话（支持对话历史）"""
    user = await get_current_user(http_request, db)
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        messages = request.messages if isinstance(request.messages, list) else []
        response = await chat_with_qwen(messages)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI服务错误: {str(e)}")


@router.post("/chat/advanced", response_model=AIChatResponse)
async def chat_advanced(
    request: AIChatRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """高级AI对话接口"""
    user = await get_current_user(http_request, db)
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    
    try:
        result = await chat(
            messages=request.messages,
            model=request.model,
            method=request.method
        )
        log_ai_request(user.username, str(request.messages), f"高级对话({request.model})", result.get("success", False))
        return AIChatResponse(**result)
    except Exception as e:
        ai_logger.error(f"高级AI对话错误: {str(e)}")
        return AIChatResponse(
            success=False,
            response="",
            model=request.model,
            method=request.method,
            error=str(e)
        )


@router.get("/models", response_model=ModelListResponse)
async def list_models(http_request: Request, db: Session = Depends(get_db)):
    """获取可用的AI模型列表"""
    user = await get_current_user(http_request, db)
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    
    return ModelListResponse(**get_available_models())


@router.post("/image/generate", response_model=ImageGenerateResponse)
async def create_image(
    request: ImageGenerateRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """文本生成图片接口"""
    user = await get_current_user(http_request, db)
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    
    if not request.prompt or len(request.prompt.strip()) == 0:
        return ImageGenerateResponse(
            success=False,
            prompt="",
            model=request.model,
            error="图片描述不能为空"
        )
    
    try:
        result = await generate_image(
            prompt=request.prompt,
            model=request.model,
            size=request.size
        )
        log_ai_request(user.username, f"图片生成: {request.prompt[:30]}...", "text2image", result.get("success", False))
        return ImageGenerateResponse(**result)
    except Exception as e:
        ai_logger.error(f"图片生成错误: {str(e)}")
        return ImageGenerateResponse(
            success=False,
            prompt=request.prompt,
            model=request.model,
            error=str(e)
        )
