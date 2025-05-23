from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import hashlib
import pandas as pd
import os
import numpy as np
import pickle
import ast
from datetime import datetime
from supabase import create_client
from vector_recomendation import MovieRecommender
from recommender import SentenceTransformerRecommender


app = Flask(__name__)
CORS(app)  # Permite peticiones desde React

SUPABASE_URL = "https://bpfdmufpudgtnnasfwin.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJwZmRtdWZwdWRndG5uYXNmd2luIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NzUwMDYwNSwiZXhwIjoyMDYzMDc2NjA1fQ.g912fWjyaD4Xww968ktEkhu7WXMRt4FD-_Vmx9BDYOM"
TABLE_NAME = "users"

# CARGO AQUÍ EL FICHERO PARA QUE A LA HORA DE MOSTRAR PREDICCIONES NO SE QUEDE PILLADA LA WEB
# CUANDO LANZAS EL BACKEND TARDA UNOS 3 MIN EN CARGAR...
path_file = os.path.join(
    os.path.dirname(__file__), "../../ruben/data/clean_data/movies_clean.csv"
)
df_movies = pd.read_csv(path_file)
df_movies["vector"] = df_movies["vector"].apply(
    ast.literal_eval
)  # Convierte de str a lista


@app.route("/api/users", methods=["GET"])
def get_users():
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
    }
    url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?select=*"
    response = requests.get(url, headers=headers)
    return jsonify(response.json())


@app.route("/api/registro", methods=["POST"])
def registro():
    data = request.get_json()
    username = data["username"]
    password = hashlib.sha256(data["password"].encode()).hexdigest()

    insert_url = f"{SUPABASE_URL}/rest/v1/users"
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

    payload = {
        "username": username,
        "hashed_password": password,
        "created_at": datetime.utcnow().isoformat(),
    }

    res = requests.post(insert_url, headers=headers, json=payload)
    return jsonify(res.json()), res.status_code


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data["username"]
    password = hashlib.sha256(data["password"].encode()).hexdigest()

    query_url = f"{SUPABASE_URL}/rest/v1/users?username=eq.{username}&hashed_password=eq.{password}&select=id"
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
    }

    res = requests.get(query_url, headers=headers)
    users = res.json()
    if users:
        return jsonify({"success": True})
    else:
        return jsonify({"error": "Credenciales incorrectas"}), 401


@app.route("/api/recomendacion", methods=["POST"])
def recomendacion():
    data = request.get_json()
    titulo_input = data.get("pelicula")
    # print(f"[DEBUG] Película buscada: {titulo_input}")

    if not titulo_input:
        return jsonify({"error": "Película no proporcionada"}), 400

    # 1. Obtener todas las películas desde Supabase
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
    }
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/peliculas?select=id,title,overview", headers=headers
    )
    st_model = SentenceTransformerRecommender()
    recommender = MovieRecommender(st_model, df_movies)

    results = []

    if titulo_input.strip():
        results = recommender.get_recommendations(titulo_input)

    recomendaciones = results["title"].tolist()

    # recomendaciones = [{"titulo": results["title"].values}]

    return jsonify(recomendaciones)


@app.route("/api/sugerencias", methods=["GET"])
def sugerencias():

    SUPABASE_URL = "https://bpfdmufpudgtnnasfwin.supabase.co"
    SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJwZmRtdWZwdWRndG5uYXNmd2luIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NzUwMDYwNSwiZXhwIjoyMDYzMDc2NjA1fQ.g912fWjyaD4Xww968ktEkhu7WXMRt4FD-_Vmx9BDYOM"
    supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

    query = request.args.get("q", "").lower()

    if not query:
        return jsonify([])

    # Buscar títulos que contengan el texto (máximo 3)
    response = (
        supabase.table("peliculas")
        .select("title")
        .ilike("title", f"%{query}%")
        .limit(3)
        .execute()
    )

    titulos = [item["title"] for item in response.data]
    return jsonify(titulos)


@app.route("/api/pelis", methods=["GET"])
def recomendaciones_personalizadas():
    # data = request.get_json()
    # titulo_input = data.get("pelicula")
    # print(f"[DEBUG] Película buscada: {titulo_input}")

    # if not titulo_input:
    #     return jsonify({"error": "Película no proporcionada"}), 400

    # 1. Obtener todas las películas desde Supabase
    # headers = {
    #     "apikey": SUPABASE_API_KEY,
    #     "Authorization": f"Bearer {SUPABASE_API_KEY}",
    # }
    # response = requests.get(
    #     f"{SUPABASE_URL}/rest/v1/peliculas?select=id,title,overview", headers=headers
    # )
    with open("user_factors.pkl", "rb") as f:
        user_factors = pickle.load(f)

    with open(f"item_factors.pkl", "rb") as f:
        item_factors = pickle.load(f)
    # Convertir listas a arrays NumPy
    user_factors["features"] = user_factors["features"].apply(lambda x: np.array(x))
    item_factors["features"] = item_factors["features"].apply(lambda x: np.array(x))

    # Crear índice para acceso rápido
    user_factors.set_index("id", inplace=True)
    item_factors.set_index("id", inplace=True)

    user_id = 123

    if user_id not in user_factors.index:
        return jsonify([])

    user_vec = user_factors.loc[user_id, "features"]
    # Sin el rango definido entre 0.5 y 5
    item_scores = item_factors["features"].apply(lambda x: np.dot(user_vec, x))

    top_items = item_scores.sort_values(ascending=False).head(20)

    recomendaciones = []

    for movie_id, score in top_items.items():
        recomendaciones.append(
            {
                "movieId": int(movie_id),
                "titulo": df_movies[df_movies["id"] == int(movie_id)]["title"].values[
                    0
                ],
                "sinopsis": df_movies[df_movies["id"] == int(movie_id)][
                    "overview"
                ].values[0],
                "score": float(score),
                "img_path": df_movies[df_movies["id"] == int(movie_id)][
                    "poster_path"
                ].values[0],
            }
        )

    return jsonify(recomendaciones)


if __name__ == "__main__":
    app.run(debug=True)
