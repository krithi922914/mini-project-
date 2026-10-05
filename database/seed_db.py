import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "tourism.db")

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

# -----------------------------
# TOURIST PLACES
# -----------------------------

places = [
    (
        "Mysore Palace",
        "Mysore",
        "Historical",
        "History",
        "A famous royal palace and major attraction of Mysore.",
        100,
        4.8,
        95,
        2,
        "Cultural"
    ),
    (
        "Chamundi Hill",
        "Mysore",
        "Religious",
        "Culture",
        "A scenic hill known for Chamundeshwari Temple and city views.",
        0,
        4.7,
        90,
        2,
        "Cultural"
    ),
    (
        "Brindavan Gardens",
        "Mysore",
        "Nature",
        "Nature",
        "Beautiful gardens known for landscaped areas and evening illumination.",
        50,
        4.6,
        88,
        3,
        "Relaxed"
    ),
    (
        "Mysore Zoo",
        "Mysore",
        "Wildlife",
        "Nature",
        "A popular zoological garden featuring a variety of animals.",
        100,
        4.5,
        85,
        3,
        "Relaxed"
    ),
    (
        "Devaraja Market",
        "Mysore",
        "Market",
        "Food",
        "A traditional market known for local products, flowers and food items.",
        0,
        4.4,
        80,
        2,
        "Cultural"
    ),
    (
        "St. Philomena's Cathedral",
        "Mysore",
        "Architecture",
        "Culture",
        "A historic cathedral known for its distinctive Gothic architecture.",
        0,
        4.6,
        78,
        1.5,
        "Cultural"
    ),
    (
        "Karanji Lake",
        "Mysore",
        "Nature",
        "Nature",
        "A peaceful lake area suitable for relaxing and bird watching.",
        50,
        4.4,
        72,
        2,
        "Relaxed"
    ),
    (
        "Railway Museum",
        "Mysore",
        "Museum",
        "History",
        "A museum showcasing railway heritage and historical exhibits.",
        50,
        4.3,
        65,
        2,
        "Cultural"
    ),
    (
        "Ranganathittu Bird Sanctuary",
        "Mysore",
        "Wildlife",
        "Nature",
        "A bird sanctuary offering nature and wildlife experiences.",
        100,
        4.5,
        75,
        3,
        "Adventure"
    ),
    (
        "GRS Fantasy Park",
        "Mysore",
        "Adventure",
        "Adventure",
        "An entertainment and water park with recreational activities.",
        800,
        4.3,
        82,
        5,
        "Adventure"
    ),
    (
        "Mysore Sand Sculpture Museum",
        "Mysore",
        "Museum",
        "Culture",
        "A museum featuring artistic sculptures created using sand.",
        100,
        4.2,
        60,
        1.5,
        "Cultural"
    ),
    (
        "Kukkarahalli Lake",
        "Mysore",
        "Nature",
        "Nature",
        "A peaceful urban lake suitable for walking and relaxation.",
        0,
        4.3,
        55,
        1.5,
        "Relaxed"
    )
]

cursor.executemany("""
INSERT INTO places
(name, destination, category, interest, description,
 price, rating, popularity, duration, travel_style)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", places)


# -----------------------------
# HOTELS
# -----------------------------

hotels = [
    (
        "Hotel Royal Orchid",
        "Mysore",
        "Hotel",
        2500,
        4.4,
        1,
        "Comfortable accommodation for tourists."
    ),
    (
        "Mysore Comfort Inn",
        "Mysore",
        "Budget Hotel",
        1500,
        4.1,
        1,
        "Budget-friendly accommodation."
    ),
    (
        "Heritage Stay Mysore",
        "Mysore",
        "Heritage Hotel",
        3000,
        4.5,
        1,
        "Heritage-style accommodation."
    )
]

cursor.executemany("""
INSERT INTO hotels
(name, destination, category, price_per_night,
 rating, availability, description)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", hotels)


# -----------------------------
# LOCAL BUSINESSES
# -----------------------------

businesses = [
    (
        "Mysore Local Food Tour",
        "Mysore",
        "Food Experience",
        500,
        "Guided local food experience featuring traditional dishes.",
        1
    ),
    (
        "Mysore Heritage Walk",
        "Mysore",
        "Cultural Experience",
        400,
        "Guided walking experience covering important heritage locations.",
        1
    ),
    (
        "Mysore Handicraft Experience",
        "Mysore",
        "Local Experience",
        600,
        "Experience local handicrafts and traditional art.",
        1
    )
]

cursor.executemany("""
INSERT INTO businesses
(name, destination, business_type, price,
 description, availability)
VALUES (?, ?, ?, ?, ?, ?)
""", businesses)


connection.commit()
connection.close()

print("SmartTour tourism data added successfully!")