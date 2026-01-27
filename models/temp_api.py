"""
氣象屬api資料 鄉鎮天氣預報－台灣未來3天天氣預報 v1/rest/datastore/F-D0047-089
目標：ElementName 抓每小時溫度資料
注意：發現資料在36小時候，資料開始變成每3小時一筆
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_tmep():
    CWB_API_KEY = os.getenv('CWB_API_KEY')

    if not CWB_API_KEY:
        print("API_KEY not found")
        return
    
    url = "https://opendata.cwa.gov.tw//api/v1/rest/datastore/F-D0047-089"

    parmas = {
        'Authorization': CWB_API_KEY,
        'ElementName': '溫度'
    }
    res = requests.get(url, params=parmas)    
    row_data = res.json()
    data = prase_data(row_data)

    return {"ok": True, "description": '全縣市每小時溫度預報', 'data': data}

def prase_data(row_data):
    locations = row_data['records']['Locations'][0]['Location']
    data = []
    for location in locations:
        city_name = location['LocationName']
        items = location['WeatherElement'][0]['Time']
        
        forcasts = []
        for item in items:
            slot = {
                item['DataTime'].replace('+08:00', ''): item['ElementValue'][0]['Temperature']
            }
            forcasts.append(slot)
        waether_map = {
            'city': city_name,
            'forcasts': forcasts
        }
        data.append(waether_map)

    return data
    
