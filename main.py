from fastapi import *
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from mysql.connector import Error
from dotenv import load_dotenv
load_dotenv()

app=FastAPI()

app.mount("/static", StaticFiles(dictionary="static"))

@app.get("/", include_in_schema=False)
async def index(request: Request):
    return FileResponse("/static/index.html", media_type="text/html")