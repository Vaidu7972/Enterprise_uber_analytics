import sys
import pathlib

# Add workspace root to sys.path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent))

import argparse
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import text
from utils.db_connection import get_engine

engine = get_engine()
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
DEMO_CSV_PATH = BASE_DIR / "data" / "raw" / "incremental_demo_trip.csv"
DEMO_SOURCE_FILE = "incremental_demo_trip.csv"


def cleanup_demo_record():
    """Safely delete demo test record from bronze.trip_raw and remove demo CSV file."""
    print("\n" + "=" * 65)
    print(" CLEANUP MODE: Removing Incremental Demo Test Record ")
    print("=" * 65)
    
    with engine.begin() as conn:
        res = conn.execute(
            text("DELETE FROM bronze.trip_raw WHERE source_file = :source_file"),
            {"source_file": DEMO_SOURCE_FILE},
        )
        print(f"  [OK] Deleted {res.rowcount} demo records from bronze.trip_raw (source_file = '{DEMO_SOURCE_FILE}')")

    if DEMO_CSV_PATH.exists():
        DEMO_CSV_PATH.unlink()
        print(f"  [OK] Removed demo CSV file: {DEMO_CSV_PATH}")

    print("=" * 65 + "\n")


def create_demo_record():
    print("=" * 65)
    print(" PREPARING INCREMENTAL TEST TRIP RECORD ")
    print("=" * 65)

    with engine.connect() as conn:
        current_wm = conn.execute(text("SELECT MAX(pickup_datetime) FROM bronze.trip_raw")).scalar()
        current_count = conn.execute(text("SELECT COUNT(*) FROM bronze.trip_raw")).scalar()

    print(f"\n[CURRENT DATABASE STATE]")
    print(f"  - Current Watermark MAX(pickup_datetime) : {current_wm}")
    print(f"  - Current Table Count COUNT(*)            : {current_count:,} rows")

    base_time = pd.to_datetime(current_wm) if current_wm is not None else datetime(2024, 1, 31, 23, 59, 0)
    new_pickup = base_time + timedelta(minutes=15)
    new_dropoff = new_pickup + timedelta(minutes=25)

    demo_data = pd.DataFrame([
        {
            "vendor_id": "V_DEMO_TEST",
            "pickup_datetime": new_pickup.strftime("%Y-%m-%d %H:%M:%S"),
            "dropoff_datetime": new_dropoff.strftime("%Y-%m-%d %H:%M:%S"),
            "passenger_count": 2,
            "trip_distance": 6.80,
            "fare_amount": 32.50,
        }
    ])

    DEMO_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    demo_data.to_csv(DEMO_CSV_PATH, index=False)

    print(f"\n[DEMO RECORD CREATED]")
    print(f"  - Vendor ID         : V_DEMO_TEST")
    print(f"  - Pickup Datetime   : {new_pickup} (Greater than watermark: {current_wm})")
    print(f"  - Dropoff Datetime  : {new_dropoff}")
    print(f"  - Saved CSV File    : {DEMO_CSV_PATH}")

    print("\n" + "=" * 65)
    print(" NEXT STEP TO RUN INCREMENTAL LOAD ")
    print("=" * 65)
    print(" Run load_trip_data in demo mode using:")
    print("   INCREMENTAL_DEMO_MODE=true python -m scripts.ingestion.load_trip_data")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create safe incremental trip demo CSV record")
    parser.add_argument("--cleanup", action="store_true", help="Remove demo records from DB and delete demo CSV file")
    args = parser.parse_args()

    if args.cleanup:
        cleanup_demo_record()
    else:
        create_demo_record()
