##Irish Weather Data Pipeline

##Overview
This project is an **end-to-end data pipeline** that collects real-time weather data for major Irish cities, stores it in a database, and performs feature engineering for further analysis and machine learning.

The pipeline follows the **ETL process (Extract → Transform → Load)** and is designed to be modular and scalable.

---

##Features

- Fetch real-time weather data using OpenWeather API  
- Store raw data in SQLite database (`weather_hourly`)  
- Remove duplicate records  
- Perform feature engineering  
- Store processed data in a separate table (`weather_features`)  
- Unit testing for core functions  
- Secure API key using config file  

---

##  Project Structure

```
.
├── data.py # Main ETL pipeline (API → SQLite)
├── feature_extraction.py # Feature engineering script
├── test_data.py # Unit tests
├── config.py # API key & DB config (ignored in Git)
├── onfig_example.py # Sample config file
├── requirements.txt # Dependencies
├── .gitignore # Ignore sensitive files
└── README.md   # Project documentation
```
---

##Setup Instructions

###Clone Repository
git clone https://github.com/your-username/Irish-weather-data-pipeline.git

cd Irish-weather-data-pipeline


---

###Create Virtual Environment (Optional)


python -m venv venv
venv\Scripts\activate # Windows


---

### 3️ Install Dependencies


pip install -r requirements.txt


---

### 4️ Configure API Key

Create a file named `config.py`:


API_KEY = "your_api_key_here"
DB_FILE = "weather_data.db"


---

## How to Run

### Run Data Pipeline


python data.py


This will:
- Fetch weather data
- Store it in `weather_hourly` table
- Remove duplicates

---

### Run Feature Extraction


python feature_extraction.py


This will:
- Read from `weather_hourly`
- Generate new features
- Store in `weather_features`

---

### Run Unit Tests


python test_data.py


---

## Feature Engineering

The following features are generated:

-  Temperature category (Cold, Mild, Warm)
-  Wind category (Calm, Breezy, Windy, Storm)
-  Humidity category
-  Pressure category
-  Time-based features (hour, day, time_of_day)
-  Feels-like difference
-  Comfort index

---

##  Database Schema

###  Raw Table: `weather_hourly`
- city
- datetime
- temp
- humidity
- pressure
- wind_speed
- weather

###  Processed Table: `weather_features`
- temp_category
- wind_category
- humidity_category
- pressure_category
- comfort_index
- time_of_day

---

##  Security

- API keys are stored in `config.py`
- `config.py` is excluded using `.gitignore`

---

##  Testing

Unit tests are implemented using Python’s built-in `unittest` module to validate:

- Temperature categorisation  
- Wind categorisation  
- Humidity categorisation  

---

##  Technologies Used

- Python
- Pandas
- SQLAlchemy
- SQLite
- OpenWeather API

---

##  Future Improvements

- Add real hourly API instead of simulation  
- Deploy pipeline on cloud (GCP/AWS)  
- Build dashboard using Flask or Streamlit  
- Add machine learning model for weather prediction  

---

##  Author

**Niranjan**  

---

##  Acknowledgements

- OpenWeather API  
- Python community  

---
