import { WeatherController } from "./WeatherController.js";

document.addEventListener("DOMContentLoaded", () => {

  // 初始化天氣面板主邏輯
  const controller = new WeatherController();
  controller.init();

});