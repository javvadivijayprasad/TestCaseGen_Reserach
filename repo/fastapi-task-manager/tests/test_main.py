from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_read_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_create_task():
    """Test creating a task"""
    response = client.post(
        "/tasks/",
        json={"title": "Test Task", "description": "Test Description"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert "id" in data


def test_read_tasks():
    """Test reading all tasks"""
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_read_task():
    """Test reading a specific task"""
    # Create a task first
    create_response = client.post(
        "/tasks/",
        json={"title": "Task to Read", "description": "Description"}
    )
    task_id = create_response.json()["id"]
    
    # Read the task
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Task to Read"


def test_update_task():
    """Test updating a task"""
    # Create a task first
    create_response = client.post(
        "/tasks/",
        json={"title": "Task to Update", "description": "Original"}
    )
    task_id = create_response.json()["id"]
    
    # Update the task
    response = client.put(
        f"/tasks/{task_id}",
        json={"completed": True, "description": "Updated"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is True
    assert data["description"] == "Updated"


def test_delete_task():
    """Test deleting a task"""
    # Create a task first
    create_response = client.post(
        "/tasks/",
        json={"title": "Task to Delete", "description": "Will be deleted"}
    )
    task_id = create_response.json()["id"]
    
    # Delete the task
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404


def test_task_not_found():
    """Test 404 error for non-existent task"""
    response = client.get("/tasks/99999")
    assert response.status_code == 404