#!/usr/bin/env python3

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_exact_frontend_flow():
    """Test the exact same flow as frontend"""
    
    print("=" * 60)
    print("DEBUGGING AUTHENTICATION - FRONTEND FLOW SIMULATION")
    print("=" * 60)
    
    # Step 1: Login (simulating frontend login)
    print("\n1. Testing login...")
    login_data = {
        "username": "test@example.com",
        "password": "testpass123"
    }
    
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    print(f"Login Status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        # Try signup first
        print("\n1b. User doesn't exist, trying signup...")
        signup_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User"
        }
        
        signup_response = requests.post(
            f"{BASE_URL}/auth/signup",
            json=signup_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Signup Status: {signup_response.status_code}")
        if signup_response.status_code == 200:
            login_result = signup_response.json()
        else:
            print(f"Signup failed: {signup_response.text}")
            return
    else:
        login_result = login_response.json()
    
    # Extract token
    token = login_result.get("access_token")
    user = login_result.get("user")
    
    print(f"Token received: {token[:20]}..." if token else "NO TOKEN")
    print(f"User: {user}")
    
    if not token:
        print("FATAL: No token received")
        return
    
    # Step 2: Start assessment (simulating frontend assessment start)
    print("\n2. Testing assessment start...")
    
    assessment_request = {
        "assessment_type": "comprehensive",
        "user_background": {
            "experience_level": "beginner",
            "current_field": "technology"
        }
    }
    
    assessment_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    assessment_response = requests.post(
        f"{BASE_URL}/assessment/start",
        json=assessment_request,
        headers=assessment_headers
    )
    
    print(f"Assessment Start Status: {assessment_response.status_code}")
    
    if assessment_response.status_code != 200:
        print(f"Assessment start failed: {assessment_response.text}")
        return
    
    assessment_data = assessment_response.json()
    thread_id = assessment_data.get("thread_id")
    
    print(f"Assessment started successfully!")
    print(f"Thread ID: {thread_id}")
    print(f"Questions received: {len(assessment_data.get('questions', []))}")
    
    # Step 3: Submit responses (simulating exact frontend submission)
    print("\n3. Testing submit responses (exact frontend pattern)...")
    
    responses_request = {
        "thread_id": thread_id,
        "responses": [
            {
                "question_id": "q1",
                "response": "python",
                "confidence_level": 4
            },
            {
                "question_id": "q2",
                "response": "startup", 
                "confidence_level": 5
            }
        ]
    }
    
    print(f"Request body: {json.dumps(responses_request, indent=2)}")
    print(f"Headers: {assessment_headers}")
    
    submit_response = requests.post(
        f"{BASE_URL}/assessment/submit-responses",
        json=responses_request,
        headers=assessment_headers
    )
    
    print(f"Submit Status: {submit_response.status_code}")
    print(f"Submit Response: {submit_response.text}")
    
    if submit_response.status_code == 401:
        print("\n🚨 FOUND THE 401 ERROR!")
        print("Let's debug this...")
        
        # Debug token
        print(f"\nToken being used: {token}")
        
        # Test /auth/me endpoint
        print("\n4. Testing /auth/me endpoint...")
        me_response = requests.get(
            f"{BASE_URL}/auth/me",
            headers=assessment_headers
        )
        
        print(f"Me endpoint status: {me_response.status_code}")
        print(f"Me endpoint response: {me_response.text}")
        
        if me_response.status_code == 401:
            print("❌ Token validation is failing on /auth/me too")
        else:
            print("✅ Token works for /auth/me but not for /assessment/submit-responses")
            print("This suggests an issue with the assessment endpoint specifically")
    
    elif submit_response.status_code == 200:
        print("✅ Submit successful!")
        submit_result = submit_response.json()
        print(f"Result: {submit_result}")
    
    else:
        print(f"❌ Unexpected error: {submit_response.status_code}")
        print(f"Response: {submit_response.text}")

if __name__ == "__main__":
    test_exact_frontend_flow()
