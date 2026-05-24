import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Base, get_db
from api.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_project():
    response = client.post(
        "/v1/projects",
        json={"name": "Test Project", "micro_market": "Test Market", "base_price_sqft": 5000, "possession_year": 2027, "amenities": "None"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Project"

def test_capture_lead():
    # First create project
    client.post(
        "/v1/projects",
        json={"name": "Test Project", "micro_market": "Test Market", "base_price_sqft": 5000, "possession_year": 2027, "amenities": "None"}
    )

    response = client.post(
        "/v1/leads",
        json={"name": "Lead Test", "phone_number": "1234567890", "project_name": "Test Project"}
    )
    assert response.status_code == 200
    assert "lead_id" in response.json()
