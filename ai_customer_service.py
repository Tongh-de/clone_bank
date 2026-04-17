"""
通义千问AI客服
"""
import httpx
import re
import config
from datetime import datetime

DASHSCOPE_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

# 常用城市列表
COMMON_CITIES = ["北京", "上海", "广州", "深圳", "杭州", "南京", "武汉", "成都", "重庆", "西安", 
                 "天津", "苏州", "郑州", "长沙", "沈阳", "青岛", "宁波", "东莞", "无锡", "昆明",
                 "大连", "厦门", "合肥", "佛山", "福州", "哈尔滨", "济南", "温州", "长春", "石家庄"]

def get_current_time_info() -> str:
    """获取当前时间信息"""
    now = datetime.now()
    weekday_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    weekday = weekday_names[now.weekday()]
    return f"{now.year}年{now.month}月{now.day}日 {weekday} {now.strftime('%H:%M:%S')}"


def extract_city_from_message(message: str) -> str:
    """从消息中提取城市名"""
    # 检查是否包含"本地"、"当地"、"这里"等词
    if any(word in message for word in ["本地", "当地", "这里", "这边", "我现在在", "我在"]):
        return "北京"  # 默认返回北京，可根据实际需求调整
    
    # 尝试匹配常见城市名
    for city in COMMON_CITIES:
        if city in message:
            return city
    
    return None


async def get_weather(city: str = "北京") -> str:
    """获取天气信息（使用免费API）"""
    try:
        # 使用wttr.in免费天气API
        url = f"https://wttr.in/{city}?format=j1"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                current = data["current_condition"][0]
                temp = current["temp_C"]
                weather = current["weatherDesc"][0]["value"]
                humidity = current["humidity"]
                wind = current["windspeedKmph"]
                feels_like = current["FeelsLikeC"]
                return f"{city}天气：{weather}，温度：{temp}°C（体感{feels_like}°C），湿度：{humidity}%，风速：{wind}km/h"
    except Exception as e:
        return f"天气查询暂时不可用"
    return "天气查询暂时不可用"


async def chat_with_qwen(messages: list) -> str:
    """调用通义千问API进行对话"""
    headers = {
        "Authorization": f"Bearer {config.DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 获取当前时间
    time_info = get_current_time_info()
    
    # 检查用户消息是否询问天气
    user_message = messages[-1]["content"] if messages else ""
    weather_keywords = ["天气", "气温", "温度", "下雨", "下雪", "晴", "阴", "冷", "热"]
    
    weather_info = ""
    if any(keyword in user_message for keyword in weather_keywords):
        city = extract_city_from_message(user_message)
        if city:
            weather_info = await get_weather(city)
    
    # 如果没有天气查询，默认提供北京天气
    if not weather_info:
        weather_info = await get_weather("北京")
    
    SYSTEM_PROMPT = f"""你是银行的AI智能客服助手，名字叫"小银"。
你的职责是：
1. 回答用户关于银行账户、转账、存款、取款等业务问题
2. 提供友好的服务体验
3. 如遇到复杂问题，引导用户联系人工客服

当前时间和天气信息：
- 当前时间：{time_info}
- {weather_info}

请用友好、专业的语气回答问题。如果用户询问天气，可以根据上述天气信息回答。"""
    
    payload = {
        "model": "qwen-plus",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            *messages
        ],
        "temperature": 0.7
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(DASHSCOPE_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
