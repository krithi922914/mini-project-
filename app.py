from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

# -----------------------------
# DATABASE PATH
# -----------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "tourism.db")


# -----------------------------
# HOME PAGE
# -----------------------------

@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# RECOMMENDATION ROUTE
# -----------------------------

@app.route("/recommend", methods=["POST"])
def recommend():

    destination = request.form.get("destination")
    budget = float(request.form.get("budget", 0))
    days = int(request.form.get("days", 1))
    interest = request.form.get("interest")
    travel_style = request.form.get("travel_style")

    # Connect to database
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # Get places from the selected destination
    cursor.execute("""
        SELECT *
        FROM places
        WHERE LOWER(destination) = LOWER(?)
        ORDER BY rating DESC
    """, (destination,))

    places = cursor.fetchall()

    # Close database connection
    connection.close()

    # Send results to recommendations page
    return render_template(
        "recommendations.html",
        places=places,
        destination=destination,
        budget=budget,
        days=days,
        interest=interest,
        travel_style=travel_style
    )


# -----------------------------
# RUN APPLICATION
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True)