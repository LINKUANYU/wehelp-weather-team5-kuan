export class WeatherView {
  constructor() {
    // 縣市區塊
    this.cityName = document.getElementById("city-name");
    this.cityDate = document.getElementById("city-date");

    // 天氣預報區塊
    this.firstMinTime = document.getElementById("weather-first-min-time");
    this.firstMaxTime = document.getElementById("weather-first-max-time");
    this.firstStateIcon = document.getElementById("weather-first-icon");
    this.firstMinTemp = document.getElementById("weather-first-min-temp");
    this.firstMaxTemp = document.getElementById("weather-first-max-temp");
    this.firstState = document.getElementById("weather-first-state");

    this.secondMinTime = document.getElementById("weather-second-min-time");
    this.secondMaxTime = document.getElementById("weather-second-max-time");
    this.secondStateIcon = document.getElementById("weather-second-icon");
    this.secondMinTemp = document.getElementById("weather-second-min-temp");
    this.secondMaxTemp = document.getElementById("weather-second-max-temp");
    this.secondTitle = document.getElementById("weather-second-title");
    this.secondState = document.getElementById("weather-second-state");

    this.thirdMinTime = document.getElementById("weather-third-min-time");
    this.thirdMaxTime = document.getElementById("weather-third-max-time");
    this.thirdStateIcon = document.getElementById("weather-third-icon");
    this.thirdMinTemp = document.getElementById("weather-third-min-temp");
    this.thirdMaxTemp = document.getElementById("weather-third-max-temp");
    this.thirdTitle = document.getElementById("weather-third-title");
    this.thirdState = document.getElementById("weather-third-state");

    // chart
    this.ctx = document.getElementById("weatherChart").getContext("2d"); // canvas
    this.chartInstance = null;
  }

  renderCityBlock(city) {
    if (city) {
      // 取現在日期
      const today = new Date();
      const month = String(today.getMonth() + 1).padStart(2, "0");
      const date = String(today.getDate()).padStart(2, "0");
      this.cityDate.textContent = `${month}/${date}`;

      // 渲染縣市
      this.cityName.textContent = city.trim();
    }
  }

  renderWeatherBlock(data) {
    if (!data || data.length === "") return;

    // 面板閃爍回饋
    this._flashAllCards();

    if (data[0]) {
      // 第一區
      this.firstMinTime.textContent = data[0]["startTime"].slice(11, 16);
      this.firstMaxTime.textContent = data[0]["endTime"].slice(11, 16);
      this.firstStateIcon.src = `static/img/${data[0]["weather_code"]}.png`;
      this.firstStateIcon.alt = data[0]["weather"];
      this.firstMinTemp.textContent = data[0]["minT"];
      this.firstMaxTemp.textContent = data[0]["maxT"];
      this.firstState.textContent = data[0]["weather"];

      // "預測天氣面板"標題
      if (data[0]["endTime"].slice(11,13)=="06") {
        this.secondTitle.textContent = "今日白天";
        this.thirdTitle.textContent = "今日晚上";
      }
      else {
        this.secondTitle.textContent = "明日白天";
        this.thirdTitle.textContent = "明日晚上";
      }
    }

    if (data[1]) {
      // 第二區
      this.secondMinTime.textContent = data[1]["startTime"].slice(11, 16);
      this.secondMaxTime.textContent = data[1]["endTime"].slice(11, 16);
      this.secondStateIcon.src = `static/img/${data[1]["weather_code"]}.png`;
      this.secondStateIcon.alt = data[1]["weather"];
      this.secondMinTemp.textContent = data[1]["minT"];
      this.secondMaxTemp.textContent = data[1]["maxT"];
      this.secondState.textContent = data[1]["weather"];
    }

    if (data[2]) {
      // 第三區
      this.thirdMinTime.textContent = data[2]["startTime"].slice(11, 16);
      this.thirdMaxTime.textContent = data[2]["endTime"].slice(11, 16);
      this.thirdStateIcon.src = `static/img/${data[2]["weather_code"]}.png`;
      this.thirdStateIcon.alt = data[2]["weather"];
      this.thirdMinTemp.textContent = data[2]["minT"];
      this.thirdMaxTemp.textContent = data[2]["maxT"];
      this.thirdState.textContent = data[2]["weather"];
    }

  }

  createWeatherChart(xLabels, yValues) {
    const labelsWithGhost = ["", ...xLabels, ""];
    const valuesWithGhost = [
      yValues[0],
      ...yValues,
      yValues[yValues.length - 1],
    ];

    // 建立漸層 (這裡要拿到 ctx 才能做)
    const gradient = this.ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, "rgba(250, 253, 214, 0.9)");
    gradient.addColorStop(0.5, "rgba(250, 253, 214, 0.2)");
    gradient.addColorStop(1, "rgba(250, 253, 214, 0)");

    const config = {
      type: "line",
      data: {
        labels: labelsWithGhost, // 填入傳進來的橫軸
        datasets: [
          {
            label: "溫度",
            data: valuesWithGhost, // 填入傳進來的縱軸
            borderColor: "#FAFDD6",
            backgroundColor: gradient,
            borderWidth: 2,
            tension: 0.4, // 平滑曲線
            pointRadius: 0,
            pointHoverRadius: 6,
            fill: true,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: "index", // 模式：索引 (只要 X 軸位置對了就觸發，不用管 Y 軸高度)
          intersect: false, // 交集：否 (不需要滑鼠真的「碰到」線條或點，只要在附近就好)
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            enabled: true,
            backgroundColor: "rgba(255, 255, 255, 0.9)", // 背景色
            titleColor: "#595959", // 標題顏色
            bodyColor: "#91ADC8", // 數值顏色
            borderColor: "rgba(255, 255, 255, 0)", // 邊框顏色
            borderWidth: 0, // 邊框寬度
            padding: 10, // 內距
            cornerRadius: 8, // 圓角

            displayColors: false, // 隱藏數值前面的那個顏色小方塊

            // 過濾幽靈節點
            filter: function (tooltipItem) {
              return tooltipItem.label !== "";
            },

            // 自訂文字內容
            callbacks: {
              // 自訂標題 (時間)
              title: function (context) {
                // context[0].label 會抓到 X 軸的時間
                return context[0].label;
              },
              // 自訂數值 (溫度)
              label: function (context) {
                // context.parsed.y 是數值
                return context.parsed.y + "°C";
              },
            },
            titleFont: {
              size: 13,
            },
            bodyFont: {
              size: 16,
              weight: "bold",
            },
          },
        },
        scales: {
          x: {
            offset: false,
            grid: {
              color: "rgba(255, 255, 255, 0.1)",
              borderDash: [5, 5],
              drawBorder: false,
            },
            ticks: {
              display: true, // 橫軸文字
              color: "#fff",
              font: {
                size: 14,
              },
              callback: function (val, index) {
                // 只顯示真實數據的標籤 (略過頭尾)
                return this.getLabelForValue(val);
              },
            },
          },
          y: {
            min: 0,
            max: 40,
            grid: {
              color: "rgba(255, 255, 255, 0.1)",
              borderDash: [5, 5],
              drawBorder: false,
            },
            ticks: {
              color: "#fff",
              stepSize: 10,
              font: {
                size: 16,
              },
              callback: function (value, index, values) {
                return value + "°";
              },
            },
          },
        },
      },
    };

    // 建立圖表
    this.chartInstance = new Chart(this.ctx, config);
  }

  updateWeatherChart(xLabels, yData) {
    if (this.chartInstance) {
      // 更新數據
      this.chartInstance.data.labels = xLabels;
      this.chartInstance.data.datasets[0].data = yData;

      // 呼叫 Chart.js 的更新方法
      this.chartInstance.update();
    } else {
      console.error("圖表尚未初始化，請先呼叫 initWeatherChart");
    }
  }

  // 資料畫面閃爍
  _flashAllCards() {
      const cards = document.querySelectorAll('.weather-card');

      if (!cards) return;

      cards.forEach(card => {
          card.classList.add('weather-flash-active');
      });

      // 0.3 秒後統一移除
      setTimeout(() => {
          cards.forEach(card => {
              card.classList.remove('weather-flash-active');
          });
      }, 200);
  }
}
