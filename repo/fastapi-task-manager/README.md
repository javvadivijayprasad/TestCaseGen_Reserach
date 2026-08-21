# Task Manager API

A simple and clean REST API built with FastAPI for managing tasks. Perfect for learning FastAPI fundamentals.

## Features

- ✅ Create, read, update, and delete tasks (CRUD operations)
- ✅ Filter tasks by completion status
- ✅ SQLite database with SQLAlchemy ORM
- ✅ Pydantic models for data validation
- ✅ Comprehensive test suite with pytest
- ✅ Interactive API documentation (Swagger UI)
- ✅ Type hints throughout the codebase
- ✅ Clean project structure following best practices

## Technologies

- **FastAPI** - Modern web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation using Python type hints
- **SQLite** - Lightweight database
- **Pytest** - Testing framework
- **Uvicorn** - ASGI server

## Project Structure

```
fastapi-task-manager/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application and routes
│   ├── models.py        # SQLAlchemy database models
│   ├── schemas.py       # Pydantic schemas
│   ├── crud.py          # Database operations
│   └── database.py      # Database configuration
├── tests/
│   ├── __init__.py
│   └── test_main.py     # API tests
├── requirements.txt     # Project dependencies
├── README.md
└── .gitignore
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone the repository:
```bash
git clone git@github.com:yourusername/fastapi-task-manager.git
cd fastapi-task-manager
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Development Mode (with auto-reload)
Start the development server using the FastAPI CLI:
```bash
fastapi dev app/main.py
```

### Production Mode (optimized)
For production deployment:
```bash
fastapi run app/main.py
```

The API will be available at `http://127.0.0.1:8000`

### Interactive Documentation

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API Endpoints

### Root
- `GET /` - Welcome message

### Tasks
- `POST /tasks/` - Create a new task
- `GET /tasks/` - Get all tasks (supports filtering and pagination)
- `GET /tasks/{task_id}` - Get a specific task
- `PUT /tasks/{task_id}` - Update a task
- `DELETE /tasks/{task_id}` - Delete a task

## Usage Examples

### Create a Task
```bash
curl -X POST "http://127.0.0.1:8000/tasks/" \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn FastAPI", "description": "Complete the tutorial", "completed": false}'
```

### Get All Tasks
```bash
curl "http://127.0.0.1:8000/tasks/"
```

### Get Completed Tasks
```bash
curl "http://127.0.0.1:8000/tasks/?completed=true"
```

### Update a Task
```bash
curl -X PUT "http://127.0.0.1:8000/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

### Delete a Task
```bash
curl -X DELETE "http://127.0.0.1:8000/tasks/1"
```

## Running Tests

Execute the test suite:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app tests/
```

## Docker Support (Optional)

### Build and Run with Docker

1. Build the Docker image:
```bash
docker build -t fastapi-task-manager .
```

2. Run the container:
```bash
docker run -p 8000:8000 fastapi-task-manager
```

### Using Docker Compose

```bash
docker-compose up
```

The API will be available at `http://localhost:8000`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Inspired by the FastAPI community