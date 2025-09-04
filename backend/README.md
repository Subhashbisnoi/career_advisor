# AI Interviewer - Backend

This is the backend service for the AI Interviewer application, built with FastAPI and PostgreSQL.

## Features

- User authentication (JWT)
- Interview session management
- Chat history storage
- Secure password hashing
- RESTful API endpoints

## Prerequisites

- Python 3.8+
- PostgreSQL (or SQLite for development)
- pip (Python package manager)

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Interviewer/backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` with your configuration.

5. **Initialize the database**
   ```bash
   python init_db.py
   ```
   To include sample data, uncomment the `create_sample_data()` line in `init_db.py` before running.

6. **Run the development server**
   ```bash
   uvicorn main:app --reload
   ```

## API Documentation

Once the server is running, you can access:

- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

## Project Structure

```
backend/
├── api/
│   ├── __init__.py
│   ├── auth.py        # Authentication endpoints
│   ├── interview.py   # Interview endpoints
│   ├── tts.py         # Text-to-speech endpoints
│   └── voice.py       # Voice processing endpoints
├── models.py          # Database models
├── database.py        # Database configuration
├── init_db.py         # Database initialization
├── main.py            # FastAPI application
└── requirements.txt   # Python dependencies
```

## Environment Variables

- `DATABASE_URL`: Database connection string (e.g., `postgresql://user:password@localhost/dbname`)
- `SECRET_KEY`: Secret key for JWT token generation
- `ALGORITHM`: Algorithm for JWT (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes (default: 30)
- `OPENAI_API_KEY`: API key for OpenAI services

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
```

### Linting
```bash
flake8
```

## Deployment

For production deployment, consider using:
- Gunicorn with Uvicorn workers
- Environment variable management
- Proper database backups
- HTTPS/TLS configuration
- CORS restrictions
- Rate limiting
