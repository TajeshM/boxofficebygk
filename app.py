from flask import Flask, jsonify, request, render_template
import requests

app = Flask(__name__)

# RapidAPI Credentials
RAPIDAPI_KEY = "993afec31amsh50cfe850a417c86p134665jsn37b373b45df0"
RAPIDAPI_HOST = "imdb236.p.rapidapi.com"

HEADERS = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": RAPIDAPI_HOST,
    "Content-Type": "application/json"
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search-page")
def search_page():
    return render_template("search.html")

@app.route("/details-page")
def details_page():
    movie_id = request.args.get("id", "")
    return render_template("details.html", movie_id=movie_id)

# API Proxies for Frontend Fetching
@app.route("/api/movies/<category>")
def get_movie_category(category):
    # Mapping friendly category names to exact RapidAPI endpoints
    endpoints = {
        "telugu": "https://imdb236.p.rapidapi.com/api/imdb/india/trending-telugu",
        "tamil": "https://imdb236.p.rapidapi.com/api/imdb/india/trending-tamil",
        "malayalam": "https://imdb236.p.rapidapi.com/api/imdb/india/top-rated-malayalam-movies",
        "top-indian": "https://imdb236.p.rapidapi.com/api/imdb/india/top-rated-indian-movies"
    }
    
    url = endpoints.get(category, endpoints["telugu"])
    try:
        response = requests.get(url, headers=HEADERS)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/person/<person_type>/<person_id>")
def get_person_titles(person_type, person_id):
    # person_type can be 'director' or 'cast'
    url = f"https://{RAPIDAPI_HOST}/api/imdb/{person_type}/{person_id}/titles"
    try:
        response = requests.get(url, headers=HEADERS)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/search")
def search_movies():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify([])
    
    url = f"https://{RAPIDAPI_HOST}/api/imdb/autocomplete"
    try:
        response = requests.get(url, headers=HEADERS, params={"query": query})
        data = response.json()
        if isinstance(data, list):
            return jsonify(data)
        elif isinstance(data, dict):
            return jsonify(data.get("results", []))
        return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/movie-details/<movie_id>")
def movie_details(movie_id):
    url = f"https://{RAPIDAPI_HOST}/api/imdb/{movie_id}"
    try:
        response = requests.get(url, headers=HEADERS)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)