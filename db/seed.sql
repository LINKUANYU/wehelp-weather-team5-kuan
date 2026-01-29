USE `weather`;

-- 1. 初始化縣市資料
INSERT IGNORE INTO `locations` (`city_name`) VALUES
('臺北市'), ('新北市'), ('桃園市'), ('臺中市'), ('臺南市'), ('高雄市'),
('基隆市'), ('新竹縣'), ('新竹市'), ('苗栗縣'), ('彰化縣'), ('南投縣'),
('雲林縣'), ('嘉義縣'), ('嘉義市'), ('屏東縣'), ('宜蘭縣'), ('花蓮縣'),
('臺東縣'), ('澎湖縣'), ('金門縣'), ('連江縣');

-- 2. 初始化天氣代碼 (參考氣象署文件)
INSERT INTO `weather_types` (`weather_code`, `icon_path`) VALUES
('01', 'icon/01.svg'),  -- 不寫static/，以免未來換路徑要改資料，寫在pyhton中
('02', 'icon/02.svg'),
('03', 'icon/03.svg'),
('04', 'icon/04.svg'),
('05', 'icon/05.svg'),
('06', 'icon/06.svg'),
('07', 'icon/07.svg'),
('08', 'icon/08.svg'),
('09', 'icon/09.svg'),
('10', 'icon/10.svg'),
('11', 'icon/11.svg'),
('12', 'icon/12.svg'),
('13', 'icon/13.svg'),
('14', 'icon/14.svg'),
('15', 'icon/15.svg'),
('16', 'icon/16.svg'),
('17', 'icon/17.svg'),
('18', 'icon/18.svg'),
('19', 'icon/19.svg'),
('20', 'icon/20.svg'),
('21', 'icon/21.svg'),
('22', 'icon/22.svg'),
('23', 'icon/23.svg'),
('24', 'icon/24.svg'),
('25', 'icon/25.svg'),
('26', 'icon/26.svg'),
('27', 'icon/27.svg'),
('28', 'icon/28.svg'),
('29', 'icon/29.svg'),
('30', 'icon/30.svg'),
('31', 'icon/31.svg'),
('32', 'icon/32.svg'),
('33', 'icon/33.svg'),
('34', 'icon/34.svg'),
('35', 'icon/35.svg'),
('36', 'icon/36.svg'),
('37', 'icon/37.svg'),
('38', 'icon/38.svg'),
('39', 'icon/39.svg'),
('41', 'icon/41.svg'),
('42', 'icon/42.svg')

