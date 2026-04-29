import asyncio
import sys
sys.path.insert(0, 'd:/bank_count_yang')

from services.ai_customer_service import chat_with_qwen

async def test():
    print("开始测试 chat_with_qwen...")
    try:
        messages = [{"role": "user", "content": "你好"}]
        result = await chat_with_qwen(messages)
        # 只打印回复长度，避免编码问题
        print(f"成功! 回复长度: {len(result)} 字符")
        print("AI服务完全正常!")
    except Exception as e:
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {e}")

asyncio.run(test())
