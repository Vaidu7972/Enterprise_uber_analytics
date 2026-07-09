import pandas as pd
from sqlalchemy import text
from utils.db_connection import get_engine

engine = get_engine()

print("Starting SCD Type 2 for Customer Dimension...")

# Incoming updated customer data
# In real project, this comes from new source file/API/database
customer_updates = pd.DataFrame([
    {
        "customer_id": "C1",
        "customer_name": "Updated Customer One",
        "city": "Mumbai",
        "gender": "Female"
    },
    {
        "customer_id": "C2",
        "customer_name": "Updated Customer Two",
        "city": "Pune",
        "gender": "Male"
    },
    {
        "customer_id": "C6000",
        "customer_name": "New Customer Added",
        "city": "Delhi",
        "gender": "Female"
    }
])

with engine.begin() as conn:
    for _, row in customer_updates.iterrows():

        # Get current active customer record
        current_customer = conn.execute(
            text("""
                SELECT
                    customer_key,
                    customer_id,
                    customer_name,
                    city,
                    gender
                FROM gold.dim_customer
                WHERE customer_id = :customer_id
                  AND is_current = TRUE
            """),
            {"customer_id": row["customer_id"]}
        ).mappings().fetchone()

        if current_customer:

            # Check if any value changed
            is_changed = (
                current_customer["customer_name"] != row["customer_name"] or
                current_customer["city"] != row["city"] or
                current_customer["gender"] != row["gender"]
            )

            if is_changed:
                # Step 1: Close old record
                conn.execute(
                    text("""
                        UPDATE gold.dim_customer
                        SET
                            end_date = CURRENT_DATE - INTERVAL '1 day',
                            is_current = FALSE
                        WHERE customer_key = :customer_key
                    """),
                    {"customer_key": current_customer["customer_key"]}
                )

                # Step 2: Insert new current record
                conn.execute(
                    text("""
                        INSERT INTO gold.dim_customer
                        (
                            customer_id,
                            customer_name,
                            city,
                            gender,
                            effective_date,
                            end_date,
                            is_current
                        )
                        VALUES
                        (
                            :customer_id,
                            :customer_name,
                            :city,
                            :gender,
                            CURRENT_DATE,
                            NULL,
                            TRUE
                        )
                    """),
                    {
                        "customer_id": row["customer_id"],
                        "customer_name": row["customer_name"],
                        "city": row["city"],
                        "gender": row["gender"]
                    }
                )

                print(f"SCD2 updated customer: {row['customer_id']}")

            else:
                print(f"No change found for customer: {row['customer_id']}")

        else:
            # Insert completely new customer
            conn.execute(
                text("""
                    INSERT INTO gold.dim_customer
                    (
                        customer_id,
                        customer_name,
                        city,
                        gender,
                        effective_date,
                        end_date,
                        is_current
                    )
                    VALUES
                    (
                        :customer_id,
                        :customer_name,
                        :city,
                        :gender,
                        CURRENT_DATE,
                        NULL,
                        TRUE
                    )
                """),
                {
                    "customer_id": row["customer_id"],
                    "customer_name": row["customer_name"],
                    "city": row["city"],
                    "gender": row["gender"]
                }
            )

            print(f"Inserted new customer: {row['customer_id']}")

print("SCD Type 2 Customer Dimension completed successfully!")