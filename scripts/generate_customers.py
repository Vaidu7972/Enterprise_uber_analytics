# Import the Faker library to generate fake data like names and cities
from faker import Faker

# Import the XML library to create and write XML files
import xml.etree.ElementTree as ET

# Create a Faker object to generate fake customer data
fake = Faker()

# Create the root element (main tag) of the XML file
# <customers>
root = ET.Element("customers")

# Loop 5000 times to create 5000 fake customer records
for i in range(5000):

    # Create a new <customer> element inside <customers>
    customer = ET.SubElement(root, "customer")

    # Create <customer_id> and assign values like C1, C2, C3...
    ET.SubElement(customer, "customer_id").text = f"C{i+1}"

    # Generate a fake customer name
    ET.SubElement(customer, "customer_name").text = fake.name()

    # Randomly assign Male or Female as the customer's gender
    ET.SubElement(customer, "gender").text = fake.random_element(
        elements=("Male", "Female")
    )

    # Generate a fake city name
    ET.SubElement(customer, "city").text = fake.city()

    # Generate a random signup date within the last 5 years
    # Convert the date into string format before storing
    ET.SubElement(customer, "signup_date").text = str(
        fake.date_between(start_date="-5y", end_date="today")
    )

# Create an XML tree using the root element
tree = ET.ElementTree(root)

# Save the XML tree to a file
tree.write(

    # File path where the XML file will be stored
    "data/raw/customers.xml",

    # Save the file using UTF-8 encoding
    encoding="utf-8",

    # Add the XML declaration at the top of the file
    # Example: <?xml version="1.0" encoding="UTF-8"?>
    xml_declaration=True
)

# Print a success message after the XML file is created
print("customers.xml created successfully")