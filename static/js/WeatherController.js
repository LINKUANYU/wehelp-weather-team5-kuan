import { WeatherView } from "./WeatherView.js";
import { getWeather, getTempPerHour, sentTempToDC } from "./weatherModel.js";

export class WeatherController {
    constructor () {
        this.view = new WeatherView();
        this.AllWeatherData = null;
        this.AllTempData = null;
    }

    async init() {
        // fetch 36小時全縣市資料
        this.AllWeatherData = await getWeather(); // 存著之後用
        // 初始用新北市的資料
        this.setWeather("臺中市");

        // fetch 每小時全縣市資料
        this.AllTempData = await getTempPerHour();
        this.initChart("臺中市");

        // discord 按鈕
        this.setDiscordBtn();
    }

    // 依照傳入縣市設置天氣面板
    setWeather(city) {
        this.view.renderCityBlock(city);

        const targetCity = this.AllWeatherData.find(item => item.city === city);
        const CityWeather = targetCity?.forecasts;
        this.view.renderWeatherBlock(CityWeather);
    }

    initChart(city) {
        const targetCity = this.AllTempData.find(item => item.city === city);
        const CityTempPerHour = targetCity?.forecasts;
        const data = this._processForecastData(CityTempPerHour);
        if (data?.x?.length > 0 && data?.y?.length > 0) {
            this.view.createWeatherChart(data.x, data.y);
        }
    }

    updateChart(city) {
        const targetCity = this.AllTempData.find(item => item.city === city);
        const CityTempPerHour = targetCity?.forecasts;
        const data = this._processForecastData(CityTempPerHour);
        if (data?.x?.length > 0 && data?.y?.length > 0) {
            this.view.updateWeatherChart(data.x, data.y);
        }
    }

    setDiscordBtn() {
        const btn = document.getElementById("dc-btn");
        btn.addEventListener("click", async () => {
           const data = await sentTempToDC();
        });
    }

    _processForecastData(data) {
        if (!data) return { x: [], y: [] };

        // 設定基準時間 (只看小時)
        const startTime = new Date();
        startTime.setMinutes(0, 0, 0);

        // 把 [{'key':'val'}] 變成 [{time: Date, val: Number}] 
        const cleanList = data.map(item => {
            const timeKey = Object.keys(item)[0];
            return {
                timestamp: new Date(timeKey),
                value: parseInt(item[timeKey], 10)
            };
        });

        // 找到第一筆資料的位置
        const startIndex = cleanList.findIndex(item => item.timestamp >= startTime);

        // 如果找不到，就回傳空陣列
        if (startIndex === -1) return { x: [], y: [] };

        // 從那個位置往後切 12 筆
        const sliceData = cleanList.slice(startIndex, startIndex + 12);

        // 拆分成 x 和 y 陣列
        const x = sliceData.map(item => {
            // 格式化時間：取得小時並補零
            const hour = item.timestamp.getHours().toString().padStart(2, '0');
            const minute = item.timestamp.getMinutes().toString().padStart(2, '0');
            return `${hour}:${minute}`;
        });

        const y = sliceData.map(item => item.value);

        return { x, y };
    }
}