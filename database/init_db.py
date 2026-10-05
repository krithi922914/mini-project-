import sqlite3
import os


# Get the main SmartTour folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database location
DB_PATH = os.path.join(BASE_DIR, "database", "tourism.db")


# Connect to SQLite database
connection = sqlite3.connect(DB_PATH)

cursor = connection.cursor()


# Create tourism places table
cursor.execute("""
CREATE TABLE IF NOT EXISTS places (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    destination TEXT NOT NULL,
    category TEXT NOT NULL,
    interest TEXT NOT NULL,
    description TEXT,
    price REAL DEFAULT 0,
    rating REAL DEFAULT 0,
    popularity INTEGER DEFAULT 0,
    duration REAL DEFAULT 1,
    travel_style TEXT,
    latitude REAL,
    longitude REAL
)
""")


# Create hotels table
cursor.execute("""
CREATE TABLE IF NOT EXISTS hotels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    destination TEXT NOT NULL,
    category TEXT,
    price_per_night REAL,
    rating REAL,
    availability INTEGER DEFAULT 1,
    description TEXT
)
""")


# Create businesses table
cursor.execute("""
CREATE TABLE IF NOT EXISTS businesses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    destination TEXT NOT NULL,
    business_type TEXT NOT NULL,
    price REAL,
    description TEXT,
    availability INTEGER DEFAULT 1
)
""")


# Save changes
connection.commit()

# Close database
connection.close()

print("SmartTour database created successfully!")