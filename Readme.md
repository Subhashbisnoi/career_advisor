# AI Interviewer

An AI-powered interview practice application that generates personalized questions based on your resume, provides instant feedback, and creates a personalized learning roadmap.

## Features

- **AI-Generated Questions**: Get personalized interview questions based on your resume and target role
- **Interactive Interview**: Answer questions with a modern, user-friendly interface
- **Instant Feedback**: Receive detailed feedback and scoring for each answer
- **Learning Roadmap**: Get a personalized plan to improve your skills
- **Resume Analysis**: Upload PDF resumes for AI analysis
- **Session Management**: Track your interview sessions and progress
- **User Authentication**: Secure login/signup with email or Google OAuth
- **Google Sign-In**: Quick authentication using your Google account

## Architecture

The application is built with a modern backend/frontend architecture:

### Backend
- **FastAPI**: High-performance Python web framework
- **LangChain**: AI/LLM integration for question generation and feedback
- **LangGraph**: Workflow orchestration for the interview process
- **PDF Processing**: Resume text extraction using pdfplumber

### Frontend
- **React**: Modern JavaScript framework for the user interface
- **Tailwind CSS**: Utility-first CSS framework for styling
- **React Router**: Client-side routing
- **React Dropzone**: File upload handling
- **Lucide React**: Beautiful icons

## Project Structure

```
interviewer/
├── backend/                 # FastAPI backend
│   ├── api/                # API routes
│   ├── venv/               # Python virtual environment
│   ├── *.py                # Core application files
│   ├── requirements.txt    # Python dependencies
│   └── start.sh           # Backend startup script
├── frontend/               # React frontend
│   ├── src/                # Source code
│   ├── public/             # Static files
│   ├── package.json        # Node.js dependencies
│   ├── tailwind.config.js  # Tailwind configuration
│   └── start.sh           # Frontend startup script
└── README.md              # This file
```

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- OpenAI API key (or compatible API)

## Setup Instructions

### 1. Environment Setup

Create environment files in both directories:

#### Backend Environment
```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` with your configuration:

```env
# Database
DATABASE_URL=sqlite:///./interviewer.db

# JWT Configuration
SECRET_KEY=your-super-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Google OAuth (Optional - for Google Sign-In)
GOOGLE_CLIENT_ID=your-google-client-id-here

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://openrouter.ai/api/v1  # Optional: for OpenRouter

# Environment
ENVIRONMENT=development
DEBUG=True
```

#### Frontend Environment
```bash
cd frontend
cp .env.example .env
```

Edit `frontend/.env` with your configuration:

```env
REACT_APP_API_URL=http://localhost:8000

# Google OAuth (Optional - for Google Sign-In)
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id-here
```

#### Google OAuth Setup (Optional)
If you want to enable Google Sign-In, follow the detailed instructions in `GOOGLE_OAUTH_SETUP.md`.

### 2. Backend Setup

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
./start.sh
```

The backend will run on `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
./start.sh
```

The frontend will run on `http://localhost:3000`

## Usage

1. **Sign Up/Login**: Create an account or sign in with email/password or Google
2. **Upload Resume**: Upload your PDF resume
3. **Set Target**: Specify your target role and company
4. **Start Interview**: AI generates personalized questions
5. **Answer Questions**: Provide detailed answers to each question
6. **Get Feedback**: Receive instant feedback and scoring
7. **View Roadmap**: Get a personalized learning plan

## API Endpoints

### Authentication
- `POST /auth/signup` - Create new user account
- `POST /auth/login` - User login with email/password
- `POST /auth/google` - Google OAuth authentication
- `GET /auth/me` - Get current user profile

### Interview Management
- `POST /interview/upload-resume` - Upload resume PDF
- `POST /interview/start` - Start new interview session
- `POST /interview/submit-answers` - Submit interview answers
- `GET /interview/session/{session_id}` - Get session details
- `GET /interview/sessions` - List all sessions

### Health Check
- `GET /health` - API health status

## Development

### Backend Development
- The backend uses FastAPI with automatic API documentation
- Visit `http://localhost:8000/docs` for interactive API docs
- The workflow is orchestrated using LangGraph

### Frontend Development
- Built with React 18 and modern hooks
- Uses Tailwind CSS for responsive design
- Component-based architecture for maintainability

## Workflow

The interview process follows this workflow:

1. **Resume Upload** → PDF processing and text extraction
2. **Question Generation** → AI generates role-specific questions
3. **Answer Collection** → User provides answers to each question
4. **Feedback Generation** → AI evaluates answers and provides feedback
5. **Roadmap Creation** → Personalized learning plan generation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on the GitHub repository.

## Future Enhancements

- Database integration for persistent storage
- User authentication and profiles
- Interview history and analytics
- Multiple interview formats
- Video interview support
- Integration with learning platforms
