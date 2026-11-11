
from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for, abort
)
import os
import sqlite3
import math

from ai.recommender import SmartTourRecommender


# ========================================================
# FLASK CONFIGURATION
# ========================================================

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "database", "tourism.db")
DATA_PATH = os.path.join(BASE_DIR, "data", "tourism_data.csv")

app.secret_key = os.environ.get(
    "SMARTTOUR_SECRET_KEY",
    "smarttour-local-development-key"
)

ADMIN_PASSWORD = os.environ.get(
    "SMARTTOUR_ADMIN_PASSWORD",
    "SmartTourAdmin123"
)


# ========================================================
# LOAD AI RECOMMENDER
# ========================================================

print("\n========================================")
print("          SMARTTOUR AI ENGINE")
print("========================================")

recommender = SmartTourRecommender(DATA_PATH)

print(f"Loaded {len(recommender.data)} destinations.")
print("Recommendation engine ready.")
print("========================================\n")


# ========================================================
# DATABASE HELPERS
# ========================================================

def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def table_exists(connection, table_name):
    result = connection.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type = 'table' AND name = ?
        """,
        (table_name,)
    ).fetchone()

    return result is not None


def get_table_records(connection, table_name, active_only=True):

    if not table_exists(connection, table_name):
        return []

    columns = {
        row["name"]
        for row in connection.execute(
            f"PRAGMA table_info({table_name})"
        ).fetchall()
    }

    query = f"SELECT * FROM {table_name}"

    if active_only and "active" in columns:
        query += " WHERE active = 1"

    return [
        dict(row)
        for row in connection.execute(query).fetchall()
    ]


def clean_value(value):

    if hasattr(value, "item"):
        value = value.item()

    if isinstance(value, float) and not math.isfinite(value):
        return None

    return value


def clean_records(records):

    return [
        {
            key: clean_value(value)
            for key, value in record.items()
        }
        for record in records
    ]


# ========================================================
# LOCAL BUSINESS DATABASE INITIALIZATION
# ========================================================

def initialize_business_table():

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS registered_businesses (

            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT NOT NULL,
            category TEXT NOT NULL,
            owner_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            location TEXT NOT NULL,
            price TEXT,
            description TEXT,
            facilities TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    connection.commit()
    connection.close()


initialize_business_table()


# ========================================================
# HOME PAGE
# ========================================================

@app.route("/")
def home():
    return render_template("index.html")


# ========================================================
# ALL DESTINATIONS API
# ========================================================

@app.route("/api/places", methods=["GET"])
def places():

    try:

        data = recommender.data.drop(
            columns=["feature_text"],
            errors="ignore"
        )

        records = data.to_dict(orient="records")

        return jsonify(clean_records(records))

    except Exception as error:

        app.logger.exception("Could not load destinations")

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ========================================================
# AI RECOMMENDATION API
# ========================================================

@app.route("/api/recommend", methods=["POST"])
def recommend():

    try:

        data = request.get_json(silent=True) or {}

        interests = data.get("interests", [])

        if isinstance(interests, str):
            interests = [interests] if interests else []

        budget = float(data.get("budget", 1000))
        available_time = int(data.get("available_time", 180))

        crowd_preference = data.get(
            "crowd_preference",
            "low"
        )

        if budget < 0:
            return jsonify({
                "success": False,
                "error": "Budget cannot be negative."
            }), 400

        if available_time <= 0:
            return jsonify({
                "success": False,
                "error": "Available time must be greater than zero."
            }), 400

        if not interests:
            interests = ["nature"]

        recommendations = recommender.recommend(
            interests=interests,
            budget=budget,
            available_time=available_time,
            crowd_preference=crowd_preference,
            top_n=6
        )

        if hasattr(recommendations, "to_dict"):
            recommendations = recommendations.to_dict(
                orient="records"
            )

        return jsonify({
            "success": True,
            "count": len(recommendations),
            "recommendations": clean_records(recommendations)
        })

    except (ValueError, TypeError):

        return jsonify({
            "success": False,
            "error": "Please enter valid budget and available time values."
        }), 400

    except Exception as error:

        app.logger.exception("Recommendation error")

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ========================================================
# HIDDEN GEMS API
# ========================================================

@app.route("/api/hidden-gems", methods=["GET"])
def hidden_gems():

    try:

        connection = get_connection()

        try:
            records = get_table_records(
                connection,
                "places",
                active_only=True
            )
        finally:
            connection.close()

        if records:

            def gem_score(place):

                value = place.get("local_discovery_score", 0)

                try:
                    return float(value or 0)
                except (ValueError, TypeError):
                    return 0

            records.sort(
                key=gem_score,
                reverse=True
            )

            if any("verified" in place for place in records):

                verified_records = [
                    place for place in records
                    if place.get("verified") in (
                        1, True, "1", "true", "True"
                    )
                ]

                if verified_records:
                    records = verified_records

            return jsonify(clean_records(records[:12]))

        data = recommender.data.drop(
            columns=["feature_text"],
            errors="ignore"
        )

        if "local_discovery_score" in data.columns:
            data = data.sort_values(
                "local_discovery_score",
                ascending=False
            )

        return jsonify(
            clean_records(
                data.head(12).to_dict(orient="records")
            )
        )

    except Exception as error:

        app.logger.exception("Hidden gems error")

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ========================================================
# ROUTE DISTANCE CALCULATION
# ========================================================

def calculate_distance(lat1, lon1, lat2, lon2):

    earth_radius = 6371

    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lon1))

    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    return earth_radius * 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )


# ========================================================
# ROUTE OPTIMIZATION API
# ========================================================

@app.route("/api/optimize-route", methods=["POST"])
def optimize_route():

    try:

        data = request.get_json(silent=True) or {}

        selected_names = data.get("destinations", [])

        if not isinstance(selected_names, list):
            return jsonify({
                "success": False,
                "error": "Destinations must be provided as a list."
            }), 400

        if len(selected_names) < 2:
            return jsonify({
                "success": False,
                "error": "Please select at least two destinations."
            }), 400

        if len(selected_names) > 8:
            return jsonify({
                "success": False,
                "error": "Please select no more than eight destinations."
            }), 400

        destination_data = recommender.data.copy()

        destination_data["name"] = (
            destination_data["name"].astype(str)
        )

        selected_places = []

        for name in selected_names:

            matches = destination_data[
                destination_data["name"].str.lower()
                == str(name).strip().lower()
            ]

            if matches.empty:
                return jsonify({
                    "success": False,
                    "error": f"Destination not found: {name}"
                }), 404

            place = matches.iloc[0]

            try:
                latitude = float(place["latitude"])
                longitude = float(place["longitude"])

            except (ValueError, TypeError, KeyError):
                continue

            if not (
                -90 <= latitude <= 90
                and -180 <= longitude <= 180
            ):
                continue

            selected_places.append({
                "name": str(place["name"]),
                "latitude": latitude,
                "longitude": longitude
            })

        if len(selected_places) < 2:
            return jsonify({
                "success": False,
                "error": "At least two destinations need valid coordinates."
            }), 400

        optimized_route = [selected_places.pop(0)]

        total_distance = 0

        while selected_places:

            current_place = optimized_route[-1]

            nearest_index = min(
                range(len(selected_places)),
                key=lambda index: calculate_distance(
                    current_place["latitude"],
                    current_place["longitude"],
                    selected_places[index]["latitude"],
                    selected_places[index]["longitude"]
                )
            )

            next_place = selected_places.pop(nearest_index)

            distance = calculate_distance(
                current_place["latitude"],
                current_place["longitude"],
                next_place["latitude"],
                next_place["longitude"]
            )

            next_place["distance_from_previous_km"] = round(
                distance, 2
            )

            total_distance += distance

            optimized_route.append(next_place)

        optimized_route[0]["distance_from_previous_km"] = 0

        return jsonify({
            "success": True,
            "optimized_route": optimized_route,
            "total_distance_km": round(total_distance, 2),
            "distance_type": "Approximate straight-line distance"
        })

    except Exception as error:

        app.logger.exception("Route optimization error")

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ========================================================
# USER FEEDBACK API - SAVE
# ========================================================

@app.route("/api/feedback", methods=["POST"])
def save_user_feedback():

    connection = None

    try:

        data = request.get_json(silent=True) or {}

        destination_name = data.get("destination_name")
        action = data.get("action")
        rating = data.get("rating")

        if not destination_name:
            return jsonify({
                "success": False,
                "error": "Destination name is required."
            }), 400

        if action not in ("like", "dislike", "rating"):
            return jsonify({
                "success": False,
                "error": "Invalid feedback action."
            }), 400

        if action == "rating" and rating is None:
            return jsonify({
                "success": False,
                "error": "A rating is required."
            }), 400

        if rating is not None:

            try:
                rating = int(rating)
            except (ValueError, TypeError):
                return jsonify({
                    "success": False,
                    "error": "Rating must be a whole number."
                }), 400

            if not 1 <= rating <= 5:
                return jsonify({
                    "success": False,
                    "error": "Rating must be between 1 and 5."
                }), 400

        connection = get_connection()

        if not table_exists(connection, "user_feedback"):
            return jsonify({
                "success": False,
                "error": "The user_feedback table does not exist."
            }), 500

        connection.execute("""
            INSERT INTO user_feedback
                (destination_name, action, rating)
            VALUES (?, ?, ?)
        """, (destination_name, action, rating))

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Feedback saved successfully."
        })

    except Exception as error:

        app.logger.exception("Feedback save error")

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500

    finally:

        if connection is not None:
            connection.close()


# ========================================================
# USER FEEDBACK API - HISTORY
# ========================================================

@app.route("/api/feedback", methods=["GET"])
def get_user_feedback():

    connection = None

    try:

        connection = get_connection()

        if not table_exists(connection, "user_feedback"):
            return jsonify({
                "success": True,
                "feedback": []
            })

        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(user_feedback)"
            ).fetchall()
        }

        selected_columns = [
            "destination_name",
            "action",
            "rating"
        ]

        if "created_at" in columns:
            selected_columns.append("created_at")

        query = (
            "SELECT "
            + ", ".join(selected_columns)
            + " FROM user_feedback"
        )

        if "created_at" in columns:
            query += " ORDER BY created_at DESC"

        rows = connection.execute(query).fetchall()

        return jsonify({
            "success": True,
            "feedback": [dict(row) for row in rows]
        })

    except Exception as error:

        app.logger.exception("Feedback history error")

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500

    finally:

        if connection is not None:
            connection.close()


# ========================================================
# TOURISM DATABASE API
# ========================================================

@app.route("/api/tourism-data", methods=["GET"])
def tourism_data():

    connection = None

    try:

        connection = get_connection()

        places_data = get_table_records(connection, "places")
        accommodations = get_table_records(connection, "accommodations")
        guides = get_table_records(connection, "guides")
        packages = get_table_records(connection, "packages")
        food = get_table_records(connection, "food_places")

        return jsonify({
            "success": True,
            "places": clean_records(places_data),
            "accommodations": clean_records(accommodations),
            "guides": clean_records(guides),
            "packages": clean_records(packages),
            "food": clean_records(food)
        })

    except Exception as error:

        app.logger.exception("Tourism database error")

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500

    finally:

        if connection is not None:
            connection.close()


# ========================================================
# EXISTING BUSINESSES API
# ========================================================

@app.route("/api/businesses", methods=["GET"])
def businesses():

    connection = None

    try:

        connection = get_connection()

        accommodations = get_table_records(
            connection, "accommodations"
        )

        guides = get_table_records(
            connection, "guides"
        )

        packages = get_table_records(
            connection, "packages"
        )

        food_places = get_table_records(
            connection, "food_places"
        )

        return jsonify({
            "success": True,
            "accommodations": clean_records(accommodations),
            "guides": clean_records(guides),
            "packages": clean_records(packages),
            "food_places": clean_records(food_places),
            "food": clean_records(food_places)
        })

    except Exception as error:

        app.logger.exception("Businesses API error")

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500

    finally:

        if connection is not None:
            connection.close()


# ========================================================
# DATABASE STATUS API
# ========================================================

@app.route("/api/database-status", methods=["GET"])
def database_status():

    connection = None

    try:

        if not os.path.exists(DB_PATH):
            return jsonify({
                "success": False,
                "database": "unavailable",
                "error": "Database file was not found."
            }), 500

        connection = get_connection()

        table_names = [
            "places",
            "accommodations",
            "guides",
            "packages",
            "food_places",
            "user_feedback",
            "registered_businesses"
        ]

        status = {}

        for table_name in table_names:

            if table_exists(connection, table_name):

                count = connection.execute(
                    f"SELECT COUNT(*) FROM {table_name}"
                ).fetchone()[0]

                status[table_name] = {
                    "exists": True,
                    "count": count
                }

            else:

                status[table_name] = {
                    "exists": False,
                    "count": 0
                }

        return jsonify({
            "success": True,
            "database": "connected",
            "tables": status,
            "dataset_destinations": len(recommender.data)
        })

    except Exception as error:

        app.logger.exception("Database status error")

        return jsonify({
            "success": False,
            "database": "error",
            "error": str(error)
        }), 500

    finally:

        if connection is not None:
            connection.close()


# ========================================================
# LOCAL BUSINESS REGISTRATION PAGE
# ========================================================

@app.route("/business/register")
def business_register():
    return render_template("business_register.html")


# ========================================================
# BUSINESS REGISTRATION API
# ========================================================

@app.route("/api/business/register", methods=["POST"])
def register_business():

    data = request.get_json(silent=True) or request.form

    required_fields = [
        "business_name",
        "category",
        "owner_name",
        "phone",
        "email",
        "location"
    ]

    for field in required_fields:

        if not str(data.get(field, "")).strip():
            return jsonify({
                "success": False,
                "error": f"{field.replace('_', ' ').title()} is required."
            }), 400

    allowed_categories = [
        "Homestay",
        "Hotel",
        "Resort",
        "Guest House",
        "Restaurant",
        "Cafe",
        "Local Guide",
        "Travel Provider"
    ]

    if data["category"] not in allowed_categories:
        return jsonify({
            "success": False,
            "error": "Invalid business category."
        }), 400

    connection = get_connection()

    try:

        connection.execute("""
            INSERT INTO registered_businesses
            (
                business_name,
                category,
                owner_name,
                phone,
                email,
                location,
                price,
                description,
                facilities
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["business_name"].strip(),
            data["category"],
            data["owner_name"].strip(),
            data["phone"].strip(),
            data["email"].strip(),
            data["location"].strip(),
            data.get("price", "").strip(),
            data.get("description", "").strip(),
            data.get("facilities", "").strip()
        ))

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Registration submitted! Your business is awaiting admin approval."
        })

    except sqlite3.Error:

        app.logger.exception("Business registration failed")

        return jsonify({
            "success": False,
            "error": "Could not save registration."
        }), 500

    finally:
        connection.close()


# ========================================================
# ADMIN LOGIN
# ========================================================

@app.route("/business/admin", methods=["GET", "POST"])
def business_admin_login():

    if request.method == "POST":

        password = request.form.get("password", "")

        if password == ADMIN_PASSWORD:

            session["business_admin"] = True

            return redirect(
                url_for("business_admin_dashboard")
            )

        return render_template(
            "business_admin_login.html",
            error="Incorrect admin password."
        )

    return render_template("business_admin_login.html")


# ========================================================
# ADMIN DASHBOARD
# ========================================================

@app.route("/business/admin/dashboard")
def business_admin_dashboard():

    if not session.get("business_admin"):
        return redirect(url_for("business_admin_login"))

    connection = get_connection()

    try:
        businesses = connection.execute("""
            SELECT * FROM registered_businesses
            ORDER BY created_at DESC
        """).fetchall()
    finally:
        connection.close()

    return render_template(
        "business_admin.html",
        businesses=businesses
    )


# ========================================================
# ADMIN APPROVE / REJECT BUSINESS
# ========================================================

@app.route(
    "/api/business/admin/<int:business_id>",
    methods=["POST"]
)
def update_business_status(business_id):

    if not session.get("business_admin"):
        return jsonify({
            "success": False,
            "error": "Admin login required."
        }), 401

    data = request.get_json(silent=True) or {}

    status = data.get("status")

    if status not in ["approved", "rejected"]:
        return jsonify({
            "success": False,
            "error": "Invalid status."
        }), 400

    connection = get_connection()

    try:

        cursor = connection.execute("""
            UPDATE registered_businesses
            SET status = ?
            WHERE id = ?
        """, (status, business_id))

        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({
                "success": False,
                "error": "Business not found."
            }), 404

        return jsonify({
            "success": True,
            "message": f"Business {status} successfully."
        })

    finally:
        connection.close()


# ========================================================
# ADMIN LOGOUT
# ========================================================

@app.route("/business/admin/logout")
def business_admin_logout():

    session.pop("business_admin", None)

    return redirect(url_for("business_admin_login"))


# ========================================================
# INDIVIDUAL BUSINESS PROFILE PAGE
# ========================================================

@app.route("/business/<int:business_id>")
def business_profile(business_id):

    connection = get_connection()

    try:

        business = connection.execute("""
            SELECT *
            FROM registered_businesses
            WHERE id = ?
            AND status = 'approved'
        """, (business_id,)).fetchone()

        if business is None:
            abort(404)

        return render_template(
            "business_profile.html",
            business=business
        )

    finally:
        connection.close()


# ========================================================
# PUBLIC LOCAL BUSINESS DIRECTORY
# ========================================================

@app.route("/local-businesses")
def local_businesses():

    connection = get_connection()

    try:

        businesses = connection.execute("""
            SELECT * FROM registered_businesses
            WHERE status = 'approved'
            ORDER BY created_at DESC
        """).fetchall()

        return render_template(
            "local_businesses.html",
            businesses=businesses
        )

    finally:
        connection.close()


# ========================================================
# PUBLIC BUSINESS DIRECTORY API
# ========================================================

@app.route("/api/local-businesses")
def local_businesses_api():

    connection = get_connection()

    try:

        businesses = connection.execute("""
            SELECT
                id,
                business_name,
                category,
                phone,
                email,
                location,
                price,
                description,
                facilities
            FROM registered_businesses
            WHERE status = 'approved'
            ORDER BY created_at DESC
        """).fetchall()

        return jsonify({
            "success": True,
            "businesses": [
                dict(row) for row in businesses
            ]
        })

    finally:
        connection.close()


# ========================================================
# RUN APPLICATION
# ========================================================

if __name__ == "__main__":
    app.run(debug=True)
