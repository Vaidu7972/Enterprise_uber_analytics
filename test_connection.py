from utils.db_connection import get_engine

engine = get_engine()

try:
    connection = engine.connect()

    print("Database Connected Successfully!")

    connection.close()

except Exception as e:
    print("Connection Failed!")
    print(e)