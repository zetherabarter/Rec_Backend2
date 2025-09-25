# Recruitment Portal Backend

A FastAPI-based backend application for managing the recruitment process.

## Features

- User management with various recruitment stages
- Email communication tracking
- MongoDB integration for data persistence
- Docker support for easy deployment

## Project Structure

```
fastapi-app/
│── app/
│   ├── main.py                 # FastAPI application instance
│   ├── core/                   # Core configuration
│   │   ├── config.py          # Settings and configuration
│   │   └── init_db.py         # Database initialization
│   │
│   ├── models/                # Database models
│   │   ├── user.py           # User model
│   │   └── email.py          # Email model
│   │
│   ├── routes/                # API routes
│   │   ├── user_routes.py    # User endpoints
│   │   └── email_routes.py   # Email endpoints
│   │
│   ├── schemas/               # Pydantic models
│   │   ├── user_schema.py    # User schemas
│   │   └── email_schema.py   # Email schemas
│   │
│   ├── services/             # Business logic
│   │   ├── user_service.py   # User services
│   │   └── email_service.py  # Email services
│   │
│   └── utils/                # Utilities
│       └── enums.py          # Enumerations
```

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\\venv\\Scripts\\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and update the values

5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Docker Setup

1. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

2. Access the API at http://localhost:8000

## API Documentation

Once the application is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

1. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Run tests:
   ```bash
   pytest
   ```

## License

MIT
