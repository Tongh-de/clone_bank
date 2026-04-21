"""
高德地图服务
提供地图相关的API接口
"""
from fastapi import APIRouter, Request, Query
from pydantic import BaseModel
from core import config
import requests

router = APIRouter(prefix="/api/map", tags=["地图"])

AMAP_BASE_URL = "https://restapi.amap.com/v3"
SERVER_KEY = config.AMAP_SERVER_KEY

class MapConfig(BaseModel):
    amap_key: str
    center: list = [116.397428, 39.90923]
    zoom: int = 13

@router.get("/config")
async def get_map_config():
    """获取地图配置"""
    return {
        "amap_key": config.AMAP_WEB_KEY,  # 前端key
        "center": [116.397428, 39.90923],
        "zoom": 13
    }

@router.get("/ip-location")
async def ip_location(ip: str = Query(None, description="IP地址，不传则自动获取")):
    """根据IP获取当前位置"""
    url = f"{AMAP_BASE_URL}/ip"
    params = {"key": SERVER_KEY}
    if ip:
        params["ip"] = ip
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if data.get("status") == "1":
            # 获取城市中心坐标
            city = data.get("city", "")
            center = None
            
            # 尝试通过城市名称获取精确坐标
            if city:
                geocode_url = f"{AMAP_BASE_URL}/geocode/geo"
                geocode_params = {"key": SERVER_KEY, "address": city}
                geo_response = requests.get(geocode_url, params=geocode_params, timeout=5)
                geo_data = geo_response.json()
                if geo_data.get("status") == "1" and geo_data.get("geocodes"):
                    location = geo_data["geocodes"][0].get("location", "")
                    if location:
                        lng, lat = location.split(",")
                        center = [float(lng), float(lat)]
            
            # 如果无法获取精确坐标，使用矩形中心点
            if not center:
                rectangle = data.get("rectangle", "").split(";")
                if len(rectangle) == 2:
                    coords = rectangle[1].split(",")
                    if len(coords) == 2:
                        center = [float(coords[0]), float(coords[1])]
            
            # 默认坐标（北京）
            if not center:
                center = [116.397428, 39.90923]
                
            return {
                "success": True,
                "province": data.get("province"),
                "city": city,
                "adcode": data.get("adcode"),
                "center": center
            }
        return {"success": False, "message": "获取位置失败"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.get("/geocode")
async def geocode(address: str):
    """地址转坐标"""
    url = f"{AMAP_BASE_URL}/geocode/geo"
    params = {"key": SERVER_KEY, "address": address}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.encoding = 'utf-8'
        data = response.json()
        if data.get("status") == "1" and data.get("geocodes"):
            geocode = data["geocodes"][0]
            location = geocode.get("location", "").split(",")
            return {
                "success": True,
                "province": geocode.get("province"),
                "city": geocode.get("city"),
                "district": geocode.get("district"),
                "location": location if len(location) == 2 else [],
                "address": geocode.get("formatted_address")
            }
        return {"success": False, "message": "未找到该地址"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.get("/poi/search")
async def search_poi(keywords: str, city: str = "全国", offset: int = 20, page: int = 1):
    """搜索POI点"""
    url = f"{AMAP_BASE_URL}/place/text"
    params = {
        "key": SERVER_KEY,
        "keywords": keywords,
        "city": city,
        "offset": offset,
        "page": page,
        "extensions": "all"
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        response.encoding = 'utf-8'  # 修复中文乱码
        data = response.json()
        if data.get("status") == "1":
            pois = []
            for poi in data.get("pois", []):
                location = poi.get("location", "").split(",")
                if len(location) == 2:
                    pois.append({
                        "id": poi.get("id"),
                        "name": poi.get("name"),
                        "type": poi.get("type"),
                        "typecode": poi.get("typecode"),
                        "address": poi.get("address"),
                        "location": [float(location[0]), float(location[1])],
                        "tel": poi.get("tel"),
                        "distance": poi.get("distance"),
                        "business_type": poi.get("business_type")
                    })
            return {
                "success": True,
                "count": data.get("count"),
                "pois": pois
            }
        return {"success": False, "message": "搜索失败", "info": data.get("info")}
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.get("/poi/nearby")
async def nearby_search(location: str, keywords: str = "", radius: int = 1000, offset: int = 20, page: int = 1):
    """周边搜索"""
    url = f"{AMAP_BASE_URL}/place/around"
    params = {
        "key": SERVER_KEY,
        "location": location,
        "keywords": keywords,
        "radius": radius,
        "offset": offset,
        "page": page,
        "extensions": "all"
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        response.encoding = 'utf-8'
        data = response.json()
        if data.get("status") == "1":
            pois = []
            for poi in data.get("pois", []):
                loc = poi.get("location", "").split(",")
                if len(loc) == 2:
                    pois.append({
                        "id": poi.get("id"),
                        "name": poi.get("name"),
                        "type": poi.get("type"),
                        "address": poi.get("address"),
                        "location": [float(loc[0]), float(loc[1])],
                        "tel": poi.get("tel"),
                        "distance": poi.get("distance")
                    })
            return {
                "success": True,
                "count": data.get("count"),
                "pois": pois
            }
        return {"success": False, "message": "搜索失败"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.get("/poi/detail")
async def poi_detail(id: str):
    """POI详情"""
    url = f"{AMAP_BASE_URL}/place/detail"
    params = {"key": SERVER_KEY, "id": id}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.encoding = 'utf-8'
        data = response.json()
        if data.get("status") == "1":
            poi = data.get("pois", [{}])[0]
            return {"success": True, "data": poi}
        return {"success": False, "message": "获取详情失败"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.get("/weather")
async def weather(city: str):
    """天气预报"""
    url = f"{AMAP_BASE_URL}/weather/weatherInfo"
    params = {"key": SERVER_KEY, "city": city, "extensions": "base"}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.encoding = 'utf-8'
        data = response.json()
        if data.get("status") == "1":
            return {"success": True, "weather": data.get("lives", [{}])[0]}
        return {"success": False, "message": "获取天气失败"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.get("/regeo")
async def regeo(location: str):
    """坐标转地址"""
    url = f"{AMAP_BASE_URL}/geocode/regeo"
    params = {
        "key": SERVER_KEY,
        "location": location,
        "extensions": "all"
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        response.encoding = 'utf-8'
        data = response.json()
        if data.get("status") == "1":
            regeocode = data.get("regeocode", {})
            address = regeocode.get("formatted_address")
            province = regeocode.get("addressComponent", {}).get("province")
            city = regeocode.get("addressComponent", {}).get("city")
            district = regeocode.get("addressComponent", {}).get("district")
            return {
                "success": True,
                "address": address,
                "province": province,
                "city": city,
                "district": district,
                "roads": [r.get("name") for r in regeocode.get("roads", [])],
                "pois": [
                    {"name": p.get("name"), "distance": p.get("distance")}
                    for p in regeocode.get("pois", [])[:10]
                ]
            }
        return {"success": False, "message": "逆地理编码失败"}
    except Exception as e:
        return {"success": False, "message": str(e)}
