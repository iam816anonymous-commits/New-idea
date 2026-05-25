import json
import random
from proppulse_os.core.database import SessionLocal
from proppulse_os.lead_engine import models

def mock_extract_project_details(file_path):
    """
    Simulates extracting project details from a brochure PDF or image.
    In a real scenario, this would use OCR and LLMs.
    """
    projects = [
        {
            "name": "Luxury Sarjapur Villas",
            "micro_market": "Sarjapur",
            "base_price_sqft": 8500,
            "possession_year": 2026,
            "amenities": "Swimming Pool, Gym, Modular Kitchen, 24/7 Security"
        },
        {
            "name": "Whitefield Heights",
            "micro_market": "Whitefield",
            "base_price_sqft": 7200,
            "possession_year": 2025,
            "amenities": "Jogging Track, Clubhouse, Garden, Power Backup"
        }
    ]

    project_data = random.choice(projects)
    print(f"Extracted data from {file_path}: {project_data['name']}")

    # Persist to DB
    db = SessionLocal()
    try:
        # Check if project exists
        db_project = db.query(models.Project).filter(models.Project.name == project_data["name"]).first()
        if not db_project:
            db_project = models.Project(**project_data)
            # Simulate embedding generation
            db_project.amenities_embeddings = json.dumps([random.random() for _ in range(8)])
            db.add(db_project)
            db.commit()
            print(f"Saved new project: {project_data['name']}")
    finally:
        db.close()

    return project_data

if __name__ == "__main__":
    mock_extract_project_details("brochure_1.pdf")
    mock_extract_project_details("brochure_2.pdf")
