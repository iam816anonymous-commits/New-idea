import json
import math
from typing import List, Tuple

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculates the cosine similarity between two vectors."""
    dot_product = sum(x * y for x, y in zip(v1, v2))
    magnitude1 = math.sqrt(sum(x * x for x in v1))
    magnitude2 = math.sqrt(sum(y * y for y in v2))
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    return dot_product / (magnitude1 * magnitude2)

def find_matching_projects(query_embedding: List[float], projects: List[object], top_k: int = 3) -> List[Tuple[object, float]]:
    """
    Simulates a vector similarity search across projects.
    """
    scored_projects = []
    for project in projects:
        if project.amenities_embeddings:
            try:
                project_embedding = json.loads(project.amenities_embeddings)
                score = cosine_similarity(query_embedding, project_embedding)
                scored_projects.append((project, score))
            except Exception as e:
                print(f"Error parsing embedding for project {project.id}: {e}")

    # Sort by score descending
    scored_projects.sort(key=lambda x: x[1], reverse=True)
    return scored_projects[:top_k]
