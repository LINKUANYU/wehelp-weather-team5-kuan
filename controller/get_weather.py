from fastapi import APIRouter
from fastapi.responses import JSONResponse
import os
from models.weather_api import *
from db.deps import get_conn, get_cur
from dotenv import load_dotenv
load_dotenv()

from service import request_temp
from models.weather_post import push_six_cities_embed



router = APIRouter()

@router.get("/api/weather")
def weather(cur = Depends(get_cur)):
    data = WeatherModel.get_weather(cur)
    return {"ok":True, "description": "全縣市36小時天氣預報", "data": data}

@router.get("/api/temp")
def temp():
    return request_temp.get_temp()


# 推送天氣到Discord

CWA_API_KEY = os.getenv("CWA_API_KEY", "").strip()
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()


@router.post("/api/weather/push-six")
def push_six():
    if not CWA_API_KEY:
        return JSONResponse({"error": True, "message": "Missing CWA_API_KEY"}, status_code=500)

    if not WEBHOOK_URL:
        return JSONResponse({"error": True, "message": "Missing DISCORD_WEBHOOK_URL"}, status_code=500)

    try:
        rows = push_six_cities_embed(CWA_API_KEY, WEBHOOK_URL)
        return {"ok": True, "message": "已推送六都天氣到 Discord", "data": rows}
    except Exception as e:
        return JSONResponse({"error": True, "message": str(e)}, status_code=500)