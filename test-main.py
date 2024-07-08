from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create an SQLAlchemy engine for the in-memory SQLite database
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create a session factory for the testing session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the test database schema based on the SQLAlchemy Base metadata
Base.metadata.create_all(bind=engine)

# Override the get_db dependency to use the testing session
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the get_db dependency in the FastAPI app
app.dependency_overrides[get_db] = override_get_db

# Create a test client for the FastAPI app
client = TestClient(app)

# Test case: Create a new cart
def test_create_cart():
    response = client.post("/carts/", json={"items": [{"name": "item1", "price": 10}]})
    assert response.status_code == 200
    assert response.json()["id"] is not None

# Test case: Delete an existing cart
def test_delete_cart():
    response = client.post("/carts/", json={"items": [{"name": "item1", "price": 10}]})
    cart_id = response.json()["id"]
    response = client.delete(f"/carts/{cart_id}")
    assert response.status_code == 200

# Test case: Attempt to delete a non-existent cart
def test_delete_non_existent_cart():
    response = client.delete("/carts/9999")
    assert response.status_code == 404

# Test case: Remove an item from a cart
def test_remove_item_from_cart():
    response = client.post("/carts/", json={"items": [{"name": "item1", "price": 10}]})
    cart_id = response.json()["id"]
    response = client.post(f"/carts/{cart_id}/items/", json={"name": "item1", "price": 10})
    response = client.delete(f"/carts/{cart_id}/items/1")
    assert response.status_code == 200

# Test case: Attempt to remove a non-existent item from a cart
def test_remove_non_existent_item_from_cart():
    response = client.post("/carts/", json={"items": [{"name": "item1", "price": 10}]})
    cart_id = response.json()["id"]
    response = client.delete(f"/carts/{cart_id}/items/9999")
    assert response.status_code == 404

