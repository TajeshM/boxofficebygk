import os

import requests
from flask import Flask, jsonify, render_template, request


app = Flask(__name__)

# Set RAPIDAPI_KEY in your environment before running the app. Keeping it out of
# source control prevents an API credential from being published accidentally.
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "993afec31amsh50cfe850a417c86p134665jsn37b373b45df0")
RAPIDAPI_HOST = "imdb236.p.rapidapi.com"
BASE_URL = f"https://{RAPIDAPI_HOST}"

CATEGORY_ENDPOINTS = {
    "telugu": "/api/imdb/india/trending-telugu",
    "tamil": "/api/imdb/india/trending-tamil",
    "malayalam": "/api/imdb/india/top-rated-malayalam-movies",
    "top-indian": "/api/imdb/india/top-rated-indian-movies",
}


def rapidapi_get(path, params=None):
    """Request RapidAPI with predictable errors for the browser client."""
    if not RAPIDAPI_KEY:
        return None, (jsonify({"error": "Server configuration is missing RAPIDAPI_KEY."}), 503)

    try:
        response = requests.get(
            f"{BASE_URL}{path}",
            headers={"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": RAPIDAPI_HOST},
            params=params,
            timeout=15,
        )
        response.raise_for_status()
        return response.json(), None
    except requests.RequestException as exc:
        return None, (jsonify({"error": "Unable to reach the movie service.", "detail": str(exc)}), 502)
    except ValueError:
        return None, (jsonify({"error": "The movie service returned invalid JSON."}), 502)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search-page")
def search_page():
    return render_template("search.html")


@app.route("/details-page")
def details_page():
    return render_template("details.html", movie_id=request.args.get("id", ""))


@app.route("/api/movies/<category>")
def get_movie_category(category):
    endpoint = CATEGORY_ENDPOINTS.get(category)
    if endpoint is None:
        return jsonify({"error": "Unknown movie category."}), 404
    data, error = rapidapi_get(endpoint)
    return error or jsonify(data)


@app.route("/api/search")
def search_movies():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify([])
    data, error = rapidapi_get("/api/imdb/autocomplete", {"query": query})
    if error:
        return error
    return jsonify(data if isinstance(data, list) else data.get("results", []))


@app.route("/api/movie-details/<movie_id>")
def movie_details(movie_id):
    data, error = rapidapi_get(f"/api/imdb/{movie_id}")
    return error or jsonify(data)


@app.route("/api/person/<person_type>/<person_id>")
def get_person_titles(person_type, person_id):
    if person_type not in {"director", "cast"}:
        return jsonify({"error": "Unknown person type."}), 404
    data, error = rapidapi_get(f"/api/imdb/{person_type}/{person_id}/titles")
    return error or jsonify(data)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
