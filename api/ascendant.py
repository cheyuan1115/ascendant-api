
from flask import Flask, request, jsonify
import swisseph as swe
import datetime

app = Flask(__name__)

ZODIAC_SIGNS = [
    "牡羊座", "金牛座", "雙子座", "巨蟹座", "獅子座", "處女座",
    "天秤座", "天蠍座", "射手座", "摩羯座", "水瓶座", "雙魚座"
]

@app.route("/api/ascendant", methods=["GET"])
def ascendant():
    try:
        date_str = request.args.get("date")  # YYYY-MM-DD
        time_str = request.args.get("time")  # HH:MM
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))

        # 日期與時間合併
        dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

        # 計算儒略日
        jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)

        # 使用預設星曆
        swe.set_ephe_path('.')  # 記得上傳 sepl_18.se1 到根目錄或設定目錄

        # 使用 Placidus 宮位系統計算上升點
        asc = swe.houses(jd, lat, lon)[0][0]  # 返回第一宮起始度數

        sign = int(asc // 30) % 12
response = jsonify({ "ascendant": ZODIAC_SIGNS[sign] })
response.headers.add('Access-Control-Allow-Origin', '*')
return response

