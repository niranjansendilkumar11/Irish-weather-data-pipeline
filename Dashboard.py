from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)
DB_FILE = "weather_data.db"

def query_db(sql, args=()):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(sql, args)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/latest")
def api_latest():
    rows = query_db("""
        SELECT wf.* FROM weather_features wf
        INNER JOIN (
            SELECT city, MAX(datetime) AS max_dt
            FROM weather_features GROUP BY city
        ) latest ON wf.city = latest.city AND wf.datetime = latest.max_dt
        ORDER BY wf.city
    """)
    return jsonify(rows)

@app.route("/api/conditions")
def api_conditions():
    rows = query_db("""
        SELECT weather, COUNT(*) as count
        FROM weather_features
        GROUP BY weather ORDER BY count DESC
    """)
    return jsonify(rows)

@app.route("/api/categories")
def api_categories():
    temp  = query_db("SELECT temp_category as label, COUNT(*) as count FROM weather_features GROUP BY temp_cate>
    wind  = query_db("SELECT wind_category as label, COUNT(*) as count FROM weather_features GROUP BY wind_cate>
    hum   = query_db("SELECT humidity_category as label, COUNT(*) as count FROM weather_features GROUP BY humid>
    press = query_db("SELECT pressure_category as label, COUNT(*) as count FROM weather_features GROUP BY press>
    tod   = query_db("SELECT time_of_day as label, COUNT(*) as count FROM weather_features GROUP BY time_of_day>
    day   = query_db("SELECT day as label, COUNT(*) as count FROM weather_features GROUP BY day")
    return jsonify({"temp": temp, "wind": wind, "humidity": hum, "pressure": press, "time_of_day": tod, "day": >

@app.route("/api/feelsdiff")
def api_feelsdiff():
    rows = query_db("""
        SELECT wf.city, wf.feels_diff, wf.comfort_index FROM weather_features wf
        INNER JOIN (
            SELECT city, MAX(datetime) AS max_dt FROM weather_features GROUP BY city
        ) latest ON wf.city = latest.city AND wf.datetime = latest.max_dt
        ORDER BY wf.city
    """)
    return jsonify(rows)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)