from faker import Faker  #import faker to generate fake data like names and cities 
import pandas as pd      

fake = Faker()           #fake object create to generate fake info

drivers = []             #create empty list  to store  driver records

for i in range(5000):    #loop 5000 times to create 5000 fake drivers
    drivers.append({     #add driver details to list
        "driver_id": f"D{i+1}",  #create unique driver ID (D1, D2, D3)
        "driver_name": fake.name(),     #generate fake driver name
        "city": fake.city(),            #generate fake city name
        "rating": round(fake.random.uniform(3.5, 5.0), 2),    #random rating
        "join_date": str(fake.date_between(start_date="-5y", end_date="today"))     # Generate a random joining date within the last 5 years
        # Convert the date into string format before saving
    })
# Convert the list into a Pandas DataFrame
# Then save it as a JSON file

pd.DataFrame(drivers).to_json(      
    "data/raw/drivers.json",
# Save data as a list of JSON objects (one object per driver)
    orient="records",

# Format the JSON file with proper indentation for readability
    indent=4
)

print("Driver file created successfully!")