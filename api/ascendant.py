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
        date_str = request.args.get("date")  # yyyy-mm-dd
        time_str = request.args.get("time")  # hh:mm
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))

        dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)
        swe.set_ephe_path(".")
        asc = swe.houses(jd, lat, lon)[0][0]
        sign = int(asc // 30) % 12

        response = jsonify({ "ascendant": ZODIAC_SIGNS[sign] })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    except Exception as e:
        error_response = jsonify({ "error": str(e) })
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500
