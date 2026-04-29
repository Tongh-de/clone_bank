import httpx
import asyncio
import sys

async def test():
    api_key = "sk-62c0f5ff0ebc4f93aca0f640db2f5287"
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen-plus",
        "messages": [{"role": "user", "content": "你好"}],
        "temperature": 0.7
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.text[:500]}")
    except Exception as e:
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
