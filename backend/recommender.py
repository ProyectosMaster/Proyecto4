from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class SentenceTransformerRecommender:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def encode(self, texts):
        return self.model.encode(texts)

    def get_most_similar_description(self, pelicula_nombre, peliculas, top_k=3):
        pelicula = next((p for p in peliculas if p["titulo"].lower() == pelicula_nombre.lower()), None)

        if not pelicula:
            return []

        input_description = pelicula["descripcion"]
        other_peliculas = [p for p in peliculas if p["titulo"].lower() != pelicula_nombre.lower()]

        descriptions = [p["descripcion"] for p in other_peliculas]
        titles = [p["titulo"] for p in other_peliculas]

        input_embedding = self.encode([input_description])
        candidate_embeddings = self.encode(descriptions)

        similarities = cosine_similarity(input_embedding, candidate_embeddings)[0]
        top_indices = similarities.argsort()[::-1][:top_k]

        return [{"titulo": titles[i], "similitud": float(similarities[i])} for i in top_indices]

