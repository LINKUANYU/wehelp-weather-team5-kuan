"""
氣象屬api資料 一般天氣預報－今明36小時 v1/rest/datastore/F-C0032-001
目標：全縣市天氣預報資料
注意：有的時候資料是6小時，有時候是12小時
官網常見問題中說明
本平臺「鄉鎮天氣預報-未來1週天氣預報」逐12小時天氣預報的時間區段原則上為 06:00~18:00 及 18:00~06:00，惟會受預報發佈時間影響，不包含已經過去的時間。舉例說明如下：
每日 05:00 發佈的預報從 當日 06:00~18:00 開始
每日 11:00 發佈的預報從 當日 12:00~18:00 開始
每日 17:00 發佈的預報從 當日 18:00~06:00 開始
每日 23:00 發佈的預報從 隔日 00:00~06:00 開始

若希望只抓取完整12小時區間的資料，可以嘗試設定如下：
2022-03-10 11:00 發佈的預報加入參數 &timeFrom=2022-03-10T18:00:00
2022-03-10 23:00 發佈的預報加入參數 &timeFrom=2022-03-11T06:00:00
以此類推

解法：只抓取06,18點資料
"""
from db.deps import *
from fastapi import *
import requests
import os
from dotenv import load_dotenv
load_dotenv()


def sync_weather_from_cwa():
    CWA_API_KEY = os.getenv('CWA_API_KEY')

    if not CWA_API_KEY:
        print("API_KEY not found")
        return
    
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"

    parmas = {
        'Authorization': CWA_API_KEY,
    }
    try:
        res = requests.get(url, params=parmas)
        row_data = res.json()
        prase_and_save_to_db(row_data)
    except Exception as e:
        print("抓取資料失敗")
    

def prase_and_save_to_db(row_data):
    locations = row_data['records']['location']
    conn = cnxpool.get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        # 1. 先抓取目前的縣市對照表，避免在迴圈裡重複查 SQL
        cur.execute("SELECT id, city_name FROM locations")
        rows = cur.fetchall()
        
        # 建立城市跟id查表，為了把城市名轉換成id
        city_to_id = {row['city_name']: row['id'] for row in rows}
        # print(f"DEBUG: 縣市對照表內容 -> {city_to_id}")

        all_forecast_records = []
        for location in locations:
            city_name = location['locationName']
            l_id = city_to_id.get(city_name)

            if not l_id:
                continue # 如果資料庫沒這個縣市就跳過

            weather_map = {}

            for item in location['weatherElement']:
                key = item['elementName']
                value = item['time'] # 如Wx, PoP, Ci
                weather_map[key] = value # [...] 整串資料

            for i in range(3):
                slot = (
                    l_id,
                    weather_map['Wx'][i]['startTime'],
                    weather_map['Wx'][i]['endTime'],
                    weather_map['Wx'][i]['parameter']['parameterName'], # 天氣概況
                    weather_map['Wx'][i]['parameter']['parameterValue'].strip().zfill(2), # 天氣概況代碼，zfill把它補成兩位數才能跟weather_types的字串相同長度

                    int(weather_map['PoP'][i]['parameter']['parameterName']),

                    int(weather_map['MinT'][i]['parameter']['parameterName']),
                    int(weather_map['MaxT'][i]['parameter']['parameterName']),

                    weather_map['CI'][i]['parameter']['parameterName'],
                )
                all_forecast_records.append(slot)
        # 2. 執行更新或插入
        upsert_sql = """
            INSERT INTO weather_forecasts (
                location_id, start_time, end_time, weather,
                weather_code, rain_pro, min_temp, max_temp, comfort
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                start_time = VALUES(start_time),  -- 確保 start_time 也被更新 (6小時變12小時)
                weather = VALUES(weather),
                weather_code = VALUES(weather_code),
                rain_pro = VALUES(rain_pro),
                min_temp = VALUES(min_temp),
                max_temp = VALUES(max_temp),
                comfort = VALUES(comfort),
                created_at = NOW()               -- 確保時間戳記更新，回給前端邏輯那邊排序才有效
        """
        cur.executemany(upsert_sql, all_forecast_records)
        upsert_affected = cur.rowcount # 如果資料已存在且有內容更新：rowcount 為 2。

        # 3. 清理過期資料 (刪除 6 小時前就已經結束的預報，留一點點緩衝)
        cur.execute("DELETE FROM weather_forecasts WHERE end_time < NOW() - INTERVAL 6 HOUR")
        delete_affected = cur.rowcount

        conn.commit()
        print(f"寫入影響 {upsert_affected} 列，刪除 {delete_affected} 列")
    except mysql.connector.Error as err:
        print(f"❌ MySQL 錯誤: {err}") 
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()
