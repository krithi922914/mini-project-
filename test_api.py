
import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:5000"


def test_endpoint(name, path, method="GET", data=None):
    url = BASE_URL + path
    print(f"\nTesting: {name}")

    try:
        request_data = None
        headers = {}

        if data is not None:
            request_data = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(
            url,
            data=request_data,
            headers=headers,
            method=method
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")

            try:
                result = json.loads(body)
            except json.JSONDecodeError:
                result = body

            print("Status:", response.status)

            if isinstance(result, dict):
                print("Response keys:", list(result.keys()))

                if "success" in result:
                    print("Success:", result["success"])

                if "count" in result:
                    print("Result count:", result["count"])

                if "recommendations" in result:
                    for place in result["recommendations"][:3]:
                        print(
                            "-",
                            place.get("name", "Unnamed place"),
                            "| Score:",
                            place.get("ai_score", "N/A")
                        )

            elif isinstance(result, list):
                print("Items returned:", len(result))
                for item in result[:3]:
                    if isinstance(item, dict):
                        print("-", item.get("name", item))

            else:
                print(str(result)[:300])

            return True

    except urllib.error.HTTPError as error:
        print("HTTP ERROR:", error.code)
        print(error.read().decode("utf-8")[:500])

    except urllib.error.URLError as error:
        print("CONNECTION ERROR:", error.reason)
        print("Make sure Flask is running at", BASE_URL)

    except Exception as error:
        print("ERROR:", error)

    return False


def main():
    print("=" * 45)
    print("       SMARTTOUR API TEST REPORT")
    print("=" * 45)

    results = []

    # 1. Tourist places
    results.append((
        "Places",
        test_endpoint("Places API", "/api/places")
    ))

    # 2. AI recommendations
    results.append((
        "AI Recommendations",
        test_endpoint(
            "AI Recommendation API",
            "/api/recommend",
            method="POST",
            data={
                "interests": ["nature", "heritage", "culture"],
                "budget": 1500,
                "available_time": 4,
                "crowd_preference": "low"
            }
        )
    ))

    # 3. Hidden gems
    results.append((
        "Hidden Gems",
        test_endpoint("Hidden Gems API", "/api/hidden-gems")
    ))

    # 4. Tourism services
    results.append((
        "Tourism Data",
        test_endpoint("Tourism Data API", "/api/tourism-data")
    ))

    # 5. Local businesses
    results.append((
        "Businesses",
        test_endpoint("Businesses API", "/api/businesses")
    ))

    # 6. Feedback history (read-only)
    results.append((
        "Feedback",
        test_endpoint("Feedback API", "/api/feedback")
    ))

    # 7. Database health
    results.append((
        "Database Status",
        test_endpoint("Database Status API", "/api/database-status")
    ))

    print("\n" + "=" * 45)
    print("             FINAL REPORT")
    print("=" * 45)

    passed = 0

    for name, success in results:
        status = "PASSED" if success else "CHECK"
        print(f"{name}: {status}")
        if success:
            passed += 1

    print(f"\nHTTP requests successful: {passed}/{len(results)}")
    print("Note: HTTP success does not guarantee correct feature output.")


if __name__ == "__main__":
    main()
