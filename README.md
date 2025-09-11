# Task Manager Backend

A comprehensive FastAPI-based backend application for task management with user authentication, CRUD operations, and integrated LLM capabilities using Ollama.

## Features

- **Task Management**: Full CRUD operations for tasks with advanced filtering and pagination
- **User Authentication**: JWT-based authentication system with secure password handling
- **LLM Integration**: Built-in Ollama integration for AI-powered task assistance and chat completion
- **Database**: SQLAlchemy ORM with Alembic for database migrations
- **RESTful API**: Well-structured API endpoints with proper documentation
- **CORS Support**: Configured for cross-origin requests from frontend applications

## Tech Stack

- **Backend**: FastAPI
- **Database**: SQLite (configurable to other databases)
- **ORM**: SQLAlchemy
- **Authentication**: JWT tokens with bcrypt password hashing
- **LLM**: Ollama integration
- **Migrations**: Alembic
- **Python**: 3.8+

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Ollama installed and running (for LLM features)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd task-manager-backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (optional):
```bash
cp .env.example .env  # If .env.example exists
# Edit .env with your configuration
```

5. Run database migrations:
```bash
alembic upgrade head
```

6. Start the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### API Tags

The API endpoints are organized into the following tags for better navigation and documentation:

- **`users`**: User authentication and management endpoints
- **`items`**: General item management endpoints
- **`tasks`**: Task management and CRUD operations
- **`llm`**: LLM integration and AI-powered features

### Key Endpoints

#### Authentication (`users` tag)
- `POST /users/register` - Register a new user
- `POST /users/login` - User login and JWT token generation

#### Tasks (`tasks` tag)
- `POST /tasks/` - Create a new task
- `GET /tasks/` - Get all tasks with pagination
- `GET /tasks/{task_id}` - Get a specific task
- `PUT /tasks/{task_id}` - Update a task
- `DELETE /tasks/{task_id}` - Delete a task
- `GET /tasks/user/{user_id}` - Get tasks by user
- `GET /tasks/status/{status}` - Get tasks by status

#### Items (`items` tag)
- `POST /items/` - Create a new item
- `GET /items/` - Get all items
- `GET /items/{item_id}` - Get a specific item
- `PUT /items/{item_id}` - Update an item
- `DELETE /items/{item_id}` - Delete an item

#### LLM Integration (`llm` tag)
- `POST /llm/chat` - Chat completion with Ollama
- `POST /llm/completion` - Text completion with Ollama
- `GET /llm/models` - List available Ollama models
- `POST /llm/models/pull` - Pull a new model
- `DELETE /llm/models/{model_name}` - Delete a model

## Project Structure

```
task-manager-backend/
├── alembic/
│   ├── versions/         # Database migration files
│   ├── env.py            # Alembic environment configuration
│   ├── script.py.mako    # Migration script template
│   └── README
├── app/
│   ├── routers/          # API route modules
│   │   ├── items.py      # Item-related endpoints
│   │   ├── llm.py        # LLM integration endpoints
│   │   ├── tasks.py      # Task management endpoints
│   │   └── users.py      # User authentication endpoints
│   ├── auth.py           # Authentication utilities
│   ├── config.py         # Application configuration
│   ├── crud.py           # Database CRUD operations
│   ├── database.py       # Database connection setup
│   ├── main.py           # FastAPI application entry point
│   ├── models.py         # SQLAlchemy database models
│   └── schemas.py        # Pydantic schemas for request/response
├── alembic.ini           # Alembic configuration
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Configuration

The application can be configured through environment variables. Key configuration options:

- `DATABASE_URL`: Database connection string (default: `sqlite:///./test.db`)
- `SECRET_KEY`: JWT secret key (default: `CHANGE_THIS` - change in production!)
- `OLLAMA_HOST`: Ollama server host (default: `http://localhost:11434`)
- `OLLAMA_MODEL`: Default Ollama model (default: `llama3.2`)
- `OLLAMA_TIMEOUT`: Ollama request timeout in seconds (default: `30`)

## Database Migrations

To create new database migrations:

1. Make changes to your models in `app/models.py`
2. Generate a migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```
3. Apply the migration:
```bash
alembic upgrade head
```

To rollback migrations:
```bash
alembic downgrade -1
```

## Development

### Running Tests

```bash
pytest
```

### Code Style

The project follows PEP 8 coding standards. You can check code style with:
```bash
flake8 app/
```

### Adding New Features

1. Add new models in `app/models.py`
2. Create corresponding schemas in `app/schemas.py`
3. Add CRUD operations in `app/crud.py`
4. Create API endpoints in appropriate router files under `app/routers/`
5. Generate and apply database migrations

## Security Notes

- Change the default `SECRET_KEY` in production
- Use HTTPS in production environments
- Implement rate limiting for API endpoints
- Validate all user inputs
- Keep dependencies updated

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
