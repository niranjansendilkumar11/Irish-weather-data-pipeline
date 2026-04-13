import os
import time
import requests
import pandas as pd
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta, timezone
from config import API_KEY, DB_FILE
print("API:", API_KEY)

IRISH_CITIES = [
    {"city": "Dublin", "lat": 53.3498, "lon": -6.2603},
    {"city": "Cork", "lat": 51.8985, "lon": -8.4756},
    {"city": "Galway", "lat": 53.2707, "lon": -9.0568},
    {"city": "Limerick", "lat": 52.6638, "lon": -8.6267},
    {"city": "Waterford", "lat": 52.2593, "lon": -7.1101},
    {"city": "Drogheda", "lat": 53.7179, "lon": -6.3561},
    {"city": "Dundalk", "lat": 54.0007, "lon": -6.4059},
    {"city": "Swords", "lat": 53.4597, "lon": -6.2181},
    {"city": "Bray", "lat": 53.2028, "lon": -6.0983},
    {"city": "Navan", "lat": 53.6528, "lon": -6.6814},
    {"city": "Kilkenny", "lat": 52.6541, "lon": -7.2448},
    {"city": "Ennis", "lat": 52.8463, "lon": -8.9807},
    {"city": "Tralee", "lat": 52.2711, "lon": -9.7026},
    {"city": "Carlow", "lat": 52.8365, "lon": -6.9341},
]

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

#  Fetch Hourly Data 
def fetch_hourly_data(city):
    records = []

    params = {
        "lat": city["lat"],
        "lon": city["lon"],
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        r = requests.get(BASE_URL, params=params, timeout=10)

        if r.status_code == 200:
            data = r.json()

            base_time = datetime.now()

            # 🔁 simulate last 5 hours
            for i in range(5):
                records.append({
                    "city": city["city"],
                    "datetime": base_time - timedelta(hours=i),
                    "temp": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"],
                    "wind_speed": data["wind"]["speed"],
                    "weather": data["weather"][0]["main"],
                    "description": data["weather"][0]["description"]
                })

        else:
            print(f"Failed {city['city']} ({r.status_code})")

    except Exception as e:
        print(f"Error {city['city']}: {e}")

    return records


#  Helper functions
def categorise_temperature(temp):
    if temp < 0: return "Freezing"
    elif temp < 8: return "Cold"
    elif temp < 14: return "Cool"
    elif temp < 19: return "Mild"
    else: return "Warm"

def categorise_wind():
    if speed < 3.0: return "Calm"
    elif speed < 8.0: return "Breezy"
    elif speed < 14.0: return "Windy"
    else: return "Storm"

def categorise_humidity(hum):
    if hum < 40: return "Dry"
    elif hum < 70: return "Comfortable"
    else: return "Humid"

def convert_unix(unix_time):
    return datetime.fromtimestamp(unix_time).strftime('%H:%M:%S')

def calc_daylight(sunrise, sunset):
    return round((sunset - sunrise) / 3600, 2)

# Fetch API 
def fetch_city_weather(city_name):
    params = {"q": city_name, "appid": API_KEY, "units": "metric"}
    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        if r.status_code == 200:
            d = r.json()
            return {
                "city": d["name"],
                "country": d["sys"]["country"],
                "latitude": d["coord"]["lat"],
                "longitude": d["coord"]["lon"],
                "temp_celsius": d["main"]["temp"],
                "feels_like": d["main"]["feels_like"],
                "temp_min": d["main"]["temp_min"],
                "temp_max": d["main"]["temp_max"],
                "humidity": d["main"]["humidity"],
                "pressure": d["main"]["pressure"],
                "visibility": d.get("visibility", None),
                "wind_speed": d["wind"]["speed"],
                "wind_degree": d["wind"].get("deg", None),
                "weather_main": d["weather"][0]["main"],
                "weather_desc": d["weather"][0]["description"],
                "cloud_coverage": d["clouds"]["all"],
                "sunrise": d["sys"]["sunrise"],
                "sunset": d["sys"]["sunset"],
                "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            print(f"Failed {city_name}: {r.status_code}")
            return None
    except Exception as e:
        print(f"Error {city_name}: {e}")
        return None

#  Transform 
def transform_weather_data(df):
    df2 = df.copy()
    df2["sunrise_time"] = df2["sunrise"].apply(convert_unix)
    df2["sunset_time"] = df2["sunset"].apply(convert_unix)
    df2["daylight_hours"] = df2.apply(lambda r: calc_daylight(r["sunrise"], r["sunset"]), axis=1)
    df2["temp_category"] = df2["temp_celsius"].apply(categorise_temperature)
    df2["wind_category"] = df2["wind_speed"].apply(categorise_wind)
    df2["humidity_category"] = df2["humidity"].apply(categorise_humidity)
    df2["visibility_km"] = (df2["visibility"] / 1000).round(2)
    df2.drop(columns=["sunrise", "sunset", "visibility"], inplace=True)
    return df2

# ── SQLite DB ───────────────────────────────────────────────────────
def get_engine():
    return create_engine(f"sqlite:///{DB_FILE}")

def create_table(engine):
    sql = text("""
        CREATE TABLE IF NOT EXISTS weather_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            country TEXT,
            latitude REAL,
            longitude REAL,
            temp_celsius REAL,
            feels_like REAL,
            temp_min REAL,
            temp_max REAL,
            humidity INTEGER,
            pressure INTEGER,
            wind_speed REAL,
            wind_degree REAL,
            weather_main TEXT,
            weather_desc TEXT,
            cloud_coverage INTEGER,
            fetched_at TEXT,
            sunrise_time TEXT,
            sunset_time TEXT,
            daylight_hours REAL,
            temp_category TEXT,
            wind_category TEXT,
            humidity_category TEXT,
            visibility_km REAL
        )
    """)
    with engine.connect() as conn:
        conn.execute(sql)
        conn.commit()
    print("SQLite table ready.")

def load_to_db(df, engine):
    df.to_sql("weather_data", con=engine, if_exists="append", index=False)
    print(f"Saved {len(df)} rows.")


def create_table(engine):
    sql = text("""
        CREATE TABLE IF NOT EXISTS weather_hourly (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            datetime TEXT,
            temp REAL,
            feels_like REAL,
            humidity INTEGER,
            pressure INTEGER,
            wind_speed REAL,
            weather TEXT,
            description TEXT
        )
    """)
    with engine.connect() as conn:
        conn.execute(sql)
        conn.commit()
    print("Hourly table ready.")

def load_to_db(df, engine):
    df.to_sql("weather_hourly", con=engine, if_exists="append", index=False)
    print(f"Saved {len(df)} rows.")

def remove_duplicates(engine):
    print("Removing duplicate rows...")

    sql = """
    DELETE FROM weather_hourly
    WHERE rowid NOT IN (
        SELECT MIN(rowid)
        FROM weather_hourly
        GROUP BY city, datetime
    );
    """

    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()

    print("Duplicates removed.")

# ── Main ────────────────────────────────────────────────────────────



def run_pipeline():
    print(f"\n[{datetime.now()}] Starting hourly pipeline...")

    all_records = []

    for city in IRISH_CITIES:
        print(f"Fetching {city['city']}...")
        recs = fetch_hourly_data(city)
        all_records.extend(recs)

    df = pd.DataFrame(all_records)

    engine = get_engine()
    create_table(engine)
    load_to_db(df, engine)

    # ✅ Remove duplicates AFTER insert
    remove_duplicates(engine)

    print(f"[{datetime.now()}] Done. Total rows: {len(df)}")
    

if __name__ == "__main__":
    run_pipeline()