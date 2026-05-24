import json
import random

def mock_extract_project_details(file_path):
    """
    Simulates extracting project details from a brochure PDF or image.
    In a real scenario, this would use OCR and LLMs.
    """
    # Sample data to return
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

    # Simulate some processing time and return a random sample or based on filename
    project_data = random.choice(projects)
    print(f"Extracted data from {file_path}: {project_data['name']}")
    return project_data

if __name__ == "__main__":
    # Test the parser
    data = mock_extract_project_details("sample_brochure.pdf")
    print(json.dumps(data, indent=2))
