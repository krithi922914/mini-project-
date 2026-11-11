
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "tourism.db")

EXPECTED_TABLES = [
    "places",
    "accommodations",
    "guides",
    "packages",
    "food_places",
    "user_feedback",
]


def main():
    print("\n========== SMARTTOUR DATABASE CHECK ==========\n")

    if not os.path.exists(DB_PATH):
        print("ERROR: Database file not found!")
        print(f"Expected location: {DB_PATH}")
        return

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
    """)

    existing_tables = {
        row[0] for row in cursor.fetchall()
    }

    print(f"Database: {DB_PATH}\n")

    for table in EXPECTED_TABLES:
        if table not in existing_tables:
            print(f"[MISSING] {table}")
            continue

        cursor.execute(f'PRAGMA table_info("{table}")')
        columns = [
            row[1] for row in cursor.fetchall()
        ]

        cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
        count = cursor.fetchone()[0]

        print(f"[OK] {table}: {count} records")
        print(f"     Columns: {', '.join(columns)}")

    print("\n========== CHECK COMPLETE ==========\n")
    connection.close()


if __name__ == "__main__":
    main()
