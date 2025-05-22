from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import hashlib
from datetime import datetime
from recommender import SentenceTransformerRecommender  # NUEVO

app = Flask(__name__)
CORS(app)  # Permite peticiones desde React

SUPABASE_URL = "https://bpfdmufpudgtnnasfwin.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJwZmRtdWZwdWRndG5uYXNmd2luIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NzUwMDYwNSwiZXhwIjoyMDYzMDc2NjA1fQ.g912fWjyaD4Xww968ktEkhu7WXMRt4FD-_Vmx9BDYOM"
TABLE_NAME = "users"

@app.route('/api/users', methods=['GET'])
def get_users():
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}"
    }
    url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?select=*"
    response = requests.get(url, headers=headers)
    return jsonify(response.json())

@app.route('/api/registro', methods=['POST'])
def registro():
    data = request.get_json()
    username = data['username']
    password = hashlib.sha256(data['password'].encode()).hexdigest()

    insert_url = f"{SUPABASE_URL}/rest/v1/users"
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    payload = {
        "username": username,
        "hashed_password": password,
        "created_at": datetime.utcnow().isoformat()
    }

    res = requests.post(insert_url, headers=headers, json=payload)
    return jsonify(res.json()), res.status_code


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = hashlib.sha256(data['password'].encode()).hexdigest()

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

# Datos simulados de películas (puedes luego cargar desde DB)
# peliculas = [
#     {"titulo": "Inception", "descripcion": "A thief who steals corporate secrets through dream-sharing technology."},
#     {"titulo": "Interstellar", "descripcion": "A group of explorers travel through a wormhole in space in an attempt to ensure humanity's survival."},
#     {"titulo": "The Matrix", "descripcion": "A computer hacker learns about the true nature of his reality."},
#     {"titulo": "The Social Network", "descripcion": "The story of the founders of the social-networking website Facebook."},
#     {"titulo": "Tenet", "descripcion": "A secret agent embarks on a time-bending mission to prevent the start of World War III."}
# ]


# recommender_model = SentenceTransformerRecommender()  # Inicializa una sola vez

@app.route('/api/recomendacion', methods=['POST'])
def recomendacion():
    from recommender import SentenceTransformerRecommender
    from sklearn.metrics.pairwise import cosine_similarity

    data = request.get_json()
    titulo_input = data.get('pelicula')
    # print(f"[DEBUG] Película buscada: {titulo_input}")

    if not titulo_input:
        return jsonify({"error": "Película no proporcionada"}), 400

    # 1. Obtener todas las películas desde Supabase
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}"
    }
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/peliculas?select=id,title,overview",
        headers=headers
    )

    peliculas = response.json()
    # print(f"[DEBUG] Total películas en Supabase: {len(peliculas)}")

    # 2. Buscar película de entrada
    pelicula_input = next((p for p in peliculas if p["title"].lower() == titulo_input.lower()), None)
    if not pelicula_input:
        return jsonify({"error": "Película no encontrada"}), 404

    descripcion_input = pelicula_input["overview"]

    # 3. Filtrar otras películas
    otras = [p for p in peliculas if p["title"].lower() != titulo_input.lower()]
    titulos_otros = [p["title"] for p in otras]
    descripciones_otros = [p["overview"] for p in otras]

    # 4. Recomendación usando SentenceTransformer
    modelo = SentenceTransformerRecommender()
    emb_input = modelo.encode([descripcion_input])
    emb_otros = modelo.encode(descripciones_otros)

    sim = cosine_similarity(emb_input, emb_otros)[0]
    top_k = 3
    indices = sim.argsort()[::-1][:top_k]

    recomendaciones = [
        {
            "titulo": titulos_otros[i],
            "similitud": float(sim[i])
        }
        for i in indices
    ]

    return jsonify(recomendaciones)


if __name__ == '__main__':
    app.run(debug=True)
