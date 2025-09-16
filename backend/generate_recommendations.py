#!/usr/bin/env python3
"""
Script to generate career recommendations for completed assessments.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db
from models import CareerAssessment, User
from api.careers import generate_career_recommendations
import asyncio

async def generate_recommendations_for_completed_assessments():
    """Generate career recommendations for all completed assessments that don't have them."""
    print("Generating career recommendations...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Find completed assessments
        completed_assessments = db.query(CareerAssessment).filter(
            CareerAssessment.status == "completed"
        ).all()
        
        print(f"Found {len(completed_assessments)} completed assessments")
        
        for assessment in completed_assessments:
            user = db.query(User).filter(User.id == assessment.user_id).first()
            if not user:
                print(f"User {assessment.user_id} not found, skipping...")
                continue
                
            print(f"Generating recommendations for assessment {assessment.id} (user: {user.email})")
            
            try:
                # Generate career recommendations
                recommendations_result = await generate_career_recommendations(user, db, assessment)
                print(f"  Generated {len(recommendations_result.get('recommendations', []))} recommendations")
                
            except Exception as e:
                print(f"  Error generating recommendations: {e}")
                continue
        
        print("Career recommendations generation completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(generate_recommendations_for_completed_assessments())
