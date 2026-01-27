import httpx

CWA_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"

SIX_CITIES = ["臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市"]


def pick(elements, name):
    for e in elements:
        if e.get("elementName") == name:
            return e.get("time") or []
    return []


def pval(arr, i):
    if i >= len(arr):
        return None
    return (arr[i].get("parameter") or {}).get("parameterName")


def ptime(arr, i, key):
    if i >= len(arr):
        return None
    return arr[i].get(key)


def to_int_or_none(x):
    try:
        return int(str(x).strip())
    except Exception:
        return None


def weather_emoji(wx_text: str) -> str:
    if not wx_text:
        return "❔"
    t = wx_text

    if "雷" in t:
        return "⛈️"
    if "雨" in t:
        return "🌧️"
    if "霧" in t or "霾" in t:
        return "🌫️"
    if "陰" in t:
        return "☁️"
    if "多雲" in t and "晴" in t:
        return "🌤️"
    if "多雲" in t:
        return "🌥️"
    if "晴" in t:
        return "☀️"

    return "🌡️"


def fetch_city_first_period(city: str, api_key: str):
    if not api_key:
        raise RuntimeError("Missing CWA_API_KEY")

    params = {
        "Authorization": api_key,
        "locationName": city,
        "format": "JSON",
    }
    r = httpx.get(CWA_URL, params=params, timeout=15)
    r.raise_for_status()
    raw = r.json()

    locs = (raw.get("records") or {}).get("location") or []
    if not locs:
        raise RuntimeError(f"No data for {city}")

    L = locs[0]
    elements = L.get("weatherElement") or []

    wx = pick(elements, "Wx")
    pop = pick(elements, "PoP")
    mint = pick(elements, "MinT")
    maxt = pick(elements, "MaxT")

    return {
        "city": L.get("locationName", city),
        "wx": pval(wx, 0) or "—",
        "pop": to_int_or_none(pval(pop, 0)),
        "tmin": to_int_or_none(pval(mint, 0)),
        "tmax": to_int_or_none(pval(maxt, 0)),
        "start": ptime(wx, 0, "startTime"),
        "end": ptime(wx, 0, "endTime"),
    }


def build_highlight(rows):
    max_tmax = [r for r in rows if r.get("tmax") is not None]
    min_tmin = [r for r in rows if r.get("tmin") is not None]
    max_pop = [r for r in rows if r.get("pop") is not None]

    hottest = max(max_tmax, key=lambda r: r["tmax"]) if max_tmax else None
    coldest = min(min_tmin, key=lambda r: r["tmin"]) if min_tmin else None

    parts = []
    if hottest:
        parts.append(f"🔥 最高溫：{hottest['city']} {hottest['tmax']}°C")
    if coldest:
        parts.append(f"🧊 最低溫：{coldest['city']} {coldest['tmin']}°C")

    if max_pop:
        top_pop = max(r["pop"] for r in max_pop)
        top_cities = [r["city"] for r in max_pop if r["pop"] == top_pop]
        city_text = "、".join(top_cities)
        parts.append(f"☔ 降雨最高：{city_text} {top_pop}%")

    return "｜".join(parts) if parts else "（今日重點：資料不足）"


def make_table(rows):
    city_short = {
        "臺北市": "臺北",
        "新北市": "新北",
        "桃園市": "桃園",
        "臺中市": "臺中",
        "臺南市": "臺南",
        "高雄市": "高雄",
    }

    def s(x):
        return "—" if x is None else str(x)

    lines = []
    header = f"{'城市':<4}  {'天氣':<10}  {'PoP%':>5}  {'T(°C)':>9}  "
    lines.append(header)
    lines.append("-" * len(header))

    for r in rows:
        city = city_short.get(r.get("city"), (r.get("city") or "")[:2])
        wx = r.get("wx") or "—"

        pop = "—" if r.get("pop") is None else str(r["pop"])
        pop_cell = f"{pop:>5}"

        tmin = s(r.get("tmin"))
        tmax = s(r.get("tmax"))
        temp_cell = f"{tmin}~{tmax}"
        temp_cell = f"{temp_cell:>9}"

        emo = weather_emoji(wx)
        lines.append(f"{city:<4}  {wx:<10}  {pop_cell}  {temp_cell}  {emo}")

    return "```text\n" + "\n".join(lines) + "\n```"


def format_message(rows):
    start = rows[0].get("start") if rows else None
    end = rows[0].get("end") if rows else None
    time_range = f"{start} ~ {end}" if start and end else "（今日時段）"

    highlight = build_highlight(rows)
    table = make_table(rows)

    msg = []
    msg.append("📢 **六都今日天氣重點**")
    msg.append(highlight)
    msg.append("")
    msg.append(f"🕒 {time_range}")
    msg.append("")
    msg.append(table)
    msg.append("")
    msg.append("資料來源：中央氣象署 OpenData（今明 36 小時 / 第一時段）")
    return "\n".join(msg).strip()


def build_embed(rows):
    start = rows[0].get("start") if rows else None
    end = rows[0].get("end") if rows else None
    time_range = f"{start} ~ {end}" if start and end else "（今日時段）"

    highlight = build_highlight(rows)

    city_short = {
        "臺北市": "臺北",
        "新北市": "新北",
        "桃園市": "桃園",
        "臺中市": "臺中",
        "臺南市": "臺南",
        "高雄市": "高雄",
    }

    def s(x):
        return "—" if x is None else str(x)

    lines = []
    for r in rows:
        city = city_short.get(r.get("city"), (r.get("city") or "")[:2])
        wx = r.get("wx") or "—"
        pop = "—" if r.get("pop") is None else f"{r['pop']}%"
        temp = f"{s(r.get('tmin'))}~{s(r.get('tmax'))}°C"
        emo = weather_emoji(wx)
        lines.append(f"{emo} **{city}**｜{wx}｜🌧️ {pop}｜🌡️ {temp}")

    desc = "\n".join(lines) if lines else "（無資料）"

    embed = {
        "title": "六都今日天氣重點",
        "description": f"{highlight}\n\n🕒 {time_range}\n\n{desc}",
        "footer": {"text": "資料來源：中央氣象署 OpenData（今明 36 小時 / 第一時段）"},
    }
    return embed


def send_webhook(webhook_url: str, content: str = None, embeds: list = None):
    if not webhook_url:
        raise RuntimeError("Missing DISCORD_WEBHOOK_URL")

    payload = {}
    if content:
        payload["content"] = content
    if embeds:
        payload["embeds"] = embeds

    r = httpx.post(webhook_url, json=payload, timeout=10)
    r.raise_for_status()


def build_rows_for_six_cities(api_key: str):
    rows = []
    for city in SIX_CITIES:
        try:
            rows.append(fetch_city_first_period(city, api_key))
        except Exception:
            rows.append(
                {
                    "city": city,
                    "wx": "取得失敗",
                    "pop": None,
                    "tmin": None,
                    "tmax": None,
                    "start": None,
                    "end": None,
                }
            )
    return rows


def push_six_cities_embed(api_key: str, webhook_url: str):
    rows = build_rows_for_six_cities(api_key)
    embed = build_embed(rows)
    send_webhook(webhook_url, embeds=[embed])
    return rows
