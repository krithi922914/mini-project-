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


connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()


# ========================================================
# PLACES
# ========================================================

places = [

    # ---------------- BENGALURU ----------------

    (
        "Bugle Rock Park",
        "Bengaluru",
        "Nature",
        "Nature",
        "A rocky park area known for greenery, walking paths and natural surroundings.",
        0,
        4.5,
        1200,
        55,
        88,
        2,
        "Relaxed",
        "low",
        12.9416,
        77.5668,
        1
    ),

    (
        "Sankey Tank",
        "Bengaluru",
        "Lake",
        "Nature",
        "A peaceful urban lake suitable for relaxed walks and scenic views.",
        20,
        4.3,
        900,
        60,
        84,
        2,
        "Relaxed",
        "medium",
        13.0035,
        77.5762,
        1
    ),

    (
        "Nrityagram",
        "Bengaluru",
        "Culture",
        "Culture",
        "A cultural centre known for Indian classical dance and artistic experiences.",
        500,
        4.7,
        700,
        35,
        94,
        3,
        "Cultural",
        "low",
        13.0878,
        77.4827,
        1
    ),

    (
        "Turahalli Forest",
        "Bengaluru",
        "Nature",
        "Nature",
        "A rocky natural landscape on the outskirts of Bengaluru.",
        0,
        4.2,
        800,
        45,
        91,
        2,
        "Adventure",
        "low",
        12.8950,
        77.5090,
        1
    ),

    (
        "Big Banyan Tree",
        "Bengaluru",
        "Nature",
        "Nature",
        "A large historic banyan tree surrounded by a rural landscape.",
        0,
        4.3,
        1000,
        50,
        86,
        2,
        "Relaxed",
        "medium",
        12.9352,
        77.3799,
        1
    ),

    # ---------------- MYSURU ----------------

    (
        "Karanji Lake",
        "Mysuru",
        "Nature",
        "Nature",
        "A peaceful lake area suitable for relaxation and bird watching.",
        50,
        4.4,
        900,
        50,
        87,
        2,
        "Relaxed",
        "low",
        12.2958,
        76.6810,
        1
    ),

    (
        "Railway Museum",
        "Mysuru",
        "Museum",
        "History",
        "A museum showcasing railway heritage and historical exhibits.",
        50,
        4.3,
        700,
        45,
        90,
        2,
        "Cultural",
        "low",
        12.3087,
        76.6548,
        1
    ),

    (
        "Mysore Sand Sculpture Museum",
        "Mysuru",
        "Museum",
        "Culture",
        "A museum featuring artistic sculptures created using sand.",
        100,
        4.2,
        600,
        40,
        89,
        1.5,
        "Cultural",
        "medium",
        12.2809,
        76.6610,
        1
    ),

    (
        "Kukkarahalli Lake",
        "Mysuru",
        "Nature",
        "Nature",
        "A peaceful urban lake suitable for walking and relaxation.",
        0,
        4.3,
        500,
        35,
        93,
        1.5,
        "Relaxed",
        "low",
        12.3078,
        76.6285,
        1
    )
]


cursor.executemany("""
INSERT INTO places (

    name,
    destination,
    category,
    interest,
    description,
    price,
    rating,
    review_count,
    popularity,
    local_discovery_score,
    duration,
    travel_style,
    crowd_level,
    latitude,
    longitude,
    verified

)

VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

""", places)


# ========================================================
# ACCOMMODATIONS
# ========================================================

accommodations = [

    (
        "Demo Heritage Stay",
        "Mysuru",
        "Homestay",
        1800,
        4.4,
        35,
        "Demo homestay profile for SmartTour development.",
        "Breakfast, WiFi, Parking",
        12.3000,
        76.6500,
        0
    ),

    (
        "Demo Nature Resort",
        "Bengaluru",
        "Resort",
        3200,
        4.5,
        20,
        "Demo resort profile for SmartTour development.",
        "Pool, Breakfast, Parking, Garden",
        12.9500,
        77.4500,
        0
    ),

    (
        "Demo Budget Hotel",
        "Mysuru",
        "Hotel",
        1200,
        4.1,
        50,
        "Demo budget hotel profile for SmartTour development.",
        "WiFi, Parking",
        12.3050,
        76.6550,
        0
    )

]


cursor.executemany("""
INSERT INTO accommodations (

    name,
    destination,
    accommodation_type,
    price_per_night,
    rating,
    review_count,
    description,
    amenities,
    latitude,
    longitude,
    verified

)

VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

""", accommodations)


# ========================================================
# TOUR GUIDES
# ========================================================

guides = [

    (
        "Demo Heritage Guide",
        "Mysuru",
        "English, Kannada, Hindi",
        "Heritage and Culture",
        5,
        800,
        4.7,
        "Demo guide profile for SmartTour development.",
        "",
        0
    ),

    (
        "Demo Nature Guide",
        "Bengaluru",
        "English, Kannada",
        "Nature and Local Experiences",
        4,
        1000,
        4.6,
        "Demo guide profile for SmartTour development.",
        "",
        0
    )

]


cursor.executemany("""
INSERT INTO guides (

    name,
    destination,
    languages,
    specialization,
    experience_years,
    price_per_tour,
    rating,
    description,
    phone,
    verified

)

VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

""", guides)


# ========================================================
# TOUR PACKAGES
# ========================================================

packages = [

    (
        "Mysuru Heritage Explorer",
        "Mysuru",
        "A demo full-day heritage experience.",
        8,
        1499,
        4.6,
        "Guide, Heritage Walk, Local Food Experience",
        "Demo Tourism Partner",
        0
    ),

    (
        "Bengaluru Hidden Nature Trail",
        "Bengaluru",
        "A demo nature-focused local exploration experience.",
        6,
        1299,
        4.5,
        "Local Guide, Nature Trail, Local Food",
        "Demo Tourism Partner",
        0
    )

]


cursor.executemany("""
INSERT INTO packages (

    name,
    destination,
    description,
    duration_hours,
    price_per_person,
    rating,
    includes,
    provider_name,
    verified

)

VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

""", packages)


# ========================================================
# FOOD
# ========================================================

food_places = [

    (
        "Demo Mysuru Local Food Experience",
        "Mysuru",
        "South Indian",
        "Local Experience",
        "Budget",
        4.5,
        40,
        "Demo food experience for SmartTour development.",
        "Traditional Mysuru dishes",
        12.3050,
        76.6550,
        0
    ),

    (
        "Demo Bengaluru Local Breakfast",
        "Bengaluru",
        "South Indian",
        "Local Food",
        "Budget",
        4.4,
        50,
        "Demo local food recommendation.",
        "Traditional breakfast",
        12.9700,
        77.5900,
        0
    )

]


cursor.executemany("""
INSERT INTO food_places (

    name,
    destination,
    cuisine,
    food_type,
    price_range,
    rating,
    review_count,
    description,
    speciality,
    latitude,
    longitude,
    verified

)

VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

""", food_places)


# ========================================================
# SAVE
# ========================================================

connection.commit()
connection.close()


print("SmartTour tourism data added successfully!")