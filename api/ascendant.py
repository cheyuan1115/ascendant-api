from flask import Flask, request, jsonify
import swisseph as swe
import datetime

app = Flask(__name__)

ZODIAC_SIGNS = [
    "牡羊座", "金牛座", "雙子座", "巨蟹座", "獅子座", "處女座",
    "天秤座", "天蝎座", "射手座", "摩羯座", "水瓶座", "雙魚座"
]

RULER_TABLE = {
    "牡羊座": "火星", "金牛座": "金星", "雙子座": "水星", "巨蟹座": "月亮",
    "獅子座": "太陽", "處女座": "水星", "天秤座": "金星", "天蝎座": "冥王星",
    "射手座": "木星", "摩羯座": "土星", "水瓶座": "天王星", "雙魚座": "海王星"
}

@app.route("/api/ascendant", methods=["GET"])
def full_astrology():
    try:
        # 取得參數
        date_str = request.args.get("date")     # 格式：YYYY-MM-DD
        time_str = request.args.get("time")     # 格式：HH:MM
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))

        # 合併時間
        dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)

        # 星曆檔目錄（使用預設目前目錄）
        swe.set_ephe_path(".")

        # 上升星座
        asc = swe.houses(jd, lat, lon)[0][0]
        asc_sign_index = int(asc // 30) % 12
        asc_sign = ZODIAC_SIGNS[asc_sign_index]

        # 命主星與落點
        chart_ruler_planet = RULER_TABLE[asc_sign]
        planet_ids = {
            "太陽": swe.SUN, "月亮": swe.MOON, "水星": swe.MERCURY,
            "金星": swe.VENUS, "火星": swe.MARS, "木星": swe.JUPITER,
            "土星": swe.SATURN, "天王星": swe.URANUS, "海王星": swe.NEPTUNE, "冥王星": swe.PLUTO
        }
        chart_ruler_deg = swe.calc_ut(jd, planet_ids[chart_ruler_planet])[0][0]
        chart_ruler_sign = ZODIAC_SIGNS[int(chart_ruler_deg // 30) % 12]

        # 太陽月亮星座
        sun_deg = swe.calc_ut(jd, swe.SUN)[0][0]
        sun_sign = ZODIAC_SIGNS[int(sun_deg // 30) % 12]

        moon_deg = swe.calc_ut(jd, swe.MOON)[0][0]
        moon_sign = ZODIAC_SIGNS[int(moon_deg // 30) % 12]

        # 凱龍星與宮位
        CHIRON_ID = 2060
        chiron_deg = swe.calc_ut(jd, CHIRON_ID)[0][0]
        chiron_sign = ZODIAC_SIGNS[int(chiron_deg // 30) % 12]

        houses, _ = swe.houses(jd, lat, lon)
        chiron_house = None
        for i in range(12):
            start = houses[i]
            end = houses[(i + 1) % 12]
            if start < end:
                if start <= chiron_deg < end:
                    chiron_house = i + 1
                    break
            else:  # 跨越0度（例如第12宮）
                if chiron_deg >= start or chiron_deg < end:
                    chiron_house = i + 1
                    break

        # 回傳結果
        response = jsonify({
            "sun": sun_sign,
            "moon": moon_sign,
            "ascendant": asc_sign,
            "chartRuler": {
                "planet": chart_ruler_planet,
                "sign": chart_ruler_sign
            },
            "chiron": {
                "sign": chiron_sign,
                "house": chiron_house
            }
        })
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    except Exception as e:
        error_response = jsonify({"error": str(e)})
        error_response.headers.add("Access-Control-Allow-Origin", "*")
        return error_response, 500
