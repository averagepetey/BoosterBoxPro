"""
Authentication schemas for request/response models
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models.user import SubscriptionStatus


class UserRegisterRequest(BaseModel):
    """Request schema for user registration"""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    username: Optional[str] = Field(None, max_length=100, description="Optional username")


class UserRegisterResponse(BaseModel):
    """Response schema for user registration"""
    
    id: UUID
    email: str
    username: Optional[str] = None
    subscription_status: str
    trial_ended_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserLoginRequest(BaseModel):
    """Request schema for user login"""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserLoginResponse(BaseModel):
    """Response schema for user login"""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user_id: UUID = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    subscription_status: str = Field(..., description="Current subscription status")
    trial_days_remaining: Optional[int] = Field(None, description="Days remaining in trial")


class UserResponse(BaseModel):
    """Response schema for user info"""
    
    id: UUID
    email: str
    username: Optional[str] = None
    subscription_status: str
    trial_started_at: Optional[datetime] = None
    trial_ended_at: Optional[datetime] = None
    trial_days_remaining: Optional[int] = None
    has_active_access: bool
    
    model_config = ConfigDict(from_attributes=True)


class SubscriptionStatusResponse(BaseModel):
    """Response schema for subscription status"""
    
    subscription_status: str
    trial_active: bool
    trial_days_remaining: Optional[int] = None
    subscription_active: bool
    has_active_access: bool
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None

