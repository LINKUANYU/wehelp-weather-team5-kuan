from fastapi import *


class WeatherModel:
    @staticmethod
    def get_weather(cur):
        try:
            # 使用 Window Function (ROW_NUMBER) 確保每個城市只取最新的 3 筆
            sql = """
                SELECT
                    res.city_name,
                    res.start_time,
                    res.end_time,
                    res.weather,
                    res.weather_code,
                    res.icon_path,
                    res.rain_pro,
                    res.min_temp,
                    res.max_temp,
                    res.comfort
                FROM (
                    SELECT
                        l.city_name,
                        f.start_time,
                        f.end_time,
                        f.weather,
                        f.weather_code,
                        t.icon_path,
                        f.rain_pro,
                        f.min_temp,
                        f.max_temp,
                        f.comfort,
                        l.id AS city_id,
                        ROW_NUMBER() OVER(
                            PARTITION BY f.location_id
                            ORDER BY f.start_time ASC
                        ) as row_num
                    FROM weather_forecasts f
                    JOIN locations l ON f.location_id = l.id
                    JOIN weather_types t ON f.weather_code = t.weather_code
                    WHERE f.end_time > NOW()  -- 只抓尚未結束的預報
                ) AS res
                WHERE res.row_num <= 3  -- 關鍵：每個城市只拿前三筆
                ORDER BY res.city_id ASC, res.start_time ASC;
            """
            cur.execute(sql)
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