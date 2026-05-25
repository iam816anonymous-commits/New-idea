from proppulse_os.core.config import settings
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from proppulse_os.core.database import Base, get_db
from proppulse_os.lead_engine.main import app
from unittest.mock import patch

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

def test_health():
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_project():
    response = client.post(
        "/v1/projects",
        headers={"X-API-Key": settings.API_KEY, "X-Brokerage-ID": "test_broker"},
        json={"name": "Test Project", "micro_market": "Test Market", "base_price_sqft": 5000, "possession_year": 2027, "amenities": "None"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Project"

def test_capture_lead():
    # Mock background tasks to avoid DB race conditions in tests
    with patch("fastapi.BackgroundTasks.add_task") as mock_add_task:
        # First create project
        client.post(
            "/v1/projects",
            headers={"X-API-Key": settings.API_KEY, "X-Brokerage-ID": "test_broker"},
            json={"name": "Test Project", "micro_market": "Test Market", "base_price_sqft": 5000, "possession_year": 2027, "amenities": "None"}
        )

        response = client.post(
            "/v1/leads",
            headers={"X-API-Key": settings.API_KEY, "X-Brokerage-ID": "test_broker"},
            json={"name": "Lead Test", "phone_number": "+919876543210", "project_name": "Test Project"}
        )
        assert response.status_code == 200
        assert "lead_id" in response.json()
        assert mock_add_task.called

def test_invalid_phone():
    response = client.post(
        "/v1/leads",
        headers={"X-API-Key": settings.API_KEY},
        json={"name": "Fail", "phone_number": "invalid", "project_name": "Test"}
    )
    assert response.status_code == 422
