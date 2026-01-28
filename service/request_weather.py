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
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_weather():
    CWB_API_KEY = os.getenv('CWB_API_KEY')

    if not CWB_API_KEY:
        print("API_KEY not found")
        return
    
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"

    parmas = {
        'Authorization': CWB_API_KEY,
    }

    res = requests.get(url, params=parmas)
    row_data = res.json()
    data = prase_data(row_data)

    return {'ok': True, 'description': '全縣市36小時天氣預報', 'data': data}

def prase_data(row_data):
    locations = row_data['records']['location']
    data = []
    for location in locations:
        city_name = location['locationName']
        
        weather_map = {}

        for item in location['weatherElement']:
            key = item['elementName']
            value = item['time'] # 如Wx, PoP, Ci
            weather_map[key] = value # [...] 整串資料

        forcasts = []

        for i in range(3):
            slot = {
                'startTime': weather_map['Wx'][i]['startTime'],
                'endTime': weather_map['Wx'][i]['endTime'],
                'weather': weather_map['Wx'][i]['parameter']['parameterName'],
                'weather_code': weather_map['Wx'][i]['parameter']['parameterValue'],

                'rain_pro': weather_map['PoP'][i]['parameter']['parameterName'],

                'minT': weather_map['MinT'][i]['parameter']['parameterName'],
                'maxT': weather_map['MaxT'][i]['parameter']['parameterName'],

                'comfort': weather_map['CI'][i]['parameter']['parameterName'],
            }
            forcasts.append(slot)
        
        city_map = {'city': city_name, 'forcasts': forcasts}
        data.append(city_map)
    
    return data

