import { WeatherController } from "./WeatherController.js";
import { getWeather } from "./weatherModel.js";

// patch WeatherController.init
// 確保 index.js 建 controller 時可以拿到實例
const __originalInit = WeatherController.prototype.init;

WeatherController.prototype.init = async function patchedInit() {
  // 拿到 controller
  window.__weatherController = this;

  if (!this.__initPromise) {
    this.__initPromise = __originalInit.call(this);
  }
  return this.__initPromise;
};

async function syncRightPanel(cityKey) {
  const c = window.__weatherController;
  if (!c) return;
  // 等待初始化
  if (c.__initPromise) await c.__initPromise;

  // 更新面板：縣市、三時段天氣、圖表
  c.setWeather(cityKey);
  c.updateChart(cityKey);
}

function pickCurrentForecast(cityObj) {
  return cityObj?.forcasts?.[0] ?? null;
}

function getIconSrc(code) {
  if (!code) return "static/img/cloudy.png";
  return `static/img/${code}.png`;
}

// 移除所有縣市的 highlight
function clearActivePaths() {
  document
    .querySelectorAll("svg .path.is-active")
    .forEach((p) => p.classList.remove("is-active"));
}

// highlight 某個縣市（ targetSelector = data-target 指到的 g )
function setActivePath(targetSelector) {
  const region = document.querySelector(targetSelector);
  if (!region) return;

  // 處理多個 path
  region.querySelectorAll(".path").forEach((p) => {
    p.classList.add("is-active");
  });
}

// 隱藏文字框
function clearActive(container) {
  container.querySelectorAll(".icon_zone.is-active").forEach((el) => {
    el.classList.remove("is-active");
  });
  clearActivePaths();
}

// 點擊 icon 或是 svg 後隱藏圖片並顯示文字框
document.addEventListener("DOMContentLoaded", async () => {
  const overlay = document.getElementById("map-weather-overlay");
  if (!overlay) return;

  const icons = Array.from(overlay.querySelectorAll(".icon_zone"));
  if (icons.length === 0) return;

  const all = await getWeather();
  if (!Array.isArray(all)) return;

  icons.forEach((icon) => {
    const cityKey = icon.dataset.city;
    const targetSelector = icon.dataset.target;

    const cityObj = all.find((x) => x.city === cityKey);
    const current = pickCurrentForecast(cityObj);

    const weatherText = current?.weather ?? "無資料";
    const iconSrc = getIconSrc(current?.weather_code);

    // 寫入文字與圖片
    icon.querySelector(".desc").textContent = weatherText;

    const img = icon.querySelector("img");
    img.src = iconSrc;
    img.alt = `${icon.querySelector(".city").textContent}：${weatherText}`;
    img.title = img.alt;

    // 點擊 icon 切換
    icon.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      clearActive(overlay);
      icon.classList.add("is-active");
      setActivePath(targetSelector);
      syncRightPanel(cityKey);
    });

    // 點擊對應縣市切換
    const region = document.querySelector(targetSelector);
    if (region) {
      region.addEventListener("click", (e) => {
        e.preventDefault?.();
        e.stopPropagation?.();
        clearActive(overlay);
        icon.classList.add("is-active");
        setActivePath(targetSelector);
        syncRightPanel(cityKey);
      });
    }
  });

  // 點擊空白處關閉全部
  document.addEventListener("click", (e) => {
    const inMap = e.target.closest?.("#map");
    const inOverlay = e.target.closest?.("#map-weather-overlay");
    if (inMap && !inOverlay) clearActive(overlay);
  });
});
