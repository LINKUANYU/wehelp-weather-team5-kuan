CREATE DATABASE IF NOT EXISTS `weather`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE `weather`;

-- 全縣市
CREATE TABLE IF NOT EXISTS `locations` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `city_name` VARCHAR(20) NOT NULL UNIQUE COMMENT '縣市名稱，如：嘉義縣',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. 修改後的 天氣代碼對照表 (Weather_Types)
CREATE TABLE IF NOT EXISTS `weather_types` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '自動增量ID',
    `weather_code` VARCHAR(10) NOT NULL COMMENT '氣象署天氣代碼，例如：01',
    `icon_path` VARCHAR(255) DEFAULT NULL COMMENT '對應的圖片檔名或路徑',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 建立索引以提升查詢速度
    INDEX `idx_weather_code` (`weather_code`)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 存放 36 小時預報
CREATE TABLE IF NOT EXISTS `weather_forecasts` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `location_id` INT NOT NULL COMMENT '對應 locations 表的 ID',
    `start_time` DATETIME NOT NULL COMMENT '預報起始時間',
    `end_time` DATETIME NOT NULL COMMENT '預報結束時間',
    `weather` VARCHAR(50) COMMENT '當時段天氣現象',
    `weather_code` VARCHAR(10) COMMENT '對應 weather_types 表的代碼',
    `rain_pro` INT COMMENT '降雨機率',
    `min_temp` INT COMMENT '最低溫度',
    `max_temp` INT COMMENT '最高溫度',
    `comfort` VARCHAR(50) COMMENT '舒適度描述',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 外鍵關聯：確保地點與代碼必須存在於母表
    CONSTRAINT `fk_forecast_location` FOREIGN KEY (`location_id`) REFERENCES `locations` (`id`) ON DELETE CASCADE,

    -- 重要：建立唯一索引，這是實現 ON DUPLICATE KEY UPDATE 的關鍵
    -- 同一個地點在同一個時段內，只會有一筆資料
    UNIQUE KEY `idx_location_time_range` (`location_id`, `start_time`, `end_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
