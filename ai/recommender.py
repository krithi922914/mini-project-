
import os
import sqlite3

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SmartTourRecommender:
    """AI tourism recommender with simulated crowd-aware scoring."""

    INTERESTS = [
        "nature", "heritage", "culture",
        "shopping", "wildlife", "entertainment"
    ]

    CROWD_SCORES = {
        "low": 20,
        "medium": 50,
        "high": 85
    }

    def __init__(self, data_path, db_path=None):
        project_root = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        self.db_path = db_path or os.path.join(
            project_root, "database", "tourism.db"
        )

        print("Loading tourism dataset...")

        self.data_source = "sqlite"

        try:
            connection = sqlite3.connect(self.db_path, timeout=10)

            try:
                self.data = pd.read_sql_query(
                    "SELECT * FROM places WHERE active = 1",
                    connection
                )
            finally:
                connection.close()

            if self.data.empty:
                raise ValueError("No active destinations found.")

            print(f"Loaded {len(self.data)} destinations from SQLite.")

        except (sqlite3.Error, ValueError) as error:

            print("SQLite loading failed:", error)

            if not os.path.exists(data_path):
                raise FileNotFoundError(data_path)

            self.data = pd.read_csv(data_path)
            self.data_source = "csv"

        self.data = self._normalize_data(self.data)

        self.data = self.data.fillna("")

        self.data["feature_text"] = self.data.apply(
            self._create_feature_text,
            axis=1
        )

        self.data["feature_text"] = self.data[
            "feature_text"
        ].apply(
            lambda value: value.strip() or "tourism destination"
        )

        self.vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        self.tfidf_matrix = self.vectorizer.fit_transform(
            self.data["feature_text"]
        )

        print("AI recommendation model initialized.")

    def _normalize_data(self, data):

        data = data.copy()

        aliases = {
            "visit_time": "duration",
            "destination": "name"
        }

        for target, source in aliases.items():

            if target not in data.columns and source in data.columns:
                data[target] = data[source]

        defaults = {
            "name": "",
            "category": "",
            "description": "",
            "price": 0,
            "rating": 0,
            "review_count": 0,
            "popularity": 0,
            "visit_time": 90,
            "crowd_level": "medium",
            "latitude": 0,
            "longitude": 0,
            "interest": "",
            "travel_style": "",
            "local_discovery_score": 0
        }

        for column, default in defaults.items():

            if column not in data.columns:
                data[column] = default

        data["crowd_level"] = data["crowd_level"].apply(
            self._crowd_label
        )

        for interest in self.INTERESTS:

            if interest not in data.columns:
                data[interest] = 0

        for index, row in data.iterrows():

            combined_text = " ".join([
                str(row.get("name", "")),
                str(row.get("category", "")),
                str(row.get("interest", "")),
                str(row.get("travel_style", "")),
                str(row.get("description", ""))
            ]).lower()

            for interest in self.INTERESTS:

                existing = pd.to_numeric(
                    pd.Series([data.at[index, interest]]),
                    errors="coerce"
                ).fillna(0).iloc[0]

                if interest in combined_text and existing < 10:
                    data.at[index, interest] = 10

        numeric_columns = [
            "price", "rating", "popularity",
            "visit_time", "latitude", "longitude",
            "local_discovery_score", "review_count"
        ]

        for column in numeric_columns:

            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            ).fillna(0)

        return data

    @staticmethod
    def _crowd_label(value):

        try:

            score = float(value)

            if score <= 40:
                return "low"

            elif score <= 65:
                return "medium"

            return "high"

        except (TypeError, ValueError):

            text = str(value or "medium").strip().lower()

            if text in {"low", "medium", "high"}:
                return text

            return "medium"

    def _create_feature_text(self, row):

        parts = [
            str(row.get("name", "")),
            str(row.get("category", "")),
            str(row.get("description", "")),
            str(row.get("interest", "")),
            str(row.get("travel_style", ""))
        ]

        for interest in self.INTERESTS:

            try:

                score = float(row.get(interest, 0))

                if score > 0:

                    repeat_count = min(
                        5,
                        max(1, int(score / 20))
                    )

                    parts.append(
                        (interest + " ") * repeat_count
                    )

            except (TypeError, ValueError):
                continue

        return " ".join(parts)

    def create_user_profile(
        self,
        interests,
        budget,
        available_time,
        crowd_preference
    ):

        profile = ""

        for interest in interests:

            cleaned = str(interest).strip().lower()

            if cleaned:
                profile += (cleaned + " ") * 3

        if budget <= 500:
            profile += "budget cheap affordable "

        elif budget <= 1500:
            profile += "moderate affordable "

        else:
            profile += "premium luxury expensive "

        if available_time <= 90:
            profile += "short quick nearby "

        elif available_time <= 180:
            profile += "medium visit "

        else:
            profile += "long extended visit "

        if crowd_preference == "low":
            profile += "peaceful quiet less crowded "

        elif crowd_preference == "medium":
            profile += "moderate crowd "

        else:
            profile += "popular lively crowded "

        return profile.strip() or "tourism destination"

    def recommend(
        self,
        interests,
        budget=1000,
        available_time=180,
        crowd_preference="low",
        top_n=6
    ):

        crowd_preference = str(
            crowd_preference
        ).lower()

        if crowd_preference not in {"low", "medium", "high"}:
            crowd_preference = "low"

        user_profile = self.create_user_profile(
            interests,
            budget,
            available_time,
            crowd_preference
        )

        user_vector = self.vectorizer.transform(
            [user_profile]
        )

        similarity_scores = cosine_similarity(
            user_vector,
            self.tfidf_matrix
        ).flatten()

        results = self.data.copy()

        results["interest_similarity"] = similarity_scores

        def budget_score(price):

            if price <= budget:
                return 1.0

            return max(
                0.0,
                1 - ((price - budget) / max(budget, 1))
            )

        results["budget_score"] = results["price"].apply(
            budget_score
        )

        def time_score(duration):

            if duration <= available_time:
                return 1.0

            return max(
                0.0,
                1 - (
                    (duration - available_time)
                    / max(available_time, 1)
                )
            )

        results["time_score"] = results["visit_time"].apply(
            time_score
        )

        def crowd_score(crowd):

            crowd = str(crowd).lower()

            scores = {
                "low": {
                    "low": 1.0,
                    "medium": 0.5,
                    "high": 0.1
                },
                "medium": {
                    "low": 0.6,
                    "medium": 1.0,
                    "high": 0.5
                },
                "high": {
                    "low": 0.4,
                    "medium": 0.7,
                    "high": 1.0
                }
            }

            return scores[crowd_preference].get(crowd, 0.5)

        results["crowd_score"] = results[
            "crowd_level"
        ].apply(crowd_score)

        results["rating_score"] = results["rating"].apply(
            lambda value: min(max(float(value) / 5, 0), 1)
        )

        results["popularity_score"] = results["popularity"].apply(
            lambda value: min(max(float(value) / 100, 0), 1)
        )

        # Weighted AI recommendation score.
        results["ai_score"] = (
            results["interest_similarity"] * 0.45
            + results["budget_score"] * 0.15
            + results["crowd_score"] * 0.15
            + results["time_score"] * 0.10
            + results["rating_score"] * 0.10
            + results["popularity_score"] * 0.05
        )

        results = results.sort_values(
            "ai_score",
            ascending=False
        ).head(max(0, int(top_n)))

        final_results = []

        for _, row in results.iterrows():

            crowd = str(row["crowd_level"])

            reasons = []

            if row["interest_similarity"] > 0.20:
                reasons.append("Matches your interests")

            if row["budget_score"] >= 0.8:
                reasons.append("Fits your budget")

            if row["time_score"] >= 0.8:
                reasons.append("Fits your available time")

            if row["crowd_score"] >= 0.8:
                reasons.append("Matches your crowd preference")

            if float(row["rating"]) >= 4:
                reasons.append("Highly rated")

            if not reasons:
                reasons.append("Recommended by AI")

            final_results.append({

                "name": str(row["name"]),

                "category": str(row["category"]),

                "description": str(row["description"]),

                "latitude": float(row["latitude"]),

                "longitude": float(row["longitude"]),

                "rating": float(row["rating"]),

                "price": float(row["price"]),

                "visit_time": float(row["visit_time"]),

                "crowd_level": crowd,

                "crowd_score": round(
                    float(row["crowd_score"]) * 100,
                    2
                ),

                "crowd_source": "Simulated demo data",

                "popularity": float(row["popularity"]),

                "ai_score": round(
                    float(row["ai_score"]) * 100,
                    2
                ),

                "reasons": reasons
            })

        return final_results

    def hidden_gems(
        self,
        interests,
        budget=1000,
        available_time=180,
        crowd_preference="low",
        top_n=6
    ):

        try:

            connection = sqlite3.connect(
                self.db_path,
                timeout=10
            )

            connection.row_factory = sqlite3.Row

            try:

                rows = connection.execute("""
                    SELECT name, category, description, price, rating,
                           popularity, local_discovery_score, duration,
                           crowd_level, latitude, longitude, destination,
                           verified, review_count
                    FROM places
                    WHERE active = 1
                """).fetchall()

            finally:
                connection.close()

        except sqlite3.Error as error:

            print("Hidden-gem database error:", error)

            return []

        hidden_gems = []

        for row in rows:

            place = dict(row)

            try:

                price = float(place.get("price") or 0)

                rating = float(place.get("rating") or 0)

                popularity = float(
                    place.get("popularity") or 0
                )

                discovery = float(
                    place.get("local_discovery_score") or 0
                )

                duration = float(
                    place.get("duration") or 0
                )

            except (TypeError, ValueError):
                continue

            if price > budget or duration > available_time:
                continue

            crowd = self._crowd_label(
                place.get("crowd_level")
            )

            if crowd_preference == "low" and crowd == "high":
                continue

            score = (
                min(max(discovery, 0), 100) * 0.50
                + min(max(rating, 0), 5) / 5 * 100 * 0.25
                + (100 - min(max(popularity, 0), 100)) * 0.25
            )

            reasons = []

            if discovery >= 70:
                reasons.append(
                    "Strong local discovery potential"
                )

            if popularity <= 50:
                reasons.append(
                    "Less widely known destination"
                )

            if rating >= 4:
                reasons.append("Highly rated destination")

            if not reasons:
                reasons.append(
                    "Worth exploring based on its score"
                )

            place["hidden_gem"] = True

            place["hidden_gem_score"] = round(score, 2)

            place["hidden_gem_reason"] = reasons

            place["ai_score"] = round(score, 2)

            place["visit_time"] = duration

            place["crowd_level"] = crowd

            place["crowd_source"] = "Simulated demo data"

            hidden_gems.append(place)

        hidden_gems.sort(
            key=lambda item: item["hidden_gem_score"],
            reverse=True
        )

        return hidden_gems[:max(0, int(top_n))]
