"""
通义千问AI客服
"""
import httpx
import re
import asyncio
from datetime import datetime, timedelta
from core import config

DASHSCOPE_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

# wttr.in 天气 API（免费，无需 key）

# 天气缓存（5分钟有效期）
_weather_cache = {}

# 城市映射 (wttr.in 支持的城市，作为备选)
CITY_PINGYIN = {
    "北京": "Beijing", "上海": "Shanghai", "广州": "Guangzhou", "深圳": "Shenzhen",
    "杭州": "Hangzhou", "南京": "Nanjing", "武汉": "Wuhan", "成都": "Chengdu",
    "重庆": "Chongqing", "西安": "Xian", "天津": "Tianjin", "苏州": "Suzhou",
    "郑州": "Zhengzhou", "长沙": "Changsha", "沈阳": "Shenyang", "青岛": "Qingdao",
    "宁波": "Ningbo", "东莞": "Dongguan", "无锡": "Wuxi", "昆明": "Kunming",
    "大连": "Dalian", "厦门": "Xiamen", "合肥": "Hefei", "佛山": "Foshan",
    "福州": "Fuzhou", "哈尔滨": "Harbin", "济南": "Jinan", "温州": "Wenzhou",
    "长春": "Changchun", "石家庄": "Shijiazhuang", "贵阳": "Guiyang",
    "太原": "Taiyuan", "南昌": "Nanchang", "南宁": "Nanning", "拉萨": "Lhasa",
    "乌鲁木齐": "Urumqi", "呼和浩特": "Hohhot", "海口": "Haikou", "三亚": "Sanya"
}
COMMON_CITIES = list(CITY_PINGYIN.keys())


def get_current_time_info() -> str:
    """获取当前时间信息"""
    now = datetime.now()
    weekday_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    weekday = weekday_names[now.weekday()]
    return f"{now.year}年{now.month}月{now.day}日 {weekday} {now.strftime('%H:%M:%S')}"


def extract_city_from_message(message: str) -> str:
    """从消息中提取城市名（支持县级）"""
    # 移除常见前缀
    msg = message
    for prefix in ["我在", "我在", "本地", "当地", "这里", "这边"]:
        msg = msg.replace(prefix, "")
    
    # 匹配省/市/县等行政区划
    patterns = [
        r'([^\s]+?(?:省|市|区|县|旗))',  # 匹配如"江苏省"、"南京市"、"浦东新区"、"某某县"
        r'([^\s]+?(?:省|市|区|县|旗))[^\s]*',  # 更宽松匹配
    ]
    
    for pattern in patterns:
        match = re.search(pattern, msg)
        if match:
            city = match.group(1).strip()
            # 和风天气API只支持到城市级别，需要规范化区县名
            return _normalize_city_for_weather(city)
    
    # 回退：检查已知城市列表
    for city in COMMON_CITIES:
        if city in message:
            return city
    return None


def _normalize_city_for_weather(city: str) -> str:
    """将区县名规范化为城市名（和风天气只支持到城市级别）"""
    # 移除区、县等后缀
    for suffix in ["区", "县", "旗", "市"]:
        if city.endswith(suffix) and len(city) > 2:
            city = city[:-1]
            break
    return city


def _get_cached_weather(city: str) -> tuple:
    """获取缓存的天气数据"""
    if city in _weather_cache:
        cached_time, cached_weather = _weather_cache[city]
        if datetime.now() - cached_time < timedelta(minutes=5):
            return cached_weather
    return None


def _set_cached_weather(city: str, weather: str):
    """设置天气缓存"""
    _weather_cache[city] = (datetime.now(), weather)


async def get_weather(city: str = "北京") -> str:
    """获取天气信息（支持县级城市）"""
    # 检查缓存
    cached = _get_cached_weather(city)
    if cached:
        return cached
    
    # 使用 wttr.in
    weather = await get_weather_wttr(city)
    if weather:
        _set_cached_weather(city, weather)
        return weather
    
    return None


async def get_weather_wttr(city: str = "北京") -> str:
    """使用 wttr.in 获取天气（备选方案）"""
    try:
        city_pinyin = CITY_PINGYIN.get(city, city)
        url = f"https://wttr.in/{city_pinyin}?format=j1"
        headers = {"User-Agent": "Mozilla/5.0"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if "current_condition" in data and len(data["current_condition"]) > 0:
                    current = data["current_condition"][0]
                    temp = current["temp_C"]
                    weather = current["weatherDesc"][0]["value"]
                    humidity = current["humidity"]
                    wind = current["windspeedKmph"]
                    feels_like = current["FeelsLikeC"]
                    weather_map = {
                        "Sunny": "晴天", "Clear": "晴朗", "Partly cloudy": "多云",
                        "Cloudy": "阴天", "Overcast": "阴天", "Mist": "有雾",
                        "Fog": "大雾", "Light rain": "小雨", "Heavy rain": "大雨",
                        "Light snow": "小雪", "Heavy snow": "大雪", "Thunderstorm": "雷阵雨",
                        "Light drizzle": "毛毛雨", "Moderate rain": "中雨"
                    }
                    weather_cn = weather_map.get(weather, weather)
                    return f"{city}天气：{weather_cn}，温度：{temp}°C（体感{feels_like}°C），湿度：{humidity}%，风速：{wind}km/h"
    except Exception as e:
        print(f"wttr.in错误: {e}")
    return None


def extract_location_keywords(message: str) -> bool:
    """检查是否包含位置/地图相关关键词"""
    keywords = ["在哪里", "地址", "位置", "怎么走", "路线", "地图", "附近",
                "距离", "离我", "导航", "找到", "搜索", "地点", "营业厅", "支行", "分行", "网点"]
    return any(keyword in message for keyword in keywords)


def extract_address_from_message(message: str) -> str:
    """从消息中提取地址或位置关键词"""
    message = message.replace("你们", "").replace("银行", "").replace("网点", "")
    message = message.replace("营业厅", "").replace("支行", "").replace("分行", "")
    
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
    """搜索位置信息"""
    try:
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
                    top_result = results[0]
                    display_name = top_result.get("display_name", "")
                    address = top_result.get("address", {})
                    short_addr = address.get("city", address.get("town", address.get("village", "")))
                    
                    return {
                        "name": keyword,
                        "address": display_name,
                        "short_address": short_addr,
                        "latitude": top_result.get("lat", ""),
                        "longitude": top_result.get("lon", ""),
                        "type": top_result.get("type", "")
                    }
        return None
    except Exception:
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
    except Exception:
        return "附近银行网点信息暂时无法获取"


async def chat_with_qwen(messages: list) -> str:
    """调用通义千问API进行对话"""
    headers = {
        "Authorization": f"Bearer {config.DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    time_info = get_current_time_info()
    user_message = messages[-1]["content"] if messages else ""
    
    # 天气查询
    weather_info = ""
    weather_keywords = ["天气", "气温", "温度", "下雨", "下雪", "晴", "阴", "冷", "热"]
    city_queried = None
    if any(keyword in user_message for keyword in weather_keywords):
        city = extract_city_from_message(user_message)
        if city:
            weather_info = await get_weather(city) or ""
            city_queried = city
    # 如果用户询问天气但查询失败，返回友好提示
    if any(keyword in user_message for keyword in weather_keywords) and not weather_info:
        weather_info = f"暂无法获取{city_queried or '该城市'}的实时天气数据"
    
    # 地图位置查询
    location_info = ""
    if extract_location_keywords(user_message):
        search_keyword = extract_address_from_message(user_message)
        if search_keyword:
            region = extract_city_from_message(user_message) or "中国"
            if any(word in user_message for word in ["银行", "网点", "营业厅", "支行", "分行"]):
                location_info = await get_nearby_bank_info(search_keyword, region)
                if location_info:
                    location_info = f"\n\n📍 {region}附近的银行网点：\n{location_info}"
            else:
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
