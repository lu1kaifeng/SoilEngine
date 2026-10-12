import sqlite3

def dump_sqlite_sample(db_path, output_txt_path, limit=100):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all non-system table names
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%';
    """)
    tables = [row[0] for row in cursor.fetchall()]

    with open(output_txt_path, 'w', encoding='utf-8') as f:
        for table in tables:
            f.write(f"{'=' * 60}\n")
            f.write(f"TABLE: {table}\n")
            f.write(f"{'=' * 60}\n")

            # Query up to `limit` rows (double quotes escape tables with spaces/keywords)
            cursor.execute(f'SELECT * FROM "{table}" LIMIT ?', (limit,))
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            # Write header and rows
            f.write(f"Columns: {', '.join(columns)}\n")
            f.write("-" * 60 + "\n")

            if rows:
                for row in rows:
                    f.write(f"{row}\n")
            else:
                f.write("(Table is empty)\n")

            f.write("\n\n")

    conn.close()
    print(f"Done! Dumped table samples to '{output_txt_path}'.")

# Usage: Replace with your actual database and output filenames
dump_sqlite_sample(r'F:\soil_data_reporting\soil_engine.sqlite', 'database_dump.txt')