import numpy as np
import ast


class MovieRecommender:
    def __init__(self, model, database):
        self.model = model
        self.database = database.copy()
        self.database_emb = np.stack(self.database["vector"].values)

    def get_recommendations(self, new_overview, top_n=5, order_by_vote: bool = False):

        new_overview_emb = self.model.encode(new_overview)
        similarities = calculate_similarity(self.database_emb, new_overview_emb)
        top_indices = similarities.argsort()[-top_n:][::-1]
        recommendations = self.database.iloc[top_indices][
            ["title", "overview", "vote_average"]
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
