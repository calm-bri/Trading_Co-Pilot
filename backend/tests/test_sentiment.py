import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)

@pytest.fixture
def auth_token(client):
    """Get authentication token for tests"""
    # Register a test user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    client.post("/auth/register", json=user_data)

    # Login to get token
    login_response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "testpass123"
    })
    return login_response.json()["access_token"]

def test_analyze_text_sentiment(client, auth_token):
    """Test single text sentiment analysis"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    test_text = "This stock is performing amazingly well!"

    response = client.post("/sentiment/analyze", json={"text": test_text}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "label" in data
    assert "score" in data
    assert "sentiment" in data
    assert data["sentiment"] in ["positive", "negative"]

def test_analyze_batch_sentiment(client, auth_token):
    """Test batch sentiment analysis"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    test_texts = [
        "Great earnings report!",
        "Stock is crashing badly",
        "Market is stable today"
    ]

    response = client.post("/sentiment/analyze/batch", json={"texts": test_texts}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == len(test_texts)
    for result in data:
        assert "label" in result
        assert "score" in result
        assert "sentiment" in result

def test_calculate_overall_sentiment(client, auth_token):
    """Test overall sentiment calculation"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    test_texts = [
        "Excellent performance!",
        "Good results this quarter",
        "Outstanding growth"
    ]

    response = client.post("/sentiment/overall", json={"texts": test_texts}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "overall_sentiment" in data
    assert "average_score" in data
    assert "positive_ratio" in data
    assert "analysis_count" in data
    assert data["overall_sentiment"] in ["positive", "negative", "neutral"]

def test_sentiment_with_empty_texts(client, auth_token):
    """Test overall sentiment with empty text list"""
    headers = {"Authorization": f"Bearer {auth_token}"}

    response = client.post("/sentiment/overall", json={"texts": []}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["overall_sentiment"] == "neutral"
    assert data["average_score"] == 0.5
    assert data["positive_ratio"] == 0.5
    assert data["analysis_count"] == 0

def test_get_sentiment_feed(client, auth_token):
    """Test getting sentiment feed"""
    headers = {"Authorization": f"Bearer {auth_token}"}

    response = client.get("/sentiment/feed", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Feed might be empty if no data sources are configured

def test_sentiment_unauthorized(client):
    """Test sentiment endpoints without authentication"""
    test_text = "This is a test"

    # Test single analysis
    response = client.post("/sentiment/analyze", json={"text": test_text})
    assert response.status_code == 401

    # Test batch analysis
    response = client.post("/sentiment/analyze/batch", json={"texts": [test_text]})
    assert response.status_code == 401

    # Test overall sentiment
    response = client.post("/sentiment/overall", json={"texts": [test_text]})
    assert response.status_code == 401

    # Test feed
    response = client.get("/sentiment/feed")
    assert response.status_code == 401
