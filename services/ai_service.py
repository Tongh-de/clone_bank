"""
AI服务 - Ollama通用接口
"""
import httpx
from core import config


async def chat(messages: list, model: str = None, method: str = "auto") -> dict:
    """
    通用AI对话接口

    Args:
        messages: 消息列表 [{"role": "user", "content": "..."}]
        model: 模型名称（可选）
        method: 调用方式 "ollama" | "dashscope" | "auto"

    Returns:
        dict: {"success": bool, "response": str, "model": str, "method": str, "error": str}
    """
    model = model or getattr(config, 'OLLAMA_MODEL', 'qwen:0.5b')
    method = method or "ollama"

    try:
        # 使用 Ollama API
        async with httpx.AsyncClient(timeout=60.0) as client:
            # qwen:0.5b 使用 /api/generate 接口
            if ":" in model or method == "ollama":
                prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
                response = await client.post(
                    "http://localhost:11434/api/generate",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                return {
                    "success": True,
                    "response": data.get("response", ""),
                    "model": model,
                    "method": "ollama"
                }
            else:
                # 备用 chat 接口
                payload = {
                    "model": model,
                    "messages": messages,
                    "stream": False
                }
                response = await client.post(
                    "http://localhost:11434/api/chat",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                return {
                    "success": True,
                    "response": data["message"]["content"],
                    "model": model,
                    "method": "ollama"
                }

    except httpx.ConnectError:
        return {
            "success": False,
            "response": "",
            "model": model,
            "method": "ollama",
            "error": "无法连接到Ollama服务，请确保Ollama已启动"
        }
    except httpx.TimeoutException:
        return {
            "success": False,
            "response": "",
            "model": model,
            "method": "ollama",
            "error": "AI服务响应超时"
        }
    except Exception as e:
        return {
            "success": False,
            "response": "",
            "model": model,
            "method": "ollama",
            "error": str(e)
        }


def get_available_models() -> dict:
    """
    获取可用的AI模型列表

    Returns:
        dict: {"chat_models": {...}}
    """
    return {
        "chat_models": {
            "ollama": {
                "default": getattr(config, 'OLLAMA_MODEL', 'qwen:0.5b'),
                "description": "本地Ollama模型"
            }
        }
    }


async def generate_content(prompt: str, system_prompt: str = None) -> dict:
    """
    使用Ollama生成内容

    Args:
        prompt: 用户提示词
        system_prompt: 系统提示词（可选）

    Returns:
        dict: {"success": bool, "content": str, "error": str}
    """
    model = getattr(config, 'OLLAMA_MODEL', 'qwen:0.5b')

    try:
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "model": model,
                "prompt": full_prompt,
                "stream": False
            }

            response = await client.post(
                "http://localhost:11434/api/generate",
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            return {
                "success": True,
                "content": data.get("response", "")
            }

    except httpx.ConnectError:
        return {
            "success": False,
            "content": "",
            "error": "无法连接到Ollama服务，请确保Ollama已启动"
        }
    except httpx.TimeoutException:
        return {
            "success": False,
            "content": "",
            "error": "AI服务响应超时，请重试"
        }
    except Exception as e:
        return {
            "success": False,
            "content": "",
            "error": f"AI服务错误: {str(e)}"
        }


async def generate_email_content(purpose: str, customer_name: str = None, extra_info: str = None) -> dict:
    """
    使用AI生成邮件内容

    Args:
        purpose: 邮件用途
        customer_name: 客户姓名（可选）
        extra_info: 额外信息（可选）

    Returns:
        dict: {"success": bool, "subject": str, "content": str, "error": str}
    """
    customer_greeting = f"尊敬的{customer_name}客户" if customer_name else "尊敬的客户"

    system_prompt = """你是一位专业的银行客服助手，负责生成专业、礼貌、规范的银行邮件内容。
邮件应该简洁明了，重点突出，结尾有礼貌的问候语。
请直接输出邮件内容，格式如下：
主题：你的主题
正文：你的内容"""

    prompt = f"""{customer_greeting}：

请生成一封{purpose}的邮件。

{f'附加信息：{extra_info}' if extra_info else ''}

请确保邮件内容符合银行规范。"""

    result = await generate_content(prompt, system_prompt)

    if result["success"]:
        content = result["content"]
        subject = "来自银行系统的邮件"

        # 尝试提取主题
        if "主题：" in content:
            parts = content.split("主题：", 1)
            if len(parts) > 1:
                theme_part = parts[1].split("\n", 1)
                subject = theme_part[0].strip()
                content = theme_part[1].strip() if len(theme_part) > 1 else ""

        return {
            "success": True,
            "subject": subject,
            "content": content
        }
    else:
        return {
            "success": False,
            "subject": "",
            "content": "",
            "error": result["error"]
        }
