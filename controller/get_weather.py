from fastapi import *
from models import temp_api, weather_api

router = APIRouter()

@router.get("/api/weather")
def weather():
    return weather_api.get_weather()

@router.get("/api/temp")
def tmep():
    return temp_api.get_tmep()

