import httpx
import asyncio

DASHSCOPE_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

async def test_full():
    api_key = "sk-62c0f5ff0ebc4f93aca0f640db2f5287"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "qwen-plus",
        "messages": [{"role": "system", "content": "你是AI助手"}, {"role": "user", "content": "你好"}],
        "temperature": 0.7
    }
    
    print("开始测试...")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print("发送请求...")
            response = await client.post(DASHSCOPE_API_URL, headers=headers, json=payload)
            print(f"状态码: {response.status_code}")
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"成功! 回复: {content[:100]}")
    except httpx.ConnectError as e:
        print(f"ConnectError: {e}")
    except httpx.TimeoutException as e:
        print(f"TimeoutException: {e}")
    except Exception as e:
        print(f"其他错误 {type(e).__name__}: {e}")

asyncio.run(test_full())
