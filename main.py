from fastapi import *
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from controller import get_weather
from dotenv import load_dotenv
load_dotenv()
from contextlib import asynccontextmanager
from service import scheduler
from models.weather_sync import sync_weather_from_cwa

@asynccontextmanager # 用來定義「非同步上下文管理器」。它能讓我們把「啟動前要做的準備」和「關閉前要做的清理」寫在同一個函式裡。
async def lifespan(app: FastAPI): # 把FastAPI 實體傳進來

    try:
        # 手動執行先抓取一次氣象資料
        sync_weather_from_cwa() # 此方程式內包含連線資料庫

        # 啟動排程器
        scheduler.start_scheduler()

        # 程式執行到這裡會「暫停」，並開始處理使用者的 API 請求（也就是讓伺服器維持在 Running 狀態）。
        # 2. 運行中：伺服器現在會處理所有 API 請求
        yield

    finally:
        # FastAPI 關閉時要做的事－關閉排程器
        # 3. 收尾：無論 yield 期間發生什麼事（正常關閉或閃退）
        scheduler.shutdown_scheduler()


app=FastAPI(lifespan=lifespan) # lifespan：FastAPI 生命週期管理器，說明server啟動跟關閉時要做什麼事

app.mount("/static", StaticFiles(directory="static"))

app.include_router(get_weather.router)

@app.get("/", include_in_schema=False)
async def index(request: Request):
    return FileResponse("static/index.html", media_type="text/html")


def initialize_database(cursor):
    # 檢查是否已經有代碼資料
    cursor.execute("SELECT COUNT(*) FROM weather_types")
    if cursor.fetchone()[0] == 0:
        print("偵測到空資料庫，正在寫入初始化天氣代碼...")
        # 這裡可以執行 seed.sql 的內容


"""
補充資料
關於 @asynccontextmanger
如果沒有他會變成下面的寫法，在app啟動跟關閉時要做的事

# ❌ 舊式寫法 (已被棄用)
@app.on_event("startup")
def startup_event():
    start_scheduler()

@app.on_event("shutdown")
def shutdown_event():
    shutdown_scheduler()

但是會有問題，如果 startup 執行到一半崩潰了，shutdown 可能根本不會被觸發，導致你剛開啟的資源（如資料庫連線）變成「殭屍狀態」掛在記憶體裡。

如果有使用 @asynccontextmanger 能讓我們把「啟動前要做的準備」和「關閉前要做的清理」寫在同一個函式裡。
A. 狀態的連貫性
如果不寫在一起，你需要用 global 變數來傳遞資源（例如資料庫連線物件）。寫在一起後，你可以直接在函式內部建立變數並在 yield 之後直接使用它，這大大減少了變數管理的混亂。

B. 異常傳遞 (Exception Propagation)
這才是它最強大的地方。當 yield 把控制權交給 FastAPI 後，如果 FastAPI 在運行中（例如處理請求時）發生崩潰：
Python 會將這個錯誤「丟回」給 lifespan 函式。錯誤會從 yield 那一行噴出來。如果你有寫 try...finally，這個錯誤就會被捕捉，進而執行清理代碼。

"""