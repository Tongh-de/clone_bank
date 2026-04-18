"""
AI服务模块 - 支持多种调用方式
"""
import httpx
import asyncio
from core import config

# API 配置
DASHSCOPE_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
DASHSCOPE_IMAGE_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"


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


async def generate_image(prompt: str, model: str = "wanx-v1", size: str = "1024*1024", timeout: int = 120) -> dict:
    """
    使用通义万相生成图片
    """
    result = {
        "success": False,
        "prompt": prompt,
        "model": model
    }
    
    model_names = [model, "wanx-plus", "wanx-v1.2-text2img", "text2image"]
    
    for try_model in model_names:
        if try_model != model and model not in model_names[1:]:
            continue
            
        try:
            headers = {
                "Authorization": f"Bearer {config.DASHSCOPE_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": try_model,
                "input": {"prompt": prompt},
                "parameters": {"size": size, "n": 1}
            }
            
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(DASHSCOPE_IMAGE_URL, headers=headers, json=payload)
                data = response.json()
                
                if data.get("code"):
                    error_msg = data.get("message", "未知错误")
                    if "AccessDenied" in error_msg or "not support" in error_msg:
                        continue
                    result["error"] = error_msg
                    return result
                
                task_id = None
                if "output" in data:
                    task_id = data["output"].get("task_id")
                if not task_id:
                    task_id = data.get("task_id")
                if not task_id:
                    task_id = data.get("request_id")
                
                if task_id:
                    result["task_id"] = task_id
                    result["model"] = try_model
                    
                    status_url = "https://dashscope.aliyuncs.com/api/v1/tasks/" + str(task_id)
                    
                    for _ in range(timeout // 5):
                        await asyncio.sleep(5)
                        
                        status_response = await client.get(status_url, headers=headers)
                        status_data = status_response.json()
                        
                        task_status = status_data.get("status", "")
                        
                        if task_status == "succeeded":
                            result["image_url"] = status_data.get("output", {}).get("image_url")
                            result["success"] = True
                            return result
                        elif task_status == "failed":
                            result["error"] = status_data.get("output", {}).get("message", "图片生成失败")
                            return result
                    
                    result["error"] = "图片生成超时，请稍后重试"
                    return result
                
                if "data" in data:
                    image_data = data["data"]
                    if "image_url" in image_data:
                        result["image_url"] = image_data["image_url"]
                        result["success"] = True
                        return result
                    
        except Exception as e:
            continue
    
    result["error"] = "您的API密钥可能没有开通'通义万相'图片生成功能。"
    return result


def get_available_models() -> dict:
    """获取可用的模型列表"""
    return {
        "chat_models": {
            "qwen-plus": "通义千问Plus - 推荐使用，中文能力强",
            "qwen-turbo": "通义千问Turbo - 响应快速",
            "qwen-max": "通义千问Max - 能力最强"
        },
        "image_models": {
            "wanx-v1": "通义万相 - 文本生成图片"
        }
    }
