from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger # 建議明確使用 Trigger 類別
import zoneinfo
from models.weather_sync import sync_weather_from_cwa

# 1. 建立時區物件
taipei_tz = zoneinfo.ZoneInfo("Asia/Taipei")
# 2. 初始化排程器時就指定時區，這樣裡面的 cron 運算都會以台北為準
scheduler = BackgroundScheduler(timezone=taipei_tz)

def start_scheduler():
    # 加入任務
    scheduler.add_job(
        sync_weather_from_cwa, 
        'cron',            # 使用 cron 模式：它不像「每隔 5 分鐘執行一次」這種規律間隔（那是 Interval 模式），而是更像「農民曆」：你可以指定具體的日期、星期、小時或分鐘。
        hour='5,17',       # 氣象站12小時資料更新時間為05,17
        minute='30'         # 設定非整點，避開尖峰
    )
    
    scheduler.start()
    print("⏰ 排程器已啟動：每天 05:30 與 17:30 更新天氣")
    

def shutdown_scheduler():
    scheduler.shutdown()
    print("🛑 排程器已關閉")

