import pandas as pd
import random

dates = pd.date_range(
    start="2024-01-01",
    end="2024-12-31"
)

weather = []

for date in dates:
    weather.append({
        "weather_date": date.date(),
        "temperature": round(random.uniform(-5, 35), 2),
        "humidity": round(random.uniform(30, 95), 2),
        "rainfall": round(random.uniform(0, 50), 2),
        "wind_speed": round(random.uniform(0, 25), 2)
    })

df = pd.DataFrame(weather)

df.to_csv(
    "data/raw/weather.csv",
    index=False
)

print("weather.csv created successfully")