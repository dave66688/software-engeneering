import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()
AMAP_KEY = os.getenv("AMAP_KEY")

async def ip_location(ip=""):
    url = "https://restapi.amap.com/v3/ip"
    params = {
        "key": AMAP_KEY,
        "ip": ip,
        "output": "json"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                data = await resp.json()
                if data.get("status") == "1":
                    return {
                        "lng": data.get("rectangle", "").split(";")[0].split(",")[0],
                        "lat": data.get("rectangle", "").split(";")[0].split(",")[1]
                    }
    except Exception as e:
        print(f"IP定位错误: {e}")
        pass

    return {"lng": "116.397428", "lat": "39.90923"}