from fastapi import *
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from controller import get_weather
from dotenv import load_dotenv
load_dotenv()

app=FastAPI()

app.mount("/static", StaticFiles(directory="static"))

app.include_router(get_weather.router)

@app.get("/", include_in_schema=False)
async def index(request: Request):
    return FileResponse("static/index.html", media_type="text/html")