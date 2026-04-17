from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import time

from llm_api import chat_with_llm, search_nearby_restaurants
from amap_api import ip_location

load_dotenv()
app = FastAPI()

# 跨域配置（开发环境）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 缓存配置（10分钟过期）
cache = {
    "restaurants": {},
    "expire": 600
}

# 请求模型增强
class ChatRequest(BaseModel):
    latitude: float = 0.0
    longitude: float = 0.0
    radius: int = 1000
    demand: str = ""
    scene: str = "normal"
    cuisine: str = ""  # 新增菜系参数

# 首页
@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# 首页推荐（3家）
@app.post("/api/home_recommend")
async def home_recommend(request: ChatRequest):
    try:
        # 校验经纬度
       # 🔥 兜底定位：如果坐标是 0,0，就使用默认广州坐标
        if request.latitude == 0 or request.longitude == 0:
            lat = 23.1200   # 广州纬度
            lng = 113.3200   # 广州经度
        else:
            lat = request.latitude
            lng = request.longitude

        key = f"{lat}_{lng}"
        now = time.time()
        
        if key in cache["restaurants"]:
            data, t = cache["restaurants"][key]
            if now - t < cache["expire"]:
                return {"code": 0, "data": data[:3]}

        restaurants = await search_nearby_restaurants(
              lat,   # 👈 使用兜底坐标
              lng,   # 👈 使用兜底坐标
              10000,
              request.cuisine or "餐厅"
        )

        cache["restaurants"][key] = (restaurants, now)
        return {"code": 0, "data": restaurants[:3]}

    except Exception as e:
        return {"code": -1, "msg": f"获取失败：{str(e)}"}

# 聊天推荐（主接口）
@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # 🔥 1. 兜底定位：坐标为0就用广州坐标
        if request.latitude == 0 or request.longitude == 0:
            lat = 23.1200
            lng = 113.3200
        else:
            lat = request.latitude
            lng = request.longitude

        # 2. 半径转换
        radius_m = request.radius * 1000 if request.radius <= 20 else 20000

        # 3. 调用高德改用lat/lng
        restaurants = await search_nearby_restaurants(
            lat,
            lng,
            radius_m,
            request.cuisine or "餐厅"
        )

        if not restaurants:
            return {"code": -1, "msg": "附近未找到符合条件的餐厅，请调整搜索范围"}

        reply = await chat_with_llm(
            request.demand,
            restaurants,
            scene=request.scene
        )

        return {"code": 0, "data": reply}

    except Exception as e:
        return {"code": -1, "msg": f"服务异常：{str(e)}"}

# IP定位（备用）
@app.get("/api/ip_location")
async def get_ip_location(request: Request):
    try:
        ip = request.client.host
        if ip in ["127.0.0.1", "localhost"]:
            ip = ""
        
        location = await ip_location(ip)
        return {"code": 0, "data": location}
    except Exception as e:
        return {"code": -1, "msg": f"定位失败：{str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=2025)