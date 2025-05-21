from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import hashlib
from datetime import datetime

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

if __name__ == '__main__':
    app.run(debug=True)
