import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()
AMAP_KEY = os.getenv("AMAP_KEY")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY")

print("✅ 已加载 llm_api.py（支持真实高德搜索）")

async def search_nearby_restaurants(lat, lng, radius, keywords):
    """调用高德地图周边搜索API，返回餐厅列表"""
    if not AMAP_KEY:
        print("❌ 高德地图API Key未配置")
        return []

    url = "https://restapi.amap.com/v3/place/around"
    params = {
        "key": AMAP_KEY,
        "location": f"{lng},{lat}",
        "radius": radius,
        "keywords": keywords,
        "types": "050000",  # 餐饮类别
        "output": "json",
        "page_size": 20
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as resp:
                data = await resp.json()
                if data.get("status") != "1":
                    print(f"高德API返回错误: {data}")
                    return []

                pois = data.get("pois", [])
                restaurants = []
                for poi in pois:
                    # 提取评分（高德返回的rating可能为字符串）
                    rating = poi.get("rating", "4.0")
                    try:
                        rating = float(rating)
                    except:
                        rating = 4.0
                    restaurants.append({
                        "name": poi.get("name", "未知餐厅"),
                        "address": poi.get("address", ""),
                        "distance": poi.get("distance", "0"),
                        "score": str(rating)
                    })
                return restaurants
    except Exception as e:
        print(f"高德周边搜索错误: {e}")
        return []

async def chat_with_llm(demand, restaurants, scene="normal"):
    if not DEEPSEEK_KEY:
        return "❌ 请配置 DeepSeek API Key"
    if not restaurants:
        return "❌ 未找到餐厅"

    rest_text = "\n".join([
        f"店名：{r['name']}，地址：{r['address']}，距离：{r['distance']}米，评分：{r['score']}"
        for r in restaurants[:10]
    ])

    prompt = f"""
你是专业美食推荐官。
周边餐厅信息：
{rest_text}

用户需求：{demand}
场景：{scene}

请直接给出推荐，分点列出，语言自然口语。
"""

    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1024
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data, timeout=30) as resp:
                res = await resp.json()
        return res["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"大模型调用失败: {e}")
        return "❌ 大模型服务异常，请稍后重试"