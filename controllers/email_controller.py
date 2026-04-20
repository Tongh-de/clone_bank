"""
邮件控制器
"""
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from core.database import get_db
from core.auth import require_login
from services.email_service import send_email
from services.ai_service import generate_email_content
from schemas import ApiResponse

router = APIRouter(prefix="/api/email", tags=["邮件"])


class EmailRequest(BaseModel):
    to_email: str = Field(..., description="收件人邮箱")
    subject: str = Field(default="来自银行系统的邮件", description="邮件主题")
    content: str = Field(..., description="邮件内容")


@router.post("/send")
async def send_mail(
    request: Request,
    email_data: EmailRequest,
    db: Session = Depends(get_db)
):
    """发送邮件"""
    user = await require_login(request, db)

    result = send_email(
        to_email=email_data.to_email,
        subject=email_data.subject,
        content=email_data.content
    )

    if result["success"]:
        return ApiResponse.success(data=result, message="邮件发送成功")
    else:
        return ApiResponse.error(message=result["message"])


class GenerateEmailRequest(BaseModel):
    purpose: str = Field(..., description="邮件用途")
    customer_name: str = Field(default=None, description="客户姓名（可选）")
    extra_info: str = Field(default=None, description="额外信息（可选）")


@router.post("/generate")
async def ai_generate_email(
    request: Request,
    email_req: GenerateEmailRequest,
    db: Session = Depends(get_db)
):
    """AI生成邮件内容"""
    user = await require_login(request, db)

    result = await generate_email_content(
        purpose=email_req.purpose,
        customer_name=email_req.customer_name,
        extra_info=email_req.extra_info
    )

    if result["success"]:
        return ApiResponse.success(data={
            "subject": result["subject"],
            "content": result["content"]
        }, message="邮件内容生成成功")
    else:
        return ApiResponse.error(message=result.get("error", "生成失败"))
