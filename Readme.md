# Personalized Career and Skills Advisor

An AI-powered career guidance platform that maps skills, recommends personalized career paths, and prepares students for the evolving job market with actionable insights tailored to the Indian context.

## Challenge
Students in India often face a bewildering array of career choices, compounded by generic guidance that fails to account for their unique interests, aptitudes, and the rapidly evolving job market. Traditional career counseling struggles to keep pace with emerging job roles and specific skills required for success, leaving many students feeling lost and unprepared.

## Objective
Leverage Google Cloud's generative AI to design an innovative solution that serves as a personalized career and skills advisor for Indian students. The platform goes beyond generic advice, using individual profiles to intelligently recommend suitable career paths and outline specific, actionable skills required for success in the modern job market.

## Features

- **Comprehensive Skills Assessment**: Evaluate technical and soft skills relevant to the Indian job market
- **AI-Powered Career Mapping**: Get personalized career path recommendations based on your unique profile
- **Skills Gap Analysis**: Identify strengths and areas for improvement with detailed analysis
- **Personalized Learning Roadmaps**: Receive step-by-step plans tailored to your chosen career path
- **Market Trend Integration**: Stay updated with emerging job roles and industry requirements
- **Interactive Career Exploration**: Discover new career possibilities through guided assessments
- **Progress Tracking**: Monitor your skill development journey over time
- **User Authentication**: Secure login/signup with email or Google OAuth
- **Document Analysis**: Upload resumes and academic transcripts for comprehensive analysis

## Architecture

The application is built with a modern backend/frontend architecture:

### Backend
- **FastAPI**: High-performance Python web framework for robust API development
- **LangChain**: AI/LLM integration for career analysis and recommendations
- **LangGraph**: Workflow orchestration for the career assessment process
- **Document Processing**: Resume and transcript analysis using advanced NLP
- **Skills Database**: Comprehensive database of skills mapped to career paths

### Frontend
- **React**: Modern JavaScript framework for dynamic user interface
- **Tailwind CSS**: Utility-first CSS framework for responsive design
- **React Router**: Client-side routing for seamless navigation
- **Data Visualization**: Interactive charts and graphs for skills and career insights
- **Lucide React**: Beautiful icons and visual elements

## Project Structure

```
career-advisor/
├── backend/                    # FastAPI backend
│   ├── api/                   # API routes
│   │   ├── assessment.py      # Career assessment endpoints
│   │   ├── skills.py          # Skills analysis endpoints
│   │   ├── careers.py         # Career recommendation endpoints
│   │   └── roadmap.py         # Learning roadmap endpoints
│   ├── workflows/             # Career assessment workflows
│   ├── models/               # Data models and schemas
│   ├── services/             # Business logic services
│   ├── requirements.txt      # Python dependencies
│   └── start.sh             # Backend startup script
├── frontend/                 # React frontend
│   ├── src/                 # Source code
│   │   ├── components/      # React components
│   │   │   ├── assessment/  # Career assessment components
│   │   │   ├── skills/      # Skills analysis components
│   │   │   ├── careers/     # Career exploration components
│   │   │   └── roadmap/     # Learning roadmap components
│   │   └── pages/           # Main page components
│   ├── public/              # Static files
│   ├── package.json         # Node.js dependencies
│   └── start.sh            # Frontend startup script
└── README.md               # This file
```

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- OpenAI API key or Google Cloud AI Platform access
- Google Cloud credentials (for enhanced AI capabilities)

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
DATABASE_URL=sqlite:///./career_advisor.db

# JWT Configuration
SECRET_KEY=your-super-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Google OAuth (Optional - for Google Sign-In)
GOOGLE_CLIENT_ID=your-google-client-id-here

# AI Configuration
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_CLOUD_PROJECT_ID=your-google-cloud-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json

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
2. **Complete Profile**: Provide basic information about your academic background and interests
3. **Take Assessment**: Complete comprehensive skills and aptitude assessments
4. **Explore Careers**: Discover personalized career recommendations based on your profile
5. **Skills Analysis**: Get detailed analysis of your current skills and market requirements
6. **Learning Roadmap**: Receive step-by-step plans to achieve your career goals
7. **Track Progress**: Monitor your skill development and career preparation journey

## API Endpoints

### Authentication
- `POST /auth/signup` - Create new user account
- `POST /auth/login` - User login with email/password
- `POST /auth/google` - Google OAuth authentication
- `GET /auth/me` - Get current user profile

### Career Assessment
- `POST /assessment/start` - Begin career assessment process
- `POST /assessment/submit` - Submit assessment responses
- `GET /assessment/results/{assessment_id}` - Get assessment results
- `GET /assessment/history` - List all assessments

### Skills Analysis
- `POST /skills/analyze` - Analyze current skills from documents/input
- `GET /skills/gaps/{career_path}` - Identify skills gaps for specific career
- `GET /skills/trending` - Get trending skills in Indian job market

### Career Recommendations
- `GET /careers/recommend/{user_id}` - Get personalized career recommendations
- `GET /careers/details/{career_path}` - Get detailed career information
- `GET /careers/market-trends` - Get job market trends and insights

### Learning Roadmaps
- `POST /roadmap/generate` - Generate personalized learning roadmap
- `GET /roadmap/{roadmap_id}` - Get specific roadmap details
- `POST /roadmap/update-progress` - Update learning progress

### Health Check
- `GET /health` - API health status

## Development

### Backend Development
- The backend uses FastAPI with automatic API documentation
- Visit `http://localhost:8000/docs` for interactive API docs
- Career assessment workflow is orchestrated using LangGraph
- AI-powered analysis using Google Cloud AI Platform and OpenAI

### Frontend Development
- Built with React 18 and modern hooks
- Uses Tailwind CSS for responsive design
- Component-based architecture for maintainability
- Interactive visualizations for skills and career data

## Career Assessment Workflow

The career guidance process follows this workflow:

1. **Profile Creation** → Collect basic academic and personal information
2. **Skills Assessment** → Comprehensive evaluation of technical and soft skills
3. **Aptitude Testing** → Assess logical reasoning, analytical thinking, and domain-specific aptitudes
4. **Interest Analysis** → Identify career interests and preferences
5. **Market Matching** → AI-powered matching with suitable career paths
6. **Gap Analysis** → Identify skills gaps and improvement areas
7. **Roadmap Generation** → Create personalized learning and development plan

## Key Features for Indian Students

### Localized Career Paths
- Focus on careers relevant to the Indian job market
- Integration with local industry requirements and trends
- Support for both traditional and emerging career options

### Skills Framework
- Technical skills mapping for IT, Engineering, Finance, Healthcare
- Soft skills evaluation crucial for Indian workplace culture
- Language proficiency assessment (English, regional languages)

### Market Intelligence
- Real-time job market trends in major Indian cities
- Salary benchmarks and growth prospects
- Company-specific requirements and preferences

### Educational Pathways
- Integration with Indian education system (10+2, graduation, post-graduation)
- Alternative learning paths (online courses, certifications, bootcamps)
- Entrance exam guidance for professional courses

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

- **Advanced AI Integration**: Enhanced Google Cloud AI Platform features
- **Career Mentorship**: Connect with industry professionals
- **Company Partnerships**: Direct integration with hiring platforms
- **Mobile Application**: Native mobile app for better accessibility
- **Multilingual Support**: Support for regional Indian languages
- **Video Interviews**: AI-powered mock interview practice
- **Certification Tracking**: Integration with online learning platforms
- **Industry-Specific Modules**: Specialized assessments for different sectors
- **Alumni Networks**: Connect with successful professionals in chosen fields
- **Real-time Job Matching**: Direct integration with job portals

## Impact Goals

- **Empowering Students**: Help students make informed career decisions
- **Reducing Uncertainty**: Provide clear, actionable career guidance
- **Bridging Skills Gap**: Align student skills with market requirements
- **Democratizing Access**: Make quality career counseling accessible to all
- **Supporting Growth**: Enable continuous professional development


## ✅ Deployment Status
- Latest vercel.json configuration fixed
- Ready for production deployment
