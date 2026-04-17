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


def extract_location_keywords(message: str) -> bool:
    """检查消息是否包含位置/地图相关关键词"""
    location_keywords = [
        "在哪里", "地址", "位置", "怎么走", "路线", "地图", "附近",
        "距离", "离我", "导航", "找到", "搜索", "地点", "营业厅",
        "支行", "分行", "网点", "位置在哪"
    ]
    return any(keyword in message for keyword in location_keywords)


def extract_address_from_message(message: str) -> str:
    """从消息中提取地址或位置关键词"""
    # 移除常见前缀
    message = message.replace("你们", "").replace("银行", "").replace("网点", "")
    message = message.replace("营业厅", "").replace("支行", "").replace("分行", "")
    
    # 提取地址关键词
    patterns = [
        r'.*?(?:在|到|去|找|搜索|查找)(.+?)(?:怎么|在哪|的位置|怎么走|多远)',
        r'(.+?)(?:支行|分行|营业厅|网点|支行|分行)',
        r'.*?(?:最近的|附近|周边)(.+?)(?:银行|网点|营业厅)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message)
        if match:
            return match.group(1).strip()
    
    return None


async def search_location(keyword: str, region: str = None) -> str:
    """搜索位置信息（使用 Nominatim 免费的 OpenStreetMap 服务）"""
    try:
        # 使用 Nominatim (OpenStreetMap) 免费API
        search_keyword = keyword if region is None else f"{keyword}, {region}"
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": search_keyword,
            "format": "json",
            "limit": 3,
            "addressdetails": 1,
            "accept-language": "zh-CN"
        }
        headers = {"User-Agent": "BankAccountSystem/1.0"}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params, headers=headers)
            if response.status_code == 200:
                results = response.json()
                if results:
                    # 返回最佳匹配结果
                    top_result = results[0]
                    display_name = top_result.get("display_name", "")
                    lat = top_result.get("lat", "")
                    lon = top_result.get("lon", "")
                    
                    # 提取简短地址
                    address = top_result.get("address", {})
                    short_addr = address.get("city", address.get("town", address.get("village", "")))
                    
                    return {
                        "name": keyword,
                        "address": display_name,
                        "short_address": short_addr,
                        "latitude": lat,
                        "longitude": lon,
                        "type": top_result.get("type", "")
                    }
        return None
    except Exception as e:
        return None


async def get_nearby_bank_info(keyword: str, region: str = None) -> str:
    """搜索附近的银行网点信息"""
    try:
        search_term = f"{keyword} bank" if region is None else f"{region} {keyword} bank"
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": search_term,
            "format": "json",
            "limit": 3,
            "addressdetails": 1,
            "accept-language": "zh-CN"
        }
        headers = {"User-Agent": "BankAccountSystem/1.0"}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params, headers=headers)
            if response.status_code == 200:
                results = response.json()
                if results:
                    locations = []
                    for i, r in enumerate(results[:3], 1):
                        address = r.get("address", {})
                        city = address.get("city", address.get("town", address.get("village", "未知")))
                        road = address.get("road", "")
                        suburb = address.get("suburb", "")
                        
                        full_addr = ", ".join(filter(None, [road, suburb, city]))
                        lat = r.get("lat", "")
                        lon = r.get("lon", "")
                        
                        locations.append(f"{i}. {city} {full_addr} (坐标: {lat}, {lon})")
                    
                    return "\n".join(locations)
        return "附近银行网点信息暂时无法获取"
    except Exception as e:
        return "附近银行网点信息暂时无法获取"


async def chat_with_qwen(messages: list) -> str:
    """调用通义千问API进行对话"""
    headers = {
        "Authorization": f"Bearer {config.DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 获取当前时间
    time_info = get_current_time_info()
    
    # 获取用户消息
    user_message = messages[-1]["content"] if messages else ""
    
    # ============ 天气查询 ============
    weather_keywords = ["天气", "气温", "温度", "下雨", "下雪", "晴", "阴", "冷", "热"]
    weather_info = ""
    if any(keyword in user_message for keyword in weather_keywords):
        city = extract_city_from_message(user_message)
        if city:
            weather_info = await get_weather(city)
    if not weather_info:
        weather_info = await get_weather("北京")
    
    # ============ 地图位置查询 ============
    location_info = ""
    if extract_location_keywords(user_message):
        # 提取搜索关键词
        search_keyword = extract_address_from_message(user_message)
        if search_keyword:
            # 确定搜索区域
            region = extract_city_from_message(user_message) or "中国"
            
            # 检查是否是搜索银行
            if any(word in user_message for word in ["银行", "网点", "营业厅", "支行", "分行"]):
                location_info = await get_nearby_bank_info(search_keyword, region)
                if location_info:
                    location_info = f"\n\n📍 {region}附近的银行网点：\n{location_info}"
            else:
                # 搜索普通地点
                location_result = await search_location(search_keyword, region)
                if location_result:
                    location_info = f"""
📍 位置信息：
• 地点：{location_result['name']}
• 地址：{location_result['address'][:100]}...
• 坐标：纬度 {location_result['latitude']}, 经度 {location_result['longitude']}
"""
    
    SYSTEM_PROMPT = f"""你是银行的AI智能客服助手，名字叫"小银"。
你的职责是：
1. 回答用户关于银行账户、转账、存款、取款等业务问题
2. 提供友好的服务体验
3. 如遇到复杂问题，引导用户联系人工客服
4. 可以帮助用户查找银行网点位置和附近设施

当前时间和天气信息：
- 当前时间：{time_info}
- {weather_info}{location_info}

请用友好、专业的语气回答问题。如果用户询问天气或位置，可以根据上述信息回答。"""
    
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
