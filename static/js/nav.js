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

function pickFirstForecast(cityObj) {
  // 你後端目前看起來是 forcasts（不是 forecasts）
  return cityObj?.forecasts?.[0] ?? null;
}

// 填入 nav 天氣資訊
function formatNavText(label, first) {
  if (!first) return `${label}：無資料`;
  const weather = first.weather ?? "";
  const minT = first.minT ?? "";
  const maxT = first.maxT ?? "";
  return `${label}：${weather}，${minT}~${maxT}°C`;
}

// 更新面板
async function syncPanel(city) {
  const c = window.__weatherController;
  if (!c) return;
  if (c.__initPromise) await c.__initPromise;

  c.setWeather(city);
  c.updateChart(city);
}

document.addEventListener("DOMContentLoaded", async () => {
  const anchors = Array.from(document.querySelectorAll(".nav-li-a"));

  const dropContainer = document.getElementById("dropbutton"); // .nav-dropcontainer
  const dropList = document.getElementById("droplist"); // 縣市ul
  const dropLabel = dropContainer?.querySelector("p"); // .nav-dropcontainer的顯示文字

  // 等待 controller 初始化完成
  const controller = window.__weatherController;
  if (controller?.__initPromise) {
    await controller.__initPromise;
  }

  // 從 getWeather 抓資料
  const all = await getWeather();
  if (!Array.isArray(all)) return;

  // ====== 螢幕寬度大於 1200px 時顯示天氣資訊於 nav ======
  if (anchors.length > 0) {
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

    for (let i = 0; i < targets.length; i++) {
      const a = anchors[i];
      if (!a) continue;

      const { api, label } = targets[i];

      // 避免 href="#" 回到頁面頂部
      a.addEventListener("click", (e) => e.preventDefault());

      // 填入天氣資訊
      const cityObj = all.find((x) => x.city === api);
      const first = pickFirstForecast(cityObj);
      a.textContent = formatNavText(label, first);

      // 點選更新面板
      a.addEventListener("click", async () => {
        await syncPanel(api);
      });
    }
  }

  // ====== 螢幕寬度小於 1200px 時顯示 dropdown list ======
  if (!dropContainer || !dropList) return;

  // 清空 li 內容
  dropList.innerHTML = "";

  // 由資料建立 li
  const frag = document.createDocumentFragment();

  all.forEach((cityObj) => {
    const cityName = cityObj.city;
    const first = pickFirstForecast(cityObj);

    const li = document.createElement("li");
    li.className = "nav-dropcontainer-li";
    li.textContent = `${cityName}`;
    li.dataset.city = cityName;

    li.addEventListener("click", async (e) => {
      e.stopPropagation(); // 不要觸發外部點擊關閉太早

      const city = li.dataset.city;
      await syncPanel(city);

      // 更新按鈕文字
      if (dropLabel) dropLabel.textContent = `${city} ▼`;

      // 點擊 li 後收合 dropdown list
      dropContainer.classList.remove("is-open");
    });

    frag.appendChild(li);
  });

  dropList.appendChild(frag);

  // 點擊 container 打開/收合 dropdown list
  dropContainer.addEventListener("click", (e) => {
    // 點擊 li 時不在這裡 toggle（li 自己處理）
    if (e.target.closest(".nav-dropcontainer-li")) return;
    dropContainer.classList.toggle("is-open");
  });

  // 點擊 list 以外部分收合 dropdown list
  document.addEventListener("click", (e) => {
    if (!dropContainer.contains(e.target)) {
      dropContainer.classList.remove("is-open");
    }
  });
});
