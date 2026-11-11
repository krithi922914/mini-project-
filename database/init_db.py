import sqlite3
import os


# ========================================================
# PATHS
# ========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "tourism.db"
)


# ========================================================
# CONNECT
# ========================================================

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()


# ========================================================
# PLACES
# ========================================================

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

    review_count INTEGER DEFAULT 0,

    popularity INTEGER DEFAULT 0,

    local_discovery_score REAL DEFAULT 0,

    duration REAL DEFAULT 1,

    travel_style TEXT,

    crowd_level TEXT DEFAULT 'medium',

    latitude REAL,

    longitude REAL,

    verified INTEGER DEFAULT 0,

    active INTEGER DEFAULT 1

)
""")


# ========================================================
# ACCOMMODATIONS
# Hotels / Resorts / Homestays
# ========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS accommodations (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    destination TEXT NOT NULL,

    accommodation_type TEXT NOT NULL,

    price_per_night REAL DEFAULT 0,

    rating REAL DEFAULT 0,

    review_count INTEGER DEFAULT 0,

    description TEXT,

    amenities TEXT,

    latitude REAL,

    longitude REAL,

    verified INTEGER DEFAULT 0,

    availability INTEGER DEFAULT 1,

    active INTEGER DEFAULT 1

)
""")


# ========================================================
# TOUR GUIDES
# ========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS guides (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    destination TEXT NOT NULL,

    languages TEXT,

    specialization TEXT,

    experience_years INTEGER DEFAULT 0,

    price_per_tour REAL DEFAULT 0,

    rating REAL DEFAULT 0,

    description TEXT,

    phone TEXT,

    verified INTEGER DEFAULT 0,

    availability INTEGER DEFAULT 1,

    active INTEGER DEFAULT 1

)
""")


# ========================================================
# TOUR PACKAGES
# ========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS packages (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    destination TEXT NOT NULL,

    description TEXT,

    duration_hours REAL DEFAULT 1,

    price_per_person REAL DEFAULT 0,

    rating REAL DEFAULT 0,

    includes TEXT,

    provider_name TEXT,

    verified INTEGER DEFAULT 0,

    availability INTEGER DEFAULT 1,

    active INTEGER DEFAULT 1

)
""")


# ========================================================
# FOOD
# ========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS food_places (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    destination TEXT NOT NULL,

    cuisine TEXT,

    food_type TEXT,

    price_range TEXT,

    rating REAL DEFAULT 0,

    review_count INTEGER DEFAULT 0,

    description TEXT,

    speciality TEXT,

    latitude REAL,

    longitude REAL,

    verified INTEGER DEFAULT 0,

    active INTEGER DEFAULT 1

)
""")


# ========================================================
# LOCAL BUSINESSES
# ========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS businesses (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    destination TEXT NOT NULL,

    business_type TEXT NOT NULL,

    owner_name TEXT,

    phone TEXT,

    email TEXT,

    description TEXT,

    website TEXT,

    verified INTEGER DEFAULT 0,

    active INTEGER DEFAULT 1

)
""")


# ========================================================
# USER FEEDBACK
# ========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_feedback (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    destination_name TEXT NOT NULL,

    action TEXT NOT NULL,

    rating INTEGER,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")


# ========================================================
# SAVE
# ========================================================

connection.commit()
connection.close()


print("SmartTour tourism database created successfully!")