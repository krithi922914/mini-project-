
import os
import sqlite3
import urllib.request
import urllib.error
import importlib.util

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "tourism.db")
CSV_PATH = os.path.join(BASE_DIR, "data", "tourism_data.csv")
BASE_URL = "http://127.0.0.1:5000"

results = []


def check(name, function):
    try:
        detail = function()
        print(f"[PASS] {name}: {detail}")
        results.append((name, True))
    except Exception as error:
        print(f"[CHECK] {name}: {error}")
        results.append((name, False))


def check_database():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    with sqlite3.connect(DB_PATH) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }

        if "places" not in tables:
            raise RuntimeError("'places' table is missing")

        count = connection.execute(
            "SELECT COUNT(*) FROM places"
        ).fetchone()[0]

    return f"{count} places in database"


def check_csv():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"CSV not found: {CSV_PATH}")

    import pandas as pd

    data = pd.read_csv(CSV_PATH)

    if data.empty:
        raise RuntimeError("CSV contains no records")

    if "name" not in data.columns:
        raise RuntimeError("CSV is missing the name column")

    return f"{len(data)} rows, {len(data.columns)} columns"


def check_recommender():
    path = os.path.join(BASE_DIR, "ai", "recommender.py")

    if not os.path.exists(path):
        raise FileNotFoundError("ai/recommender.py not found")

    spec = importlib.util.spec_from_file_location(
        "smarttour_recommender_check", path
    )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "SmartTourRecommender"):
        raise RuntimeError("SmartTourRecommender class not found")

    return "Recommender class imported successfully"


def check_api(path):
    request = urllib.request.Request(BASE_URL + path)

    with urllib.request.urlopen(request, timeout=10) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP status {response.status}")

        return f"HTTP {response.status}"


if __name__ == "__main__":
    print("\n===== SMARTTOUR PROJECT HEALTH CHECK =====\n")

    check("SQLite database", check_database)
    check("Tourism CSV", check_csv)
    check("AI recommender import", check_recommender)

    for route in [
        "/api/places",
        "/api/hidden-gems",
        "/api/tourism-data",
        "/api/businesses",
        "/api/feedback",
        "/api/database-status",
    ]:
        check(f"API {route}", lambda route=route: check_api(route))

    print("\n===== SUMMARY =====")
    passed = sum(success for _, success in results)
    print(f"Passed: {passed}/{len(results)} checks")

    for name, success in results:
        if not success:
            print("Needs attention:", name)

    print("\nThis report checks basic availability, not full feature correctness.")
