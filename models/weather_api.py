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

