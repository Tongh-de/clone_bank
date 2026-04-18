"""
AI服务模块 - 支持多种调用方式
"""
import httpx
from core import config

# API 配置
DASHSCOPE_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"


async def chat_with_openai_style(messages: list, model: str = "qwen-plus") -> str:
    """使用 OpenAI SDK 兼容方式调用通义千问"""
    try:
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(
            api_key=config.DASHSCOPE_API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except ImportError:
        return await chat_with_dashscope_direct(messages, model)


async def chat_with_dashscope_direct(messages: list, model: str = "qwen-plus") -> str:
    """直接使用 HTTP 请求调用通义千问 API"""
    headers = {
        "Authorization": f"Bearer {config.DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(DASHSCOPE_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]


async def chat(messages: list, model: str = "qwen-plus", method: str = "auto") -> dict:
    """
    统一对话接口
    """
    result = {
        "success": True,
        "response": "",
        "model": model,
        "method": method
    }
    
    try:
        if method == "openai":
            result["response"] = await chat_with_openai_style(messages, model)
            result["method"] = "openai"
        elif method == "dashscope":
            result["response"] = await chat_with_dashscope_direct(messages, model)
            result["method"] = "dashscope"
        else:
            try:
                result["response"] = await chat_with_openai_style(messages, model)
                result["method"] = "openai"
            except Exception:
                result["response"] = await chat_with_dashscope_direct(messages, model)
                result["method"] = "dashscope"
                
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        result["response"] = f"调用失败: {str(e)}"
    
    return result


def get_available_models() -> dict:
    """获取可用的模型列表"""
    return {
        "chat_models": {
            "qwen-plus": "通义千问Plus - 推荐使用，中文能力强",
            "qwen-turbo": "通义千问Turbo - 响应快速",
            "qwen-max": "通义千问Max - 能力最强"
        }
    }
