export async function getWeather() {
    try {
        const response = await fetch(`/api/weather`, { method: "GET" });
        
        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const data = await response.json();
        return data.data;
    } catch (err) {
        console.error("全縣市36小時氣候資料載入錯誤：", err);
        return null;
    }
}

export async function getTempPerHour() {
    try {
        const response = await fetch(`/api/temp`, { method: "GET" });
        
        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const data = await response.json();
        return data.data;
    } catch (err) {
        console.error("全縣市每小時氣候資料載入錯誤：", err);
        return null;
    }
}

export async function sentTempToDC() {
    try {
        const response = await fetch(`/api/weather/push-six`, { method: "POST" });
        
        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }
        
    } catch (err) {
        console.error("Discord 傳送六都天氣錯誤：", err);
        return null;
    }
}