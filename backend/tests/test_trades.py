import pytest
from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime

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

@pytest.fixture
def sample_trade():
    """Sample trade data for testing"""
    return {
        "symbol": "AAPL",
        "side": "buy",
        "quantity": 100,
        "price": 150.50,
        "timestamp": datetime.now().isoformat(),
        "strategy": "momentum",
        "notes": "Test trade"
    }

def test_create_trade(client, auth_token, sample_trade):
    """Test creating a new trade"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/trades/", json=sample_trade, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == sample_trade["symbol"]
    assert data["side"] == sample_trade["side"]
    assert data["quantity"] == sample_trade["quantity"]

def test_get_trades(client, auth_token, sample_trade):
    """Test getting user's trades"""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create a trade first
    client.post("/trades/", json=sample_trade, headers=headers)

    # Get trades
    response = client.get("/trades/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_get_trade_by_id(client, auth_token, sample_trade):
    """Test getting a specific trade by ID"""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create a trade first
    create_response = client.post("/trades/", json=sample_trade, headers=headers)
    trade_id = create_response.json()["id"]

    # Get the specific trade
    response = client.get(f"/trades/{trade_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == trade_id
    assert data["symbol"] == sample_trade["symbol"]

def test_update_trade(client, auth_token, sample_trade):
    """Test updating a trade"""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create a trade first
    create_response = client.post("/trades/", json=sample_trade, headers=headers)
    trade_id = create_response.json()["id"]

    # Update the trade
    update_data = sample_trade.copy()
    update_data["quantity"] = 200
    update_data["notes"] = "Updated test trade"

    response = client.put(f"/trades/{trade_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 200
    assert data["notes"] == "Updated test trade"

def test_delete_trade(client, auth_token, sample_trade):
    """Test deleting a trade"""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create a trade first
    create_response = client.post("/trades/", json=sample_trade, headers=headers)
    trade_id = create_response.json()["id"]

    # Delete the trade
    response = client.delete(f"/trades/{trade_id}", headers=headers)
    assert response.status_code == 200

    # Verify it's deleted
    get_response = client.get(f"/trades/{trade_id}", headers=headers)
    assert get_response.status_code == 404

def test_get_portfolio_summary(client, auth_token, sample_trade):
    """Test getting portfolio summary"""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create a trade first
    client.post("/trades/", json=sample_trade, headers=headers)

    # Get portfolio summary
    response = client.get("/trades/portfolio/summary", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_trades" in data
    assert "total_value" in data
