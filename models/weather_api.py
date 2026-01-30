from fastapi import *
from service.utils import get_taipei_now


class WeatherModel:
    @staticmethod
    def get_weather(cur):
        try:
            now_taipei = get_taipei_now()
            # 使用 Window Function (ROW_NUMBER) 確保每個城市只取最新的 3 筆
            sql = """
                WITH latest AS (
                    SELECT 
                        l.city_name, f.start_time, f.end_time, f.weather, f.weather_code, 
                        ti.icon_path, f.rain_pro, f.min_temp, f.max_temp, f.comfort, 
                        l.id AS city_id,
                        ROW_NUMBER() OVER(
                            PARTITION BY f.location_id, f.end_time 
                            ORDER BY f.created_at DESC
                        ) AS last_rank 
                    FROM weather_forecasts f
                    JOIN locations l ON l.id = f.location_id
                    JOIN weather_types ti ON f.weather_code = ti.weather_code
                    WHERE f.end_time > %s -- 只選擇還沒有過期的資料
                ), 
                middle AS (
                    SELECT * FROM latest WHERE last_rank = 1  -- 這裡不可有分號
                ), 
                top3 AS (
                    SELECT *, 
                        ROW_NUMBER() OVER(
                            PARTITION BY city_id 
                            ORDER BY start_time ASC -- 這裡改成時間排序，拿最近的三場預報
                        ) AS row_num 
                    FROM middle
                )
                SELECT * FROM top3 
                WHERE row_num <= 3 
                ORDER BY city_id ASC, start_time ASC;
            """
            cur.execute(sql, (now_taipei,))
            rows = cur.fetchall()
            
            if not rows:
                print("Warning: No weather data found. Check if sync is running.")

            return WeatherModel.format_forecast_data(rows)
        except Exception as e:
            print(f"DB Error: {e}")
            raise HTTPException(status_code=500, detail={"error": True, "message": "can't get data from DB"})
    
        
    
    @staticmethod
    def format_forecast_data(rows):
        """將扁平的 DB 資料轉換為前端所需的巢狀結構"""
        # 用來存放最終結果的字典，key 為城市名
        city_groups = {}

        for row in rows:
            city = row["city_name"]

            if city not in city_groups:
                city_groups[city] = {
                    'city': city,
                    'forecasts': []
                }

            forecast_item = {
                'startTime': row['start_time'].strftime('%Y-%m-%d %H:%M:%S'),
                'endTime': row['end_time'].strftime('%Y-%m-%d %H:%M:%S'),
                'weather': row['weather'],
                'weather_code': row['weather_code'],
                'weather_icon_path': f"static/{row['icon_path']}",
                'rain_pro': str(row['rain_pro']),
                'minT': str(row['min_temp']),
                'maxT': str(row['max_temp']),
                'comfort': row['comfort']
            }
            city_groups[city]['forecasts'].append(forecast_item)

        # 最後只回傳字典裡的 values 部分（轉成 list）
        return list(city_groups.values())