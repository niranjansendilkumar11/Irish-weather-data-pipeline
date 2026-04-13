import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

#  Config
DB_FILE = "weather_data.db"

#  DB Connection 
def get_engine():
    return create_engine(f"sqlite:///{DB_FILE}")

#  Helper Functions
def categorise_temperature(temp):
    if temp < 0: return "Freezing"
    elif temp < 8: return "Cold"
    elif temp < 14: return "Cool"
    elif temp < 19: return "Mild"
    else: return "Warm"

def categorise_wind(speed):
    if speed < 3.0: return "Calm"
    elif speed < 8.0: return "Breezy"
    elif speed < 14.0: return "Windy"
    else: return "Storm"

def categorise_humidity(hum):
    if hum < 40: return "Dry"
    elif hum < 70: return "Comfortable"
    else: return "Humid"

def categorise_pressure(p):
    if p < 1000: return "Low"
    elif p < 1020: return "Normal"
    else: return "High"

def time_of_day(hour):
    if 5 <= hour < 12: return "Morning"
    elif 12 <= hour < 17: return "Afternoon"
    elif 17 <= hour < 21: return "Evening"
    else: return "Night"

# Feature Extraction 
def extract_features(df):
    df = df.copy()

    df["temp_category"] = df["temp"].apply(categorise_temperature)
    df["wind_category"] = df["wind_speed"].apply(categorise_wind)
    df["humidity_category"] = df["humidity"].apply(categorise_humidity)
    df["pressure_category"] = df["pressure"].apply(categorise_pressure)

    df["feels_diff"] = df["feels_like"] - df["temp"]

    df["datetime"] = pd.to_datetime(df["datetime"])
    df["hour"] = df["datetime"].dt.hour
    df["day"] = df["datetime"].dt.day_name()
    df["time_of_day"] = df["hour"].apply(time_of_day)

    df["comfort_index"] = df["temp"] - ((100 - df["humidity"]) / 5)

    return df

# Create Features Table
def create_features_table(engine):
    sql = text("""
        CREATE TABLE IF NOT EXISTS weather_features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            datetime TEXT,
            temp REAL,
            temp_category TEXT,
            feels_like REAL,
            feels_diff REAL,
            humidity INTEGER,
            humidity_category TEXT,
            pressure INTEGER,
            pressure_category TEXT,
            wind_speed REAL,
            wind_category TEXT,
            weather TEXT,
            description TEXT,
            hour INTEGER,
            day TEXT,
            time_of_day TEXT,
            comfort_index REAL
        )
    """)
    with engine.connect() as conn:
        conn.execute(sql)
        conn.commit()

def remove_feature_duplicates(engine):
    print("Removing duplicate rows from weather_features...")

    sql = """
    DELETE FROM weather_features
    WHERE rowid NOT IN (
        SELECT MIN(rowid)
        FROM weather_features
        GROUP BY city, datetime
    );
    """

    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()

    print("Duplicates removed from weather_features.")

# Load + Transform + Save 
def run_feature_extraction():
    print(f"\n[{datetime.now()}] Starting feature extraction...")

    engine = get_engine()

    df = pd.read_sql("SELECT * FROM weather_hourly", engine)

    if df.empty:
        print("No data found in weather_hourly")
        return

    # Apply features
    df_features = extract_features(df)

    df_final = df_features[[
        "city", "datetime", "temp", "temp_category",
        "feels_like", "feels_diff",
        "humidity", "humidity_category",
        "pressure", "pressure_category",
        "wind_speed", "wind_category",
        "weather", "description",
        "hour", "day", "time_of_day",
        "comfort_index"
    ]]

    df_final = df_final.drop_duplicates()

    create_features_table(engine)

    df_final.to_sql("weather_features", con=engine, if_exists="append", index=False)

    #Remove duplicates from DB
    remove_feature_duplicates(engine)

    print(f"Feature extraction completed. Rows inserted: {len(df_final)}")
if __name__ == "__main__":
    run_feature_extraction()