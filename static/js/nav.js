import { WeatherController } from "./WeatherController.js";
import { getWeather } from "./weatherModel.js";

// patch WeatherController.init
// 確保 index.js 建 controller 時可以拿到實例
const originalInit = WeatherController.prototype.init;

WeatherController.prototype.init = async function patchedInit() {
  // 拿到 controller
  window.__weatherController = this;

  if (!this.__initPromise) {
    this.__initPromise = originalInit.call(this);
  }
  return this.__initPromise;
};

document.addEventListener("DOMContentLoaded", async () => {
  const anchors = Array.from(document.querySelectorAll(".nav-li-a"));
  if (anchors.length === 0) return;

  // 四個城市
  const targets = [
    { api: "臺北市", label: "台北" },
    { api: "臺中市", label: "台中" },
    { api: "臺南市", label: "台南" },
    { api: "高雄市", label: "高雄" },
  ];

  // 先把 nav 顯示成載入中
  targets.forEach((t, i) => {
    if (anchors[i]) anchors[i].textContent = `${t.label}：載入中`;
  });

  // 等待 controller 初始化完成
  const controller = window.__weatherController;
  if (controller?.__initPromise) {
    await controller.__initPromise;
  }

  // 從 getWeather 抓資料
  const all = await getWeather();

  for (let i = 0; i < targets.length; i++) {
    const a = anchors[i];
    if (!a) continue;

    const { api, label } = targets[i];

    // 避免 href="#" 回到頁面頂部
    a.addEventListener("click", (e) => e.preventDefault());

    // 填入天氣資訊
    const cityObj = Array.isArray(all) ? all.find((x) => x.city === api) : null;
    const first = cityObj?.forcasts?.[0];

    if (first) {
      const weather = first.weather ?? "";
      const minT = first.minT ?? "";
      const maxT = first.maxT ?? "";
      a.textContent = `${label}：${weather}，${minT}~${maxT}°C`;
    } else {
      a.textContent = `${label}：無資料`;
    }

    // 點選 nav 更新面板
    a.addEventListener("click", async () => {
      const c = window.__weatherController;

      // 等待初始化
      if (c?.__initPromise) await c.__initPromise;

      // 更新面板：縣市、三時段天氣、圖表
      c.setWeather(api);
      c.updateChart(api);
    });
  }
});
