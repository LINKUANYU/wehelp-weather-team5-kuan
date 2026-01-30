from apscheduler.schedulers.background import BackgroundScheduler
from models.weather_sync import sync_weather_from_cwa

# 建立一個全域的排程器實體
scheduler = BackgroundScheduler()

def start_scheduler():
    # 加入任務
    scheduler.add_job(
        sync_weather_from_cwa, 
        'cron',            # 使用 cron 模式：它不像「每隔 5 分鐘執行一次」這種規律間隔（那是 Interval 模式），而是更像「農民曆」：你可以指定具體的日期、星期、小時或分鐘。
        hour='*',       # 設定每1小時抓一次
        minute='5'         # 設定非整點，避開尖峰
    )
    
    scheduler.start()
    print("⏰ 排程器已啟動：每天 06:00 與 18:00 更新天氣")
    

def shutdown_scheduler():
    scheduler.shutdown()
    print("🛑 排程器已關閉")

