from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, description="Full name is required")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters long")

class UserInDB(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class UserResponse(UserInDB):
    """User response model for API responses"""
    pass

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupRequest(UserCreate):
    """Signup request with validation"""
    pass
