from datetime import datetime
import zoneinfo

def get_taipei_now():
    """統一獲取台北時間的工具函數"""
    return datetime.now(zoneinfo.ZoneInfo("Asia/Taipei"))