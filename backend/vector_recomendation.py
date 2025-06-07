import numpy as np
import ast


class MovieRecommender:
    def __init__(self, model, database):
        self.model = model
        self.database = database.copy()
        self.database_emb_des = np.stack(self.database["vector"].values)
        self.database_emb_title = np.stack(self.database["vector_titulo"].values)

    def get_recommendations(
        self, new_overview, tipo, top_n=12, order_by_vote: bool = False
    ):

        new_overview_emb = self.model.encode(new_overview)
        if tipo == "titulo":
            similarities = calculate_similarity(
                self.database_emb_title, new_overview_emb
            )
            top_indices = similarities.argsort()[-top_n:][::-1]
            recommendations = self.database.iloc[top_indices][
                ["id", "title", "overview", "vote_average", "poster_path"]
            ]
        else:
            similarities = calculate_similarity(self.database_emb_des, new_overview_emb)
            top_indices = similarities.argsort()[-top_n:][::-1]
            recommendations = self.database.iloc[top_indices][
                ["id", "title", "overview", "vote_average", "poster_path"]
            ]

        if order_by_vote:
            recommendations = recommendations.sort_values(
                by="vote_average", ascending=False
            )

        return recommendations


def calculate_similarity(embeddings, target_embedding):
    """
    Calculate the cosine similarity between the target embedding and all other embeddings.
    """
    similarities = np.dot(embeddings, target_embedding) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(target_embedding)
    )
    return similarities
