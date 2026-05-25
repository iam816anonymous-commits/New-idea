from typing import List, Dict
from sqlalchemy.orm import Session
from proppulse_os.lead_engine.models import Project
import numpy as np

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

class SemanticSearchService:
    def __init__(self, db: Session):
        self.db = db

    def search_projects(self, query: str, tenant_id: int) -> List[Dict]:
        """
        Simulates semantic search by matching keywords in project amenities and specifications.
        In a real system, this would use embeddings (e.g., SentenceTransformers) + pgvector.
        """
        projects = self.db.query(Project).filter(Project.brokerage_id == tenant_id).all()
        results = []

        query_words = query.lower().split()

        for proj in projects:
            score = 0
            searchable_text = f"{proj.name} {proj.micro_market} {proj.amenities}".lower()

            # Simple keyword matching for simulation
            for word in query_words:
                if word in searchable_text:
                    score += 0.5

            if score > 0:
                results.append({
                    "id": proj.id,
                    "name": proj.name,
                    "micro_market": proj.micro_market,
                    "score": score
                })

        # Sort by score
        return sorted(results, key=lambda x: x['score'], reverse=True)
