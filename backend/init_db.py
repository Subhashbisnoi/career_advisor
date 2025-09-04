import sys
import os
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from database import engine, Base, get_db
from models import User, InterviewSession, ChatMessage

# Initialize password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    """Initialize the database with tables and sample data."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def create_sample_data():
    """Create sample data for testing if it doesn't already exist."""
    print("Checking for existing sample data...")
    
    # Get a database session
    db = Session(engine, expire_on_commit=False)
    
    try:
        # Check if sample user already exists
        user = db.query(User).filter(User.email == "test@example.com").first()
        
        if user:
            print("Sample data already exists. Skipping creation.")
            return
            
        print("Creating sample data...")
        
        # Create a sample user
        user = User(
            email="test@example.com",
            full_name="Test User",
            hashed_password=pwd_context.hash("testpassword"),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create a sample interview session
        interview = InterviewSession(
            user_id=user.id,
            role="Software Engineer",
            company="Tech Corp",
            created_at=datetime.now(timezone.utc)
        )
        db.add(interview)
        db.commit()
        db.refresh(interview)
        
        # Create sample chat messages
        messages = [
            {
                "session_id": interview.id,
                "role": "assistant",
                "content": "Welcome to your interview for the Software Engineer position at Tech Corp. Let's start with some basic questions.",
                "metadata": {"question_type": "introduction"}
            },
            {
                "session_id": interview.id,
                "role": "user",
                "content": "Thank you, I'm excited to be here!",
                "metadata": {}
            },
            {
                "session_id": interview.id,
                "role": "assistant",
                "content": "Can you tell me about your experience with Python?",
                "metadata": {"question_type": "technical"}
            }
        ]
        
        for msg in messages:
            chat_msg = ChatMessage(
                session_id=msg["session_id"],
                role=msg["role"],
                content=msg["content"],
                metadata=msg["metadata"],
                created_at=datetime.now(timezone.utc)
            )
            db.add(chat_msg)
        
        db.commit()
        print("Sample data created successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating sample data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    # Initialize the database
    init_db()
    
    # Create sample data
    create_sample_data()
