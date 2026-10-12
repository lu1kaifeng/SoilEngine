import sqlite3

# Update with your database file path
DB_PATH = r'F:\soil_data_reporting\soil_reporting.sqlite'
NEW_DB_PATH = r'F:\soil_data_reporting\soil_engine.sqlite'
TABLES = [
    "bulk_density", "carbon", "change_tracking_history", "nitrogen",
    "ph_ec", "sampling_points", "sites", "sites_csv", "texture", "weom"
]


def verify_migration():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(f"ATTACH DATABASE '{NEW_DB_PATH}' AS new_schema;")

    all_passed = True

    print(f"{'TABLE':<25} | {'COUNT (MAIN)':<12} | {'COUNT (NEW)':<12} | STATUS")
    print("-" * 65)

    for table in TABLES:
        # Get column names from main table (excludes 'id' present in new_schema)
        cursor.execute(f"PRAGMA main.table_info('{table}')")
        cols = [f'"{row[1]}"' for row in cursor.fetchall()]
        col_list = ", ".join(cols)

        # 1. Row count comparison
        cursor.execute(f"SELECT COUNT(*) FROM main.{table}")
        count_main = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM new_schema.{table}")
        count_new = cursor.fetchone()[0]

        if count_main != count_new:
            print(f"{table:<25} | {count_main:<12} | {count_new:<12} | ❌ COUNT MISMATCH")
            all_passed = False
            continue

        # 2. Data content comparison (main -> new)
        diff_1 = cursor.execute(f"""
            SELECT {col_list} FROM main.{table}
            EXCEPT
            SELECT {col_list} FROM new_schema.{table}
        """).fetchall()

        # 3. Data content comparison (new -> main)
        diff_2 = cursor.execute(f"""
            SELECT {col_list} FROM new_schema.{table}
            EXCEPT
            SELECT {col_list} FROM main.{table}
        """).fetchall()

        if diff_1 or diff_2:
            print(f"{table:<25} | {count_main:<12} | {count_new:<12} | ❌ CONTENT MISMATCH")
            all_passed = False
        else:
            print(f"{table:<25} | {count_main:<12} | {count_new:<12} | MATCH")

    conn.close()

    if all_passed:
        print("\nAll tables in new_schema match main perfectly!")


if __name__ == "__main__":
    verify_migration()