from fastapi import *
from models.temp_api import *
from models.weather_api import *
router = APIRouter()

@router.get("/api/weather")
def weather():
    return get_weather()

@router.get("/api/temp")
def tmep():
    return get_tmep()

    